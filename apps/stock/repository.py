from django.db import models
from repositories.base import BaseRepository
from .models import MouvementStock
from apps.produits.models import Produit

# Repository de cette app
# Hérite de BaseRepository qui injecte automatiquement le tenant_id

class ProduitRepository(BaseRepository):

    def liste_actifs(self):
        return Produit.objects.filter(tenant=self.tenant, actif=True)

    def par_id(self, produit_id):
        try:
            return Produit.objects.get(tenant=self.tenant, id=produit_id, actif=True)
        except Produit.DoesNotExist:
            return None

    def par_reference(self, reference):
        try:
            return Produit.objects.get(tenant=self.tenant, reference=reference, actif=True)
        except Produit.DoesNotExist:
            return None

    def creer(self, data):
        return Produit.objects.create(tenant=self.tenant, **data)

    def modifier(self, produit, data):
        for champ, valeur in data.items():
            setattr(produit, champ, valeur)
        produit.save()
        return produit

    def archiver(self, produit):
        produit.actif = False
        produit.save()
        return produit

    def sous_seuil_alerte(self):
        return Produit.objects.filter(
            tenant=self.tenant,
            actif=True,
            quantite_stock__lte=models.F('seuil_alerte')
        )


class MouvementStockRepository(BaseRepository):

    def creer(self, produit, type, motif, quantite, quantite_avant, quantite_apres, note=None):
        return MouvementStock.objects.create(
            tenant=self.tenant,
            produit=produit,
            type=type,
            motif=motif,
            quantite=quantite,
            quantite_avant=quantite_avant,
            quantite_apres=quantite_apres,
            note=note
        )

    def historique(self, produit_id=None):
        qs = MouvementStock.objects.filter(tenant=self.tenant)
        if produit_id:
            qs = qs.filter(produit_id=produit_id)
        return qs.order_by('-date')
