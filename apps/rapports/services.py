from .repository import RapportRepository
from django.utils import timezone
import datetime


class RapportService:

    def __init__(self):
        self.repo = RapportRepository()

    def tableau_de_bord(self):
        """
        Données du tableau de bord principal — section 3.10 du CDC.
        """
        aujourd_hui = timezone.now().date()
        debut_mois = aujourd_hui.replace(day=1)
        debut_semaine = aujourd_hui - datetime.timedelta(days=aujourd_hui.weekday())

        # CA du jour
        paiements_jour = self.repo.paiements_periode(aujourd_hui, aujourd_hui)
        ca_jour_total = sum(p.montant_total for p in paiements_jour)
        ca_jour_encaisse = sum(p.montant_verse for p in paiements_jour)

        # CA de la semaine
        paiements_semaine = self.repo.paiements_periode(debut_semaine, aujourd_hui)
        ca_semaine_total = sum(p.montant_total for p in paiements_semaine)
        ca_semaine_encaisse = sum(p.montant_verse for p in paiements_semaine)

        # CA du mois
        paiements_mois = self.repo.paiements_periode(debut_mois, aujourd_hui)
        ca_mois_total = sum(p.montant_total for p in paiements_mois)
        ca_mois_encaisse = sum(p.montant_verse for p in paiements_mois)

        # RDV du jour
        rdv_stats = self.repo.rdv_stats(aujourd_hui, aujourd_hui)
        rdv_par_statut = {s['statut']: s['total'] for s in rdv_stats}

        # Ardoises
        ardoises = self.repo.ardoises_en_cours()

        return {
            'ca': {
                'jour': {
                    'total': ca_jour_total,
                    'encaisse': ca_jour_encaisse,
                    'en_attente': ca_jour_total - ca_jour_encaisse
                },
                'semaine': {
                    'total': ca_semaine_total,
                    'encaisse': ca_semaine_encaisse,
                    'en_attente': ca_semaine_total - ca_semaine_encaisse
                },
                'mois': {
                    'total': ca_mois_total,
                    'encaisse': ca_mois_encaisse,
                    'en_attente': ca_mois_total - ca_mois_encaisse
                },
            },
            'rdv_aujourd_hui': {
                'confirmes': rdv_par_statut.get('confirme', 0),
                'en_cours': rdv_par_statut.get('en_cours', 0),
                'termines': rdv_par_statut.get('termine', 0),
                'annules': rdv_par_statut.get('annule', 0),
                'en_attente': rdv_par_statut.get('en_attente', 0),
            },
            'alertes': {
                'ardoises_non_soldees': ardoises['nombre'],
                'montant_total_du': ardoises['total_du'],
                'produits_sous_seuil': self.repo.stock_sous_seuil(),
                'commandes_a_traiter': self.repo.commandes_a_traiter(),
            },
            'clientes': {
                'total_actives': self.repo.clientes_actives(),
            }
        }

    def rapport_financier(self, date_debut, date_fin):
        """
        Rapport financier complet sur une période — section 3.10 du CDC.
        """
        ca_par_activite = list(self.repo.ca_par_activite(date_debut, date_fin))
        ca_par_canal = list(self.repo.ca_par_canal(date_debut, date_fin))
        ca_par_mode = list(self.repo.ca_par_mode_paiement(date_debut, date_fin))
        evolution = self.repo.evolution_ca_mensuel()

        # Totaux globaux
        paiements = self.repo.paiements_periode(date_debut, date_fin)
        ca_total = sum(p.montant_total for p in paiements)
        ca_encaisse = sum(p.montant_verse for p in paiements)

        return {
            'periode': {
                'debut': str(date_debut),
                'fin': str(date_fin)
            },
            'totaux': {
                'ca_total': ca_total,
                'ca_encaisse': ca_encaisse,
                'ca_en_attente': ca_total - ca_encaisse
            },
            'par_activite': ca_par_activite,
            'par_canal': ca_par_canal,
            'par_mode_paiement': ca_par_mode,
            'evolution_6_mois': evolution,
        }

    def rapport_impayés(self):
        ardoises = self.repo.ardoises_en_cours()
        from apps.caisse.serializers import PaiementSerializer
        return {
            'total_du': ardoises['total_du'],
            'nombre': ardoises['nombre'],
            'detail': ardoises['detail']
        }

    def rapport_clients(self, semaines_inactivite=4):
        clientes_fideles = self.repo.clientes_fideles()
        clientes_inactives = self.repo.clientes_inactives(semaines=semaines_inactivite)

        return {
            'total_actives': self.repo.clientes_actives(),
            'fideles': list(clientes_fideles.values(
                'id', 'nom', 'prenom', 'telephone',
                'nb_visites', 'ca_genere', 'solde_points'
            )),
            'inactives': list(clientes_inactives.values(
                'id', 'nom', 'prenom', 'telephone'
            )),
        }

    def rapport_stock(self, date_debut, date_fin):
        produits_vendus = list(self.repo.produits_plus_vendus(date_debut, date_fin))
        return {
            'produits_sous_seuil': self.repo.stock_sous_seuil(),
            'produits_plus_vendus': produits_vendus,
        }