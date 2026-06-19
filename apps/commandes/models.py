from django.db import models
from tenants.models import Tenant
from apps.clients.models import Cliente
from apps.produits.models import Produit
from apps.coupons.models import Coupon


class Commande(models.Model):

    STATUT_CHOICES = [
        ('en_preparation', 'En préparation'),
        ('prete', 'Prête'),
        ('livree', 'Livrée'),
        ('annulee', 'Annulée'),
    ]

    MODE_LIVRAISON_CHOICES = [
        ('retrait', 'Retrait en salon'),
        ('livraison_domicile', 'Livraison à domicile'),
    ]

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='commandes'
    )
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='commandes'
    )
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='commandes'
    )
    date = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='en_preparation'
    )
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)
    mode_livraison = models.CharField(
        max_length=20,
        choices=MODE_LIVRAISON_CHOICES,
        default='retrait'
    )
    adresse_livraison = models.TextField(null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"

    def __str__(self):
        return f"Commande #{self.id} — {self.statut}"


class LigneCommande(models.Model):

    commande = models.ForeignKey(
        Commande,
        on_delete=models.CASCADE,
        related_name='lignes'
    )
    produit = models.ForeignKey(
        Produit,
        on_delete=models.CASCADE,
        related_name='lignes_commande'
    )
    quantite = models.IntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Ligne de commande"
        verbose_name_plural = "Lignes de commande"

    def __str__(self):
        return f"{self.quantite} x {self.produit.nom}"