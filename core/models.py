from django.db import models


class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} - {self.subject or "No subject"}'


class SiteSettings(models.Model):
    """Singleton-style model holding company/about info, editable from admin."""
    site_name = models.CharField(max_length=100, default='Kisba Beauty')
    tagline = models.CharField(max_length=200, blank=True, default='Beauty, delivered.')
    about_text = models.TextField(blank=True, default='Kisba Beauty brings you authentic, high quality beauty and cosmetic products.')
    mission = models.TextField(blank=True)
    email = models.EmailField(blank=True, default='support@kisbabeauty.com')
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    logo = models.ImageField(upload_to='site/', blank=True, null=True)
    favicon = models.ImageField(upload_to='site/', blank=True, null=True)
    about_image = models.ImageField(upload_to='site/', blank=True, null=True, help_text='Image shown on the About Us page')
    # Returns & Refunds policy text
    returns_policy = models.TextField(blank=True, help_text='Returns & Refunds policy shown on the Returns page')
    # Social media links
    facebook_url  = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    youtube_url   = models.URLField(blank=True)
    tiktok_url    = models.URLField(blank=True)

    class Meta:
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
