from rest_framework import serializers
from .models import Tenant


class TenantPublicSerializer(serializers.ModelSerializer):
    # On ajoute un champ personnalisé qui récupère le texte lisible
    type_entreprise_label = serializers.CharField(source='get_type_entreprise_display', read_only=True)

    class Meta:
        model = Tenant
        fields = [
            'nom', 'slogan','description',
            'couleur_primaire', 'couleur_secondaire',
            'logo_url', 'photo_couverture_url',
            'police', 'theme',
            'adresse', 'telephone', 'whatsapp', 'email_contact',
            'horaires', 'instagram', 'facebook', 'tiktok', 'type_entreprise',
            'type_entreprise_label',
        ]


class TenantLicenceSerializer(serializers.ModelSerializer):
    """
    Serializer dédié à l'état de licence du tenant courant — distinct de
    TenantPublicSerializer (qui reste volontairement sans authentification
    et sans donnée sensible). Utilisé par le backoffice authentifié pour
    adapter son affichage (menu, bannières d'expiration) au statut et à la
    formule réels du tenant, peu importe le rôle de l'utilisateur connecté.
    """
    jours_restants = serializers.SerializerMethodField()

    class Meta:
        model = Tenant
        fields = [
            'statut', 'type_licence', 'formule',
            'date_expiration', 'jours_restants',
        ]

    def get_jours_restants(self, obj):
        if obj.date_expiration is None:
            return None
        from django.utils import timezone
        delta = obj.date_expiration - timezone.now()
        return max(delta.days, 0)


class TenantUpdateSerializer(serializers.Serializer):
    nom = serializers.CharField(max_length=150, required=False)
    slogan = serializers.CharField(max_length=255, required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_null=True)
    couleur_primaire = serializers.CharField(max_length=7, required=False)
    couleur_secondaire = serializers.CharField(max_length=7, required=False)
    logo_url = serializers.URLField(required=False, allow_null=True)
    photo_couverture_url = serializers.URLField(required=False, allow_null=True)
    police = serializers.ChoiceField(
        choices=['poppins', 'nunito', 'lato', 'montserrat'],
        required=False
    )
    theme = serializers.ChoiceField(
        choices=['elegant', 'moderne', 'minimaliste'],
        required=False
    )
    type_entreprise = serializers.CharField(required=False, allow_null=True)
    adresse = serializers.CharField(required=False, allow_null=True)
    telephone = serializers.CharField(max_length=20, required=False, allow_null=True)
    whatsapp = serializers.CharField(max_length=20, required=False, allow_null=True)
    email_contact = serializers.EmailField(required=False, allow_null=True)
    horaires = serializers.JSONField(required=False, allow_null=True)
    instagram = serializers.URLField(required=False, allow_null=True)
    facebook = serializers.URLField(required=False, allow_null=True)
    tiktok = serializers.URLField(required=False, allow_null=True)