

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sponsors', '0002_correspondence_godfather_income_sponsor'),
    ]

    operations = [
        migrations.CreateModel(
            name='Descr_Godfather',
            fields=[
                ('id', models.AutoField(db_column='spn_descr_godfather_id', primary_key=True, serialize=False)),
                ('name', models.CharField(db_column='name', max_length=10, verbose_name='Código')),
                ('description', models.CharField(db_column='description', max_length=100, verbose_name='Descripción')),
            ],
            options={
                'db_table': 'tbl_spn_descr_godfather',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Sponsored',
            fields=[
                ('id', models.AutoField(db_column='spn_sponsored_id', primary_key=True, serialize=False)),
                ('last_name_1', models.CharField(blank=True, db_column='last_name_1', max_length=100, null=True, verbose_name='Apellido 1')),
                ('last_name_2', models.CharField(blank=True, db_column='last_name_2', max_length=100, null=True, verbose_name='Apellido 2')),
                ('first_name_1', models.CharField(blank=True, db_column='first_name_1', max_length=100, null=True, verbose_name='Nombre 1')),
                ('first_name_2', models.CharField(blank=True, db_column='first_name_2', max_length=100, null=True, verbose_name='Nombre 2')),
                ('active', models.BooleanField(db_column='active', default=True, verbose_name='Activo')),
            ],
            options={
                'db_table': 'tbl_spn_sponsored',
                'managed': False,
            },
        ),
    ]
