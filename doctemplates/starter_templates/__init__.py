"""Ready-made templates, created by the create_is_* management commands."""
import os

from django.conf import settings
from django.core.files import File

from doctemplates.models import ImageAsset

STARTER_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(settings.BASE_DIR, 'assets')


def read_starter_file(folder, filename):
    with open(os.path.join(STARTER_DIR, folder, filename), encoding='utf-8') as f:
        return f.read()


def get_image(title, asset_path):
    """Reuse an image from the library by title, or upload it from assets/ (path relative to assets/)."""
    image = ImageAsset.objects.filter(title=title).first()
    if image:
        return image
    image = ImageAsset(title=title)
    with open(os.path.join(ASSETS_DIR, asset_path), 'rb') as f:
        image.image.save(os.path.basename(asset_path), File(f), save=True)
    return image
