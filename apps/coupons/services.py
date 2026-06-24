from django.utils import timezone
from apps.journal.services import JournalService
from apps.clients.repository import ClienteRepository
from .repository import CouponRepository, CouponUtilisationRepository


class CouponService:

    def __init__(self):
        self.coupon_repo = CouponRepository()
        self.utilisation_repo = CouponUtilisationRepository()
        self.cliente_repo = ClienteRepository()
        self.journal = JournalService()

    def lister(self):
        return self.coupon_repo.liste_actifs()

    def obtenir(self, coupon_id):
        coupon = self.coupon_repo.par_id(coupon_id)
        if coupon is None:
            raise ValueError("Coupon introuvable.")
        return coupon

    def creer(self, data, utilisateur=None):
        # Vérifier que le code n'existe pas déjà
        if self.coupon_repo.par_code(data.get('code')):
            raise ValueError("Un coupon existe déjà avec ce code.")

        coupon = self.coupon_repo.creer(data)

        self.journal.enregistrer(
            utilisateur=utilisateur,
            type_action='creation_coupon',
            ressource='Coupon',
            ressource_id=coupon.id,
            details_apres={'code': coupon.code, 'type': coupon.type, 'valeur': str(coupon.valeur)}
        )
        return coupon

    def desactiver(self, coupon_id, utilisateur=None):
        coupon = self.obtenir(coupon_id)
        coupon_desactive = self.coupon_repo.desactiver(coupon)

        self.journal.enregistrer(
            utilisateur=utilisateur,
            type_action='desactivation_coupon',
            ressource='Coupon',
            ressource_id=coupon.id
        )
        return coupon_desactive

    def valider_et_appliquer(self, code, cliente_id, rendez_vous=None, commande=None, utilisateur=None):
        """
        Valide un coupon et l'applique — retourne la réduction calculée.
        Vérifie : existence, expiration, usage unique, cliente ciblée.
        """
        coupon = self.coupon_repo.par_code(code)
        if coupon is None:
            raise ValueError("Code coupon invalide ou inexistant.")

        # Vérifier l'expiration
        if coupon.date_expiration and coupon.date_expiration < timezone.now().date():
            raise ValueError("Ce coupon a expiré.")

        # Vérifier si le coupon est ciblé sur une cliente spécifique
        if coupon.cliente_id and coupon.cliente_id != cliente_id:
            raise ValueError("Ce coupon n'est pas valide pour cette cliente.")

        # Vérifier l'usage unique
        cliente = self.cliente_repo.par_id(cliente_id)
        if cliente is None:
            raise ValueError("Cliente introuvable.")

        if coupon.usage_unique and self.utilisation_repo.existe(coupon, cliente):
            raise ValueError("Ce coupon a déjà été utilisé par cette cliente.")

        # Enregistrer l'utilisation
        self.utilisation_repo.creer(
            coupon=coupon,
            cliente=cliente,
            rendez_vous=rendez_vous,
            commande=commande
        )

        # Calculer la réduction
        if coupon.type == 'montant_fixe':
            reduction = coupon.valeur
        else:
            reduction = coupon.valeur  # Le frontend calculera le % sur le montant total

        self.journal.enregistrer(
            utilisateur=utilisateur,
            type_action='utilisation_coupon',
            ressource='Coupon',
            ressource_id=coupon.id,
            details_apres={
                'code': coupon.code,
                'cliente_id': cliente_id,
                'reduction': str(reduction)
            }
        )

        return {
            'coupon_id': coupon.id,
            'code': coupon.code,
            'type': coupon.type,
            'valeur': coupon.valeur,
            'reduction': reduction
        }

    def historique_utilisations(self, coupon_id):
        self.obtenir(coupon_id)
        return self.utilisation_repo.historique(coupon_id)