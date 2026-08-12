from django.contrib import admin
from django.utils.html import format_html
from django_summernote.admin import SummernoteModelAdmin
from .models import ContactMessage, SiteSettings


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'short_message', 'is_resolved', 'created_at')
    list_filter = ('is_resolved', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    list_editable = ('is_resolved',)
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

    def short_message(self, obj):
        return obj.message[:80] + '...' if len(obj.message) > 80 else obj.message
    short_message.short_description = 'Message Preview'

    def has_add_permission(self, request):
        # Messages come from the contact form only
        return False


@admin.register(SiteSettings)
class SiteSettingsAdmin(SummernoteModelAdmin):
    summernote_fields = ('returns_policy',)
    list_display = ('site_name', 'tagline', 'email', 'phone', 'address')

    fieldsets = (
        ('Brand', {
            'fields': ('site_name', 'tagline', 'logo', 'favicon'),
        }),
        ('About Content', {
            'fields': ('about_text', 'mission', 'about_image'),
        }),
        ('Contact Info', {
            'fields': ('email', 'phone', 'address'),
        }),
        ('Social Media Links', {
            'description': 'Add full URLs e.g. https://facebook.com/yourpage',
            'fields': ('facebook_url', 'instagram_url', 'youtube_url', 'tiktok_url'),
        }),
        ('Returns & Refunds Policy', {
            'description': 'Leave blank to show the default policy. Write your own to override it.',
            'fields': ('returns_policy',),
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
