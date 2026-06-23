from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    LoginSerializer, InscriptionPersonnelSerializer, 
    LogoutSerializer, UtilisateurMeSerializer,
    PersonnelSerializer, PersonnelUpdateSerializer
)
from .services import AuthService, PersonnelService
from drf_spectacular.utils import extend_schema
from core.responses import success, error, created, not_found
from core.permissions import EstDuTenantCourant, EstProprietaire, EstProprietaireOuEmploye
from tenants.services import TenantService
from tenants.serializers import TenantPublicSerializer, TenantUpdateSerializer

# Endpoints de cette app
# ==================================================
# 1. CONNEXION
# ==================================================
class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=LoginSerializer, responses=None)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message="Les données fournies ne correspondent pas.", errors=serializer.errors)
        
        service = AuthService()
        try:
            resultat = service.connecter(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            return success(data=resultat, message="Connexion Réussie")
        except ValueError as e:
            return error(message=str(e), status_code=401)
        

# ========================================================
# 2. INSCRIPTION PERSONNEL
# ========================================================
class InscriptionPersonnelView(APIView):
    permission_classes = [IsAuthenticated, EstDuTenantCourant, EstProprietaire] # Ne pas oublier de restreindre l'accès ici uniquement au propriétaire après

    @extend_schema(request=InscriptionPersonnelSerializer, responses=None)
    def post(self, request):
        serializer = InscriptionPersonnelSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message="Données invalides", errors=serializer.errors)

        service = AuthService()
        try:
            utilisateur, personnel = service.inscrire_personnel(**serializer.validated_data)
            return created(
                data={'id': utilisateur.id, 'email': utilisateur.email},
                message="Compte créé avec succès"
            )
        except ValueError as e:
            return error(message=str(e), status_code=400)
        

# ===========================================================
# 3. LOGOUT (DECONNEXION ET BLACKLISTING)
# ===========================================================
class LogoutView(APIView):
    permission_classes = [IsAuthenticated, EstDuTenantCourant]

    @extend_schema(request=LogoutSerializer, responses=None)
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message="Données invalides", errors=serializer.errors)

        try:
            token = RefreshToken(serializer.validated_data['refresh'])
            token.blacklist()
            return success(message="Déconnexion réussie")
        except Exception:
            return error(message="Token invalide ou déjà expiré", status_code=400)
        

# ===============================================================
# 4. PROFIL PERSONNEL
# ===============================================================
class MeView(APIView):
    permission_classes = [IsAuthenticated, EstDuTenantCourant]

    @extend_schema(responses=UtilisateurMeSerializer)
    def get(self, request):
        service = AuthService()
        profil = service.obtenir_profil(request.user)
        return success(data=profil, message="Profil récupéré")
    

class PersonnelListView(APIView):
    permission_classes = [IsAuthenticated, EstDuTenantCourant, EstProprietaire]

    @extend_schema(responses=PersonnelSerializer(many=True))
    def get(self, request):
        service = PersonnelService()
        personnel = service.lister()
        return success(
            data=PersonnelSerializer(personnel, many=True).data,
            message="Liste du personnel"
        )


# ==================================================
# 5. DETAIL D'UN MEMBRE DU PERSONNEL
# =================================================
class PersonnelDetailView(APIView):
    permission_classes = [IsAuthenticated, EstDuTenantCourant, EstProprietaire]

    @extend_schema(responses=PersonnelSerializer)
    def get(self, request, personnel_id):
        service = PersonnelService()
        try:
            personnel = service.obtenir(personnel_id)
            return success(
                data=PersonnelSerializer(personnel).data,
                message="Membre du personnel trouvé"
            )
        except ValueError as e:
            return not_found(str(e))

    @extend_schema(request=PersonnelUpdateSerializer, responses=PersonnelSerializer)
    def patch(self, request, personnel_id):
        serializer = PersonnelUpdateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return error(message="Données invalides", errors=serializer.errors)

        service = PersonnelService()
        try:
            personnel = service.modifier(
                personnel_id,
                serializer.validated_data,
                utilisateur=request.user
            )
            return success(
                data=PersonnelSerializer(personnel).data,
                message="Personnel mis à jour"
            )
        except ValueError as e:
            return not_found(str(e))

    @extend_schema(responses=None)
    def delete(self, request, personnel_id):
        service = PersonnelService()
        try:
            service.desactiver(personnel_id, utilisateur=request.user)
            return success(message="Compte désactivé")
        except ValueError as e:
            return not_found(str(e))
        

# =============================================================
# 6. MON SALON
# =============================================================
class MonSalonView(APIView):
    permission_classes = [IsAuthenticated, EstDuTenantCourant, EstProprietaire]

    @extend_schema(responses=TenantPublicSerializer)
    def get(self, request):
        service = TenantService()
        try:
            tenant = service.obtenir_courant()
            return success(
                data=TenantPublicSerializer(tenant).data,
                message="Informations du salon"
            )
        except ValueError as e:
            return error(message=str(e), status_code=404)

    @extend_schema(request=TenantUpdateSerializer, responses=TenantPublicSerializer)
    def patch(self, request):
        serializer = TenantUpdateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return error(message="Données invalides", errors=serializer.errors)

        service = TenantService()
        try:
            tenant = service.modifier(serializer.validated_data)
            return success(
                data=TenantPublicSerializer(tenant).data,
                message="Informations du salon mises à jour"
            )
        except ValueError as e:
            return error(message=str(e), status_code=404)
