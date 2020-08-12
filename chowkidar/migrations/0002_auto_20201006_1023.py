from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chowkidar', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='refreshtoken',
            old_name='created',
            new_name='issued',
        ),
    ]
