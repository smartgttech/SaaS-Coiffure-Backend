from rest_framework import serializers

# Serializers de cette app
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class InscriptionPersonnelSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    nom = serializers.CharField(max_length=100)
    prenom = serializers.CharField(max_length=100)
    role = serializers.ChoiceField(
        choices=[
            'proprietaire',
            'employe', 
            'stagiaire'
        ],
        default='employe'
    )
    date_entree = serializers.DateField()
    specialite = serializers.CharField(max_length=150, required=False, allow_null=True)
