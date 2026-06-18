from django.db import models
from django_tenants.models import TenantMixin, DomainMixin

# Create your models here.

# =====================================================
# 1. MODELE TENANT
# =====================================================

class Tenant(TenantMixin):
    nom = models.CharField(max_length=150)
    sous_domaine = models.CharField(max_length=100, unique=True)
    domaine_custom = models.CharField(max_length=255, blank=True, null=True)

    # Licence
    TYPE_LICENCE_CHOICES = [
        ('essai', 'Période d\'essai '),
        ('Mensuel', 'Abonnement mensuel'),
        ('trimestriel', 'Abonnement trimestriel'),
        ('semestriel', 'Abonnement semestriel'),
        ('annuel', 'Abonnement annuel'),
    ]
    type_licence = models.CharField(
        max_length=30, 
        choices=TYPE_LICENCE_CHOICES, 
        default='essai'
    )
    date_expiration = models.DateTimeField(blank=True, null=True)

    # Personnalisation visuelle
    couleur_primaire = models.CharField(
        max_length=7, 
        default='#E91E63'
    )  # Couleur par défaut : rouge rose
    couleur_secondaire = models.CharField(
        max_length=7, 
        default='#FFFFFF'
    )  # Couleur par défaut : blanc
    logo_url = models.URLField(blank=True, null=True)

    # Statut
    STATUT_CHOICES = [
        ('actif', 'Actif'),
        ('expire', 'Expiré'),
        ('suspendu', 'Suspendu'),
        ('essai', 'Période d\'essai'),
    ]
    statut = models.CharField(
        max_length=20, 
        choices=STATUT_CHOICES, 
        default='essai'
    )

    # date de création et de mise à jour
    date_creation = models.DateTimeField(auto_now_add=True)
    date_mise_a_jour = models.DateTimeField(auto_now=True)

    # Requis par django-tenants
    auto_create_schema = True  # Crée automatiquement le schéma pour ce tenant

    class Meta:
        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"

    def __str__(self):
        return self.nom
    

# =====================================================
# 2. MODELE DOMAIN 
# =====================================================

class Domain(DomainMixin):
    class Meta:
        verbose_name = "Domaine"
        verbose_name_plural = "Domaines"