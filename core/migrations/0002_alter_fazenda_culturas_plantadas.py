# Generated by Django 5.0.2 on 2024-02-24 21:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fazenda',
            name='culturas_plantadas',
            field=models.ManyToManyField(related_name='fazendas', to='core.cultura'),
        ),
    ]
