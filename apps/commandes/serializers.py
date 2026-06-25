from rest_framework import serializers
from .models import Commande, LigneCommande


class LigneCommandeSerializer(serializers.ModelSerializer):
    produit_nom = serializers.CharField(source='produit.nom', read_only=True)
    produit_reference = serializers.CharField(source='produit.reference', read_only=True)

    class Meta:
        model = LigneCommande
        fields = ['id', 'produit', 'produit_nom', 'produit_reference', 'quantite', 'prix_unitaire']


class CommandeSerializer(serializers.ModelSerializer):
    lignes = LigneCommandeSerializer(many=True, read_only=True)
    cliente_nom = serializers.CharField(source='cliente.nom', read_only=True, allow_null=True)
    cliente_prenom = serializers.CharField(source='cliente.prenom', read_only=True, allow_null=True)

    class Meta:
        model = Commande
        fields = [
            'id', 'cliente', 'cliente_nom', 'cliente_prenom',
            'coupon', 'date', 'statut', 'montant_total',
            'mode_livraison', 'adresse_livraison',
            'lignes', 'date_creation', 'date_modification'
        ]
        read_only_fields = ['id', 'date', 'date_creation', 'date_modification']


class LigneCommandeCreateSerializer(serializers.Serializer):
    produit_id = serializers.IntegerField()
    quantite = serializers.IntegerField(min_value=1)


class CommandeCreateSerializer(serializers.Serializer):
    cliente_id = serializers.IntegerField(required=False, allow_null=True)
    coupon_id = serializers.IntegerField(required=False, allow_null=True)
    coupon_code = serializers.CharField(required=False, allow_null=True)
    mode_livraison = serializers.ChoiceField(choices=['retrait', 'livraison_domicile'])
    adresse_livraison = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    lignes = LigneCommandeCreateSerializer(many=True, min_length=1)


class ChangerStatutCommandeSerializer(serializers.Serializer):
    statut = serializers.ChoiceField(choices=['prete', 'livree', 'annulee'])