from rest_framework.views import APIView
from rest_framework import status
from django.utils import timezone
from core.responses import success

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