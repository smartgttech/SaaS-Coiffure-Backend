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
    

# ==================================================
# 5. LISTE DU PERSONNEL DU TENANT 
# ==================================================
class PersonnelSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nom = serializers.CharField()
    prenom = serializers.CharField()
    specialite = serializers.CharField(allow_null=True)
    date_entree = serializers.DateField()
    statut = serializers.CharField()
    solde_points_performance = serializers.IntegerField()
    actif = serializers.BooleanField()
    email = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    def get_email(self, obj):
        return obj.utilisateur.email if obj.utilisateur else None

    def get_role(self, obj):
        return obj.utilisateur.role if obj.utilisateur else None


# ==================================================
# 6. MISE A JOUR DU PERSONNEL DU TENANT 
# ==================================================
class PersonnelUpdateSerializer(serializers.Serializer):
    nom = serializers.CharField(max_length=100, required=False)
    prenom = serializers.CharField(max_length=100, required=False)
    specialite = serializers.CharField(max_length=150, required=False, allow_null=True)
    date_entree = serializers.DateField(required=False)
    statut = serializers.ChoiceField(
        choices=['actif', 'en_stage', 'inactif'],
        required=False
    )