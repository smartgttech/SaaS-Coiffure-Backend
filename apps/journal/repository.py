from repositories.base import BaseRepository
from .models import JournalAction


class JournalRepository(BaseRepository):

    def enregistrer(self, utilisateur, type_action, ressource, ressource_id=None, details_avant=None, details_apres=None):
        return JournalAction.objects.create(
            tenant=self.tenant,
            utilisateur_id=utilisateur.id if utilisateur else None,
            utilisateur_email=utilisateur.email if utilisateur else None,
            type_action=type_action,
            ressource=ressource,
            ressource_id=ressource_id,
            details_avant=details_avant,
            details_apres=details_apres
        )

    def historique_ressource(self, ressource, ressource_id):
        return JournalAction.objects.filter(
            tenant=self.tenant,
            ressource=ressource,
            ressource_id=ressource_id
        )

    def historique_utilisateur(self, utilisateur_id):
        return JournalAction.objects.filter(
            tenant=self.tenant,
            utilisateur_id=utilisateur_id
        )
    
    def liste(self, ressource=None, type_action=None):
        qs = JournalAction.objects.filter(tenant=self.tenant)
        if ressource:
            qs = qs.filter(ressource=ressource)
        if type_action:
            qs = qs.filter(type_action=type_action)
        return qs