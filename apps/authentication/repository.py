from repositories.base import BaseRepository
from .models import Utilisateur, Personnel

# Repository de cette app
# Hérite de BaseRepository qui injecte automatiquement le tenant_id

class UtilisateurRepository(BaseRepository):

    def par_email(self, email):
        try: 
            return Utilisateur.objects.get(email=email, tenant=self.tenant)
        except Utilisateur.DoesNotExist:
            return None
    
    def par_id(self, utilisateur_id):
        try:
            return Utilisateur.objects.get(id=utilisateur_id, tenant=self.tenant)
        except Utilisateur.DoesNotExist:
            return None
    
    def creer(self, email, password, role):
        utilisateur = Utilisateur.objects.create_user(
            email=email,
            password=password,
            tenant=self.tenant,
            role=role
        )
        return utilisateur



class PersonnalRepository(BaseRepository):

    def creer(self, utilisateur, nom, prenom, date_entree, specialite=None):
        return Personnel.objects.create(
            tenant=self.tenant,
            utilisateur=utilisateur,
            nom=nom,
            prenom=prenom,
            specialite=specialite,
            date_entree=date_entree
        )
    
    def par_utilisateur(self, utilisateur):
        try:
            return Personnel.objects.get(utilisateur=utilisateur)
        except Personnel.DoesNotExist:
            return None
        
    def par_id(self, personnel_id):
        try:
            return Personnel.objects.get(id=personnel_id, tenant=self.tenant)
        except Personnel.DoesNotExist:
            return None