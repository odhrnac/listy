import importlib.util
import os
import threading
import uuid
from datetime import date

from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from generator.models import GenerationJob, UserProfile
from .forms import TemplateForm, ImageAssetForm, TemplatePlacedImageForm, TemplateFieldForm, GenerateForm
from .jobs import process_job
from .models import Template, ImageAsset, TemplatePlacedImage, TemplateField
from .pdf_renderer import PLAYWRIGHT_MISSING
from .rendering import letter_document
from .sample_data import excel_rows, build_context

from config import get_letter_date, OUTPUT_DIR
from readers import read_excel

# Used for the preview when the template has no sample Excel
BUILTIN_SAMPLE_DATA = {
    'PHName': 'Jón Jónsson',
    'PHAddrPermStreet': 'Laugavegur',
    'PHAddrPermNumber': '100',
    'PHAddrPermZIP': '101',
    'PHAddrPermTown': 'Reykjavík',
    'ContractNumber': 'C-12345',
    'PremiumOwed': '1906.81',
    'PHGenderCode': 'M',
    'RegionCode': 'ISreg',
}


@login_required
def template_list(request):
    """List all shared templates."""
    templates = Template.objects.all()
    return render(request, 'doctemplates/template_list.html', {'templates': templates})

@login_required
def template_edit(request, template_id=None):
    """Create a new template or edit an existing one, with live preview."""
    if template_id:
        template = get_object_or_404(Template, id=template_id)
    else:
        template = None

    preview = None

    if request.method == 'POST':
        form = TemplateForm(request.POST, request.FILES, instance=template)
        if form.is_valid():
            # If the user clicked "Preview", don't save yet; just render preview
            if 'preview' in request.POST:
                # Build a temporary Template instance to render
                temp_template = form.save(commit=False)
                if template:
                    temp_template.id = template.id  # to keep pk for rendered context
                preview = _render_preview(temp_template, form.cleaned_data.get('preview_row') or 1)
            else:
                form.save()
                return redirect('template_list')
        else:
            # If form invalid, still allow preview if requested
            if 'preview' in request.POST:
                temp_template = Template(
                    html_content=request.POST.get('html_content', ''),
                    css_content=request.POST.get('css_content', ''),
                )
                preview = _render_preview(temp_template)
    else:
        form = TemplateForm(instance=template)

    return render(request, 'doctemplates/template_edit.html', {
        'form': form,
        'template': template,
        'preview': preview,
    })


def _preview_data(template, preview_row):
    """Context for the preview: chosen row of the sample Excel (with its second-Excel rows), or built-in data."""
    rows = excel_rows(template.sample_excel)
    if not rows:
        data = dict(BUILTIN_SAMPLE_DATA, letter_date=get_letter_date())
        return data, 'Built-in sample data (upload a sample Excel to preview real columns)'
    index = min(max(preview_row, 1), len(rows)) - 1
    context = build_context(template, rows[index], excel_rows(template.detail_excel))
    context['letter_date'] = get_letter_date()
    info = f'Sample Excel row {index + 1} of {len(rows)}'
    if template.detail_excel:
        info += f' · {len(context[template.detail_name or "details"])} linked row(s) from the second Excel'
    return context, info


def _render_preview(template, preview_row=1):
    """Preview of the letter filled with sample data: (info line, HTML document shown in an iframe, error)."""
    try:
        data, info = _preview_data(template, preview_row)
        return info, letter_document(template, data), None
    except Exception as e:
        return None, None, f'Preview error: {e}'

@login_required
def template_delete(request, template_id):
    template = get_object_or_404(Template, id=template_id)
    if request.method == 'POST':
        template.delete()
        return redirect('template_list')
    return render(request, 'doctemplates/template_confirm_delete.html', {'template': template})

# ── Shared image library (logos, signatures, backgrounds — reusable across templates) ──

@login_required
def image_asset_list(request):
    """List all shared images; upload a new one from the same page."""
    if request.method == 'POST':
        form = ImageAssetForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('image_asset_list')
    else:
        form = ImageAssetForm()

    images = ImageAsset.objects.all()
    return render(request, 'doctemplates/image_asset_list.html', {
        'images': images,
        'form': form,
    })


@login_required
def image_asset_delete(request, image_id):
    image = get_object_or_404(ImageAsset, id=image_id)
    if request.method == 'POST':
        image.delete()
        return redirect('image_asset_list')
    return render(request, 'doctemplates/image_asset_confirm_delete.html', {'image': image})


# ── Placed images on a specific template (logo/signature/background positioning) ──

@login_required
def template_image_list(request, template_id):
    """List images placed on this template; add a new one from the same page."""
    template = get_object_or_404(Template, id=template_id)

    if request.method == 'POST':
        form = TemplatePlacedImageForm(request.POST)
        if form.is_valid():
            placed = form.save(commit=False)
            placed.template = template
            placed.save()
            return redirect('template_image_list', template_id=template.id)
    else:
        form = TemplatePlacedImageForm()

    placed_images = template.images.all()
    return render(request, 'doctemplates/template_image_list.html', {
        'template': template,
        'placed_images': placed_images,
        'form': form,
    })


@login_required
def template_image_edit(request, template_id, image_id):
    template = get_object_or_404(Template, id=template_id)
    placed = get_object_or_404(TemplatePlacedImage, id=image_id, template=template)

    if request.method == 'POST':
        form = TemplatePlacedImageForm(request.POST, instance=placed)
        if form.is_valid():
            form.save()
            return redirect('template_image_list', template_id=template.id)
    else:
        form = TemplatePlacedImageForm(instance=placed)

    return render(request, 'doctemplates/template_image_edit.html', {
        'template': template,
        'form': form,
        'placed': placed,
    })


@login_required
def template_image_delete(request, template_id, image_id):
    template = get_object_or_404(Template, id=template_id)
    placed = get_object_or_404(TemplatePlacedImage, id=image_id, template=template)
    if request.method == 'POST':
        placed.delete()
        return redirect('template_image_list', template_id=template.id)
    return render(request, 'doctemplates/template_image_confirm_delete.html', {
        'template': template,
        'placed': placed,
    })


# ── Exact-position text fields on a specific template ──

@login_required
def template_field_list(request, template_id):
    """List exact-position fields on this template; add a new one from the same page."""
    template = get_object_or_404(Template, id=template_id)

    if request.method == 'POST':
        form = TemplateFieldForm(request.POST)
        if form.is_valid():
            field = form.save(commit=False)
            field.template = template
            field.save()
            return redirect('template_field_list', template_id=template.id)
    else:
        form = TemplateFieldForm()

    fields = template.fields.all()
    return render(request, 'doctemplates/template_field_list.html', {
        'template': template,
        'fields': fields,
        'form': form,
    })


@login_required
def template_field_edit(request, template_id, field_id):
    template = get_object_or_404(Template, id=template_id)
    field = get_object_or_404(TemplateField, id=field_id, template=template)

    if request.method == 'POST':
        form = TemplateFieldForm(request.POST, instance=field)
        if form.is_valid():
            form.save()
            return redirect('template_field_list', template_id=template.id)
    else:
        form = TemplateFieldForm(instance=field)

    return render(request, 'doctemplates/template_field_edit.html', {
        'template': template,
        'form': form,
        'field': field,
    })

@login_required
def template_field_delete(request, template_id, field_id):
    template = get_object_or_404(Template, id=template_id)
    field = get_object_or_404(TemplateField, id=field_id, template=template)
    if request.method == 'POST':
        field.delete()
        return redirect('template_field_list', template_id=template.id)
    return render(request, 'doctemplates/template_field_confirm_delete.html', {
        'template': template,
        'field': field,
    })


# ── v2: generating letters from a template ──

@login_required
def generate_v2(request):
    """Generate letters from a template; the job then shows up in History like the old generator's jobs."""
    templates = _templates_for(request.user)
    if request.method == 'POST':
        form = GenerateForm(request.POST, request.FILES, templates=templates)
        if form.is_valid():
            error = _start_v2_job(request, form)
            if not error:
                return redirect('history')
            form.add_error(None, error)
    else:
        form = GenerateForm(templates=templates)
    return render(request, 'doctemplates/generate.html', {'form': form, 'templates': templates})


def _templates_for(user):
    """Templates of the countries the user may generate letters for (country permissions in the admin)."""
    try:
        allowed = user.profile.get_country_list()
    except UserProfile.DoesNotExist:
        allowed = []
    ids = [t.id for t in Template.objects.all() if t.country_code.strip().upper() in allowed]
    return Template.objects.filter(id__in=ids).order_by('country_code', 'name')


def _start_v2_job(request, form):
    """Check the uploaded Excels and start generating in a background thread. Returns an error message or None."""
    if importlib.util.find_spec('playwright') is None:
        return PLAYWRIGHT_MISSING

    template = form.cleaned_data['template']
    letter_date = (form.cleaned_data.get('letter_date') or date.today()).strftime('%d.%m.%Y')
    encrypt_pdfs = form.cleaned_data.get('encrypt_pdfs', False)
    needs_detail = bool(template.main_key and template.detail_key)

    job_id = uuid.uuid4().hex[:8]
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    main_path = _save_upload(form.cleaned_data['excel_file'], upload_dir, job_id)
    detail_path = (_save_upload(form.cleaned_data['detail_excel_file'], upload_dir, f'{job_id}_detail')
                   if needs_detail else None)

    try:
        letter_count = _check_excels(template, main_path, detail_path, encrypt_pdfs)
    except Exception as e:
        for path in (main_path, detail_path):
            if path and os.path.exists(path):
                os.remove(path)
        return str(e) if isinstance(e, ValueError) else f'Error reading Excel: {e}'

    job = GenerationJob.objects.create(
        user=request.user,
        country_code=template.country_code[:5],
        document_type=(template.document_type or 'v2')[:20],
        template_name=template.name,
        excel_file=f"uploads/{os.path.basename(main_path)}",
        output_dir=job_id,
        pdf_count=letter_count,
        status='processing',
    )
    os.makedirs(os.path.join(OUTPUT_DIR, job_id), exist_ok=True)

    threading.Thread(
        target=process_job,
        args=(job.id, template.id, main_path, detail_path, letter_date, encrypt_pdfs),
        daemon=True,
    ).start()
    return None


def _save_upload(uploaded, upload_dir, prefix):
    path = os.path.join(upload_dir, f"{prefix}_{os.path.basename(uploaded.name)}")
    with open(path, 'wb') as f:
        for chunk in uploaded.chunks():
            f.write(chunk)
    return path


def _check_excels(template, main_path, detail_path, encrypt_pdfs):
    """Number of letters in the main Excel. Raises ValueError with a message for the user if the files do not fit."""
    rows = read_excel(main_path)
    if not rows:
        raise ValueError('No data rows found in the Excel file.')

    if detail_path:
        if template.main_key not in rows[0]:
            raise ValueError(f'The Excel file has no "{template.main_key}" column (it links the second Excel).')
        detail_rows = read_excel(detail_path)
        if detail_rows and template.detail_key not in detail_rows[0]:
            raise ValueError(f'The second Excel file has no "{template.detail_key}" column.')

    if encrypt_pdfs:
        if 'Password' not in rows[0]:
            raise ValueError('Encryption is enabled but the Excel file has no "Password" column.')
        missing = [str(row.get('ContractNumber') or row.get('Contract_number') or f'row {i}')
                   for i, row in enumerate(rows, start=1) if not row.get('Password', '').strip()]
        if missing:
            suffix = f' and {len(missing) - 10} more...' if len(missing) > 10 else ''
            raise ValueError(f'Encryption is enabled but passwords are missing for: {", ".join(missing[:10])}{suffix}')

    return len(rows)
