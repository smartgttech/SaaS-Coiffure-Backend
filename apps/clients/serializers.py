from rest_framework import serializers
from .models import Cliente, TransactionPoints


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = [
            'id', 'nom', 'prenom', 'telephone', 'date_naissance',
            'date_premiere_visite', 'notes', 'solde_points',
            'actif', 'date_creation', 'date_modification'
        ]
        read_only_fields = ['id', 'solde_points', 'date_premiere_visite', 'date_creation', 'date_modification']


class ClienteCreateSerializer(serializers.Serializer):
    nom = serializers.CharField(max_length=100)
    prenom = serializers.CharField(max_length=100)
    telephone = serializers.CharField(max_length=20)
    date_naissance = serializers.DateField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class ClienteUpdateSerializer(serializers.Serializer):
    nom = serializers.CharField(max_length=100, required=False)
    prenom = serializers.CharField(max_length=100, required=False)
    telephone = serializers.CharField(max_length=20, required=False)
    date_naissance = serializers.DateField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class TransactionPointsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionPoints
        fields = ['id', 'type', 'points', 'motif', 'date']


class PointsActionSerializer(serializers.Serializer):
    points = serializers.IntegerField(min_value=1)
    motif = serializers.CharField(max_length=255)