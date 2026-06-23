from django.db import connection
from .models import Tenant

class TenantRepository:

    def obtenir_courant(self):
        try:
            return Tenant.objects.get(schema_name=connection.schema_name)
        except Tenant.DoesNotExist:
            return None
        
    def modifier(self, tenant, data):
        for champ, valeur in data.items():
            setattr(tenant, champ, valeur)
        tenant.save()
        return tenant