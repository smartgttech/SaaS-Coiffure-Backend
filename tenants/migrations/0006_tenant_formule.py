# Generated manually — ajoute le champ `formule` (palier fonctionnel),
# distinct de `type_licence` (cadence de facturation). Voir core/licences.py
# et tenants/models.py pour la justification de cette séparation.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0005_tenant_statut_avant_suspension_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenant',
            name='formule',
            field=models.CharField(
                choices=[
                    ('essai', 'Essai — accès complet, durée limitée'),
                    ('basic', 'Basic'),
                    ('basic_plus', 'Basic+'),
                    ('pro', 'Pro'),
                    ('full', 'Full'),
                ],
                default='essai',
                help_text='Détermine les modules accessibles. Voir core/licences.py',
                max_length=20,
            ),
        ),
    ]
