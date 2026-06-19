from django.db import models
from tenants.models import Tenant


class Coupon(models.Model):

    TYPE_CHOICES = [
        ('montant_fixe', 'Montant fixe'),
        ('pourcentage', 'Pourcentage'),
    ]

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='coupons'
    )
    cliente = models.ForeignKey(
        'clients.Cliente',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='coupons'
    )
    code = models.CharField(max_length=50)
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES
    )
    valeur = models.DecimalField(max_digits=10, decimal_places=2)
    date_expiration = models.DateField(null=True, blank=True)
    usage_unique = models.BooleanField(default=True)
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Coupon"
        verbose_name_plural = "Coupons"
        unique_together = [['tenant', 'code']]

    def __str__(self):
        return f"{self.code} — {self.type} — {self.valeur}"
    

class CouponUtilisation(models.Model):

    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.CASCADE,
        related_name='utilisations'
    )
    cliente = models.ForeignKey(
        'clients.Cliente',
        on_delete=models.CASCADE,
        related_name='coupons_utilises'
    )
    rendez_vous = models.ForeignKey(
        'rendez_vous.RendezVous',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='coupon_utilisations'
    )
    commande = models.ForeignKey(
        'commandes.Commande',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='coupon_utilisations'
    )
    date_utilisation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Utilisation de coupon"
        verbose_name_plural = "Utilisations de coupons"
        unique_together = [['coupon', 'cliente']]

    def __str__(self):
        return f"{self.coupon.code} — {self.cliente}"