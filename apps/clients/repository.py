from repositories.base import BaseRepository
from .models import Cliente, TransactionPoints

# Repository de cette app
# Hérite de BaseRepository qui injecte automatiquement le tenant_id

class ClienteRepository(BaseRepository):
    # Clientes actives
    def list_actives(self, search=None):
        return Cliente.objects.filter(tenant=self.tenant, actif=True)

    # Cliente Par son Id
    def par_id(self, cliente_id):
        try:
            return Cliente.objects.get(tenant=self.tenant, id=cliente_id, actif=True)
        except Cliente.DoesNotExist:
            return None
        
    # Cliente Par son numéro de téléphone
    def par_telephone(self, telephone):
        try:
            return Cliente.objects.get(tenant=self.tenant, telephone=telephone, actif=True)
        except Cliente.DoesNotExist:
            return None
        
    # Créer un compte Cliente
    def creer(self, data):
        return Cliente.objects.create(tenant=self.tenant, **data)
    
    # Modiifier un compte client
    def modifier(self, cliente, data):
        for champ, valeur in data.items():
            setattr(cliente, champ, valeur)
        cliente.save()
        return cliente
    
    # Archiver un compte cliente
    def archiver(self, cliente):
        cliente.actif = False
        cliente.save()
        return cliente
    
    # Liste des clientes Inactives depuis un long moment
    def inactive_depuis(self, date_limite):
        return self.list_actives().filter(rendez_vous__date_heure__lt=date_limite).distinct()
    


# POINTS DE TRANSACTIONS POUR LA FIDELISATION
class TransactionPointRepository(BaseRepository):

    # Créer un point de transaction
    def creer(self, cliente, type, points, motif):
        return TransactionPoints.objects.create(
            tenant=self.tenant,
            cliente=cliente,
            type=type,
            points=points,
            motif=motif
        )
    
    # Historique d'attribution des points
    def historique(self, cliente):
        return TransactionPoints.objects.filter(tenant=self.tenant, cliente=cliente).order_by('-date')
    
