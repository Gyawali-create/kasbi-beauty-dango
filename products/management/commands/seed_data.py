from django.core.management.base import BaseCommand
from django.core.files import File
from django.utils import timezone
from datetime import timedelta
from products.models import Category, Brand, Product, Coupon
from core.models import SiteSettings


class Command(BaseCommand):
    help = 'Seed the database with sample Kisba Beauty data'

    def handle(self, *args, **options):
        # Site settings with logo/favicon
        site = SiteSettings.load()
        site.site_name = 'Kisba Beauty'
        site.tagline = 'Beauty, delivered.'
        site.about_text = (
            'Kisba Beauty is Nepal\'s trusted destination for authentic skincare, '
            'makeup, and self-care essentials. We partner directly with trusted brands '
            'to bring you genuine products at honest prices, delivered right to your door.'
        )
        site.mission = (
            'To make quality beauty and self-care accessible to everyone, while '
            'championing transparency, authenticity, and excellent customer service.'
        )
        site.email = 'support@kisbabeauty.com'
        site.phone = '+977-1-4123456'
        site.address = 'Durbarmarg, Kathmandu, Nepal'
        try:
            with open('static/img/logo.png', 'rb') as f:
                site.logo.save('logo.png', File(f), save=False)
            with open('static/img/favicon.png', 'rb') as f:
                site.favicon.save('favicon.png', File(f), save=False)
        except FileNotFoundError:
            pass
        site.save()
        self.stdout.write(self.style.SUCCESS('Site settings ready.'))

        categories = ['Skincare', 'Makeup', 'Haircare', 'Fragrance', 'Bath & Body', 'Tools & Accessories']
        cat_objs = {}
        for name in categories:
            cat, _ = Category.objects.get_or_create(name=name)
            cat_objs[name] = cat

        brands = ['Kisba Originals', 'Glow Lab', 'Himal Botanics', 'Pure Skin Co.', 'Velvet Rose']
        brand_objs = {}
        for name in brands:
            b, _ = Brand.objects.get_or_create(name=name)
            brand_objs[name] = b

        products = [
            ('Hydrating Vitamin C Serum', 'Skincare', 'Glow Lab', 1450, 1199, 40, True,
             'A lightweight serum packed with Vitamin C and hyaluronic acid to brighten skin and even out tone.'),
            ('Matte Liquid Lipstick - Rosewood', 'Makeup', 'Velvet Rose', 650, None, 60, True,
             'Long-lasting, transfer-proof matte lipstick in a rich rosewood shade.'),
            ('Argan Oil Hair Serum', 'Haircare', 'Himal Botanics', 990, 799, 25, True,
             'Nourishing argan oil serum that tames frizz and adds shine without weighing hair down.'),
            ('Rose & Jasmine Eau de Parfum', 'Fragrance', 'Velvet Rose', 2200, None, 15, False,
             'A romantic floral fragrance blending fresh rose petals with jasmine and soft musk.'),
            ('Shea Butter Body Lotion', 'Bath & Body', 'Pure Skin Co.', 550, 449, 80, False,
             'Rich, fast-absorbing body lotion with shea butter for 24-hour hydration.'),
            ('Jade Facial Roller', 'Tools & Accessories', 'Kisba Originals', 850, None, 30, False,
             'Natural jade roller that helps reduce puffiness and improve circulation.'),
            ('Gentle Foaming Cleanser', 'Skincare', 'Pure Skin Co.', 720, None, 3, True,
             'A sulfate-free foaming cleanser suitable for all skin types, including sensitive skin.'),
            ('Charcoal Detox Face Mask', 'Skincare', 'Himal Botanics', 680, 599, 50, False,
             'Deep-cleansing charcoal mask that draws out impurities and unclogs pores.'),
            ('Volumizing Mascara', 'Makeup', 'Glow Lab', 590, None, 45, False,
             'Buildable formula that adds dramatic volume and length without clumping.'),
            ('Silk Hair Wrap Towel', 'Tools & Accessories', 'Kisba Originals', 450, None, 4, False,
             'Ultra-absorbent, gentle-on-hair towel wrap that reduces frizz and drying time.'),
            ('Coconut Milk Shampoo Bar', 'Haircare', 'Himal Botanics', 380, 320, 70, True,
             'Eco-friendly, plastic-free shampoo bar that cleanses and moisturizes hair naturally.'),
            ('Lavender Bath Salts', 'Bath & Body', 'Pure Skin Co.', 480, None, 55, False,
             'Calming lavender-infused Epsom salts for a relaxing, muscle-soothing soak.'),
        ]

        created_count = 0
        for name, cat, brand, price, discount, stock, featured, desc in products:
            obj, created = Product.objects.get_or_create(
                name=name,
                defaults=dict(
                    category=cat_objs[cat],
                    brand=brand_objs[brand],
                    price=price,
                    discount_price=discount,
                    stock=stock,
                    is_featured=featured,
                    is_active=True,
                    description=desc,
                    popularity=0,
                )
            )
            if created:
                created_count += 1
        self.stdout.write(self.style.SUCCESS(f'{created_count} products created.'))

        coupon, created = Coupon.objects.get_or_create(
            code='WELCOME10',
            defaults=dict(
                description='10% off for new customers',
                discount_percent=10,
                active=True,
                valid_from=timezone.now(),
                valid_until=timezone.now() + timedelta(days=365),
                usage_limit=0,
            )
        )
        self.stdout.write(self.style.SUCCESS('Coupon WELCOME10 ready.'))

        self.stdout.write(self.style.SUCCESS('Seeding complete! Visit /admin/ (admin / Kisba@2026) to manage everything.'))
