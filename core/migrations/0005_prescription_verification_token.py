
import uuid

from django.db import migrations, models


def generate_verification_tokens(apps, schema_editor):
    Prescription = apps.get_model('core', 'Prescription')

    for prescription in Prescription.objects.all().iterator():
        prescription.verification_token = uuid.uuid4()
        prescription.save(update_fields=['verification_token'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_prescriptionversion_action'),
    ]

    operations = [
        migrations.AddField(
            model_name='prescription',
            name='verification_token',
            field=models.UUIDField(
                null=True,
                editable=False,
            ),
        ),

        migrations.RunPython(
            generate_verification_tokens,
            reverse_code=migrations.RunPython.noop,
        ),

        migrations.AlterField(
            model_name='prescription',
            name='verification_token',
            field=models.UUIDField(
                default=uuid.uuid4,
                unique=True,
                editable=False,
            ),
        ),
    ]
