from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    allowed_countries = models.CharField(
        max_length=100,
        help_text='Comma-separated country codes, e.g. "IS,SK"',
        default='',
        blank=True,
    )

    def get_country_list(self):
        """Returns list of allowed country codes."""
        if not self.allowed_countries:
            return []
        return [c.strip().upper() for c in self.allowed_countries.split(',') if c.strip()]

    def __str__(self):
        return f"{self.user.username} → {self.allowed_countries}"

class GenerationJob(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jobs')

    # Input details
    country_code = models.CharField(max_length=5)
    document_type = models.CharField(max_length=20)
    signer_key = models.CharField(max_length=10, blank=True, default='')
    excel_file = models.FileField(upload_to='uploads/')
    sheet_name = models.CharField(max_length=100, blank=True, default='')
    template_name = models.CharField(max_length=100, blank=True, default='',
                                     help_text='Set for letters generated from a template (v2)')

    # Results
    pdf_count = models.IntegerField(default=0)
    output_dir = models.CharField(max_length=500, blank=True, default='')

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing...'),
        ('success', 'Success'),
        ('error', 'Error'),
    ])
    error_message = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.country_code}/{self.document_type} - {self.created_at:%Y-%m-%d %H:%M}"


class GeneratedPDF(models.Model):
    job = models.ForeignKey(GenerationJob, on_delete=models.CASCADE, related_name='pdfs')
    filename = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename

# class Template(models.Model): # moved to doctempaltes -> models.py
#     """Shared PDF template – any logged‑in user can use it."""
#     name = models.CharField(max_length=100)
#     country_code = models.CharField(max_length=5)
#     document_type = models.CharField(max_length=20, blank=True, default='')
#     html_content = models.TextField(
#         help_text='HTML with {{ field_name }} placeholders. '
#                   'e.g. {{ PHName }}, {{ ContractNumber }}'
#     )
#     css_content = models.TextField(blank=True, default='', help_text='Optional CSS')
#     is_default = models.BooleanField(default=False)
#     margin_top = models.IntegerField(default=50, help_text='Top margin in points (1pt = 0.3528mm)')
#     margin_bottom = models.IntegerField(default=80, help_text='Bottom margin in points')
#     margin_left = models.IntegerField(default=50, help_text='Left margin in points')
#     margin_right = models.IntegerField(default=50, help_text='Right margin in points')
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         ordering = ['-is_default', '-updated_at']
#
#     def __str__(self):
#         return f"{self.name} ({self.country_code})"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)

# class ImageAsset(models.Model): # moved to doctempaltes -> models.py
#     """Shared image repository – any logged‑in user can use these images in templates."""
#     title = models.CharField(max_length=100)
#     image = models.ImageField(upload_to='template_assets/')
#     uploaded_at = models.DateTimeField(auto_now_add=True)
#
#     class Meta:
#         ordering = ['-uploaded_at']
#
#     def __str__(self):
#         return self.title
