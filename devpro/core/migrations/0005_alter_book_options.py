# Generated by Django 4.1 on 2022-08-10 10:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_book_edition_alter_book_publication_year'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='book',
            options={'ordering': ('name',)},
        ),
    ]
