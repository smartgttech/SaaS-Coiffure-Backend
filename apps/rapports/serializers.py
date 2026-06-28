from rest_framework import serializers


class PeriodeSerializer(serializers.Serializer):
    date_debut = serializers.DateField()
    date_fin = serializers.DateField()

    def validate(self, data):
        if data['date_debut'] > data['date_fin']:
            raise serializers.ValidationError(
                "La date de début doit être antérieure à la date de fin."
            )
        return data


class InactiviteSerializer(serializers.Serializer):
    semaines = serializers.IntegerField(min_value=1, default=4)