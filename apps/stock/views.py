from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from rest_framework import serializers as drf_serializers
from core.responses import success, error, created, not_found
from core.permissions import EstDuTenantCourant, EstProprietaireOuEmploye, EstProprietaire, AccesModuleRequis
from core.licences import MODULE_PRODUITS, MODULE_STOCK
from .services import StockService
from .serializers import (
    ProduitSerializer, ProduitCreateSerializer, ProduitUpdateSerializer,
    ApprovisionnerSerializer, MouvementStockSerializer
)


class ValeurStockSerializer(drf_serializers.Serializer):
    valeur_totale = drf_serializers.DecimalField(max_digits=14, decimal_places=2)


class ProduitListCreateView(APIView):
    permission_classes = [EstDuTenantCourant, AccesModuleRequis(MODULE_PRODUITS), EstProprietaireOuEmploye]

    @extend_schema(responses=ProduitSerializer(many=True))
    def get(self, request):
        service = StockService()
        produits = service.lister_produits()
        return success(
            data=ProduitSerializer(produits, many=True).data,
            message="Liste des produits"
        )

    @extend_schema(request=ProduitCreateSerializer, responses=ProduitSerializer)
    def post(self, request):
        serializer = ProduitCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message="Données invalides", errors=serializer.errors)

        service = StockService()
        try:
            produit = service.creer_produit(serializer.validated_data, utilisateur=request.user)
            return created(data=ProduitSerializer(produit).data, message="Produit créé")
        except ValueError as e:
            return error(message=str(e), status_code=400)


class ProduitDetailView(APIView):
    permission_classes = [EstDuTenantCourant, AccesModuleRequis(MODULE_PRODUITS), EstProprietaireOuEmploye]

    @extend_schema(responses=ProduitSerializer)
    def get(self, request, produit_id):
        service = StockService()
        try:
            produit = service.obtenir_produit(produit_id)
            return success(data=ProduitSerializer(produit).data, message="Produit trouvé")
        except ValueError as e:
            return not_found(str(e))

    @extend_schema(request=ProduitUpdateSerializer, responses=ProduitSerializer)
    def patch(self, request, produit_id):
        serializer = ProduitUpdateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return error(message="Données invalides", errors=serializer.errors)

        service = StockService()
        try:
            produit = service.modifier_produit(
                produit_id,
                serializer.validated_data,
                utilisateur=request.user
            )
            return success(data=ProduitSerializer(produit).data, message="Produit mis à jour")
        except ValueError as e:
            return not_found(str(e))

    @extend_schema(responses=None)
    def delete(self, request, produit_id):
        service = StockService()
        try:
            service.archiver_produit(produit_id, utilisateur=request.user)
            return success(message="Produit archivé")
        except ValueError as e:
            return not_found(str(e))


class StockApprovisionnerView(APIView):
    permission_classes = [EstDuTenantCourant, AccesModuleRequis(MODULE_STOCK), EstProprietaire]

    @extend_schema(request=ApprovisionnerSerializer, responses=ProduitSerializer)
    def post(self, request, produit_id):
        serializer = ApprovisionnerSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message="Données invalides", errors=serializer.errors)

        service = StockService()
        try:
            produit = service.approvisionner(
                produit_id,
                serializer.validated_data['quantite'],
                note=serializer.validated_data.get('note'),
                utilisateur=request.user
            )
            return success(data=ProduitSerializer(produit).data, message="Stock approvisionné")
        except ValueError as e:
            return error(message=str(e), status_code=400)


class StockAlertesView(APIView):
    permission_classes = [EstDuTenantCourant, AccesModuleRequis(MODULE_STOCK), EstProprietaireOuEmploye]

    @extend_schema(responses=ProduitSerializer(many=True))
    def get(self, request):
        service = StockService()
        produits = service.alertes_stock()
        return success(
            data=ProduitSerializer(produits, many=True).data,
            message="Produits sous le seuil d'alerte"
        )


class StockMouvementsView(APIView):
    permission_classes = [EstDuTenantCourant, AccesModuleRequis(MODULE_STOCK), EstProprietaireOuEmploye]

    @extend_schema(responses=MouvementStockSerializer(many=True))
    def get(self, request, produit_id=None):
        service = StockService()
        mouvements = service.historique_mouvements(produit_id=produit_id)
        return success(
            data=MouvementStockSerializer(mouvements, many=True).data,
            message="Historique des mouvements de stock"
        )


class StockValeurTotaleView(APIView):
    permission_classes = [EstDuTenantCourant, AccesModuleRequis(MODULE_STOCK), EstProprietaire]

    @extend_schema(responses=ValeurStockSerializer)
    def get(self, request):
        service = StockService()
        valeur = service.valeur_totale_stock()
        return success(data={'valeur_totale': valeur}, message="Valeur totale du stock")