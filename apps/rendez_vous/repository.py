from repositories.base import BaseRepository
from .models import RendezVous, Prestation
# Repository de cette app
# Hérite de BaseRepository qui injecte automatiquement le tenant_id

class PrestationRepository(BaseRepository):

    def liste_actives(self):
        return Prestation.objects.filter(tenant=self.tenant, actif=True)
    
    def par_id(self, prestatin_id):
        try:
            return Prestation.objects.get(tenant=self.tenant, id=prestatin_id, actif=True)
        except Prestation.DoesNotExist:
            return None
    
    def creer(self, data):
        return Prestation.objects.create(tenant=self.tenant, **data)
    
    def modifier(self, prestation, data):
        for champ, valeur in data.items():
            setattr(prestation, champ, valeur)
        prestation.save()
        return prestation
    
    def archiver(self, prestation):
        prestation.actif = False
        prestation.save()
        return prestation
    


# =-----------------------------------------------------
class RendezVousRepository(BaseRepository):

    def liste(self, date_debut=None, date_fin=None, statut=None, personnel_id=None, cliente_id=None):
        qs = RendezVous.objects.filter(tenant=self.tenant)

        if date_debut:
            qs = qs.filter(date_heure__gte=date_debut)
        if date_fin:
            qs = qs.filter(date_heure__lte=date_fin)
        if statut:
            qs.filter(statut=statut)
        if personnel_id:
            qs.filter(personnel_id=personnel_id)
        if cliente_id:
            qs.filter(cliente_id=cliente_id)
        return qs.order_by('date_heure')
    
    def par_id(self, rdv_id):
        try:
            return RendezVous.objects.get(tenant=self.tenant, id=rdv_id)
        except RendezVous.DoesNotExist:
            return None
        
    def existe_doublon(self, personnel_id, date_heure, exclude_id=None):
        """
        Vérifie si le personnel a déjà un rendez-vous non annulé sur ce créneau exact
        """
        qs = RendezVous.objects.filter(
            tenant=self.tenant,
            personnel_id=personnel_id,
            date_heure=date_heure,
        ).exclude(statut='annule')
        if exclude_id:
            qs = qs.exclude(id=exclude_id)
        
        return qs.exists()
    
    def creer(self, data):
        return RendezVous.objects.create(tenant=self.tenant, **data)
    
    def modifier_statut(self, rdv, nouveau_statut):
        rdv.statut = nouveau_statut
        rdv.save()
        return rdv
    
    def modifier(self, rdv, data):
        for champ, valeur in data.items():
            setattr(rdv, champ, valeur)
        rdv.save()
        return rdv
    