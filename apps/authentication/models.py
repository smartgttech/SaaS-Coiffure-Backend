from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from tenants.models import Tenant


# Modèles de cette app à définir ici
#===============================================

class UtilisateurManager(BaseUserManager):
    """
    Manager personnalisé — utilise email comme identifiant
    à la place du username par défaut de Django.
    """

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'adresse email est obligatoire")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'super_admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class Utilisateur(AbstractBaseUser, PermissionsMixin):

    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('proprietaire', 'Propriétaire'),
        ('employe', 'Employé(e)'),
        ('stagiaire', 'Stagiaire'),
        ('cliente', 'Cliente'),
    ]

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='utilisateurs'
        # null=True pour le super_admin qui n'appartient à aucun tenant
    )
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='employe'
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)

    objects = UtilisateurManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        return f"{self.email} ({self.role})"


class Personnel(models.Model):

    STATUT_CHOICES = [
        ('actif', 'Actif'),
        ('en_stage', 'En stage'),
        ('inactif', 'Inactif'),
    ]

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='personnel'
    )
    utilisateur = models.OneToOneField(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name='profil_personnel'
    )
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    specialite = models.CharField(max_length=150, blank=True, null=True)
    date_entree = models.DateField()
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='actif'
    )
    solde_points_performance = models.IntegerField(default=0)
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Personnel"
        verbose_name_plural = "Personnel"

    def __str__(self):
        return f"{self.prenom} {self.nom} — {self.tenant.nom}"