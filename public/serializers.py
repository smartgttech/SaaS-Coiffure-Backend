from rest_framework import serializers
from tenants.models import Tenant
from tenants.serializers import TenantPublicSerializer
from drf_spectacular.utils import extend_schema_field


class TenantAdminSerializer(serializers.ModelSerializer):
    domaines = serializers.SerializerMethodField()
    jours_restants = serializers.SerializerMethodField()

    class Meta:
        model = Tenant
        fields = [
            'id', 'nom', 'sous_domaine', 'domaine_custom',
            'type_licence', 'statut', 'date_expiration',
            'couleur_primaire', 'couleur_secondaire',
            'logo_url', 'photo_couverture_url',
            'police', 'theme',
            'slogan', 'description',
            'adresse', 'telephone', 'whatsapp', 'email_contact',
            'horaires', 'instagram', 'facebook', 'tiktok',
            'domaines', 'jours_restants',
            'date_creation', 'date_mise_a_jour'
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
        choices=['essai', 'mensuel', 'annuel', 'definitif'],
        default='essai'
    )
    couleur_primaire = serializers.CharField(max_length=7, default='#E91E63')
    couleur_secondaire = serializers.CharField(max_length=7, default='#D8B26E')


class ActiverLicenceSerializer(serializers.Serializer):
    type_licence = serializers.ChoiceField(
        choices=['mensuel', 'annuel', 'definitif']
    )
    duree_jours = serializers.IntegerField(min_value=1)


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