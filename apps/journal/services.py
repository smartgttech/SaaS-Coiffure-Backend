from .repository import JournalRepository


class JournalService:

    def __init__(self):
        self.repo = JournalRepository()

    def enregistrer(self, utilisateur, type_action, ressource, ressource_id=None, details_avant=None, details_apres=None):
        return self.repo.enregistrer(
            utilisateur=utilisateur,
            type_action=type_action,
            ressource=ressource,
            ressource_id=ressource_id,
            details_avant=details_avant,
            details_apres=details_apres
        )
    
    def liste(self, ressource=None, type_action=None):
        return self.repo.liste(ressource=ressource, type_action=type_action)

    def historique_ressource(self, ressource, ressource_id):
        return self.repo.historique_ressource(ressource, ressource_id)