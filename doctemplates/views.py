
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .forms import TemplateForm, ImageAssetForm, TemplatePlacedImageForm, TemplateFieldForm
from .models import Template, ImageAsset, TemplatePlacedImage, TemplateField #,GenerationJob, GeneratedPDF, UserProfile,

from config import  get_letter_date, MARGIN_LEFT, MARGIN_RIGHT, MARGIN_TOP, MARGIN_BOTTOM



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

    preview_html = None

    if request.method == 'POST':
        form = TemplateForm(request.POST, instance=template)
        if form.is_valid():
            # If the user clicked "Preview", don't save yet; just render preview
            if 'preview' in request.POST:
                # Build a temporary Template instance to render
                temp_template = form.save(commit=False)
                if template:
                    temp_template.id = template.id  # to keep pk for rendered context
                preview_html = _render_preview(temp_template)
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
                preview_html = _render_preview(temp_template)
    else:
        form = TemplateForm(instance=template)

    return render(request, 'doctemplates/template_edit.html', {
        'form': form,
        'template': template,
        'preview_html': preview_html,
    })

def _render_preview(template):
    """Render template with sample data inside an A4-sized preview box (pixels),
    including placed images (logo/signature/background), exact-position fields, and footer."""
    sample_data = {
        'PHName': 'Jón Jónsson',
        'PHAddrPermStreet': 'Laugavegur',
        'PHAddrPermNumber': '100',
        'PHAddrPermZIP': '101',
        'PHAddrPermTown': 'Reykjavík',
        'ContractNumber': 'C-12345',
        'PremiumOwed': '15.500',
        'PHGenderCode': 'M',
        'RegionCode': 'ISreg',
        'letter_date': get_letter_date(),
    }
    try:
        from django.template import Template as DjangoTemplate, Context
        django_template = DjangoTemplate(template.html_content)
        body_html = django_template.render(Context(sample_data))
        style_block = f"<style>{template.css_content}</style>"

        # Margins are still stored in points (pt) from the old system; convert to px for display (1pt = 1.333px)
        mt = (template.margin_top if template.margin_top is not None else MARGIN_TOP) * 1.333
        mb = (template.margin_bottom if template.margin_bottom is not None else MARGIN_BOTTOM) * 1.333
        ml = (template.margin_left if template.margin_left is not None else MARGIN_LEFT) * 1.333
        mr = (template.margin_right if template.margin_right is not None else MARGIN_RIGHT) * 1.333

        images_html = ''
        fields_html = ''
        footer_html = ''

        if template.pk:
            for placed in template.images.all():
                images_html += f"""
                <img src="{placed.image.image.url}" style="
                    position: absolute;
                    left: {placed.x}px;
                    top: {placed.y}px;
                    width: {placed.width}px;
                    height: {placed.height}px;
                    z-index: {placed.z_index};
                ">
                """

            for field in template.fields.all():
                value = sample_data.get(field.field_name, field.default_value)
                bold_style = 'font-weight: bold;' if field.bold else ''
                width_style = f'width: {field.max_width}px;' if field.max_width else ''
                fields_html += f"""
                <div style="
                    position: absolute;
                    left: {field.x}px;
                    top: {field.y}px;
                    font-size: {field.font_size}pt;
                    {bold_style}
                    {width_style}
                    z-index: 6;
                ">{value}</div>
                """

            if template.footer_html:
                django_footer = DjangoTemplate(template.footer_html)
                footer_body = django_footer.render(Context(sample_data))
                footer_html = f"""
                <div style="
                    position: absolute;
                    left: 0;
                    right: 0;
                    bottom: {template.footer_top}px;
                    font-size: 8pt;
                    color: #666;
                    z-index: 6;
                ">{footer_body}</div>
                """

        return f"""
        <div style="
            width: 794px;
            aspect-ratio: 794 / 1123;
            max-width: 100%;
            margin: 20px auto;
            background: white;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            box-sizing: border-box;
            position: relative;
            overflow: hidden;
        ">
            {style_block}
            {images_html}
            {fields_html}
            {footer_html}
            <div style="
                position: absolute;
                top: {mt}px;
                left: {ml}px;
                right: {mr}px;
                bottom: {mb}px;
                border: 1px dotted #aaa;
                overflow: hidden;
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                font-size: 10pt;
                line-height: 1.5;
                color: #333;
                z-index: 10;
            ">
                {body_html}
            </div>
        </div>
        """
    except Exception as e:
        return f'<p style="color:red;">Preview error: {e}</p>'

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
