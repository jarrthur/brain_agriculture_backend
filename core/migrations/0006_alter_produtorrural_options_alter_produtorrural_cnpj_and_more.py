# Generated by Django 5.0.2 on 2024-02-26 16:41

from django.db import migrations, models

import core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_remove_fazenda_estado'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='produtorrural',
            options={'verbose_name': 'Produtor Rural', 'verbose_name_plural': 'Produtores Rurais'},
        ),
        migrations.AlterField(
            model_name='produtorrural',
            name='cnpj',
            field=models.CharField(blank=True, default=None, max_length=14, null=True, unique=True, validators=[core.validators.validate_cnpj], verbose_name='CNPJ'),
        ),
        migrations.AlterField(
            model_name='produtorrural',
            name='cpf',
            field=models.CharField(blank=True, default=None, max_length=11, null=True, unique=True, validators=[core.validators.validate_cpf], verbose_name='CPF'),
        ),
    ]
