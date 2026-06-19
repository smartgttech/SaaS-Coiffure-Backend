from django.db import connection
from tenants.models import Tenant


def get_current_tenant():
    """
    Retourne le tenant actuellement actif basé sur le schéma courant.
    À utiliser dans les services et repositories pour récupérer
    le tenant sans avoir à le passer manuellement.
    """
    schema_name = connection.schema_name
    try:
        return Tenant.objects.get(schema_name=schema_name)
    except Tenant.DoesNotExist:
        return None