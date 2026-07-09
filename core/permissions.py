# Fichier de sécurité ajoutée. 
from rest_framework.permissions import BasePermission
from django.db import connection

class EstDuTenantCourant(BasePermission):
    """
    Vérifie que l'utilisateur authentifié appartient bien au tenant correspondant
    au schéma actuellement actif. Empêche un utilisateur du tenant A d'utiliser son
    token sur le tenant B.
    """

    message = "Cet utilisateur n'appartient pas à ce salon."

    def has_permission(self, request, view):
        # Vérifier que l'utilisateur existe et est authentifié
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Vérifier que le compte est toujours actif en base 
        if not request.user.is_active:
            return False
        
        # Sinon continuer
        from tenants.models import Tenant
        try:
            tenant_courant = Tenant.objects.get(schema_name=connection.schema_name)
        except Tenant.DoesNotExist:
            return False
        
        return request.user.tenant_id == tenant_courant.id
    

class EstProprietaire(BasePermission):
    message = "Action réservée au propriétaire."

    def has_permission(self, request, view):
        return (
            request.user 
            and request.user.is_authenticated 
            and request.user.role == 'proprietaire'
        )
    
class EstProprietaireOuEmploye(BasePermission):
    message = "Action réservée au personnel du salon."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated 
            and request.user.role in ['proprietaire', 'employe', 'stagiaire']
        )
    
class EstSuperAdmin(BasePermission):
    message = "Action réservée au Super Administrateur"

    def has_permission(self, request, view):
        return (
            request.user 
            and request.user.is_authenticated 
            and request.user.role == 'super_admin'
            and request.user.is_staff == True
        )


def AccesModuleRequis(module: str):
    """
    Fabrique une classe de permission DRF qui vérifie que le tenant courant
    a accès au module donné, selon son type_licence (voir core/licences.py).

    Usage dans une vue :
        permission_classes = [IsAuthenticated, EstDuTenantCourant, AccesModuleRequis('stock')]

    Pourquoi une fabrique de classe plutôt qu'une permission unique paramétrée
    à l'instanciation : DRF instancie les permission_classes sans arguments
    (`Permission()`), donc on ne peut pas leur passer `module` via __init__
    sans réécrire le mécanisme d'instanciation de DRF. Générer une classe
    dédiée par appel est le pattern standard pour ce besoin.
    """
    from core.licences import tenant_a_acces_module
    from tenants.models import Tenant

    class _AccesModuleRequis(BasePermission):
        message = f"Ce module ({module}) n'est pas inclus dans votre palier de licence actuel."

        def has_permission(self, request, view):
            try:
                tenant = Tenant.objects.get(schema_name=connection.schema_name)
            except Tenant.DoesNotExist:
                return False
            return tenant_a_acces_module(tenant, module)

    _AccesModuleRequis.__name__ = f"AccesModuleRequis_{module}"
    return _AccesModuleRequis