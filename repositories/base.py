class BaseRepository:
    """
    Classe de base pour tous les repositories.
    Injecte automatiquement le tenant_id dans chaque accès aux données.
    Tous les repositories héritent de cette classe.
    """

    def __init__(self, tenant_id):
        self.tenant_id = tenant_id
