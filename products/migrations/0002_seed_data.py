from django.db import migrations
from decimal import Decimal


def seed_data(apps, schema_editor):
    Category = apps.get_model('products', 'Category')
    Product = apps.get_model('products', 'Product')

    cat_map = {}
    for name in ['Default', 'Electronics', 'Books']:
        cat, _ = Category.objects.get_or_create(name=name)
        cat_map[name] = cat

    items = [
        ('USB Cable', 'Electronics', Decimal('5.50')),
        ('Django Book', 'Books', Decimal('25.00')),
        ('Notebook', 'Default', Decimal('2.00')),
    ]
    for name, cat_name, price in items:
        Product.objects.get_or_create(
            name=name,
            defaults={
                'price': price,
                'category': cat_map[cat_name],
                'description': '',
            },
        )


def unseed_data(apps, schema_editor):
    Category = apps.get_model('products', 'Category')
    Product = apps.get_model('products', 'Product')
    Product.objects.filter(name__in=['USB Cable', 'Django Book', 'Notebook']).delete()
    Category.objects.filter(name__in=['Default', 'Electronics', 'Books']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_data, unseed_data),
    ]


