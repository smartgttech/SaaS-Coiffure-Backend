from rest_framework.views import APIView
from drf_spectacular .utils import extend_schema
from core.responses import success, error, created, not_found
from core.permissions import EstDuTenantCourant, EstProprietaireOuEmploye, AccesModuleRequis
from core.licences import (
    MODULE_CLIENTS
)
from .services import ClienteService
from .serializers import (
    ClienteSerializer, ClienteCreateSerializer, ClienteUpdateSerializer,
    TransactionPointsSerializer, PointsActionSerializer
)

# Endpoints de cette app
# ===================================
# 1. CREATE LIST
# ===================================
class ClienteListCreateView(APIView):
    permission_classes = [EstDuTenantCourant, AccesModuleRequis(MODULE_CLIENTS) ,EstProprietaireOuEmploye]

    @extend_schema(responses=ClienteSerializer(many=True))
    def get(self, request):
        service = ClienteService()
        clientes = service.lister()
        serializer = ClienteSerializer(clientes, many=True)
        return success(data=serializer.data, message="Liste des clientes")
    

    @extend_schema(request=ClienteCreateSerializer)
    def post(self, request):
        serializer = ClienteCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message="Les données fournies sont invalides", errors=serializer.errors)
        
        service = ClienteService()
        try:
            cliente = service.creer(serializer.validated_data, utilisateur=request.user)
            return created(
                data=ClienteSerializer(cliente).data,
                message="Client créé avec succès"
            )
        except ValueError as e:
            return error(message=str(e), status_code=400)


# =============================
# 2. DETAILS & UPDATE CLIENT
# =============================
class ClienteDetailView(APIView):
    permission_classes = [EstDuTenantCourant, AccesModuleRequis(MODULE_CLIENTS) ,EstProprietaireOuEmploye]

    @extend_schema(responses=ClienteSerializer)
    def get(self, request, cliente_id):
        service = ClienteService()
        try:
            cliente = service.obtenir_par_id(cliente_id)
            return success(data=ClienteSerializer(cliente).data, message="Cliente trouvée")
        except ValueError as e:
            return not_found(str(e))

    @extend_schema(request=ClienteUpdateSerializer, responses=ClienteSerializer)
    def patch(self, request, cliente_id):
        serializer = ClienteUpdateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return error(message="Données invalides", errors=serializer.errors)

        service = ClienteService()
        try:
            cliente = service.modifier(cliente_id, serializer.validated_data, utilisateur=request.user)
            return success(data=ClienteSerializer(cliente).data, message="Cliente mise à jour")
        except ValueError as e:
            return not_found(str(e))

    @extend_schema(responses=None)
    def delete(self, request, cliente_id):
        service = ClienteService()
        try:
            service.archiver(cliente_id, utilisateur=request.user)
            return success(message="Cliente archivée")
        except ValueError as e:
            return not_found(str(e))
        

# ===================================
# 3. POINTS FIDELITE HISTORIQUE CLIENT
# ===================================
class ClientePointsHistoriqueView(APIView):
    permission_classes = [EstDuTenantCourant, AccesModuleRequis(MODULE_CLIENTS) ,EstProprietaireOuEmploye]

    @extend_schema(responses=TransactionPointsSerializer(many=True))
    def get(self, request, cliente_id):
        service = ClienteService()
        try:
            historique = service.historique_points(cliente_id)
            serializer = TransactionPointsSerializer(historique, many=True)
            return success(data=serializer.data, message="Historique des points")
        except ValueError as e:
            return not_found(str(e))
        

# =====================================
# 4. POINTS FIDELITE AJOUTER ET RETIRER CLIENT
# =====================================
class ClientePointsAjouterView(APIView):
    permission_classes = [EstDuTenantCourant, AccesModuleRequis(MODULE_CLIENTS) ,EstProprietaireOuEmploye]

    @extend_schema(request=PointsActionSerializer, responses=ClienteSerializer)
    def post(self, request, cliente_id):
        serializer = PointsActionSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message="Données invalides", errors=serializer.errors)

        service = ClienteService()
        try:
            cliente = service.ajouter_points(
                cliente_id,
                serializer.validated_data['points'],
                serializer.validated_data['motif'],
                utilisateur=request.user
            )
            return success(data=ClienteSerializer(cliente).data, message="Points ajoutés")
        except ValueError as e:
            return error(message=str(e), status_code=400)


class ClientePointsRetirerView(APIView):
    permission_classes = [EstDuTenantCourant, EstProprietaireOuEmploye, AccesModuleRequis(MODULE_CLIENTS)]

    @extend_schema(request=PointsActionSerializer, responses=ClienteSerializer)
    def post(self, request, cliente_id):
        serializer = PointsActionSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message="Données invalides", errors=serializer.errors)

        service = ClienteService()
        try:
            cliente = service.retirer_points(
                cliente_id,
                serializer.validated_data['points'],
                serializer.validated_data['motif'],
                utilisateur=request.user
            )
            return success(data=ClienteSerializer(cliente).data, message="Points retirés")
        except ValueError as e:
            return error(message=str(e), status_code=400)
