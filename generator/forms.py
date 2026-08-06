from django import forms
from .models import Template
from countries import COUNTRY_REGISTRY, get_document_registry, get_country_config
import json


# Define required Excel columns per country|doc_type
DOCUMENT_FIELDS = {
    "IS|NOT": {
        "required": ["ContractNumber", "PHGenderCode", "PHName", "PHAddrPermStreet", "PHAddrPermNumber", "PHAddrPermZIP", "PHAddrPermTown", "RegionCode", "PremiumOwed"],
        "sheet": "FINALNOTICE",
    },
    "IS|REM": {
        "required": ["ContractNumber", "PHGenderCode", "PHName", "PHAddrPermStreet", "PHAddrPermNumber", "PHAddrPermZIP", "PHAddrPermTown", "RegionCode", "PremiumOwed"],
        "sheet": "REMINDER",
    },
    "IS|CAN_DP": {
        "required": ["ContractNumber", "PHGenderCode", "PHName", "PHAddrPermStreet", "PHAddrPermNumber", "PHAddrPermZIP", "PHAddrPermTown", "RegionCode", "PremiumOwed", "ContractCloseDate"],
        "sheet": "List1",
    },
    "IS|CAN_PH_WSV": {
        "required": ["ContractNumber", "PHGenderCode", "PHName", "PHAddrPermStreet", "PHAddrPermNumber", "PHAddrPermZIP", "PHAddrPermTown", "RegionCode"],
        "sheet": "List1",
    },
    "IS|CAN_PH_NSV": {
        "required": ["ContractNumber", "PHGenderCode", "PHName", "PHAddrPermStreet", "PHAddrPermNumber", "PHAddrPermZIP", "PHAddrPermTown", "RegionCode"],
        "sheet": "List1",
    },
    "SK|CAN_DP": {
        "required": ["ContractNumber", "PHGenderCode", "PHTitleBefore", "PHFirstName", "PHMiddleName", "PHLastName", "PHTitleAfter", "PHAddrPermStreet", "PHAddrPermNumber", "PHAddrPermZIP", "PHAddrPermTown", "ContractCloseDate", "surrender Value", "IBAN"],
        "sheet": "Data",
    },
    "SK|REM": {
        "required": ["ContractNumber", "PHGenderCode", "PHTitleBefore", "PHFirstName", "PHMiddleName", "PHLastName", "PHTitleAfter", "PHAddrPermStreet", "PHAddrPermNumber", "PHAddrPermZIP", "PHAddrPermTown", "30/60", "MonthsOwed", "TotalBalance", "PremiumOwed", "CC", "LastPairedDate", "AgentContactEmail"],
        "optional": ["PDF"],
        "sheet": "Sheet1",
    },
}


class UploadForm(forms.Form):
    country_code = forms.ChoiceField(
        choices=[],
        label='Country',
    )
    document_type = forms.ChoiceField(
        choices=[],
        label='Document Type',
    )
    signer = forms.ChoiceField(
        choices=[],
        label='Signer',
        required=False,
    )
    excel_file = forms.FileField(
        label='Excel File (.xlsx)',
    )
    sheet_name = forms.CharField(
        label='Sheet Name (leave blank for default)',
        required=False,
        max_length=100,
    )
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
    template = forms.ModelChoiceField(
        queryset=Template.objects.none(),  # we'll filter in __init__
        required=False,
        label="Use Template (optional)"
    )

    def __init__(self, *args, allowed_countries=None, **kwargs):
        super().__init__(*args, **kwargs)


        if allowed_countries:
            available_countries = {
                code: name for code, name in COUNTRY_REGISTRY.items()
                if code in allowed_countries
            }
        else:
            available_countries = {}

        self.fields['country_code'].choices = [
            (code, f"{code} - {name}") for code, name in available_countries.items()
        ]

        all_doc_choices = []
        for country_code in available_countries:
            registry = get_document_registry(country_code)
            for doc_code, doc_cls in registry.items():
                handler = doc_cls()
                label = f"{doc_code} - {handler.get_title()}"
                all_doc_choices.append((f"{country_code}|{doc_code}", label))
        self.fields['document_type'].choices = all_doc_choices

        all_signer_choices = [('', '— None —')]
        for country_code in available_countries:
            try:
                config = get_country_config(country_code)
                if hasattr(config, 'SIGNERS') and config.SIGNERS:
                    for key, signer in config.SIGNERS.items():
                        all_signer_choices.append(
                            (f"{country_code}|{key}", signer['name'])
                        )
            except Exception:
                pass
        self.fields['signer'].choices = all_signer_choices

        self.fields['template'].queryset = Template.objects.all()

    def get_document_fields_json(self):
        """Return DOCUMENT_FIELDS as JSON for the frontend."""
        return json.dumps(DOCUMENT_FIELDS)

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