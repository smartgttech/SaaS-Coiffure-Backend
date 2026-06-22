from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from core.responses import success, error, created, not_found
from core.permissions import EstDuTenantCourant, EstProprietaireOuEmploye
from .services import PaiementService
from .serializers import (
    PaiementSerializer, PaiementCreateSerializer,
    ReglerArdoiseSerializer, CADuJourSerializer
)


class PaiementListCreateView(APIView):
    permission_classes = [EstDuTenantCourant, EstProprietaireOuEmploye]

    @extend_schema(responses=PaiementSerializer(many=True))
    def get(self, request):
        service = PaiementService()
        filtres = {
            'date_debut': request.query_params.get('date_debut'),
            'date_fin': request.query_params.get('date_fin'),
            'statut': request.query_params.get('statut'),
            'canal': request.query_params.get('canal'),
            'activite': request.query_params.get('activite'),
        }
        filtres = {k: v for k, v in filtres.items() if v is not None}
        paiements = service.lister(**filtres)
        return success(data=PaiementSerializer(paiements, many=True).data, message="Liste des paiements")

    @extend_schema(request=PaiementCreateSerializer, responses=PaiementSerializer)
    def post(self, request):
        serializer = PaiementCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message="Données invalides", errors=serializer.errors)

        service = PaiementService()
        try:
            paiement = service.enregistrer(serializer.validated_data, utilisateur=request.user)
            return created(data=PaiementSerializer(paiement).data, message="Paiement enregistré")
        except ValueError as e:
            return error(message=str(e), status_code=400)


class PaiementDetailView(APIView):
    permission_classes = [EstDuTenantCourant, EstProprietaireOuEmploye]

    @extend_schema(responses=PaiementSerializer)
    def get(self, request, paiement_id):
        service = PaiementService()
        try:
            paiement = service.obtenir(paiement_id)
            return success(data=PaiementSerializer(paiement).data, message="Paiement trouvé")
        except ValueError as e:
            return not_found(str(e))


class ArdoiseListView(APIView):
    permission_classes = [EstDuTenantCourant, EstProprietaireOuEmploye]

    @extend_schema(responses=PaiementSerializer(many=True))
    def get(self, request):
        service = PaiementService()
        ardoises = service.liste_ardoises()
        return success(data=PaiementSerializer(ardoises, many=True).data, message="Liste des ardoises en cours")


class ArdoiseClienteView(APIView):
    permission_classes = [EstDuTenantCourant, EstProprietaireOuEmploye]

    @extend_schema(responses=PaiementSerializer(many=True))
    def get(self, request, cliente_id):
        service = PaiementService()
        ardoises = service.ardoises_cliente(cliente_id)
        return success(data=PaiementSerializer(ardoises, many=True).data, message="Ardoises de la cliente")


class ArdoiseReglerView(APIView):
    permission_classes = [EstDuTenantCourant, EstProprietaireOuEmploye]

    @extend_schema(request=ReglerArdoiseSerializer, responses=PaiementSerializer)
    def post(self, request, paiement_id):
        serializer = ReglerArdoiseSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message="Données invalides", errors=serializer.errors)

        service = PaiementService()
        try:
            paiement = service.regler_ardoise(
                paiement_id,
                serializer.validated_data['montant_supplementaire'],
                utilisateur=request.user
            )
            return success(data=PaiementSerializer(paiement).data, message="Ardoise mise à jour")
        except ValueError as e:
            return error(message=str(e), status_code=400)


class CaisseTableauDuJourView(APIView):
    permission_classes = [EstDuTenantCourant, EstProprietaireOuEmploye]

    @extend_schema(responses=CADuJourSerializer)
    def get(self, request):
        service = PaiementService()
        donnees = service.ca_du_jour()
        return success(data=donnees, message="Chiffre d'affaires du jour")