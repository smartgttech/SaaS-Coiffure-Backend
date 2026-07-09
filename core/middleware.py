"""
Fichier: core/middleware.py
Rôle: Fait respecter au niveau HTTP ce que le Super Admin décide au niveau métier.

Sans ce middleware, suspendre un tenant depuis le dashboard Super Admin ne fait
que changer une valeur en base de données — les employés du salon suspendu
peuvent continuer à utiliser l'application normalement, puisqu'aucune vue ne
vérifiait `tenant.statut` avant ce correctif.

Ce middleware s'exécute pour CHAQUE requête entrant dans le schéma d'un tenant
(donc jamais pour le schéma public / le Super Admin lui-même).
"""

from django.db import connection
from django.utils import timezone
from django.http import JsonResponse


def _reponse_bloquee(message: str, status_code: int, code: str):
    """
    IMPORTANT : on n'utilise volontairement PAS core.responses.error() ici.
    error() renvoie un rest_framework.response.Response, qui a besoin d'être
    "rendu" par le cycle de vie normal d'une APIView (accepted_renderer, etc.).
    Un middleware Django classique s'exécute EN DEHORS de ce cycle DRF, donc
    renvoyer un Response DRF brut depuis ici lèverait une erreur de rendu.
    JsonResponse est le bon outil pour un middleware — on garde volontairement
    le même format JSON que core.responses.error() pour que le frontend n'ait
    pas à distinguer les deux cas, avec un `code` machine-readable en plus
    pour que le frontend n'ait jamais à parser le texte du message (fragile,
    casse silencieusement si le message est reformulé plus tard).
    """
    return JsonResponse(
        {'success': False, 'message': message, 'errors': None, 'code': code},
        status=status_code,
    )


# Chemins toujours autorisés, même pour un tenant suspendu/expiré.
# - Authentification : l'utilisateur doit pouvoir se connecter pour au moins
#   VOIR le message d'erreur clair, plutôt que de rester bloqué sur un écran
#   de chargement infini côté frontend sans explication.
# - Documentation API : utile en debug, sans risque (lecture de schéma OpenAPI).
CHEMINS_EXEMPTES = (
    '/api/auth/login',
    '/api/auth/refresh',
    '/api/schema',
    '/api/docs',
)


class VerifierLicenceTenantMiddleware:
    """
    Bloque l'accès à l'API pour un tenant :
    - dont le statut est 'suspendu' (action manuelle du Super Admin)
    - dont la date_expiration est dépassée (licence arrivée à terme, hors 'illimite')

    Renvoie une réponse JSON cohérente avec le reste de l'API (même format que
    core.responses.error), plutôt qu'une page d'erreur HTML Django par défaut.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Le schéma 'public' correspond au Super Admin lui-même — jamais concerné.
        if connection.schema_name == 'public':
            return self.get_response(request)

        # Chemins toujours autorisés, peu importe le statut du tenant.
        if any(request.path.startswith(chemin) for chemin in CHEMINS_EXEMPTES):
            return self.get_response(request)

        from tenants.models import Tenant
        try:
            tenant = Tenant.objects.get(schema_name=connection.schema_name)
        except Tenant.DoesNotExist:
            # Schéma orphelin ou en cours de création — on laisse passer,
            # ce n'est pas à ce middleware de gérer ce cas limite.
            return self.get_response(request)

        if tenant.statut == 'suspendu':
            return _reponse_bloquee(
                "Ce compte a été suspendu. Contactez le support pour plus d'informations.",
                status_code=403,
                code='tenant_suspendu',
            )

        licence_expiree = (
            tenant.date_expiration is not None
            and tenant.date_expiration < timezone.now()
        )
        if licence_expiree:
            return _reponse_bloquee(
                "Votre licence a expiré. Merci de la renouveler pour continuer à utiliser HosJos.",
                status_code=402,  # 402 Payment Required — sémantiquement le bon code ici
                code='licence_expiree',
            )

        return self.get_response(request)
