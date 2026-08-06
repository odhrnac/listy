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
