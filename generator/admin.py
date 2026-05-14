from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, GenerationJob, GeneratedPDF


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