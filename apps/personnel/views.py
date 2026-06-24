from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from core.responses import success, error, not_found
from core.permissions import EstDuTenantCourant, EstProprietaire
from .services import PerformanceService
from .serializers import (
    TransactionPerformanceSerializer, PointsActionSerializer,
    RecapitulatifPeriodeSerializer, RecapitulatifPersonnelSerializer
)


class PersonnelPointsAjouterView(APIView):
    permission_classes = [EstDuTenantCourant, EstProprietaire]

    @extend_schema(request=PointsActionSerializer, responses=None)
    def post(self, request, personnel_id):
        serializer = PointsActionSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message="Données invalides", errors=serializer.errors)

        service = PerformanceService()
        try:
            personnel = service.ajouter_points(
                personnel_id,
                serializer.validated_data['points'],
                serializer.validated_data['motif'],
                utilisateur=request.user
            )
            return success(
                data={'solde_points_performance': personnel.solde_points_performance},
                message="Points ajoutés"
            )
        except ValueError as e:
            return error(message=str(e), status_code=400)


class PersonnelPointsRetirerView(APIView):
    permission_classes = [EstDuTenantCourant, EstProprietaire]

    @extend_schema(request=PointsActionSerializer, responses=None)
    def post(self, request, personnel_id):
        serializer = PointsActionSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message="Données invalides", errors=serializer.errors)

        service = PerformanceService()
        try:
            personnel = service.retirer_points(
                personnel_id,
                serializer.validated_data['points'],
                serializer.validated_data['motif'],
                utilisateur=request.user
            )
            return success(
                data={'solde_points_performance': personnel.solde_points_performance},
                message="Points retirés"
            )
        except ValueError as e:
            return error(message=str(e), status_code=400)


class PersonnelPointsHistoriqueView(APIView):
    permission_classes = [EstDuTenantCourant, EstProprietaire]

    @extend_schema(responses=TransactionPerformanceSerializer(many=True))
    def get(self, request, personnel_id):
        service = PerformanceService()
        try:
            historique = service.historique(personnel_id)
            return success(
                data=TransactionPerformanceSerializer(historique, many=True).data,
                message="Historique des points"
            )
        except ValueError as e:
            return not_found(str(e))


class PersonnelRecapitulatifView(APIView):
    permission_classes = [EstDuTenantCourant, EstProprietaire]

    @extend_schema(request=RecapitulatifPeriodeSerializer, responses=None)
    def post(self, request, personnel_id):
        serializer = RecapitulatifPeriodeSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message="Données invalides", errors=serializer.errors)

        service = PerformanceService()
        try:
            recap = service.recapitulatif_periode(
                personnel_id,
                serializer.validated_data['date_debut'],
                serializer.validated_data['date_fin']
            )
            return success(data=recap, message="Récapitulatif de la période")
        except ValueError as e:
            return not_found(str(e))


class PersonnelRecapitulatifTousView(APIView):
    permission_classes = [EstDuTenantCourant, EstProprietaire]

    @extend_schema(
        request=RecapitulatifPeriodeSerializer,
        responses=RecapitulatifPersonnelSerializer(many=True)
    )
    def post(self, request):
        serializer = RecapitulatifPeriodeSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message="Données invalides", errors=serializer.errors)

        service = PerformanceService()
        resultats = service.recapitulatif_tous(
            serializer.validated_data['date_debut'],
            serializer.validated_data['date_fin']
        )
        return success(
            data=resultats,
            message="Récapitulatif de tout le personnel"
        )