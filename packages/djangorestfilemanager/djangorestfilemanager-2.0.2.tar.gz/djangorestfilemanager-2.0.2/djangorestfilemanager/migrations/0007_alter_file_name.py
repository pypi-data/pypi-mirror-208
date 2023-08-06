from django.db import migrations, models
import djangorestfilemanager.models


class Migration(migrations.Migration):

    dependencies = [
        ('djangorestfilemanager', '0006_auto_20200429_1220'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Name'),
        ),
    ]
