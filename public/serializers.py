from rest_framework import serializers
from tenants.models import Tenant
from tenants.serializers import TenantPublicSerializer
from drf_spectacular.utils import extend_schema_field


class TenantAdminSerializer(serializers.ModelSerializer):
    domaines = serializers.SerializerMethodField()
    jours_restants = serializers.SerializerMethodField()
    # On ajoute un champ personnalisé qui récupère le texte lisible
    type_entreprise_label = serializers.CharField(source='get_type_entreprise_display', read_only=True)

    class Meta:
        model = Tenant
        fields = [
            'id', 'nom', 'sous_domaine', 'domaine_custom',
            'type_licence', 'formule', 'statut', 'date_expiration',
            'couleur_primaire', 'couleur_secondaire',
            'logo_url', 'photo_couverture_url',
            'police', 'theme',
            'slogan', 'description',
            'adresse', 'telephone', 'whatsapp', 'email_contact',
            'horaires', 'instagram', 'facebook', 'tiktok',
            'domaines', 'jours_restants',
            'date_creation', 'date_mise_a_jour', 'type_entreprise',
            'type_entreprise_label',
        ]

    @extend_schema_field(serializers.ListField())
    def get_domaines(self, obj):
        return list(obj.domains.values('domain', 'is_primary'))

    @extend_schema_field(serializers.IntegerField(allow_null=True))
    def get_jours_restants(self, obj):
        if obj.date_expiration:
            from django.utils import timezone
            delta = obj.date_expiration - timezone.now()
            return max(delta.days, 0)
        return None


class TenantCreateSerializer(serializers.Serializer):
    nom = serializers.CharField(max_length=150)
    sous_domaine = serializers.CharField(max_length=100)
    type_licence = serializers.ChoiceField(
        choices=['essai', 'mensuel', 'trimestriel', 'annuel', 'illimite'],
        default='essai'
    )
    formule = serializers.ChoiceField(
        choices=['essai', 'basic', 'basic_plus', 'pro', 'full'],
        default='essai'
    )
    statut = serializers.ChoiceField(
        choices=['essai', 'actif', 'expire', 'suspendu'],
        default='essai'
    )
    couleur_primaire = serializers.CharField(max_length=7, default='#E91E63')
    couleur_secondaire = serializers.CharField(max_length=7, default='#D8B26E')
    type_entreprise = serializers.CharField(required=False, allow_null=True)
    # Compte propriétaire à créer dans le nouveau schéma
    proprietaire_email = serializers.EmailField()
    proprietaire_prenom = serializers.CharField(max_length=100)
    proprietaire_nom = serializers.CharField(max_length=100)
    proprietaire_mot_de_passe = serializers.CharField(
        write_only=True, min_length=8
    )

class ActiverLicenceSerializer(serializers.Serializer):
    type_licence = serializers.ChoiceField(
        choices=['mensuel', 'annuel', 'illimite', 'essai', 'trimestriel', 'semestriel']
    )
    formule = serializers.ChoiceField(
        choices=['essai', 'basic', 'basic_plus', 'pro', 'full']
    )


class ProlongerEssaiSerializer(serializers.Serializer):
    jours_supplementaires = serializers.IntegerField(min_value=1, max_value=90)


class DomainCustomSerializer(serializers.Serializer):
    domaine_custom = serializers.CharField(max_length=255)


class StatistiquesSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    actifs = serializers.IntegerField()
    en_essai = serializers.IntegerField()
    suspendus = serializers.IntegerField()
    expires = serializers.IntegerField()
    expirant_bientot = serializers.IntegerField()