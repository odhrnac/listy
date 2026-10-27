import os

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from doctemplates.models import Template, TemplatePlacedImage
from doctemplates.starter_templates import ASSETS_DIR, read_starter_file, get_image
from doctemplates.starter_templates import is_annual_letter_samples as samples

TEMPLATE_NAME = 'IS Annual Letter (AL)'
FOLDER = 'is_annual_letter'
SIGNATURE_FILE = 'IS/SF_n.png'

# (role, image title, file in assets/, x, y, width, height, z_index, page) – positions in px on the 794 x 1123 A4 page
PLACED_IMAGES = [
    ('background', 'IS background', 'IS/Novis_HP_motyl_06062019_prev.png', 0, 0, 794, 1123, 0, 'all'),
    ('logo', 'IS logo', 'IS/NOVISLG.png', 53, 56, 156, 97, 10, 'all'),
    ('signature', 'IS signature SF', SIGNATURE_FILE, 360, 700, 227, 155, 10, 'last'),
]


class Command(BaseCommand):
    help = ('Create (or reset) the IS Annual Letter template (Jasper report AL_IS) with made-up sample Excels '
            '(main + insured persons) for the preview.')

    def handle(self, *args, **options):
        template, created = Template.objects.update_or_create(
            name=TEMPLATE_NAME,
            defaults={
                'country_code': 'IS',
                'document_type': 'AL',
                'html_content': read_starter_file(FOLDER, 'body.html'),
                'css_content': read_starter_file(FOLDER, 'style.css'),
                'footer_html': read_starter_file(FOLDER, 'footer.html'),
                'footer_top': 28,
                'margin_top': 115,
                'margin_bottom': 80,
                'margin_left': 40,
                'margin_right': 40,
                'detail_name': 'insured',
                'main_key': 'Contract_number',
                'detail_key': 'IdNum',
            },
        )

        for field, filename, columns, rows in (
            (template.sample_excel, 'al_is_sample_main.xlsx', samples.MAIN_COLUMNS, samples.MAIN_ROWS),
            (template.detail_excel, 'al_is_sample_insured.xlsx', samples.DETAIL_COLUMNS, samples.DETAIL_ROWS),
        ):
            if field:
                field.delete(save=False)
            field.save(filename, ContentFile(samples.to_xlsx(columns, rows)), save=False)
        template.save()

        # Re-place images from scratch so running the command again restores the original layout
        template.images.all().delete()
        for role, title, asset_path, x, y, width, height, z_index, page in PLACED_IMAGES:
            if not os.path.exists(os.path.join(ASSETS_DIR, asset_path)):
                self.stdout.write(self.style.WARNING(
                    f'assets/{asset_path} not found – the {role} is left out. Add the file and run the command again.'))
                continue
            TemplatePlacedImage.objects.create(
                template=template,
                role=role,
                image=get_image(title, asset_path),
                x=x, y=y, width=width, height=height, z_index=z_index, page=page,
            )

        action = 'Created' if created else 'Updated'
        self.stdout.write(self.style.SUCCESS(
            f'{action} template "{template.name}" (id {template.id}). '
            f'Preview rows: 1 = Wealth Insuring (7 insured persons), 2 = Life Savings Plan, '
            f'3 = Flexible Savings Plan, 4 = Life Protector.'))
