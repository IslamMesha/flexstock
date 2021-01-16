# Generated by Django 3.1.5 on 2021-01-12 19:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myshopify', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shopifyproduct',
            name='price',
        ),
        migrations.AddField(
            model_name='shopifyproduct',
            name='vendor',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='shopifyproduct',
            name='product_id',
            field=models.BigIntegerField(unique=True),
        ),
    ]
