# tenants/management/commands/initialiser_plateforme.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tenants.models import Tenant, Domain

User = get_user_model()

class Command(BaseCommand):
    help = 'Initialise la plateforme : tenant public + compte Super Admin'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email du Super Admin')
        parser.add_argument('--mot-de-passe', type=str, help='Mot de passe du Super Admin')

    def handle(self, *args, **kwargs):
        tenant_public = self._assurer_tenant_public()
        self._assurer_super_admin(tenant_public, **kwargs)

    def _assurer_tenant_public(self):
        try:
            tenant_public = Tenant.objects.get(schema_name='public')
            self.stdout.write(self.style.WARNING('Le tenant public existe déjà — étape ignorée.'))
            return tenant_public
        except Tenant.DoesNotExist:
            self.stdout.write(self.style.NOTICE('Tenant public introuvable. Création en cours...'))

            tenant_public = Tenant(
                schema_name='public',
                nom='HosJos Platform',
                sous_domaine='public',
                statut='actif',
                type_licence='illimite',
                couleur_primaire="#0F172A",
                couleur_secondaire="#1E293B"
            )
            tenant_public.save()

            Domain.objects.create(
                domain='localhost',
                tenant=tenant_public,
                is_primary=True
            )

            self.stdout.write(self.style.SUCCESS('Tenant public créé avec succès.'))
            return tenant_public

    def _assurer_super_admin(self, tenant_public, **kwargs):
        email = kwargs.get('email') or input('Email du Super Admin : ')
        mot_de_passe = kwargs.get('mot_de_passe') or input('Mot de passe : ')

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'Un Super Admin avec l\'email {email} existe déjà — étape ignorée.'))
            return

        user = User.objects.create_superuser(
            email=email,
            password=mot_de_passe,
            role='super_admin',
            tenant=tenant_public,
        )

        self.stdout.write(self.style.SUCCESS(
            f'Super Admin créé avec succès : {user.email} — affecté à {tenant_public.nom}'
        ))