from django import forms
from .models import Template, ImageAsset, TemplatePlacedImage, TemplateField
from countries import COUNTRY_REGISTRY, get_document_registry, get_country_config
import json

class TemplateForm(forms.ModelForm):
    class Meta:
        model = Template
        fields = [
            'name', 'country_code', 'document_type',
            'html_content', 'css_content', 'is_default',
            'margin_top', 'margin_bottom', 'margin_left', 'margin_right',
            'footer_html', 'footer_top',
            'sample_excel', 'detail_excel', 'detail_name', 'main_key', 'detail_key',
        ]
        widgets = {
            'html_content': forms.Textarea(attrs={'rows': 20, 'style': 'width:100%; font-family:monospace;'}),
            'css_content': forms.Textarea(attrs={'rows': 10, 'style': 'width:100%; font-family:monospace;'}),
            'footer_html': forms.Textarea(attrs={'rows': 5, 'style': 'width:100%; font-family:monospace;'}),
            'margin_top': forms.NumberInput(attrs={'style': 'width: 80px;'}),
            'margin_bottom': forms.NumberInput(attrs={'style': 'width: 80px;'}),
            'margin_left': forms.NumberInput(attrs={'style': 'width: 80px;'}),
            'margin_right': forms.NumberInput(attrs={'style': 'width: 80px;'}),
            'footer_top': forms.NumberInput(attrs={'style': 'width: 80px;'}),
        }

    # Not stored: which row of the sample Excel the preview shows
    preview_row = forms.IntegerField(required=False, min_value=1, initial=1,
                                     widget=forms.NumberInput(attrs={'style': 'width: 80px;'}),
                                     help_text='Row of the sample Excel shown by Preview')

class ImageAssetForm(forms.ModelForm):
    class Meta:
        model = ImageAsset
        fields = ['title', 'image']


class TemplatePlacedImageForm(forms.ModelForm):
    class Meta:
        model = TemplatePlacedImage
        fields = ['role', 'image', 'x', 'y', 'width', 'height', 'z_index', 'page']


class TemplateFieldForm(forms.ModelForm):
    class Meta:
        model = TemplateField
        fields = ['field_name', 'default_value', 'x', 'y', 'font_size', 'bold', 'max_width', 'page']

class GenerateForm(forms.Form):
    """v2: generate letters from a template."""
    template = forms.ModelChoiceField(queryset=Template.objects.none(), label='Template')
    excel_file = forms.FileField(label='Excel file (.xlsx)')
    detail_excel_file = forms.FileField(label='Second Excel file (.xlsx)', required=False)
    letter_date = forms.DateField(
        label='Letter Date',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text='Leave blank for today\'s date.',
    )
    encrypt_pdfs = forms.BooleanField(
        label='Encrypt PDFs with password',
        required=False,
        help_text='Requires a "Password" column in the Excel file.',
    )

    def __init__(self, *args, templates=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['template'].queryset = templates if templates is not None else Template.objects.none()

    def clean(self):
        data = super().clean()
        template = data.get('template')
        if template and template.main_key and template.detail_key and not data.get('detail_excel_file'):
            self.add_error('detail_excel_file',
                           f'This template needs a second Excel (rows linked by {template.detail_key}).')
        return data
