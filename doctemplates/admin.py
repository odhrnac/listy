from django.contrib import admin
from .models import Template, ImageAsset

# Register your models here.
@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'country_code', 'document_type', 'is_default', 'updated_at']
    list_filter = ['country_code', 'document_type', 'is_default']
    search_fields = ['name', 'html_content']

@admin.register(ImageAsset)
class ImageAssetAdmin(admin.ModelAdmin):
    list_display = ['title', 'uploaded_at']