# Generated by Django 5.1.4 on 2024-12-06 20:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_item_discount_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='description',
            field=models.TextField(default='this is a test descreption', max_length=1000),
            preserve_default=False,
        ),
    ]
