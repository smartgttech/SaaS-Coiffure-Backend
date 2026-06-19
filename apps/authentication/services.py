# Logique métier de cette app
# Utilise le repository pour accéder aux données
from rest_framework_simplejwt.tokens import RefreshToken
from .repository import UtilisateurRepository, PersonnalRepository

class AuthService:

    def __init__(self):
        self.utilisateur_repo = UtilisateurRepository()
        self.personnel_repo = PersonnalRepository()

    def inscrire_personnel(self, email, password, nom, prenom, date_entree, role='employe', specialite=None):
        """
        Crée un utilisateur + son profil Personnel associé
        """
        utilisateur_existant = self.utilisateur_repo.par_email(email)
        if utilisateur_existant:
            raise ValueError("Un compte existe déjà avec cet email.")
        
        utilisateur = self.utilisateur_repo.creer(email=email, password=password, role=role)
        personnel = self.personnel_repo.creer(
            utilisateur=utilisateur,
            nom=nom,
            prenom=prenom,
            date_entree=date_entree,
            specialite=specialite,
        )
        return utilisateur, personnel
    
    def connecter(self, email, password):
        """
        Verifie les identifiants et retourne les tokens JWT si valides
        """
        utilisateur = self.utilisateur_repo.par_email(email)
        
        if utilisateur is None:
            raise ValueError("Email ou mot de passe invalide.")
        
        if not utilisateur.check_password(password):
            raise ValueError("Email ou mot de passe invalide.")
        
        if not utilisateur.is_active:
            raise ValueError("Le compte auquel vous voulez accéder n'est pas activé.")
        
        refresh = RefreshToken.for_user(utilisateur)
        refresh['role'] = utilisateur.role
        refresh['tenant_id'] = utilisateur.tenant_id

        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'utililsateur': {
                'id': utilisateur.id,
                'email': utilisateur.email,
                'role': utilisateur.role,
            }
        }