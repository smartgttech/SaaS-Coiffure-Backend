from apps.journal.services import JournalService
from apps.clients.repository import ClienteRepository
from apps.authentication.repository import PersonnalRepository
from .repository import PrestationRepository, RendezVousRepository

# Logique métier de cette app
# Utilise le repository pour accéder aux données

# Transitions de statut autorisées - Section 3.4 du CDC
TRANSITIONS_AUTORISEES = {
    'en_attente': ['confirme', 'annule'],
    'confirme': ['en_cours', 'annule'],
    'en_cours': ['termine', 'annule'],
    'termine': [],
    'annule': [],
}

# 1. PRESTATION SERVICE
# =======================================================
class PrestationService:

    def __init__(self):
        self.presta_repo = PrestationRepository()

    def lister(self):
        return self.presta_repo.liste_actives()
    
    def obtenir(self, prestation_id):
        prestation = self.presta_repo.par_id(prestation_id)
        if prestation is None:
            raise ValueError("Prestation Introuvable.")
        return prestation
    
    def creer(self, data):
        return self.presta_repo.creer(data)
    
    def modifier(self, prestation_id, data):
        prestation = self.obtenir(prestation_id)
        return self.presta_repo.modifier(prestation, data)
    
    def archiver(self, prestation_id):
        prestation = self.obtenir(prestation_id)
        return self.presta_repo.archiver(prestation)
    

# 2. RENDEZ-VOUS SERVICE
# ===========================================================
class RendezVousService:

    def __init__(self):
        self.rdv_repo = RendezVousRepository()
        self.presta_repo = PrestationRepository()
        self.cliente_repo = ClienteRepository()
        self.personnel_repo = PersonnalRepository()
        self.journal = JournalService()

    def lister(self, **filtres):
        return self.rdv_repo.liste(**filtres)
    
    def obtenir(self, rdv_id):
        rdv = self.rdv_repo.par_id(rdv_id)
        if rdv is None:
            raise ValueError("Rendez-vous introuvable.")
        return rdv
    
    def creer(self, data, utilisateur=None):
        cliente = self.cliente_repo.par_id(data['cliente_id'])
        if cliente is None:
            raise ValueError("Cliente introuvable.")
        
        prestation = self.presta_repo.par_id(data['prestation_id'])
        if prestation is None:
            raise ValueError("Prestation Introuvable.")
        
        personnel = self.personnel_repo.par_id(data['personnel_id'])
        if personnel is None:
            raise ValueError("Membre du personnel introuvable.")
        
        # détection de doublon dans le rendez-vous
        if self.rdv_repo.existe_doublon(data['personnel_id'], data['date_heure']):
            raise ValueError("Ce créneau est déjà pris pour ce membre du personnel")
        
        # le prix doit être figé au moment de la réservation
        prix_final = data.get('prix_final') or prestation.prix_min

        rdv_data = {
            'cliente_id': data['cliente_id'],
            'prestation_id': data['prestation_id'],
            'personnel_id': data['personnel_id'],
            'date_heure': data['date_heure'],
            'prix_final': prix_final,
            'note_cliente': data.get('note_cliente'),
            'apporte_meche': data.get('apporte_meche', False),
        }

        rdv = self.rdv_repo.creer(rdv_data)

        self.journal.enregistrer(
            utilisateur=utilisateur,
            type_action='creation_rdv',
            ressource='RendezVous',
            ressource_id=rdv.id,
            details_apres={'date_heure': str(rdv.date_heure), 'prix_final': str(rdv.prix_final)}
        )
        return rdv
    
    def changer_statut(self, rdv_id, nouveau_statut, utilisateur=None):
        rdv = self.obtenir(rdv_id)

        transitions_possibles = TRANSITIONS_AUTORISEES.get(rdv.statut, [])
        if nouveau_statut not in transitions_possibles:
            raise ValueError(
                f"Impossible de passer du statut '{rdv.statut}' à '{nouveau_statut}'."
            )

        ancien_statut = rdv.statut
        rdv_modifie = self.rdv_repo.modifier_statut(rdv, nouveau_statut)

        self.journal.enregistrer(
            utilisateur=utilisateur,
            type_action='changement_statut_rdv',
            ressource='RendezVous',
            ressource_id=rdv.id,
            details_avant={'statut': ancien_statut},
            details_apres={'statut': nouveau_statut}
        )
        return rdv_modifie

    def modifier(self, rdv_id, data, utilisateur=None):
        rdv = self.obtenir(rdv_id)

        # Si on change le créneau, revérifier les doublons
        if 'date_heure' in data:
            if self.rdv_repo.existe_doublon(rdv.personnel_id, data['date_heure'], exclude_id=rdv.id):
                raise ValueError("Ce créneau est déjà pris pour ce membre du personnel.")

        return self.rdv_repo.modifier(rdv, data)