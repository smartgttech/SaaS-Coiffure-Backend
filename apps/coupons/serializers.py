from rest_framework import serializers

# Serializers de cette app
from rest_framework import serializers
from .models import Coupon, CouponUtilisation


class CouponSerializer(serializers.ModelSerializer):
    est_expire = serializers.SerializerMethodField()
    nombre_utilisations = serializers.SerializerMethodField()

    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'type', 'valeur',
            'date_expiration', 'usage_unique',
            'cliente', 'actif',
            'est_expire', 'nombre_utilisations',
            'date_creation', 'date_modification'
        ]
        read_only_fields = ['id', 'date_creation', 'date_modification']

    def get_est_expire(self, obj):
        from django.utils import timezone
        if obj.date_expiration:
            return obj.date_expiration < timezone.now().date()
        return False

    def get_nombre_utilisations(self, obj):
        return obj.utilisations.count()


class CouponCreateSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50)
    type = serializers.ChoiceField(choices=['montant_fixe', 'pourcentage'])
    valeur = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    date_expiration = serializers.DateField(required=False, allow_null=True)
    usage_unique = serializers.BooleanField(default=True)
    cliente_id = serializers.IntegerField(required=False, allow_null=True)


class ValiderCouponSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50)
    cliente_id = serializers.IntegerField()


class CouponUtilisationSerializer(serializers.ModelSerializer):
    cliente_nom = serializers.CharField(source='cliente.nom', read_only=True)
    cliente_prenom = serializers.CharField(source='cliente.prenom', read_only=True)

    class Meta:
        model = CouponUtilisation
        fields = [
            'id', 'cliente', 'cliente_nom', 'cliente_prenom',
            'rendez_vous', 'commande', 'date_utilisation'
        ]