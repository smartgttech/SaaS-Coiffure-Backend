from repositories.base import BaseRepository
from .models import Paiement

# Repository de cette app
# Hérite de BaseRepository qui injecte automatiquement le tenant_id

class PaiementRepository(BaseRepository):

    def liste(self, date_debut=None, date_fin=None, statut=None, canal=None, activite=None):
        qs = Paiement.objects.filter(tenant=self.tenant)
        if date_debut:
            qs = qs.filter(date__gte=date_debut)
        if date_fin:
            qs = qs.filter(date__lte=date_fin)
        if statut:
            qs = qs.filter(statut=statut)
        if canal:
            qs = qs.filter(canal=canal)
        if activite:
            qs = qs.filter(activite=activite)
        return qs.order_by('-date')
    
    def par_id(self, paiement_id):
        try:
            return Paiement.objects.get(tenant=self.tenant, id=paiement_id)
        except Paiement.DoesNotExist:
            return None
        
    def creer(self, data):
        paiement = Paiement.objects.create(tenant=self.tenant, **data)
        return Paiement.objects.select_related(
            'cliente', 'rendez_vous', 'commande'
        ).get(id=paiement.id)
    
    def modifier(self, paiement, data):
        for champ, valeur in data.items():
            setattr(paiement, champ, valeur)
        paiement.save()
        return paiement
    
    def ardoises_en_cours(self):
        """
        Paiements avec un solde restant dû - Coeur du module Ardoises.
        """
        return Paiement.objects.filter(
            tenant=self.tenant,
            statut__in=['partiel', 'impaye']
        ).order_by('-date')
    
    def ardoises_cliente(self, cliente_id):
        return self.ardoises_en_cours().filter(cliente_id=cliente_id)
    
    def solde_du_jour(self):
        from django.utils import timezone
        return Paiement.objects.filter(
            tenant=self.tenant,
            date__date=timezone.now().date()
        )
    
    def generer_reference(self):
        from django.utils import timezone
        annee = timezone.now().year
        compteur = Paiement.objects.filter(
            tenant=self.tenant,
            date__year=annee
        ).count() + 1
        return f"REC-{annee}-{compteur:04d}"