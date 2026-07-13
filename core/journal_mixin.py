# core/journal_mixin.py

from functools import wraps
from tenants.journal_service import JournalPlateformeService

def journaliser_action(type_action):
    """
    Décorateur pour les méthodes de service Super Admin.
    Attend que la méthode reçoive `super_admin` et `request` en kwargs,
    et que le tenant soit soit passé en argument, soit retourné par la méthode.
    """
    def decorateur(fonction):
        @wraps(fonction)
        def wrapper(self, *args, super_admin, request=None, details=None, **kwargs):
            resultat = fonction(self, *args, super_admin=super_admin, request=request, **kwargs)

            tenant = resultat if hasattr(resultat, 'schema_name') else kwargs.get('tenant')

            JournalPlateformeService.enregistrer(
                super_admin=super_admin,
                type_action=type_action,
                tenant=tenant,
                details=details,
                request=request
            )
            return resultat
        return wrapper
    return decorateur