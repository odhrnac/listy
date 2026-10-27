import os

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from doctemplates.models import Template, ImageAsset, TemplatePlacedImage

TEMPLATE_NAME = 'IS Final Notice (NOT)'
STARTER_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'starter_templates', 'is_final_notice')
ASSETS_DIR = os.path.join(settings.BASE_DIR, 'assets', 'IS')

# (role, image title, file in assets/IS, x, y, width, height, z_index) – positions in px on the 794 x 1123 A4 page
PLACED_IMAGES = [
    ('background', 'IS background', 'Novis_HP_motyl_06062019_prev.png', 0, 0, 794, 1123, 0),
    ('logo', 'IS logo', 'NOVISLG.png', 29, 23, 156, 97, 10),
    ('signature', 'IS signature AD', 'sign_AD.png', 596, 854, 130, 53, 10),
]


class Command(BaseCommand):
    help = 'Create (or reset) the IS Final Notice template, including its logo, signature and background images.'

    def handle(self, *args, **options):
        template, created = Template.objects.update_or_create(
            name=TEMPLATE_NAME,
            defaults={
                'country_code': 'IS',
                'document_type': 'NOT',
                'html_content': self._read('body.html'),
                'css_content': self._read('style.css'),
                'footer_html': self._read('footer.html'),
                'footer_top': 16,
                'margin_top': 125,
                'margin_bottom': 80,
                'margin_left': 50,
                'margin_right': 50,
            },
        )

        # Re-place images from scratch so running the command again restores the original layout
        template.images.all().delete()
        for role, title, filename, x, y, width, height, z_index in PLACED_IMAGES:
            TemplatePlacedImage.objects.create(
                template=template,
                role=role,
                image=self._get_image(title, filename),
                x=x, y=y, width=width, height=height, z_index=z_index,
            )

        action = 'Created' if created else 'Updated'
        self.stdout.write(self.style.SUCCESS(f'{action} template "{template.name}" (id {template.id}).'))

    def _read(self, filename):
        with open(os.path.join(STARTER_DIR, filename), encoding='utf-8') as f:
            return f.read()

    def _get_image(self, title, filename):
        """Reuse an image from the library by title, or upload it from assets/IS."""
        image = ImageAsset.objects.filter(title=title).first()
        if image:
            return image
        image = ImageAsset(title=title)
        with open(os.path.join(ASSETS_DIR, filename), 'rb') as f:
            image.image.save(filename, File(f), save=True)
        return image
