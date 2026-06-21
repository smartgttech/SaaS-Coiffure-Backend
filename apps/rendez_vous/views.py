from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from core.responses import success, error, created, not_found
from core.permissions import EstDuTenantCourant, EstProprietaireOuEmploye
from .services import PrestationService, RendezVousService
from .serializers import (
    PrestationSerializer, PrestationCreateSerializer,
    RendezVousSerializer, RendezVousCreateSerializer,
    RendezVousUpdateSerializer, ChangerStatutSerializer
)


class PrestationListCreateView(APIView):
    permission_classes = [EstDuTenantCourant, EstProprietaireOuEmploye]

    @extend_schema(responses=PrestationSerializer(many=True))
    def get(self, request):
        service = PrestationService()
        prestations = service.lister()
        return success(data=PrestationSerializer(prestations, many=True).data, message="Liste des prestations")

    @extend_schema(request=PrestationCreateSerializer, responses=PrestationSerializer)
    def post(self, request):
        serializer = PrestationCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message="Données invalides", errors=serializer.errors)

        service = PrestationService()
        prestation = service.creer(serializer.validated_data)
        return created(data=PrestationSerializer(prestation).data, message="Prestation créée")


class PrestationDetailView(APIView):
    permission_classes = [EstDuTenantCourant, EstProprietaireOuEmploye]

    @extend_schema(responses=PrestationSerializer)
    def get(self, request, prestation_id):
        service = PrestationService()
        try:
            prestation = service.obtenir(prestation_id)
            return success(data=PrestationSerializer(prestation).data, message="Prestation trouvée")
        except ValueError as e:
            return not_found(str(e))

    @extend_schema(request=PrestationCreateSerializer, responses=PrestationSerializer)
    def patch(self, request, prestation_id):
        serializer = PrestationCreateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return error(message="Données invalides", errors=serializer.errors)

        service = PrestationService()
        try:
            prestation = service.modifier(prestation_id, serializer.validated_data)
            return success(data=PrestationSerializer(prestation).data, message="Prestation mise à jour")
        except ValueError as e:
            return not_found(str(e))

    @extend_schema(responses=None)
    def delete(self, request, prestation_id):
        service = PrestationService()
        try:
            service.archiver(prestation_id)
            return success(message="Prestation archivée")
        except ValueError as e:
            return not_found(str(e))


class RendezVousListCreateView(APIView):
    permission_classes = [EstDuTenantCourant, EstProprietaireOuEmploye]

    @extend_schema(responses=RendezVousSerializer(many=True))
    def get(self, request):
        service = RendezVousService()
        filtres = {
            'date_debut': request.query_params.get('date_debut'),
            'date_fin': request.query_params.get('date_fin'),
            'statut': request.query_params.get('statut'),
            'personnel_id': request.query_params.get('personnel_id'),
            'cliente_id': request.query_params.get('cliente_id'),
        }
        filtres = {k: v for k, v in filtres.items() if v is not None}
        rdvs = service.lister(**filtres)
        return success(data=RendezVousSerializer(rdvs, many=True).data, message="Liste des rendez-vous")

    @extend_schema(request=RendezVousCreateSerializer, responses=RendezVousSerializer)
    def post(self, request):
        serializer = RendezVousCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message="Données invalides", errors=serializer.errors)

        service = RendezVousService()
        try:
            rdv = service.creer(serializer.validated_data, utilisateur=request.user)
            return created(data=RendezVousSerializer(rdv).data, message="Rendez-vous créé")
        except ValueError as e:
            return error(message=str(e), status_code=400)


class RendezVousDetailView(APIView):
    permission_classes = [EstDuTenantCourant, EstProprietaireOuEmploye]

    @extend_schema(responses=RendezVousSerializer)
    def get(self, request, rdv_id):
        service = RendezVousService()
        try:
            rdv = service.obtenir(rdv_id)
            return success(data=RendezVousSerializer(rdv).data, message="Rendez-vous trouvé")
        except ValueError as e:
            return not_found(str(e))

    @extend_schema(request=RendezVousUpdateSerializer, responses=RendezVousSerializer)
    def patch(self, request, rdv_id):
        serializer = RendezVousUpdateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return error(message="Données invalides", errors=serializer.errors)

        service = RendezVousService()
        try:
            rdv = service.modifier(rdv_id, serializer.validated_data, utilisateur=request.user)
            return success(data=RendezVousSerializer(rdv).data, message="Rendez-vous mis à jour")
        except ValueError as e:
            return error(message=str(e), status_code=400)


class RendezVousChangerStatutView(APIView):
    permission_classes = [EstDuTenantCourant, EstProprietaireOuEmploye]

    @extend_schema(request=ChangerStatutSerializer, responses=RendezVousSerializer)
    def post(self, request, rdv_id):
        serializer = ChangerStatutSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message="Données invalides", errors=serializer.errors)

        service = RendezVousService()
        try:
            rdv = service.changer_statut(
                rdv_id,
                serializer.validated_data['statut'],
                utilisateur=request.user
            )
            return success(data=RendezVousSerializer(rdv).data, message="Statut mis à jour")
        except ValueError as e:
            return error(message=str(e), status_code=400)