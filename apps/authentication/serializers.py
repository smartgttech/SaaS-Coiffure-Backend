from rest_framework import serializers

# Serializers de cette app

# ===========================================
# 1. CONNEXION
# ===========================================
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

# =============================================
# 2. INSCRIPTION PERSONNEL
# =============================================
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

# ===============================================
# 3. DECONNEXION
# ===============================================
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


# ================================================
# 4. PROFIL PERSONNEL
# ================================================
class UtilisateurMeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    role = serializers.CharField()
    tenant_id = serializers.IntegerField()
    nom = serializers.CharField()
    prenom = serializers.CharField()
    