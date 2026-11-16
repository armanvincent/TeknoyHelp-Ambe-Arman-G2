from django.db import migrations

DEFAULTS = [
    'Claiming Documents',
    'Submitting Forms',
    'Buying Items',
    'Picking Up Belongings',
    'Printing / Photocopying',
    'Others',
]


def add_categories(apps, schema_editor):
    Category = apps.get_model('errands', 'Category')
    for name in DEFAULTS:
        Category.objects.get_or_create(name=name)


def remove_categories(apps, schema_editor):
    Category = apps.get_model('errands', 'Category')
    Category.objects.filter(name__in=DEFAULTS).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('errands', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_categories, remove_categories),
    ]