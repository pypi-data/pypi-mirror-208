from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djangorestfilemanager', '0009_auto_20210810_0945'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='data',
            field=models.JSONField(default=dict, blank=True, null=True)
        ),
    ]
