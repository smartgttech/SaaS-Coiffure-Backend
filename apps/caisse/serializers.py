from rest_framework import serializers
from .models import Paiement


class PaiementSerializer(serializers.ModelSerializer):
    cliente_nom = serializers.CharField(source='cliente.nom', read_only=True, allow_null=True)
    cliente_prenom = serializers.CharField(source='cliente.prenom', read_only=True, allow_null=True)

    class Meta:
        model = Paiement
        fields = [
            'id', 'cliente', 'cliente_nom', 'cliente_prenom',
            'rendez_vous', 'commande',
            'montant_total', 'montant_verse', 'solde_restant',
            'mode_paiement', 'statut', 'activite', 'canal',
            'date', 'date_creation', 'date_modification', 'reference',
        ]
        read_only_fields = [
            'id', 'solde_restant', 'statut', 'activite', 'canal',
            'date', 'date_creation', 'date_modification','reference',
        ]


class PaiementCreateSerializer(serializers.Serializer):
    cliente_id = serializers.IntegerField(required=False, allow_null=True)
    rendez_vous_id = serializers.IntegerField(required=False, allow_null=True)
    commande_id = serializers.IntegerField(required=False, allow_null=True)
    montant_total = serializers.DecimalField(max_digits=10, decimal_places=2)
    montant_verse = serializers.DecimalField(max_digits=10, decimal_places=2)
    mode_paiement = serializers.ChoiceField(choices=['cash', 'orange_money', 'mtn_money', 'en_ligne'])
    activite_produit = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class ReglerArdoiseSerializer(serializers.Serializer):
    montant_supplementaire = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)


class CADuJourSerializer(serializers.Serializer):
    ca_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    ca_encaisse = serializers.DecimalField(max_digits=12, decimal_places=2)
    ca_en_attente = serializers.DecimalField(max_digits=12, decimal_places=2)