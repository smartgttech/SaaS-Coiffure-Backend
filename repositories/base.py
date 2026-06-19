from core.tenant_context import get_current_tenant


class BaseRepository:
    """
    Classe de base pour tous les repositories.
    Injecte automatiquement le tenant_id dans chaque accès aux données.
    Tous les repositories héritent de cette classe.
    """

    def __init__(self):
        self.tenant = get_current_tenant()
        if self.tenant is None:
            raise Exception("Aucun tenant actif trouvé dans le contexte courant..")
