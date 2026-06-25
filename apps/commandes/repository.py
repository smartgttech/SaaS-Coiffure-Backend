from repositories.base import BaseRepository
from .models import Commande, LigneCommande

# Repository de cette app
# Hérite de BaseRepository qui injecte automatiquement le tenant_id

class CommandeRepository(BaseRepository):

    def liste(self, statut=None, cliente_id=None):
        qs = Commande.objects.filter(tenant=self.tenant)
        if statut:
            qs = qs.filter(statut=statut)
        if cliente_id:
            qs = qs.filter(cliente_id=cliente_id)
        return qs.order_by('-date').prefetch_related('lignes__produit')
    
    def par_id(self, commande_id):
        try:
            return Commande.objects.prefetch_related(
                'lignes__produit'
            ).get(tenant=self.tenant, id=commande_id)
        except Commande.DoesNotExist:
            return None
        
    def creer(self, data):
        return Commande.objects.create(tenant=self.tenant, **data)
    
    def modifier_statut(self, commande, nouveau_statut):
        commande.statut = nouveau_statut
        commande.save()
        return commande
    

class LigneCommandeRepository(BaseRepository):
    
    def creer(self, commande, produit, quantite, prix_unitaire):
        return LigneCommande.objects.create(
            commande=commande,
            produit=produit,
            quantite=quantite,
            prix_unitaire=prix_unitaire
        )
    
    def par_commande(self, commande_id):
        return LigneCommande.objects.filter(
            commande_id=commande_id
        ).select_related('produit')