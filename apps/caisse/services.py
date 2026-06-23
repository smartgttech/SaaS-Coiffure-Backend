from apps.journal.services import JournalService
from apps.clients.repository import ClienteRepository
from apps.rendez_vous.repository import RendezVousRepository
from .repository import PaiementRepository
from django.utils import timezone
# from apps.caisse.models import Paiement

# Logique métier de cette app
# Utilise le repository pour accéder aux données

class PaiementService:
    
    def __init__(self):
        self.repo = PaiementRepository()
        self.cliente_repo = ClienteRepository()
        self.rdv_repo = RendezVousRepository()
        self.journal = JournalService()

    def lister(self, **filtres):
        return self.repo.liste(**filtres)

    def obtenir(self, paiement_id):
        paiement = self.repo.par_id(paiement_id)
        if paiement is None:
            raise ValueError("Aucune trace de ce paiement")
        return paiement
        
    def deduire_activite_et_canal(self, rendez_vous_id=None, commande_id=None, activite_produit=None):
        """
        Déduit automatiquement l'activité et le canal selon l'origine du paiement.
        - RDV -> activité = catégorie de la prestation, canal = physique
        - Commande -> activité = catégorie du/des produits, canal = en_ligne
        - Ni l'un ni l'autre (vente physique directe) -> activité = catégorie produit fournie, canal = physique
        """
            
        if rendez_vous_id:
            rdv = self.rdv_repo.par_id(rendez_vous_id)
            if rdv is None:
                raise ValueError("Rendez-vous introuvable.")
            return rdv.prestation.categorie, 'physique'
            
        if commande_id:
            # La logique précise sera affinée avec le module commandes
            # Pour l'instant on utilise l'activité produit fournie en entrée
            return activite_produit or 'Boutique en ligne', 'en_ligne'
            
        # Vente physique directe (Produit en caisse, sans RDV ni commande)
        if not activite_produit:
            raise ValueError("L'activité doit être précisée pour une vente physique")
        return activite_produit, 'physique'
        
    def enregistrer(self, data, utilisateur=None):
        rendez_vous_id = data.get('rendez_vous_id') or None
        commande_id = data.get('commande_id') or None

        # Jamais commande et rendez-vous en même temps
        if rendez_vous_id and commande_id:
            raise ValueError("Un paiement ne peut pas être lié à la fois à un rendez-vous et à une commande en ligne")
            
        montant_total = data['montant_total']
        montant_verse = data['montant_verse']

        if montant_verse > montant_total:
            raise ValueError("Le montant versé ne peut pas dépasser le montant total.")
            
        solde_restant = montant_total - montant_verse

        if solde_restant == 0:
            statut = 'paye'
        elif montant_verse == 0:
            statut = 'impaye'
        else:
            statut = 'partiel'

        activite, canal = self.deduire_activite_et_canal(
            rendez_vous_id=rendez_vous_id,
            commande_id=commande_id,
            activite_produit=data.get('activite_produit')
        )

        cliente = None
        if data.get('cliente_id'):
            cliente = self.cliente_repo.par_id(data['cliente_id'])
            if cliente is None:
                raise ValueError("Cliente Introuvable.")
                
        paiement_data = {
            'cliente_id': data.get('cliente_id'),
            'rendez_vous_id': rendez_vous_id,
            'commande_id': commande_id,
            'montant_total': montant_total,
            'montant_verse': montant_verse,
            'solde_restant': solde_restant,
            'mode_paiement': data['mode_paiement'],
            'statut': statut,
            'activite': activite,
            'canal': canal,
            'reference': self.repo.generer_reference(),
        }

        paiement = self.repo.creer(paiement_data)

        # Si lié à un RDV, le clore automatiquement vers " termine "
        # Clôture d'un rendez-vous: redirection vers l'enregistrement
        if rendez_vous_id and paiement.rendez_vous.statut != 'termine':
            from apps.rendez_vous.services import RendezVousService
            rdv_service = RendezVousService()
            try:
                rdv = rdv_service.obtenir(rendez_vous_id)
                # Si le RDV n'est pas encore en_cours, on l'y amène d'abord
                if rdv.statut == 'en_attente':
                    rdv_service.changer_statut(rendez_vous_id, 'confirme', utilisateur=utilisateur)
                    rdv_service.changer_statut(rendez_vous_id, 'en_cours', utilisateur=utilisateur)
                elif rdv.statut == 'confirme':
                    rdv_service.changer_statut(rendez_vous_id, 'en_cours', utilisateur=utilisateur)
                # Dans tous les cas on clôture vers termine
                rdv_service.changer_statut(rendez_vous_id, 'termine', utilisateur=utilisateur)
            except ValueError:
                pass # Le rendez-vous était peut-être déjà dans un état incompatible

            self.journal.enregistrer(
                utilisateur=utilisateur,
                type_action='enregistrement_paiement',
                ressource='Paiement',
                ressource_id=paiement.id,
                details_apres={
                    'montant_total': str(montant_total),
                    'montant_verse': str(montant_verse),
                    'statut': statut
                }
            )
            return paiement

    def regler_ardoise(self, paiement_id, montant_supplementaire, utilisateur=None):
        """
        Permet de solder progressivement une ardoise existante.
        """
        paiement = self.obtenir(paiement_id)

        if paiement.statut == 'paye':
            raise ValueError("Ce paiement est déjà soldé.")

        nouveau_montant_verse = paiement.montant_verse + montant_supplementaire
        if nouveau_montant_verse > paiement.montant_total:
            raise ValueError("Le montant versé dépasserait le montant total dû.")

        nouveau_solde = paiement.montant_total - nouveau_montant_verse
        nouveau_statut = 'paye' if nouveau_solde == 0 else 'partiel'

        ancien_solde = paiement.solde_restant

        paiement = self.repo.modifier(paiement, {
            'montant_verse': nouveau_montant_verse,
            'solde_restant': nouveau_solde,
            'statut': nouveau_statut,
        })

        self.journal.enregistrer(
            utilisateur=utilisateur,
            type_action='reglement_ardoise',
            ressource='Paiement',
            ressource_id=paiement.id,
            details_avant={'solde_restant': str(ancien_solde)},
            details_apres={'solde_restant': str(nouveau_solde), 'statut': nouveau_statut}
        )
        return paiement

    def liste_ardoises(self):
        return self.repo.ardoises_en_cours()

    def ardoises_cliente(self, cliente_id):
        return self.repo.ardoises_cliente(cliente_id)

    def ca_du_jour(self):
        """
        Distinction CA encaissé vs CA total — section 3.10 du CDC.
        """
        paiements_jour = self.repo.solde_du_jour()
        ca_total = sum(p.montant_total for p in paiements_jour)
        ca_encaisse = sum(p.montant_verse for p in paiements_jour)
        return {
            'ca_total': ca_total,
            'ca_encaisse': ca_encaisse,
            'ca_en_attente': ca_total - ca_encaisse,
        }