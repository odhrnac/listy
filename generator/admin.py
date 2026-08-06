from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import GenerationJob, GeneratedPDF, UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name = 'Country Permissions'
    extra = 0


class CustomUserAdmin(UserAdmin):
    inlines = [UserProfileInline]


# Re-register User with the inline profile
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.register(GenerationJob)
admin.site.register(GeneratedPDF)

# @admin.register(Template)
# class TemplateAdmin(admin.ModelAdmin):
#     list_display = ['name', 'country_code', 'document_type', 'is_default', 'updated_at']
#     list_filter = ['country_code', 'document_type', 'is_default']
#     search_fields = ['name', 'html_content']