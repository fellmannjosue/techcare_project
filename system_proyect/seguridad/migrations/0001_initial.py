# Generated by Django 5.1.7 on 2025-05-22 16:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ContableCamara',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('modelo', models.CharField(max_length=100, verbose_name='Modelo')),
                ('nombre', models.CharField(max_length=100, verbose_name='Nombre')),
                ('cantidad_modelo', models.PositiveIntegerField(verbose_name='Cantidad')),
                ('total', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Total')),
            ],
        ),
        migrations.CreateModel(
            name='InventarioCamara',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, verbose_name='Nombre de cámara')),
                ('modelo', models.CharField(max_length=100, verbose_name='Modelo')),
                ('serie', models.CharField(max_length=100, verbose_name='Serie')),
                ('tipo', models.CharField(max_length=50, verbose_name='Tipo de cámara')),
                ('ip_camara', models.GenericIPAddressField(verbose_name='IP cámara')),
                ('ip_acceso', models.GenericIPAddressField(verbose_name='IP de acceso')),
                ('ubic_gabinete', models.CharField(max_length=100, verbose_name='Ubicación gabinete')),
                ('canal', models.CharField(max_length=10, verbose_name='Canal')),
                ('nvr', models.CharField(max_length=100, verbose_name='NVR')),
            ],
        ),
        migrations.CreateModel(
            name='IdentificacionCamaraGabinete',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_gabinete', models.CharField(max_length=50, verbose_name='Núm. Gabinete')),
                ('switches', models.PositiveIntegerField(verbose_name='Cant. switches')),
                ('patchcords', models.PositiveIntegerField(verbose_name='Cant. patchcord')),
                ('puerto', models.CharField(max_length=50, verbose_name='Puerto')),
                ('nvr', models.CharField(max_length=100, verbose_name='NVR')),
                ('camara', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='seguridad.inventariocamara', verbose_name='Cámara')),
            ],
        ),
    ]
