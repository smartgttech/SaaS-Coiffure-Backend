from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from core.responses import success, error, created, not_found
from core.permissions import EstDuTenantCourant, EstProprietaireOuEmploye
from .services import CommandeService
from .serializers import (
    CommandeSerializer, CommandeCreateSerializer,
    ChangerStatutCommandeSerializer
)


class CommandeListCreateView(APIView):
    permission_classes = [EstDuTenantCourant, EstProprietaireOuEmploye]

    @extend_schema(responses=CommandeSerializer(many=True))
    def get(self, request):
        service = CommandeService()
        filtres = {
            'statut': request.query_params.get('statut'),
            'cliente_id': request.query_params.get('cliente_id'),
        }
        filtres = {k: v for k, v in filtres.items() if v is not None}
        commandes = service.lister(**filtres)
        return success(
            data=CommandeSerializer(commandes, many=True).data,
            message="Liste des commandes"
        )

    @extend_schema(request=CommandeCreateSerializer, responses=CommandeSerializer)
    def post(self, request):
        serializer = CommandeCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message="Données invalides", errors=serializer.errors)

        service = CommandeService()
        try:
            commande = service.creer(serializer.validated_data, utilisateur=request.user)
            return created(
                data=CommandeSerializer(commande).data,
                message="Commande créée"
            )
        except ValueError as e:
            return error(message=str(e), status_code=400)


class CommandeDetailView(APIView):
    permission_classes = [EstDuTenantCourant, EstProprietaireOuEmploye]

    @extend_schema(responses=CommandeSerializer)
    def get(self, request, commande_id):
        service = CommandeService()
        try:
            commande = service.obtenir(commande_id)
            return success(
                data=CommandeSerializer(commande).data,
                message="Commande trouvée"
            )
        except ValueError as e:
            return not_found(str(e))


class CommandeChangerStatutView(APIView):
    permission_classes = [EstDuTenantCourant, EstProprietaireOuEmploye]

    @extend_schema(request=ChangerStatutCommandeSerializer, responses=CommandeSerializer)
    def post(self, request, commande_id):
        serializer = ChangerStatutCommandeSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message="Données invalides", errors=serializer.errors)

        service = CommandeService()
        try:
            commande = service.changer_statut(
                commande_id,
                serializer.validated_data['statut'],
                utilisateur=request.user
            )
            return success(
                data=CommandeSerializer(commande).data,
                message="Statut mis à jour"
            )
        except ValueError as e:
            return error(message=str(e), status_code=400)