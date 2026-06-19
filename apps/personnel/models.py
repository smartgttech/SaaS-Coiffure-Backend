from django.db import models
from tenants.models import Tenant


class TransactionPerformance(models.Model):

    TYPE_CHOICES = [
        ('credit', 'Crédit'),
        ('debit', 'Débit'),
    ]

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='transactions_performance'
    )
    personnel = models.ForeignKey(
        'authentication.Personnel',
        on_delete=models.CASCADE,
        related_name='transactions_performance'
    )
    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES
    )
    points = models.IntegerField()
    motif = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Transaction de performance"
        verbose_name_plural = "Transactions de performance"

    def __str__(self):
        return f"{self.type} — {self.points} pts — {self.personnel}"