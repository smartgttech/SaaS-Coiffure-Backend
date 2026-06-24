from rest_framework import serializers
from rest_framework import serializers
from .models import TransactionPerformance

# Serializers de cette app
class TransactionPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionPerformance
        fields = ['id', 'type', 'points', 'motif', 'date']


class PointsActionSerializer(serializers.Serializer):
    points = serializers.IntegerField(min_value=1)
    motif = serializers.CharField(max_length=255)


class RecapitulatifPeriodeSerializer(serializers.Serializer):
    date_debut = serializers.DateField()
    date_fin = serializers.DateField()


class RecapitulatifPersonnelSerializer(serializers.Serializer):
    personnel_id = serializers.IntegerField()
    nom = serializers.CharField()
    prenom = serializers.CharField()
    specialite = serializers.CharField(allow_null=True)
    solde_actuel = serializers.IntegerField()
    points_periode = serializers.IntegerField()