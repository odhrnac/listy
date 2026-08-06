from django import forms
from .models import Template
from countries import COUNTRY_REGISTRY, get_document_registry, get_country_config
import json

class TemplateForm(forms.ModelForm):
    class Meta:
        model = Template
        fields = [
            'name', 'country_code', 'document_type',
            'html_content', 'css_content', 'is_default',
            'margin_top', 'margin_bottom', 'margin_left', 'margin_right',
        ]
        widgets = {
            'html_content': forms.Textarea(attrs={'rows': 20, 'style': 'width:100%; font-family:monospace;'}),
            'css_content': forms.Textarea(attrs={'rows': 10, 'style': 'width:100%; font-family:monospace;'}),
            'margin_top': forms.NumberInput(attrs={'style': 'width: 80px;'}),
            'margin_bottom': forms.NumberInput(attrs={'style': 'width: 80px;'}),
            'margin_left': forms.NumberInput(attrs={'style': 'width: 80px;'}),
            'margin_right': forms.NumberInput(attrs={'style': 'width: 80px;'}),
        }