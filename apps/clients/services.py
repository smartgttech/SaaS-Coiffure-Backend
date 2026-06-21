from .repository import ClienteRepository, TransactionPointRepository
from apps.journal.services import JournalService
# Logique métier de cette app
# Utilise le repository pour accéder aux données

class ClienteService:
    
    def __init__(self):
        self.cliente_repo = ClienteRepository()
        self.points_repo = TransactionPointRepository()
        self.journal = JournalService()

    # Lister les clientes actives
    def lister(self):
        return self.cliente_repo.list_actives()
    
    # Obtenir les informations d'une cliente par son id
    def obtenir_par_id(self, cliente_id):
        cliente = self.cliente_repo.par_id(cliente_id)
        if cliente is None:
            raise ValueError("Cliente Introuvable.")
        return cliente
    
    # Creér un compte cliente (A partir de son téléphone)
    def creer(self, data, utilisateur=None):
        telephone = data.get('telephone')
        if self.cliente_repo.par_telephone(telephone):
            raise ValueError("Un client existe déjà avec ce numéro de téléphone.")
        
        cliente = self.cliente_repo.creer(data)
        self.journal.enregistrer(
            utilisateur=utilisateur,
            type_action='creation_client',
            ressource='Cliente',
            ressource_id=cliente.id,
            details_apres=data
        )
        return cliente
    
    # Modifier le compte client
    def modifier(self, cliente_id, data, utilisateur=None):
        cliente = self.obtenir_par_id(cliente_id)

        # Détails avant
        details_avant = {
            champ: getattr(cliente, champ) for champ in data.keys()
        }
        # Conversion des dates en chaines de caractères pour le JSONField
        details_avant = {k: str(v) if v is not None else None for k, v in details_avant.items()}

        cliente_modifiee = self.cliente_repo.modifier(cliente, data)

        details_apres = {k: str(v) if v is not None else None for k, v in data.items()}

        self.journal.enregistrer(
            utilisateur=utilisateur,
            type_action='modification_client',
            ressource='Cliente',
            ressource_id=cliente.id,
            details_avant=details_avant,
            details_apres=details_apres
        )
        return cliente_modifiee
    
    # Archiver un compte client
    def archiver(self, cliente_id, utilisateur=None):
        cliente = self.obtenir_par_id(cliente_id)
        cliente_archivee =  self.cliente_repo.archiver(cliente)

        self.journal.enregistrer(
            utilisateur=utilisateur,
            type_action='archivage_client',
            ressource='Cliente',
            ressource_id=cliente.id
        )
        return cliente_archivee
    
    # Ajouter des points à un compte client
    def ajouter_points(self, cliente_id, points, motif, utilisateur=None):
        """
        Ajoute des points et mets à jour le solde courant du client
        """

        cliente = self.obtenir_par_id(cliente_id)
        self.points_repo.creer(cliente=cliente, type='credit', points=points, motif=motif)
        cliente.solde_points += points
        cliente.save()

        self.journal.enregistrer(
            utilisateur=utilisateur,
            type_action='ajout_points',
            ressource='Cliente',
            ressource_id=cliente.id,
            details_apres={'points': points, 'motif': motif}
        )
        return cliente
    
    def retirer_points(self, cliente_id, points, motif, utilisateur=None):
        """
        Retire des points et mets à jour le solde courant du client
        """
        cliente = self.obtenir_par_id(cliente_id)
        if cliente.solde_points < points:
            raise ValueError("Solde de points insuffisants.")
        self.points_repo.creer(cliente=cliente, type='debit', points=points, motif=motif)
        cliente.solde_points -= points
        cliente.save()

        self.journal.enregistrer(
            utilisateur=utilisateur,
            type_action='retrait_points',
            ressource='Cliente',
            ressource_id=cliente.id,
            details_apres={'points': points, 'motif': motif}
        )
        return cliente
    
    # Historique des mouvements de points
    def historique_points(self, cliente_id):
        cliente = self.obtenir_par_id(cliente_id)
        return self.points_repo.historique(cliente)