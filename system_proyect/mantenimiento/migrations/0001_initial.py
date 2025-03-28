# Generated by Django 5.1.7 on 2025-03-17 18:28

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MaintenanceRecord',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('equipment_name', models.CharField(max_length=255)),
                ('problem_description', models.TextField()),
                ('maintenance_date', models.DateField()),
                ('technician', models.CharField(max_length=255)),
                ('maintenance_type', models.CharField(choices=[('Preventivo', 'Preventivo'), ('Correctivo', 'Correctivo'), ('Predictivo', 'Predictivo')], max_length=50)),
                ('maintenance_status', models.CharField(choices=[('Pendiente', 'Pendiente'), ('En Proceso', 'En Proceso'), ('Completado', 'Completado')], max_length=50)),
                ('activities_done', models.TextField(blank=True, null=True)),
                ('observations', models.TextField(blank=True, null=True)),
            ],
        ),
    ]
