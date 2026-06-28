from repositories.base import BaseRepository
from apps.caisse.models import Paiement
from apps.rendez_vous.models import RendezVous
from apps.clients.models import Cliente
from apps.produits.models import Produit
from apps.commandes.models import Commande
from django.db.models import Sum, Count, Q
from django.utils import timezone
import datetime


class RapportRepository(BaseRepository):

    def paiements_periode(self, date_debut, date_fin):
        date_fin_complete = datetime.datetime.combine(
            date_fin, datetime.time.max,
            tzinfo=timezone.get_current_timezone()
        )
        date_debut_complete = datetime.datetime.combine(
            date_debut, datetime.time.min,
            tzinfo=timezone.get_current_timezone()
        )
        return Paiement.objects.filter(
            tenant=self.tenant,
            date__gte=date_debut_complete,
            date__lte=date_fin_complete
        )

    def ca_par_activite(self, date_debut, date_fin):
        paiements = self.paiements_periode(date_debut, date_fin)
        return paiements.values('activite').annotate(
            ca_total=Sum('montant_total'),
            ca_encaisse=Sum('montant_verse')
        ).order_by('-ca_total')

    def ca_par_canal(self, date_debut, date_fin):
        paiements = self.paiements_periode(date_debut, date_fin)
        return paiements.values('canal').annotate(
            ca_total=Sum('montant_total'),
            ca_encaisse=Sum('montant_verse')
        )

    def ca_par_mode_paiement(self, date_debut, date_fin):
        paiements = self.paiements_periode(date_debut, date_fin)
        return paiements.values('mode_paiement').annotate(
            total=Sum('montant_verse')
        ).order_by('-total')

    def rdv_stats(self, date_debut, date_fin):
        date_fin_complete = datetime.datetime.combine(
            date_fin, datetime.time.max,
            tzinfo=timezone.get_current_timezone()
        )
        date_debut_complete = datetime.datetime.combine(
            date_debut, datetime.time.min,
            tzinfo=timezone.get_current_timezone()
        )
        rdvs = RendezVous.objects.filter(
            tenant=self.tenant,
            date_heure__gte=date_debut_complete,
            date_heure__lte=date_fin_complete
        )
        return rdvs.values('statut').annotate(total=Count('id'))

    def ardoises_en_cours(self):
        from django.db.models import Sum
        ardoises = Paiement.objects.filter(
            tenant=self.tenant,
            statut__in=['partiel', 'impaye']
        )
        total = ardoises.aggregate(
            total_du=Sum('solde_restant'),
            nombre=Count('id')
        )
        return {
            'total_du': total['total_du'] or 0,
            'nombre': total['nombre'] or 0,
            'detail': ardoises.order_by('-date')
        }

    def clientes_actives(self):
        return Cliente.objects.filter(
            tenant=self.tenant,
            actif=True
        ).count()

    def clientes_inactives(self, semaines=4):
        date_limite = timezone.now() - datetime.timedelta(weeks=semaines)
        return Cliente.objects.filter(
            tenant=self.tenant,
            actif=True
        ).exclude(
            rendez_vous__date_heure__gte=date_limite
        ).distinct()

    def clientes_fideles(self, limit=10):
        return Cliente.objects.filter(
            tenant=self.tenant,
            actif=True
        ).annotate(
            nb_visites=Count('rendez_vous'),
            ca_genere=Sum('paiements__montant_verse')
        ).order_by('-nb_visites')[:limit]

    def produits_plus_vendus(self, date_debut, date_fin, limit=10):
        from apps.commandes.models import LigneCommande
        return LigneCommande.objects.filter(
            commande__tenant=self.tenant,
            commande__date__date__gte=date_debut,
            commande__date__date__lte=date_fin
        ).values(
            'produit__nom', 'produit__reference'
        ).annotate(
            total_vendu=Sum('quantite')
        ).order_by('-total_vendu')[:limit]

    def stock_sous_seuil(self):
        from django.db.models import F
        return Produit.objects.filter(
            tenant=self.tenant,
            actif=True,
            quantite_stock__lte=F('seuil_alerte')
        ).count()

    def commandes_a_traiter(self):
        return Commande.objects.filter(
            tenant=self.tenant,
            statut='en_preparation'
        ).count()

    def evolution_ca_mensuel(self, nb_mois=6):
        resultats = []
        aujourd_hui = timezone.now().date()

        for i in range(nb_mois - 1, -1, -1):
            # Calculer le premier et dernier jour du mois
            mois = aujourd_hui.month - i
            annee = aujourd_hui.year
            while mois <= 0:
                mois += 12
                annee -= 1

            premier_jour = datetime.date(annee, mois, 1)
            if mois == 12:
                dernier_jour = datetime.date(annee + 1, 1, 1) - datetime.timedelta(days=1)
            else:
                dernier_jour = datetime.date(annee, mois + 1, 1) - datetime.timedelta(days=1)

            paiements = self.paiements_periode(premier_jour, dernier_jour)
            ca_total = paiements.aggregate(total=Sum('montant_total'))['total'] or 0
            ca_encaisse = paiements.aggregate(total=Sum('montant_verse'))['total'] or 0

            resultats.append({
                'mois': premier_jour.strftime('%Y-%m'),
                'label': premier_jour.strftime('%B %Y'),
                'ca_total': ca_total,
                'ca_encaisse': ca_encaisse,
            })

        return resultats