import os

# Liste des apps métier à créer dans le dossier apps/
APPS = [
    'authentication',
    'clients',
    'rendez_vous',
    'caisse',
    'ardoises',
    'stock',
    'produits',
    'commandes',
    'personnel',
    'coupons',
    'rapports',
]

# Fichiers à créer dans chaque app
FICHIERS_APP = [
    '__init__.py',
    'models.py',
    'repository.py',
    'services.py',
    'views.py',
    'serializers.py',
    'urls.py',
    'admin.py',
    'apps.py',
]

def creer_app(nom_app):
    chemin = os.path.join('apps', nom_app)
    os.makedirs(chemin, exist_ok=True)

    for fichier in FICHIERS_APP:
        chemin_fichier = os.path.join(chemin, fichier)
        if not os.path.exists(chemin_fichier):
            with open(chemin_fichier, 'w', encoding='utf-8') as f:
                # Contenu minimal selon le fichier
                if fichier == 'apps.py':
                    f.write(
f"""from django.apps import AppConfig


class {nom_app.capitalize()}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.{nom_app}'
"""
                    )
                elif fichier == 'urls.py':
                    f.write(
"""from django.urls import path

urlpatterns = [
]
"""
                    )
                elif fichier == 'models.py':
                    f.write(
"""from django.db import models

# Modèles de cette app à définir ici
"""
                    )
                elif fichier == 'repository.py':
                    f.write(
"""from repositories.base import BaseRepository

# Repository de cette app
# Hérite de BaseRepository qui injecte automatiquement le tenant_id
"""
                    )
                elif fichier == 'services.py':
                    f.write(
"""# Logique métier de cette app
# Utilise le repository pour accéder aux données
"""
                    )
                elif fichier == 'views.py':
                    f.write(
"""from rest_framework.views import APIView
from rest_framework.response import Response

# Endpoints de cette app
"""
                    )
                elif fichier == 'serializers.py':
                    f.write(
"""from rest_framework import serializers

# Serializers de cette app
"""
                    )
                else:
                    f.write('')

    print(f"  ✓ App '{nom_app}' créée")


def creer_repositories_base():
    os.makedirs('repositories', exist_ok=True)

    # __init__.py
    init_path = os.path.join('repositories', '__init__.py')
    if not os.path.exists(init_path):
        with open(init_path, 'w', encoding='utf-8') as f:
            f.write('')

    # base.py — classe de base dont tous les repositories hériteront
    base_path = os.path.join('repositories', 'base.py')
    if not os.path.exists(base_path):
        with open(base_path, 'w', encoding='utf-8') as f:
            f.write(
"""class BaseRepository:
    \"\"\"
    Classe de base pour tous les repositories.
    Injecte automatiquement le tenant_id dans chaque accès aux données.
    Tous les repositories héritent de cette classe.
    \"\"\"

    def __init__(self, tenant_id):
        self.tenant_id = tenant_id
"""
            )

    print("  ✓ Dossier 'repositories' créé avec la classe de base")


def creer_init_apps():
    init_path = os.path.join('apps', '__init__.py')
    if not os.path.exists(init_path):
        with open(init_path, 'w', encoding='utf-8') as f:
            f.write('')
    print("  ✓ Dossier 'apps' initialisé")


if __name__ == '__main__':
    print("\n=== Création de la structure du projet ===\n")

    print("[ Dossier apps/ ]")
    creer_init_apps()
    for app in APPS:
        creer_app(app)

    print("\n[ Dossier repositories/ ]")
    creer_repositories_base()

    print("\n=== Structure créée avec succès ===\n")