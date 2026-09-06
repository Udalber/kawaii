from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('sorpresas_kawai', '0006_scoop_normal_inicial')]

    operations = [
        migrations.AddField(
            model_name='combo',
            name='descripcion',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='combo',
            name='imagen_url',
            field=models.URLField(blank=True, max_length=700, null=True),
        ),
    ]
