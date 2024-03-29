# Generated by Django 5.0.2 on 2024-02-24 02:41

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='E-mail')),
                ('nome', models.CharField(max_length=100)),
                ('data_registro', models.DateTimeField(auto_now_add=True, verbose_name='Data de registro')),
                ('is_active', models.BooleanField(default=True, verbose_name='Ativo?')),
                ('is_admin', models.BooleanField(default=False, verbose_name='Administrador?')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
