from django.contrib import admin
from .models import ContactMessage, SiteSettings


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_resolved', 'created_at')
    list_filter = ('is_resolved',)
    search_fields = ('name', 'email', 'subject', 'message')
    list_editable = ('is_resolved',)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'email', 'phone')

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()
