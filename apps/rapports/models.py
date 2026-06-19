from django.db import models
from tenants.models import Tenant


class SMSCampagne(models.Model):

    SEGMENT_CHOICES = [
        ('toutes', 'Toutes les clientes'),
        ('inactives', 'Clientes inactives'),
        ('anniversaire', 'Anniversaires'),
        ('par_categorie_prestation', 'Par catégorie de prestation'),
    ]

    STATUT_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('planifiee', 'Planifiée'),
        ('envoyee', 'Envoyée'),
        ('echouee', 'Échouée'),
    ]

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='sms_campagnes'
    )
    titre = models.CharField(max_length=150)
    message = models.TextField()
    segment_cible = models.CharField(
        max_length=50,
        choices=SEGMENT_CHOICES
    )
    valeur_segment = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
    date_envoi = models.DateTimeField()
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='brouillon'
    )
    nombre_destinataires = models.IntegerField(null=True, blank=True)
    nombre_coupons_utilises = models.IntegerField(null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Campagne SMS"
        verbose_name_plural = "Campagnes SMS"

    def __str__(self):
        return f"{self.titre} — {self.statut}"