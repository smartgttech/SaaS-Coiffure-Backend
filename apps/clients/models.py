from django.db import models
from tenants.models import Tenant
from apps.authentication.models import Utilisateur


class Cliente(models.Model):

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='clientes'
    )
    utilisateur = models.OneToOneField(
        Utilisateur,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='profil_cliente'
    )
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20)
    date_naissance = models.DateField(null=True, blank=True)
    date_premiere_visite = models.DateField(auto_now_add=True)
    notes = models.TextField(null=True, blank=True)
    solde_points = models.IntegerField(default=0)
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        unique_together = [['tenant', 'telephone']]

    def __str__(self):
        return f"{self.prenom} {self.nom} — {self.telephone}"


class TransactionPoints(models.Model):

    TYPE_CHOICES = [
        ('credit', 'Crédit'),
        ('debit', 'Débit'),
    ]

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='transactions_points'
    )
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='transactions_points'
    )
    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES
    )
    points = models.IntegerField()
    motif = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Transaction de points"
        verbose_name_plural = "Transactions de points"

    def __str__(self):
        return f"{self.type} — {self.points} pts — {self.cliente}"