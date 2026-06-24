from repositories.base import BaseRepository
from .models import TransactionPerformance
from apps.authentication.models import Personnel
from django.utils import timezone
import datetime


class TransactionPerformanceRepository(BaseRepository):

    def creer(self, personnel, type, points, motif):
        return TransactionPerformance.objects.create(
            tenant=self.tenant,
            personnel=personnel,
            type=type,
            points=points,
            motif=motif
        )

    def historique(self, personnel_id):
        return TransactionPerformance.objects.filter(
            tenant=self.tenant,
            personnel_id=personnel_id
        ).order_by('-date')

    def historique_periode(self, personnel_id, date_debut, date_fin):
        # Convertir date_fin en fin de journée pour inclure toutes les transactions du jour
        date_fin_complete = datetime.datetime.combine(
            date_fin,
            datetime.time.max,
            tzinfo=timezone.get_current_timezone()
        )
        date_debut_complete = datetime.datetime.combine(
            date_debut,
            datetime.time.min,
            tzinfo=timezone.get_current_timezone()
        )
        return self.historique(personnel_id).filter(
            date__gte=date_debut_complete,
            date__lte=date_fin_complete
        )

    def total_points_periode(self, personnel_id, date_debut, date_fin):
        transactions = self.historique_periode(personnel_id, date_debut, date_fin)
        credits = sum(t.points for t in transactions if t.type == 'credit')
        debits = sum(t.points for t in transactions if t.type == 'debit')
        return credits - debits