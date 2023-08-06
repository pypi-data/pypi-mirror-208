from django.db import migrations, models
import djangorestfilemanager.models


class Migration(migrations.Migration):

    dependencies = [
        ('djangorestfilemanager', '0007_alter_file_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='file',
            field=models.FileField(max_length=255, null=True, upload_to=djangorestfilemanager.models.set_storage_file_dir, verbose_name='File'),
        ),
    ]
