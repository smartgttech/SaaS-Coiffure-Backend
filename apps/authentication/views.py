from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer, InscriptionPersonnelSerializer, LogoutSerializer
from .services import AuthService
from drf_spectacular.utils import extend_schema
from core.responses import success, error, created

# Endpoints de cette app
# ==================================================
# 1. CONNEXION
# ==================================================
class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message="Les données fournies ne correspondent pas.", errors=serializer.error)
        
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
    permission_classes = [AllowAny] # Ne pas oublier de restreindre l'accès ici uniquement au propriétaire après

    @extend_schema(request=InscriptionPersonnelSerializer)
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
    permission_classes = [IsAuthenticated]

    @extend_schema(request=LogoutSerializer)
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