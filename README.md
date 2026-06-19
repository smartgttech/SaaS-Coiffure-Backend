# HosJos — Backend

API backend de la plateforme SaaS de gestion pour salons de coiffure et de beauté à Douala, Cameroun.

## Stack technique

- Python 3.14
- Django + Django REST Framework
- django-tenants (architecture multi-tenant)
- PostgreSQL
- JWT (authentification)

## Prérequis

- Python 3.12+ installé
- PostgreSQL installé et fonctionnel
- Git

## Installation

1. Cloner le repo

\`\`\`bash
git clone https://github.com/smartgttech/SaaS-Coiffure-Backend.git
cd SaaS-Coiffure-Backend
\`\`\`

2. Créer et activer l'environnement virtuel

\`\`\`bash
python -m venv venv
venv\Scripts\activate
\`\`\`

3. Installer les dépendances

\`\`\`bash
pip install -r requirements.txt
\`\`\`

4. Créer la base de données PostgreSQL

\`\`\`sql
CREATE DATABASE hosjossalon;
\`\`\`

5. Configurer les variables d'environnement

Copier `.env.example` vers `.env` et renseigner les vraies valeurs :

\`\`\`bash
cp .env.example .env
\`\`\`

6. Appliquer les migrations

\`\`\`bash
python manage.py migrate_schemas --shared
\`\`\`

7. Créer le tenant public (requis pour accéder à l'admin en local)

\`\`\`bash
python manage.py shell
\`\`\`

\`\`\`python
from tenants.models import Tenant, Domain

tenant_public = Tenant(
    schema_name='public',
    nom='HosJos Platform',
    sous_domaine='public',
    statut='actif',
    type_licence='definitif'
)
tenant_public.save()

domain = Domain(domain='localhost', tenant=tenant_public, is_primary=True)
domain.save()
\`\`\`

8. Créer un superutilisateur

\`\`\`bash
python manage.py createsuperuser
\`\`\`

9. Lancer le serveur

\`\`\`bash
python manage.py runserver
\`\`\`

## Accès utiles

- Admin Django : http://localhost:8000/admin
- Documentation API (Swagger) : http://localhost:8000/api/docs/
- Health check : http://localhost:8000/api/health/

## Architecture

Le projet suit une Clean Architecture avec séparation en couches :

\`\`\`
apps/<nom_app>/
├── models.py        → structure des données
├── repository.py    → accès aux données (hérite de BaseRepository)
├── services.py       → logique métier
├── views.py          → endpoints API
├── serializers.py    → validation et formatage
└── urls.py            → routing
\`\`\`

Le tenant courant est automatiquement injecté dans les repositories via `core/tenant_context.py`.

## Modèles principaux

- `authentication` — Utilisateur (auth), Personnel
- `clients` — Cliente, TransactionPoints
- `rendez_vous` — Prestation, RendezVous
- `produits` — Produit
- `commandes` — Commande, LigneCommande
- `caisse` — Paiement
- `stock` — MouvementStock
- `coupons` — Coupon, CouponUtilisation
- `personnel` — TransactionPerformance
- `rapports` — SMSCampagne

Note : le module `ardoises` n'a pas de modèle dédié — le solde se calcule dynamiquement à partir des `Paiement` avec statut `partiel` ou `impaye`.