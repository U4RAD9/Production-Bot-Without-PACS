# Generated by Django 5.1 on 2024-10-04 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_alter_dicomdata_age_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dicomfile',
            name='dicom_file',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='jpegfile',
            name='jpeg_file',
            field=models.CharField(max_length=500),
        ),
    ]
