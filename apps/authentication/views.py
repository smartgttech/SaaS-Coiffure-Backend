from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer, InscriptionPersonnelSerializer, LogoutSerializer, UtilisateurMeSerializer
from .services import AuthService
from drf_spectacular.utils import extend_schema
from core.responses import success, error, created
from core.permissions import EstDuTenantCourant, EstProprietaire

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