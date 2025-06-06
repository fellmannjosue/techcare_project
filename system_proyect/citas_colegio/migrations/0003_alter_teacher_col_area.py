

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('citas_colegio', '0002_alter_schedule_col_day_of_week_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacher_col',
            name='area',
            field=models.CharField(choices=[('Matematicas Bachillerato', 'Matematicas Bachillerato'), ('Matematicas Basica', 'Matematicas Basica'), ('Generales Bachillerato', 'Generales Bachillerato'), ('Español General ', 'Español General '), ('Ciencias Sociales Basicas ', 'Ciencias Sociales Basicas '), ('Ciencias Sociales Bachillerato ', 'Ciencias Sociales Bachillerato '), ('Generales Basicas ', 'Generales Basicas '), ('Ciencias Naturales Bachillerato', 'Ciencias Naturales Bachillerato'), ('Ciencias Naturales Basica', 'Ciencias Naturales Basica'), ('Artes', 'Artes'), ('Ingles ', 'Ingles ')], max_length=50),
        ),
    ]
