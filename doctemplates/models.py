import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


def private_storage():
    """Storage outside MEDIA_ROOT, so sample Excel files (customer data) are never served at /media/."""
    return FileSystemStorage(location=os.path.join(settings.BASE_DIR, 'private_media'))


PAGE_CHOICES = [
    ('all', 'Every page'),
    ('first', 'First page only'),
    ('last', 'Last page only'),
]


class Template(models.Model):
    """Shared PDF template – any logged‑in user can use it."""
    name = models.CharField(max_length=100)
    country_code = models.CharField(max_length=5)
    document_type = models.CharField(max_length=20, blank=True, default='')
    html_content = models.TextField(
        help_text='HTML with {{ field_name }} placeholders. '
                  'e.g. {{ PHName }}, {{ ContractNumber }}'
    )
    css_content = models.TextField(blank=True, default='', help_text='Optional CSS')
    is_default = models.BooleanField(default=False)
    margin_top = models.IntegerField(default=50, help_text='Top margin in points (1pt = 0.3528mm)')
    margin_bottom = models.IntegerField(default=80, help_text='Bottom margin in points')
    margin_left = models.IntegerField(default=50, help_text='Left margin in points')
    margin_right = models.IntegerField(default=50, help_text='Right margin in points')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    footer_html = models.TextField(blank=True, default='', help_text='Footer content, placed below the bottom margin')
    footer_top = models.IntegerField(default=30,
                                     help_text='Distance from bottom of page to top of footer, in points (pt)')

    # Sample data for the preview; the real data comes from the Excel files uploaded when generating
    sample_excel = models.FileField(upload_to='template_samples/', storage=private_storage, blank=True,
                                    help_text='Main Excel with sample data for the preview (one row = one letter)')
    detail_excel = models.FileField(upload_to='template_samples/', storage=private_storage, blank=True,
                                    help_text='Optional second Excel with several rows per letter, e.g. insured persons')
    detail_name = models.CharField(max_length=50, blank=True, default='details',
                                   help_text='Name of the list of second-Excel rows in the template, '
                                             'e.g. insured → {% for person in insured %}')
    main_key = models.CharField(max_length=100, blank=True, default='',
                                help_text='Column in the main Excel that links the rows, e.g. Contract_number')
    detail_key = models.CharField(max_length=100, blank=True, default='',
                                  help_text='Matching column in the second Excel, e.g. IdNum')

    class Meta:
        ordering = ['-is_default', '-updated_at']

    def __str__(self):
        return f"{self.name} ({self.country_code})"

class ImageAsset(models.Model):
    """Shared image repository – any logged‑in user can use these images in templates."""
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='template_assets/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title

class TemplatePlacedImage(models.Model):
    ROLE_CHOICES = [
        ('logo', 'Logo'),
        ('signature', 'Signature'),
        ('background', 'Background'),
        ('other', 'Other'),
    ]
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='images')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='other')
    image = models.ForeignKey(ImageAsset, on_delete=models.CASCADE)
    x = models.IntegerField(default=0, help_text='Distance from LEFT edge of page, in pixels. A4 width ≈ 794px.')
    y = models.IntegerField(default=0, help_text='Distance from TOP edge of page, in pixels. A4 height ≈ 1123px.')
    width = models.IntegerField(default=100, help_text='Width in pixels')
    height = models.IntegerField(default=50, help_text='Height in pixels')
    z_index = models.IntegerField(default=10, help_text='Layer order: LOWER = further back. Set background to 0.')
    page = models.CharField(max_length=10, choices=PAGE_CHOICES, default='all',
                            help_text='On which pages of a multi-page letter the image is shown')

    class Meta:
        ordering = ['z_index', 'role']

    def __str__(self):
        return f"{self.get_role_display()} on {self.template.name}"


class TemplateField(models.Model):
    """An exact-position text field, filled from an Excel column, with a fallback default."""
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='fields')
    field_name = models.CharField(max_length=100, help_text='Excel column name to pull the value from, e.g. PHName')
    default_value = models.CharField(max_length=255, blank=True, default='', help_text='Used when the Excel row has no value for this field')
    font_size = models.IntegerField(default=10)
    bold = models.BooleanField(default=False)
    x = models.IntegerField(default=0, help_text='Distance from LEFT edge of page, in pixels')
    y = models.IntegerField(default=0, help_text='Distance from TOP edge of page, in pixels')
    max_width = models.IntegerField(null=True, blank=True,
                                    help_text='Optional wrap width in pixels; leave blank for no wrapping')
    page = models.CharField(max_length=10, choices=PAGE_CHOICES, default='all',
                            help_text='On which pages of a multi-page letter the field is shown')

    class Meta:
        ordering = ['field_name']

    def __str__(self):
        return f"{self.field_name} on {self.template.name}"
