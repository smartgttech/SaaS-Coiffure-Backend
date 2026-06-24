from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from core.responses import success, error, created, not_found
from core.permissions import EstDuTenantCourant, EstProprietaireOuEmploye, EstProprietaire
from .services import CouponService
from .serializers import (
    CouponSerializer, CouponCreateSerializer,
    ValiderCouponSerializer, CouponUtilisationSerializer
)


class CouponListCreateView(APIView):
    permission_classes = [EstDuTenantCourant, EstProprietaire]

    @extend_schema(responses=CouponSerializer(many=True))
    def get(self, request):
        service = CouponService()
        coupons = service.lister()
        return success(
            data=CouponSerializer(coupons, many=True).data,
            message="Liste des coupons"
        )

    @extend_schema(request=CouponCreateSerializer, responses=CouponSerializer)
    def post(self, request):
        serializer = CouponCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message="Données invalides", errors=serializer.errors)

        service = CouponService()
        try:
            coupon = service.creer(serializer.validated_data, utilisateur=request.user)
            return created(data=CouponSerializer(coupon).data, message="Coupon créé")
        except ValueError as e:
            return error(message=str(e), status_code=400)


class CouponDetailView(APIView):
    permission_classes = [EstDuTenantCourant, EstProprietaire]

    @extend_schema(responses=CouponSerializer)
    def get(self, request, coupon_id):
        service = CouponService()
        try:
            coupon = service.obtenir(coupon_id)
            return success(data=CouponSerializer(coupon).data, message="Coupon trouvé")
        except ValueError as e:
            return not_found(str(e))

    @extend_schema(responses=None)
    def delete(self, request, coupon_id):
        service = CouponService()
        try:
            service.desactiver(coupon_id, utilisateur=request.user)
            return success(message="Coupon désactivé")
        except ValueError as e:
            return not_found(str(e))


class CouponValiderView(APIView):
    permission_classes = [EstDuTenantCourant, EstProprietaireOuEmploye]

    @extend_schema(request=ValiderCouponSerializer, responses=None)
    def post(self, request):
        serializer = ValiderCouponSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message="Données invalides", errors=serializer.errors)

        service = CouponService()
        try:
            resultat = service.valider_et_appliquer(
                code=serializer.validated_data['code'],
                cliente_id=serializer.validated_data['cliente_id'],
                utilisateur=request.user
            )
            return success(data=resultat, message="Coupon valide et appliqué")
        except ValueError as e:
            return error(message=str(e), status_code=400)


class CouponHistoriqueView(APIView):
    permission_classes = [EstDuTenantCourant, EstProprietaire]

    @extend_schema(responses=CouponUtilisationSerializer(many=True))
    def get(self, request, coupon_id):
        service = CouponService()
        try:
            historique = service.historique_utilisations(coupon_id)
            return success(
                data=CouponUtilisationSerializer(historique, many=True).data,
                message="Historique des utilisations"
            )
        except ValueError as e:
            return not_found(str(e))