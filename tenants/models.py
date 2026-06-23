from django.db import models
from django_tenants.models import TenantMixin, DomainMixin

# Create your models here.

# =====================================================
# 1. MODELE TENANT
# =====================================================

class Tenant(TenantMixin):

    # Informations de Base
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
        ('illimite', 'Abonnement illimité'),
    ]
    type_licence = models.CharField(
        max_length=30, 
        choices=TYPE_LICENCE_CHOICES, 
        default='essai'
    )
    date_expiration = models.DateTimeField(blank=True, null=True)

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

    # Identité visuelle
     # Personnalisation visuelle
    couleur_primaire = models.CharField(
        max_length=7, 
        default='#E91E63'
    )  # Couleur par défaut : rouge rose
    couleur_secondaire = models.CharField(
        max_length=7, 
        default='#FFFFFF'
    )  # Couleur par défaut : blanc
    logo_url = models.URLField(max_length=500, blank=True, null=True)
    photo_couverture_url = models.URLField(blank=True, null=True, max_length=500)

    POLICE_CHOICES = [
        ('poppins', 'Poppins'),
        ('nunito', 'Nunito'),
        ('lato', 'Lato'),
        ('montserrat', 'Montserrat'),
    ]
    police = models.CharField(
        max_length=20,
        choices=POLICE_CHOICES,
        default='poppins'
    )
    THEME_CHOICES = [
        ('elegant', 'Élégant'),
        ('moderne', 'Moderne'),
        ('minimaliste', 'Minimaliste'),
    ]
    theme = models.CharField(
        max_length=20,
        choices=THEME_CHOICES,
        default='elegant'
    )

    # Informations du salon
    slogan = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    adresse = models.TextField(blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    whatsapp = models.CharField(max_length=20, blank=True, null=True)
    email_contact = models.EmailField(blank=True, null=True)

    # Horaires d'ouverture (format JSON — ex: {"lundi": "08:00-18:00", ...})
    horaires = models.JSONField(blank=True, null=True)

    # Réseaux sociaux
    instagram = models.URLField(max_length=255, blank=True, null=True)
    facebook = models.URLField(max_length=255, blank=True, null=True)
    tiktok = models.URLField(max_length=255, blank=True, null=True)

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