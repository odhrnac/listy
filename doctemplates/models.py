from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

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

    class Meta:
        ordering = ['field_name']

    def __str__(self):
        return f"{self.field_name} on {self.template.name}"
