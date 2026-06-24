from repositories.base import BaseRepository
from .models import Coupon, CouponUtilisation


class CouponRepository(BaseRepository):

    def liste_actifs(self):
        return Coupon.objects.filter(tenant=self.tenant, actif=True)

    def par_id(self, coupon_id):
        try:
            return Coupon.objects.get(tenant=self.tenant, id=coupon_id, actif=True)
        except Coupon.DoesNotExist:
            return None

    def par_code(self, code):
        try:
            return Coupon.objects.get(tenant=self.tenant, code=code, actif=True)
        except Coupon.DoesNotExist:
            return None

    def creer(self, data):
        return Coupon.objects.create(tenant=self.tenant, **data)

    def desactiver(self, coupon):
        coupon.actif = False
        coupon.save()
        return coupon


class CouponUtilisationRepository(BaseRepository):

    def creer(self, coupon, cliente, rendez_vous=None, commande=None):
        return CouponUtilisation.objects.create(
            coupon=coupon,
            cliente=cliente,
            rendez_vous=rendez_vous,
            commande=commande
        )

    def existe(self, coupon, cliente):
        return CouponUtilisation.objects.filter(
            coupon=coupon,
            cliente=cliente
        ).exists()

    def historique(self, coupon_id):
        return CouponUtilisation.objects.filter(
            coupon_id=coupon_id
        ).order_by('-date_utilisation')