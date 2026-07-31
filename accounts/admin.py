from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'city', 'country', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone', 'city')
    readonly_fields = ('user', 'created_at')

    def has_add_permission(self, request):
        # Profiles are auto-created when users register — never add manually
        return False
