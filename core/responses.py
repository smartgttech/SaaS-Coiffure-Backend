from rest_framework.response import Response
from rest_framework import status

# ==========================================================
# 1. REUSSITE
def success(data=None, message="Success", status_code=status.HTTP_200_OK):
    """
    Réponse Standard pour les requêtes réussies.
    """
    return Response({
        'success': True,
        'message': message,
        'data': data
    }, status=status_code)


# ==========================================================
# 2. CREATION
def created(data=None, message=None):
    """
    Réponse Standard pour les ressources créées avec succès.
    """
    return success(data=data, message=message, status_code=status.HTTP_201_CREATED)


# ==========================================================
# 3. ERREUR
def error(message=None, errors=None, status_code=status.HTTP_400_BAD_REQUEST):
    """
    Réponse Standard pour les requêtes échouées.
    """
    return Response({
        'success': False,
        'message': message,
        'errors': errors
    }, status=status_code)


# ==========================================================
# 4. INTROUVABLE
def not_found(message="Ressource non trouvée"):
    """
    Réponse Standard pour les ressources non trouvées.
    """
    return error(message=message, status_code=status.HTTP_404_NOT_FOUND)


# ==========================================================
# 5. NON AUTORISÉ
def unauthorized(message="Non autorisé"):
    """
    Réponse Standard pour les accès non autorisés.
    """
    return error(message=message, status_code=status.HTTP_401_UNAUTHORIZED)


# ==========================================================
# 6. ACCESS INTERDIT
def forbidden(message="Accès interdit"):
    """
    Réponse Standard pour les accès interdits.
    """
    return error(message=message, status_code=status.HTTP_403_FORBIDDEN)