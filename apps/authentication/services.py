# Logique métier de cette app
# Utilise le repository pour accéder aux données
from rest_framework_simplejwt.tokens import RefreshToken
from .repository import UtilisateurRepository, PersonnalRepository
from datetime import timedelta
from django.utils import timezone

MAX_TENTATIVES = 3
DUREE_BLOCAGE_MINUTES = 15

class AuthService:

    def __init__(self):
        self.utilisateur_repo = UtilisateurRepository()
        self.personnel_repo = PersonnalRepository()


    # Service d'inscription
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
    
    # Service de connexion
    def connecter(self, email, password):
        """
        Verifie les identifiants et retourne les tokens JWT si valides
        """
        utilisateur = self.utilisateur_repo.par_email(email)
        
        if utilisateur is None:
            raise ValueError("Email ou mot de passe invalide.")
        
        # Vérification si le compte est actuellement bloqué
        if utilisateur.bloque_jusqu_a and utilisateur.bloque_jusqu_a > timezone.now():

            minutes_restantes = int((utilisateur.bloque_jusqu_a - timezone.now()).total_seconds() / 60) + 1
            raise ValueError(f"Compte temporairement bloqué. Réessayez dans {minutes_restantes} minute(s).")

        # Si le blocage est expiré, on réinitialise
        if utilisateur.bloque_jusqu_a and utilisateur.bloque_jusqu_a <= timezone.now():
            utilisateur.tentatives_echouees = 0
            utilisateur.bloque_jusqu_a = None
            utilisateur.save()
        
        if not utilisateur.check_password(password):
            utilisateur.tentatives_echouees += 1

            # Blocage du compte après nombre de tentatives échouées maximum
            if utilisateur.tentatives_echouees >= MAX_TENTATIVES:
                utilisateur.bloque_jusqu_a = timezone.now() + timedelta(minutes=DUREE_BLOCAGE_MINUTES)
                utilisateur.save()
                raise ValueError("Trop de tentatives échouées. Compte bloqué pendant {int{DUREE_BLOCAGE_MINUTES}} minutes. ")
        
            # Incrémentation du nombre de tentatives en cas d'identifiants incorrects et mise à jour des variables correspondantes
            utilisateur.save()
            tentative_restantes = MAX_TENTATIVES - utilisateur.tentatives_echouees
            raise ValueError(f"Identifiants invalides . {tentative_restantes} tentatives restantes")
        

        if not utilisateur.is_active:
            raise ValueError("Le compte auquel vous voulez accéder n'est pas activé.")
        
        # Connexion réussie - On réinitialise tous les compteurs et toutes les valeurs
        utilisateur.tentatives_echouees = 0
        utilisateur.bloque_jusqu_a = None
        utilisateur.save()

        # Création et envoi des informations nécessaires dans la réponse
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
    
    # Service d'obtention du profil personnel
    def obtenir_profil(self, utilisateur):
        """
        Retourne les informations du profil de l'utilisateur connecté,
        en allant chercher son profil personnel si disponible.
        """

        personnel = self.personnel_repo.par_utilisateur(utilisateur)

        return { 
            'id': utilisateur.id,
            'email': utilisateur.email,
            'role': utilisateur.role,
            'tenant_id': utilisateur.tenant_id,
            'nom': personnel.nom if personnel else None,
            'prenom': personnel.prenom if personnel else None,
        }