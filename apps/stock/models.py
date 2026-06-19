from django.db import models
from tenants.models import Tenant
from apps.produits.models import Produit


class MouvementStock(models.Model):

    TYPE_CHOICES = [
        ('entree', 'Entrée'),
        ('sortie', 'Sortie'),
    ]

    MOTIF_CHOICES = [
        ('vente_physique', 'Vente physique'),
        ('vente_en_ligne', 'Vente en ligne'),
        ('approvisionnement', 'Approvisionnement'),
        ('correction', 'Correction manuelle'),
    ]

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='mouvements_stock'
    )
    produit = models.ForeignKey(
        Produit,
        on_delete=models.CASCADE,
        related_name='mouvements_stock'
    )
    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES
    )
    motif = models.CharField(
        max_length=20,
        choices=MOTIF_CHOICES
    )
    quantite = models.IntegerField()
    quantite_avant = models.IntegerField()
    quantite_apres = models.IntegerField()
    note = models.CharField(max_length=255, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mouvement de stock"
        verbose_name_plural = "Mouvements de stock"

    def __str__(self):
        return f"{self.type} — {self.produit.nom} — {self.quantite}"