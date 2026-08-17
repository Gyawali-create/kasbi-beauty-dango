from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_brand_logo_category_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_new_arrival',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='product',
            name='is_bestseller',
            field=models.BooleanField(default=False),
        ),
    ]
