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
        if not request.user or not request.user.is_authenticated:
            return False
        
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