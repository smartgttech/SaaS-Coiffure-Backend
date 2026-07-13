from django.db import models
from django_tenants.models import TenantMixin, DomainMixin
from django.conf import settings

# Create your models here.

# =====================================================
# 1. MODELE TENANT
# =====================================================

class Tenant(TenantMixin):

    # Informations de Base
    nom = models.CharField(max_length=150)
    sous_domaine = models.CharField(max_length=100, unique=True)
    domaine_custom = models.CharField(max_length=255, blank=True, null=True)

    # Licence — CADENCE DE FACTURATION (durée entre paiements)
    TYPE_LICENCE_CHOICES = [
        ('essai', 'Période d\'essai '),
        ('mensuel', 'Abonnement mensuel'),
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

    # Formule — PALIER FONCTIONNEL (quels modules sont accessibles).
    # Champ volontairement distinct de type_licence : la cadence de
    # facturation et le périmètre de fonctionnalités sont deux décisions
    # indépendantes (voir core/licences.py pour le détail des modules
    # inclus par formule). Un tenant 'pro' peut être facturé mensuellement
    # ou annuellement, sans que ça change les modules auxquels il accède.
    FORMULE_CHOICES = [
        ('essai', 'Essai — accès complet, durée limitée'),
        ('basic', 'Basic'),
        ('basic_plus', 'Basic+'),
        ('pro', 'Pro'),
        ('full', 'Full'),
    ]
    formule = models.CharField(
        max_length=20,
        choices=FORMULE_CHOICES,
        default='essai',
        help_text="Détermine les modules accessibles. Voir core/licences.py"
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
    statut_avant_suspension = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Mémorise le statut du tenant juste avant sa suspension, pour restauration fidèle."
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

    # En prévision du multi-domain + multi_tenant
    TYPE_CHOICES = [
        ('beauty', 'Institut de beauté'),
        ('coiffure', 'Salon de coiffure'),
        ('restaurant', 'Restaurant'),
        ('quincaillerie', 'Quincaillerie'),
        ('hotel', 'Hôtel')
    ]
    type_entreprise = models.CharField(blank=True, null=True, choices=TYPE_CHOICES, default='beauty')

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


# =====================================================
# 3. MODELE JOURNALISATION ACTIONS - Super Admin
# =====================================================

class JournalPlateforme(models.Model):
    """
    Trace les actions du Super Admin sur la plateforme.
    Vit exclusivement dans le schéma public.
    """
    TYPE_ACTIONS = [
        ('impersonnalisation', 'Accès support (impersonnalisation)'),
        ('consultation_journal', 'Consultation du journal d\'un tenant'),
        ('creation_tenant', 'Création tenant'),
        ('suspension', 'Suspension tenant'),
        ('reactivation', 'Réactivation tenant'),
        ('activation_licence', 'Activation licence'),
        ('prolongation_essai', 'Prolongation essai'),
        ('ajout_jours_licence', 'Ajout de jours licence'),
        ('domaine_custom', 'Association domaine custom'),
    ]

    super_admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='journal_plateforme'
    )
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='journal_plateforme',
        null=True,
        blank=True
    )
    type_action = models.CharField(max_length=50, choices=TYPE_ACTIONS)
    details = models.JSONField(null=True, blank=True)
    adresse_ip = models.GenericIPAddressField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Journal plateforme"
        verbose_name_plural = "Journal plateforme"
        ordering = ['-date']

    def __str__(self):
        return f"{self.type_action} — {self.super_admin} — {self.date}"
    


# =====================================================
# 4. MODELE JOURNALISATION ACTIONS - impersonnalisation
# =====================================================


class JournalImpersonnalisation(models.Model):
    """
    Table dédiée à l'historique des sessions d'impersonnalisation,
    séparée du journal générique pour un accès rapide depuis la page
    détail d'un tenant (CDC section 3.11 et 8.5).
    """
    super_admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='impersonnalisations'
    )
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='journaux_impersonnalisation'
    )
    proprietaire_email = models.EmailField()
    date_acces = models.DateTimeField(auto_now_add=True)
    adresse_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Session d'impersonnalisation"
        verbose_name_plural = "Sessions d'impersonnalisation"
        ordering = ['-date_acces']

    def __str__(self):
        return f"{self.super_admin} → {self.tenant.nom} le {self.date_acces}"