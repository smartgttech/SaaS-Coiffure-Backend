from django_tenants.utils import get_current_schema_name
from tenants.models import Tenant

def get_current_tenant():
    """
    Retourne le tenant actuellement actif basé sur le schéma courant.
    A utiliser dans les services et les repositories pour récupérer le tenant
    sans avoir à le passer explicitement et manuellement.
    """
    schema_name = get_current_schema_name()
    try:
        return Tenant.objects.get(schema_name=schema_name)
    except Tenant.DoesNotExist:
        return None