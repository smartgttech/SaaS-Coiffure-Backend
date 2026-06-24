from apps.journal.services import JournalService
from apps.authentication.repository import PersonnalRepository
from .repository import TransactionPerformanceRepository


class PerformanceService:

    def __init__(self):
        self.personnel_repo = PersonnalRepository()
        self.transaction_repo = TransactionPerformanceRepository()
        self.journal = JournalService()

    def obtenir_personnel(self, personnel_id):
        personnel = self.personnel_repo.par_id(personnel_id)
        if personnel is None:
            raise ValueError("Membre du personnel introuvable.")
        return personnel

    def ajouter_points(self, personnel_id, points, motif, utilisateur=None):
        if points <= 0:
            raise ValueError("Le nombre de points doit être supérieur à zéro.")

        personnel = self.obtenir_personnel(personnel_id)

        self.transaction_repo.creer(
            personnel=personnel,
            type='credit',
            points=points,
            motif=motif
        )

        personnel.solde_points_performance += points
        personnel.save()

        self.journal.enregistrer(
            utilisateur=utilisateur,
            type_action='ajout_points_performance',
            ressource='Personnel',
            ressource_id=personnel.id,
            details_apres={'points': points, 'motif': motif}
        )
        return personnel

    def retirer_points(self, personnel_id, points, motif, utilisateur=None):
        if points <= 0:
            raise ValueError("Le nombre de points doit être supérieur à zéro.")

        personnel = self.obtenir_personnel(personnel_id)

        if personnel.solde_points_performance < points:
            raise ValueError("Solde de points insuffisant.")

        self.transaction_repo.creer(
            personnel=personnel,
            type='debit',
            points=points,
            motif=motif
        )

        personnel.solde_points_performance -= points
        personnel.save()

        self.journal.enregistrer(
            utilisateur=utilisateur,
            type_action='retrait_points_performance',
            ressource='Personnel',
            ressource_id=personnel.id,
            details_apres={'points': points, 'motif': motif}
        )
        return personnel

    def historique(self, personnel_id):
        self.obtenir_personnel(personnel_id)
        return self.transaction_repo.historique(personnel_id)

    def recapitulatif_periode(self, personnel_id, date_debut, date_fin):
        """
        Récapitulatif des points sur une période — section 3.9 du CDC.
        Exportable PDF/Excel côté frontend.
        """
        personnel = self.obtenir_personnel(personnel_id)
        transactions = self.transaction_repo.historique_periode(
            personnel_id, date_debut, date_fin
        )
        total = self.transaction_repo.total_points_periode(
            personnel_id, date_debut, date_fin
        )

        return {
            'personnel_id': personnel.id,
            'nom': personnel.nom,
            'prenom': personnel.prenom,
            'periode': {
                'debut': str(date_debut),
                'fin': str(date_fin)
            },
            'solde_actuel': personnel.solde_points_performance,
            'points_periode': total,
            'transactions': transactions
        }

    def recapitulatif_tous(self, date_debut, date_fin):
        """
        Récapitulatif de tous les membres du personnel sur une période.
        """
        tout_le_personnel = self.personnel_repo.liste_active()
        resultats = []

        for personnel in tout_le_personnel:
            total = self.transaction_repo.total_points_periode(
                personnel.id, date_debut, date_fin
            )
            resultats.append({
                'personnel_id': personnel.id,
                'nom': personnel.nom,
                'prenom': personnel.prenom,
                'specialite': personnel.specialite,
                'solde_actuel': personnel.solde_points_performance,
                'points_periode': total,
            })

        return resultats