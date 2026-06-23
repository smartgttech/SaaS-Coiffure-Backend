from .repository import TenantRepository

class TenantService:

    def __init__(self):
        self.repo = TenantRepository()

    def obtenir_courant(self):
        tenant = self.repo.obtenir_courant()
        if tenant is None:
            raise ValueError("Salon introuvable.")
        return tenant

    def modifier(self, data):
        tenant = self.obtenir_courant()
        return self.repo.modifier(tenant, data)