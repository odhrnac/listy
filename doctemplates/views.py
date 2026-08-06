
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .forms import TemplateForm
from .models import Template #,GenerationJob, GeneratedPDF, UserProfile,

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
    """Render template with sample data inside an A4-like preview box, using template's margins."""
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

        # Use template's margins if set, else fallback to global config values
        mt = template.margin_top if template.margin_top is not None else MARGIN_TOP
        mb = template.margin_bottom if template.margin_bottom is not None else MARGIN_BOTTOM
        ml = template.margin_left if template.margin_left is not None else MARGIN_LEFT
        mr = template.margin_right if template.margin_right is not None else MARGIN_RIGHT

        return f"""
        <div style="
            width: 210mm;
            max-width: 100%;
            aspect-ratio: 210 / 297;
            margin: 20px auto;
            background: white;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            box-sizing: border-box;
            position: relative;
        ">
            <div style="
                position: absolute;
                top: {mt}pt;
                left: {ml}pt;
                right: {mr}pt;
                bottom: {mb}pt;
                border: 1px dotted #aaa;
                overflow: auto;
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                font-size: 10pt;
                line-height: 1.5;
                color: #333;
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
