from rest_framework import serializers
from apps.produits.models import Produit
from .models import MouvementStock
from drf_spectacular.utils import extend_schema_field

class ProduitSerializer(serializers.ModelSerializer):
    en_alerte = serializers.SerializerMethodField()

    class Meta:
        model = Produit
        fields = [
            'id', 'reference', 'nom', 'description', 'photo_url',
            'prix_achat', 'prix_vente', 'quantite_stock', 'seuil_alerte',
            'categorie', 'actif', 'en_alerte',
            'date_creation', 'date_modification'
        ]
        read_only_fields = ['id', 'date_creation', 'date_modification']

    @extend_schema_field(serializers.BooleanField())
    def get_en_alerte(self, obj):
        return obj.quantite_stock <= obj.seuil_alerte


class ProduitCreateSerializer(serializers.Serializer):
    reference = serializers.CharField(max_length=100)
    nom = serializers.CharField(max_length=150)
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    photo_url = serializers.URLField(required=False, allow_null=True)
    prix_achat = serializers.DecimalField(max_digits=10, decimal_places=2)
    prix_vente = serializers.DecimalField(max_digits=10, decimal_places=2)
    quantite_stock = serializers.IntegerField(required=False, default=0)
    seuil_alerte = serializers.IntegerField(required=False, default=5)
    categorie = serializers.CharField(max_length=100)


class ProduitUpdateSerializer(serializers.Serializer):
    nom = serializers.CharField(max_length=150, required=False)
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    photo_url = serializers.URLField(required=False, allow_null=True)
    prix_achat = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    prix_vente = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    seuil_alerte = serializers.IntegerField(required=False)
    categorie = serializers.CharField(max_length=100, required=False)


class ApprovisionnerSerializer(serializers.Serializer):
    quantite = serializers.IntegerField(min_value=1)
    note = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class MouvementStockSerializer(serializers.ModelSerializer):
    produit_nom = serializers.CharField(source='produit.nom', read_only=True)

    class Meta:
        model = MouvementStock
        fields = [
            'id', 'produit', 'produit_nom', 'type', 'motif',
            'quantite', 'quantite_avant', 'quantite_apres',
            'note', 'date'
        ]