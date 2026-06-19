from django.db import models
from tenants.models import Tenant
from apps.clients.models import Cliente


class Paiement(models.Model):

    MODE_PAIEMENT_CHOICES = [
        ('cash', 'Cash'),
        ('orange_money', 'Orange Money'),
        ('mtn_money', 'MTN Money'),
        ('en_ligne', 'En ligne'),
    ]

    STATUT_CHOICES = [
        ('paye', 'Payé'),
        ('partiel', 'Partiel'),
        ('impaye', 'Impayé'),
    ]

    CANAL_CHOICES = [
        ('physique', 'Physique'),
        ('en_ligne', 'En ligne'),
    ]

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='paiements'
    )
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='paiements'
    )
    rendez_vous = models.ForeignKey(
        'rendez_vous.RendezVous',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='paiements'
    )
    commande = models.ForeignKey(
        'commandes.Commande',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='paiements'
    )
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)
    montant_verse = models.DecimalField(max_digits=10, decimal_places=2)
    solde_restant = models.DecimalField(max_digits=10, decimal_places=2)
    mode_paiement = models.CharField(
        max_length=20,
        choices=MODE_PAIEMENT_CHOICES
    )
    statut = models.CharField(
        max_length=10,
        choices=STATUT_CHOICES,
        default='impaye'
    )
    activite = models.CharField(max_length=100)
    canal = models.CharField(
        max_length=10,
        choices=CANAL_CHOICES,
        default='physique'
    )
    date = models.DateTimeField(auto_now_add=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(rendez_vous__isnull=True) |
                    models.Q(commande__isnull=True)
                ),
                name='paiement_rdv_ou_commande_pas_les_deux'
            )
        ]

    def __str__(self):
        return f"Paiement #{self.id} — {self.statut} — {self.montant_total} FCFA"