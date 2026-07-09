# apps/journal/views.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from core.responses import success
from core.permissions import EstDuTenantCourant, EstProprietaire, AccesModuleRequis
from core.licences import MODULE_JOURNAL
from .services import JournalService
from .serializers import JournalActionSerializer


class JournalListeView(APIView):
    permission_classes = [IsAuthenticated, EstDuTenantCourant, AccesModuleRequis(MODULE_JOURNAL), EstProprietaire]

    def get(self, request):
        service = JournalService()
        actions = service.liste(
            ressource=request.query_params.get('ressource'),
            type_action=request.query_params.get('type_action'),
        )
        return success(data=JournalActionSerializer(actions, many=True).data)


class JournalRessourceView(APIView):
    permission_classes = [IsAuthenticated, EstDuTenantCourant, AccesModuleRequis(MODULE_JOURNAL), EstProprietaire]

    def get(self, request, ressource, ressource_id):
        service = JournalService()
        actions = service.historique_ressource(ressource, ressource_id)
        return success(data=JournalActionSerializer(actions, many=True).data)