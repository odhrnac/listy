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

class ImageAssetForm(forms.ModelForm):
    class Meta:
        model = ImageAsset
        fields = ['title', 'image']


class TemplatePlacedImageForm(forms.ModelForm):
    class Meta:
        model = TemplatePlacedImage
        fields = ['role', 'image', 'x', 'y', 'width', 'height', 'z_index']


class TemplateFieldForm(forms.ModelForm):
    class Meta:
        model = TemplateField
        fields = ['field_name', 'default_value', 'x', 'y', 'font_size', 'bold', 'max_width']