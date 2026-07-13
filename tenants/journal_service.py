# tenants/journal_service.py

from django_tenants.utils import schema_context
from .models import JournalPlateforme


class JournalPlateformeService:

    @staticmethod
    def _extraire_ip(request):
        if not request:
            return None
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded:
            return x_forwarded.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')

    @classmethod
    def enregistrer(cls, super_admin, type_action, tenant=None, details=None, request=None):
        JournalPlateforme.objects.create(
            super_admin=super_admin,
            tenant=tenant,
            type_action=type_action,
            details=details,
            adresse_ip=cls._extraire_ip(request)
        )

    @staticmethod
    def lire_journal_tenant(tenant, ressource=None, type_action=None, limite=100):
        """
        Lit le journal d'actions métier d'un tenant (apps.journal.JournalAction)
        depuis le schéma public, en basculant temporairement sur le schéma
        du tenant concerné.
        """
        from apps.journal.models import JournalAction
        from apps.journal.serializers import JournalActionSerializer

        with schema_context(tenant.schema_name):
            qs = JournalAction.objects.all().order_by('-date')[:limite]
            if ressource:
                qs = qs.filter(ressource=ressource)
            if type_action:
                qs = qs.filter(type_action=type_action)
            return JournalActionSerializer(qs, many=True).data

    @staticmethod
    def liste_plateforme(tenant=None, type_action=None, limite=200):
        """Liste le journal plateforme (actions Super Admin), filtrable."""
        qs = JournalPlateforme.objects.select_related('super_admin', 'tenant').all()
        if tenant:
            qs = qs.filter(tenant=tenant)
        if type_action:
            qs = qs.filter(type_action=type_action)
        return qs[:limite]