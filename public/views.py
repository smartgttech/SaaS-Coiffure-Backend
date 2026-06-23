from rest_framework.views import APIView
from django.utils import timezone
from core.responses import success, error
from tenants.models import Tenant
from tenants.services import TenantService
from tenants.serializers import TenantPublicSerializer
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny

class HealthCheckView(APIView):
    """
    Endpoint de vérification que l'API fonctionne correctement.
    """

    def get(self, request):
        return success(
            data = {
                'status': 'ok',
                'timestamp': timezone.now(),
            },
            message="L'API fonctionne correctement"
        )


class TenantInfoView(APIView):
    """
    Endpoint public — retourne les infos de personnalisation
    du salon courant sans authentification.
    """
    permission_classes = [AllowAny]

    @extend_schema(responses=TenantPublicSerializer)
    def get(self, request):
        service = TenantService()
        try:
            tenant = service.obtenir_courant()
            return success(
                data=TenantPublicSerializer(tenant).data,
                message="Informations du salon"
            )
        except ValueError as e:
            return error(message=str(e), status_code=404)