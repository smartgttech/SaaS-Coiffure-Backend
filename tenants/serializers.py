from rest_framework import serializers
from .models import Tenant


class TenantPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = [
            'nom', 'slogan','description',
            'couleur_primaire', 'couleur_secondaire',
            'logo_url', 'photo_couverture_url',
            'police', 'theme',
            'adresse', 'telephone', 'whatsapp', 'email_contact',
            'horaires', 'instagram', 'facebook', 'tiktok',
        ]


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
    adresse = serializers.CharField(required=False, allow_null=True)
    telephone = serializers.CharField(max_length=20, required=False, allow_null=True)
    whatsapp = serializers.CharField(max_length=20, required=False, allow_null=True)
    email_contact = serializers.EmailField(required=False, allow_null=True)
    horaires = serializers.JSONField(required=False, allow_null=True)
    instagram = serializers.URLField(required=False, allow_null=True)
    facebook = serializers.URLField(required=False, allow_null=True)
    tiktok = serializers.URLField(required=False, allow_null=True)