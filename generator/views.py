import os
import uuid
import zipfile
import tempfile
import shutil
import threading
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from .forms import UploadForm
from .models import GenerationJob, GeneratedPDF, UserProfile
from .pdf_tools import encrypt_pdf

from config import OUTPUT_DIR, get_letter_date, set_letter_date, MARGIN_LEFT, MARGIN_RIGHT, MARGIN_TOP, MARGIN_BOTTOM
from readers import read_excel
from countries import get_country_config, get_document_registry


@login_required
def upload_view(request):
    _cleanup_expired_jobs()

    try:
        allowed = request.user.profile.get_country_list()
    except UserProfile.DoesNotExist:
        allowed = []

    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES, allowed_countries=allowed)
        if form.is_valid():
            return _start_job(request, form, allowed)
    else:
        form = UploadForm(allowed_countries=allowed)
    return render(request, 'generator/upload.html', {
        'form': form,
        'document_fields_json': form.get_document_fields_json(),
    })


def _start_job(request, form, allowed):
    """Validate input, create job record, and start background processing."""
    country_code = form.cleaned_data['country_code']
    doc_type_raw = form.cleaned_data['document_type']
    doc_type = doc_type_raw.split('|')[1] if '|' in doc_type_raw else doc_type_raw
    signer_raw = form.cleaned_data.get('signer', '')
    sheet_name = form.cleaned_data.get('sheet_name', '')
    excel_file = form.cleaned_data['excel_file']
    encrypt_pdfs = form.cleaned_data.get('encrypt_pdfs', False)

    # Set letter date
    letter_date = form.cleaned_data.get('letter_date')
    if letter_date:
        date_str_formatted = letter_date.strftime("%d.%m.%Y")
    else:
        date_str_formatted = None

    # Create unique output subdirectory
    job_id = uuid.uuid4().hex[:8]
    job_output_dir = os.path.join(OUTPUT_DIR, job_id)
    os.makedirs(job_output_dir, exist_ok=True)

    # Save uploaded file
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    excel_path = os.path.join(upload_dir, f"{job_id}_{excel_file.name}")
    with open(excel_path, 'wb') as f:
        for chunk in excel_file.chunks():
            f.write(chunk)

    # Quick validation before starting background job
    try:
        doc_registry = get_document_registry(country_code)
        handler = doc_registry[doc_type]()
        country_config = get_country_config(country_code)
        handler.country_config = country_config

        if not sheet_name:
            sheet_name = handler.get_sheet_name()

        rows = read_excel(excel_path, sheet_name=sheet_name)
        if not rows:
            return render(request, 'generator/upload.html', {
                'form': UploadForm(allowed_countries=allowed),
                'error': 'No data rows found in the Excel file.',
            })

        # Validate passwords if encryption is enabled
        if encrypt_pdfs:
            if 'Password' not in rows[0]:
                return render(request, 'generator/upload.html', {
                    'form': UploadForm(allowed_countries=allowed),
                    'error': 'Encryption is enabled but the Excel file has no "Password" column.',
                })

            missing = []
            for i, row in enumerate(rows, start=1):
                pw = row.get('Password', '').strip()
                if not pw:
                    contract = row.get('ContractNumber', f'row {i}')
                    missing.append(str(contract))

            if missing:
                missing_list = ', '.join(missing[:10])
                suffix = f' and {len(missing) - 10} more...' if len(missing) > 10 else ''
                return render(request, 'generator/upload.html', {
                    'form': UploadForm(allowed_countries=allowed),
                    'error': f'Encryption is enabled but passwords are missing for: {missing_list}{suffix}',
                })

    except Exception as e:
        return render(request, 'generator/upload.html', {
            'form': UploadForm(allowed_countries=allowed),
            'error': f'Error reading Excel: {str(e)}',
        })

    # Create DB record
    job = GenerationJob.objects.create(
        user=request.user,
        country_code=country_code,
        document_type=doc_type,
        signer_key=signer_raw,
        excel_file=f"uploads/{job_id}_{excel_file.name}",
        sheet_name=sheet_name,
        output_dir=job_id,
        pdf_count=len(rows),
        status='processing',
    )

    # Start background thread
    thread = threading.Thread(
        target=_process_job,
        args=(job.id, country_code, doc_type, signer_raw, sheet_name,
              excel_path, job_output_dir, encrypt_pdfs, date_str_formatted),
        daemon=True,
    )
    thread.start()

    return redirect('history')


def _process_job(job_id, country_code, doc_type, signer_raw, sheet_name,
                 excel_path, job_output_dir, encrypt_pdfs, date_str_formatted):
    """Background thread: generate PDFs."""
    import django
    django.setup()

    from .models import GenerationJob, GeneratedPDF

    try:
        job = GenerationJob.objects.get(id=job_id)

        # Set letter date for this thread
        set_letter_date(date_str_formatted)

        doc_registry = get_document_registry(country_code)
        handler = doc_registry[doc_type]()
        country_config = get_country_config(country_code)
        handler.country_config = country_config

        if not sheet_name:
            sheet_name = handler.get_sheet_name()

        rows = read_excel(excel_path, sheet_name=sheet_name)

        # Resolve signer
        signer = None
        if signer_raw and '|' in signer_raw:
            signer_key = signer_raw.split('|')[1]
            if hasattr(country_config, 'SIGNERS') and signer_key in country_config.SIGNERS:
                signer = country_config.SIGNERS[signer_key]

        from countries.IS.generator import generate_pdf
        from countries.SK.generator import generate_pdf_sk

        date_str = get_letter_date().replace(".", "")

        for i, row_data in enumerate(rows, start=1):
            contract_nr = row_data.get("ContractNumber", f"row_{i}")
            safe_name = str(contract_nr).replace("/", "_").replace("\\", "_")

            if hasattr(handler, 'get_filename_from_data'):
                custom_name = handler.get_filename_from_data(row_data)
                if custom_name:
                    filename = f"{custom_name}_{date_str}.pdf"
                else:
                    filename = f"{handler.get_filename_prefix()}_{safe_name}_{date_str}.pdf"
            else:
                filename = f"{handler.get_filename_prefix()}_{safe_name}_{date_str}.pdf"

            output_path = os.path.join(job_output_dir, filename)

            if country_code == "SK":
                generate_pdf_sk(
                    data=row_data, handler=handler,
                    output_path=output_path, country_config=country_config,
                    signer=signer,
                )
            else:
                generate_pdf(
                    data=row_data, handler=handler,
                    output_path=output_path, country_config=country_config,
                )

            # Encrypt if enabled
            if encrypt_pdfs:
                pdf_password = row_data.get("Password", "").strip()
                if pdf_password:
                    encrypt_pdf(output_path, pdf_password)

            GeneratedPDF.objects.create(
                job=job,
                filename=filename,
                file_path=f"outputs/{job.output_dir}/{filename}",
            )

        job.status = 'success'
        job.save()

        # Delete uploaded Excel
        if os.path.exists(excel_path):
            os.remove(excel_path)

    except Exception as e:
        try:
            job = GenerationJob.objects.get(id=job_id)
            job.status = 'error'
            job.error_message = str(e)
            job.save()
        except Exception:
            pass


@login_required
def history_view(request):
    _cleanup_expired_jobs()
    if request.user.is_staff:
        jobs = GenerationJob.objects.all()
    else:
        jobs = GenerationJob.objects.filter(user=request.user)

    now = timezone.now()
    has_processing = False
    for job in jobs:
        expires_at = job.created_at + timedelta(hours=72)
        remaining = expires_at - now
        if remaining.total_seconds() > 0:
            hours = int(remaining.total_seconds() // 3600)
            minutes = int((remaining.total_seconds() % 3600) // 60)
            job.time_remaining = f"{hours}h {minutes}m"
        else:
            job.time_remaining = "Expired"
        if job.status == 'processing':
            has_processing = True

    return render(request, 'generator/history.html', {
        'jobs': jobs,
        'has_processing': has_processing,
    })


@login_required
def job_detail_view(request, job_id):
    try:
        job = GenerationJob.objects.get(id=job_id, user=request.user)
    except GenerationJob.DoesNotExist:
        raise Http404

    expired = timezone.now() > job.created_at + timedelta(hours=72)
    pdfs = job.pdfs.all().order_by('filename')

    return render(request, 'generator/job_detail.html', {
        'job': job,
        'pdfs': pdfs,
        'expired': expired,
    })


@login_required
def download_zip(request, job_id):
    try:
        job = GenerationJob.objects.get(id=job_id, user=request.user, status='success')
    except GenerationJob.DoesNotExist:
        # Allow staff to download any job
        if request.user.is_staff:
            try:
                job = GenerationJob.objects.get(id=job_id, status='success')
            except GenerationJob.DoesNotExist:
                raise Http404
        else:
            raise Http404

    if timezone.now() > job.created_at + timedelta(hours=72):
        raise Http404("Download expired.")

    job_output_dir = os.path.join(OUTPUT_DIR, job.output_dir)
    if not os.path.exists(job_output_dir):
        raise Http404("Files no longer available.")

    zip_filename = f"{job.country_code}_{job.document_type}_{job.created_at:%Y%m%d_%H%M}.zip"

    tmp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
    with zipfile.ZipFile(tmp_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        for pdf in job.pdfs.all():
            full_path = os.path.join(settings.MEDIA_ROOT, pdf.file_path)
            if os.path.exists(full_path):
                zf.write(full_path, pdf.filename)
    tmp_zip.close()

    return FileResponse(
        open(tmp_zip.name, 'rb'),
        content_type='application/zip',
        filename=zip_filename,
    )


@login_required
def download_pdf(request, pdf_id):
    try:
        pdf = GeneratedPDF.objects.get(id=pdf_id, job__user=request.user)
    except GeneratedPDF.DoesNotExist:
        if request.user.is_staff:
            try:
                pdf = GeneratedPDF.objects.get(id=pdf_id)
            except GeneratedPDF.DoesNotExist:
                raise Http404
        else:
            raise Http404

    if timezone.now() > pdf.job.created_at + timedelta(hours=72):
        raise Http404("Download expired.")

    full_path = os.path.join(settings.MEDIA_ROOT, pdf.file_path)
    if not os.path.exists(full_path):
        raise Http404

    return FileResponse(open(full_path, 'rb'), content_type='application/pdf', filename=pdf.filename)


def _cleanup_expired_jobs():
    cutoff = timezone.now() - timedelta(hours=72)
    expired_jobs = GenerationJob.objects.filter(created_at__lt=cutoff)

    for job in expired_jobs:
        job_output_dir = os.path.join(OUTPUT_DIR, job.output_dir)
        if job.output_dir and os.path.exists(job_output_dir):
            shutil.rmtree(job_output_dir, ignore_errors=True)
        excel_path = os.path.join(settings.MEDIA_ROOT, str(job.excel_file))
        if os.path.exists(excel_path):
            os.remove(excel_path)

    expired_jobs.delete()

# @login_required # moved to doctemplates/views.py
# def template_list(request):
#     """List all shared templates."""
#     templates = Template.objects.all()
#     return render(request, 'generator/template_list.html', {'templates': templates})

# @login_required # moved to doctemplates/views.py
# def template_edit(request, template_id=None):
#     """Create a new template or edit an existing one, with live preview."""
#     if template_id:
#         template = get_object_or_404(Template, id=template_id)
#     else:
#         template = None
#
#     preview_html = None
#
#     if request.method == 'POST':
#         form = TemplateForm(request.POST, instance=template)
#         if form.is_valid():
#             # If the user clicked "Preview", don't save yet; just render preview
#             if 'preview' in request.POST:
#                 # Build a temporary Template instance to render
#                 temp_template = form.save(commit=False)
#                 if template:
#                     temp_template.id = template.id  # to keep pk for rendered context
#                 preview_html = _render_preview(temp_template)
#             else:
#                 form.save()
#                 return redirect('template_list')
#         else:
#             # If form invalid, still allow preview if requested
#             if 'preview' in request.POST:
#                 temp_template = Template(
#                     html_content=request.POST.get('html_content', ''),
#                     css_content=request.POST.get('css_content', ''),
#                 )
#                 preview_html = _render_preview(temp_template)
#     else:
#         form = TemplateForm(instance=template)
#
#     return render(request, 'generator/template_edit.html', {
#         'form': form,
#         'template': template,
#         'preview_html': preview_html,
#     })


# def _render_preview(template): # moved to doctemplates/views.py
#     """Render template with sample data inside an A4-like preview box, using template's margins."""
#     sample_data = {
#         'PHName': 'Jón Jónsson',
#         'PHAddrPermStreet': 'Laugavegur',
#         'PHAddrPermNumber': '100',
#         'PHAddrPermZIP': '101',
#         'PHAddrPermTown': 'Reykjavík',
#         'ContractNumber': 'C-12345',
#         'PremiumOwed': '15.500',
#         'PHGenderCode': 'M',
#         'RegionCode': 'ISreg',
#         'letter_date': get_letter_date(),
#     }
#     try:
#         from django.template import Template as DjangoTemplate, Context
#         django_template = DjangoTemplate(template.html_content)
#         body_html = django_template.render(Context(sample_data))
#
#         # Use template's margins if set, else fallback to global config values
#         mt = template.margin_top if template.margin_top is not None else MARGIN_TOP
#         mb = template.margin_bottom if template.margin_bottom is not None else MARGIN_BOTTOM
#         ml = template.margin_left if template.margin_left is not None else MARGIN_LEFT
#         mr = template.margin_right if template.margin_right is not None else MARGIN_RIGHT
#
#         return f"""
#         <div style="
#             width: 210mm;
#             max-width: 100%;
#             aspect-ratio: 210 / 297;
#             margin: 20px auto;
#             background: white;
#             box-shadow: 0 0 10px rgba(0,0,0,0.1);
#             box-sizing: border-box;
#             position: relative;
#         ">
#             <div style="
#                 position: absolute;
#                 top: {mt}pt;
#                 left: {ml}pt;
#                 right: {mr}pt;
#                 bottom: {mb}pt;
#                 border: 1px dotted #aaa;
#                 overflow: auto;
#                 font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
#                 font-size: 10pt;
#                 line-height: 1.5;
#                 color: #333;
#             ">
#                 {body_html}
#             </div>
#         </div>
#         """
#     except Exception as e:
#         return f'<p style="color:red;">Preview error: {e}</p>'

# @login_required
# def template_delete(request, template_id):
#     template = get_object_or_404(Template, id=template_id)
#     if request.method == 'POST':
#         template.delete()
#         return redirect('template_list')
#     return render(request, 'generator/template_confirm_delete.html', {'template': template})