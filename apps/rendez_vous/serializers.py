from rest_framework import serializers
from .models import Prestation, RendezVous


class PrestationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prestation
        fields = [
            'id', 'nom', 'description', 'categorie', 'prix_min', 'prix_max',
            'duree_minutes', 'points_performance', 'actif',
            'date_creation', 'date_modification'
        ]
        read_only_fields = ['id', 'date_creation', 'date_modification']


class PrestationCreateSerializer(serializers.Serializer):
    nom = serializers.CharField(max_length=150)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    categorie = serializers.CharField(max_length=100)
    prix_min = serializers.DecimalField(max_digits=10, decimal_places=2)
    prix_max = serializers.DecimalField(max_digits=10, decimal_places=2)
    duree_minutes = serializers.IntegerField(min_value=1)
    points_performance = serializers.IntegerField(required=False, default=0)


class RendezVousSerializer(serializers.ModelSerializer):
    cliente_nom = serializers.CharField(source='cliente.nom', read_only=True)
    cliente_prenom = serializers.CharField(source='cliente.prenom', read_only=True)
    prestation_nom = serializers.CharField(source='prestation.nom', read_only=True)
    personnel_nom = serializers.CharField(source='personnel.nom', read_only=True)

    class Meta:
        model = RendezVous
        fields = [
            'id', 'cliente', 'cliente_nom', 'cliente_prenom',
            'prestation', 'prestation_nom',
            'personnel', 'personnel_nom',
            'date_heure', 'statut', 'prix_final', 'note_cliente',
            'apporte_meche', 'date_creation', 'date_modification'
        ]
        read_only_fields = ['id', 'statut', 'date_creation', 'date_modification']


class RendezVousCreateSerializer(serializers.Serializer):
    cliente_id = serializers.IntegerField()
    prestation_id = serializers.IntegerField()
    personnel_id = serializers.IntegerField()
    date_heure = serializers.DateTimeField()
    prix_final = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    note_cliente = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    apporte_meche = serializers.BooleanField(required=False, default=False)


class RendezVousUpdateSerializer(serializers.Serializer):
    date_heure = serializers.DateTimeField(required=False)
    note_cliente = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    apporte_meche = serializers.BooleanField(required=False)


class ChangerStatutSerializer(serializers.Serializer):
    statut = serializers.ChoiceField(choices=['confirme', 'en_cours', 'termine', 'annule'])