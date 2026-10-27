from django.core.management.base import BaseCommand

from doctemplates.models import Template, TemplatePlacedImage
from doctemplates.starter_templates import read_starter_file, get_image

TEMPLATE_NAME = 'IS Final Notice (NOT)'
FOLDER = 'is_final_notice'

# (role, image title, file in assets/, x, y, width, height, z_index) – positions in px on the 794 x 1123 A4 page
PLACED_IMAGES = [
    ('background', 'IS background', 'IS/Novis_HP_motyl_06062019_prev.png', 0, 0, 794, 1123, 0),
    ('logo', 'IS logo', 'IS/NOVISLG.png', 29, 23, 156, 97, 10),
    ('signature', 'IS signature AD', 'IS/sign_AD.png', 596, 852, 130, 53, 10),
]


class Command(BaseCommand):
    help = 'Create (or reset) the IS Final Notice template, including its logo, signature and background images.'

    def handle(self, *args, **options):
        template, created = Template.objects.update_or_create(
            name=TEMPLATE_NAME,
            defaults={
                'country_code': 'IS',
                'document_type': 'NOT',
                'html_content': read_starter_file(FOLDER, 'body.html'),
                'css_content': read_starter_file(FOLDER, 'style.css'),
                'footer_html': read_starter_file(FOLDER, 'footer.html'),
                'footer_top': 16,
                'margin_top': 125,
                'margin_bottom': 80,
                'margin_left': 50,
                'margin_right': 50,
            },
        )

        # Re-place images from scratch so running the command again restores the original layout
        template.images.all().delete()
        for role, title, asset_path, x, y, width, height, z_index in PLACED_IMAGES:
            TemplatePlacedImage.objects.create(
                template=template,
                role=role,
                image=get_image(title, asset_path),
                x=x, y=y, width=width, height=height, z_index=z_index,
            )

        action = 'Created' if created else 'Updated'
        self.stdout.write(self.style.SUCCESS(f'{action} template "{template.name}" (id {template.id}).'))
