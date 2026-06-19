from django.db import models
from tenants.models import Tenant
from apps.clients.models import Cliente
from apps.authentication.models import Personnel


class Prestation(models.Model):

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='prestations'
    )
    nom = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    categorie = models.CharField(max_length=100)
    prix_min = models.DecimalField(max_digits=10, decimal_places=2)
    prix_max = models.DecimalField(max_digits=10, decimal_places=2)
    duree_minutes = models.IntegerField()
    points_performance = models.IntegerField(default=0)
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Prestation"
        verbose_name_plural = "Prestations"

    def __str__(self):
        return f"{self.nom} — {self.categorie}"


class RendezVous(models.Model):

    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirme', 'Confirmé'),
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
        ('annule', 'Annulé'),
    ]

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='rendez_vous'
    )
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='rendez_vous'
    )
    prestation = models.ForeignKey(
        Prestation,
        on_delete=models.CASCADE,
        related_name='rendez_vous'
    )
    personnel = models.ForeignKey(
        Personnel,
        on_delete=models.CASCADE,
        related_name='rendez_vous'
    )
    coupon = models.ForeignKey(
        'coupons.Coupon',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rendez_vous'
    )
    date_heure = models.DateTimeField()
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='en_attente'
    )
    prix_final = models.DecimalField(max_digits=10, decimal_places=2)
    note_cliente = models.TextField(null=True, blank=True)
    apporte_meche = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Rendez-vous"
        verbose_name_plural = "Rendez-vous"

    def __str__(self):
        return f"{self.cliente} — {self.prestation} — {self.date_heure}"