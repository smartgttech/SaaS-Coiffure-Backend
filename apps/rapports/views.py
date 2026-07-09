from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from core.responses import success, error
from core.permissions import EstDuTenantCourant, EstProprietaire, AccesModuleRequis
from core.licences import MODULE_TABLEAU_BORD, MODULE_RAPPORTS_AVANCES, MODULE_SMS_MARKETING
from .services import RapportService
from .serializers import PeriodeSerializer, InactiviteSerializer
from apps.caisse.serializers import PaiementSerializer


class TableauDeBordView(APIView):
    permission_classes = [EstDuTenantCourant, AccesModuleRequis(MODULE_TABLEAU_BORD), EstProprietaire]

    @extend_schema(responses=None)
    def get(self, request):
        service = RapportService()
        donnees = service.tableau_de_bord()
        return success(data=donnees, message="Tableau de bord")


class RapportFinancierView(APIView):
    permission_classes = [EstDuTenantCourant, AccesModuleRequis(MODULE_TABLEAU_BORD), EstProprietaire]

    @extend_schema(request=PeriodeSerializer, responses=None)
    def post(self, request):
        serializer = PeriodeSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message="Données invalides", errors=serializer.errors)

        service = RapportService()
        rapport = service.rapport_financier(
            serializer.validated_data['date_debut'],
            serializer.validated_data['date_fin']
        )
        return success(data=rapport, message="Rapport financier")


class RapportImpayesView(APIView):
    permission_classes = [EstDuTenantCourant, AccesModuleRequis(MODULE_TABLEAU_BORD), EstProprietaire]

    @extend_schema(responses=None)
    def get(self, request):
        service = RapportService()
        rapport = service.rapport_impayés()
        return success(
            data={
                'total_du': rapport['total_du'],
                'nombre': rapport['nombre'],
                'detail': PaiementSerializer(rapport['detail'], many=True).data
            },
            message="Rapport des impayés"
        )


class RapportClientsView(APIView):
    permission_classes = [EstDuTenantCourant, AccesModuleRequis(MODULE_RAPPORTS_AVANCES), EstProprietaire]

    @extend_schema(request=InactiviteSerializer, responses=None)
    def post(self, request):
        serializer = InactiviteSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message="Données invalides", errors=serializer.errors)

        service = RapportService()
        rapport = service.rapport_clients(
            semaines_inactivite=serializer.validated_data['semaines']
        )
        return success(data=rapport, message="Rapport clients")


class RapportStockView(APIView):
    permission_classes = [EstDuTenantCourant, AccesModuleRequis(MODULE_RAPPORTS_AVANCES), EstProprietaire]

    @extend_schema(request=PeriodeSerializer, responses=None)
    def post(self, request):
        serializer = PeriodeSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message="Données invalides", errors=serializer.errors)

        service = RapportService()
        rapport = service.rapport_stock(
            serializer.validated_data['date_debut'],
            serializer.validated_data['date_fin']
        )
        return success(data=rapport, message="Rapport stock")


class RapportSMSCampagneView(APIView):
    permission_classes = [EstDuTenantCourant, AccesModuleRequis(MODULE_SMS_MARKETING), EstProprietaire]

    @extend_schema(responses=None)
    def get(self, request):
        from apps.rapports.models import SMSCampagne
        campagnes = SMSCampagne.objects.filter(
            tenant__schema_name=__import__('django.db', fromlist=['connection']).connection.schema_name
        ).order_by('-date_envoi')

        data = list(campagnes.values(
            'id', 'titre', 'segment_cible', 'statut',
            'date_envoi', 'nombre_destinataires', 'nombre_coupons_utilises'
        ))
        return success(data=data, message="Campagnes SMS")