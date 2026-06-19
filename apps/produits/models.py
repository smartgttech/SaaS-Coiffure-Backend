from django.db import models
from tenants.models import Tenant


class Produit(models.Model):

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='produits'
    )
    reference = models.CharField(max_length=100)
    nom = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    photo_url = models.URLField(max_length=500, null=True, blank=True)
    prix_achat = models.DecimalField(max_digits=10, decimal_places=2)
    prix_vente = models.DecimalField(max_digits=10, decimal_places=2)
    quantite_stock = models.IntegerField(default=0)
    seuil_alerte = models.IntegerField(default=5)
    categorie = models.CharField(max_length=100)
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        unique_together = [['tenant', 'reference']]

    def __str__(self):
        return f"{self.nom} — {self.reference}"