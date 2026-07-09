"""
Fichier: core/licences.py
Rôle: Source unique de vérité pour la segmentation des fonctionnalités par palier de licence.

PRINCIPE DE CONCEPTION
----------------------
Ce système est volontairement implémenté en configuration Python statique (ce fichier),
et NON via un modèle de base de données (Plan / Module en tables relationnelles).

Pourquoi ce choix :
- Les paliers (Essai / Basic / Basic+ / Pro / Full) sont une décision produit stable,
  définie dans le CDC. Ce n'est pas une donnée qui change au quotidien.
- Un système Plan/Module en base de données apporterait de la flexibilité (modifier les
  paliers sans déploiement) mais au prix d'une complexité largement disproportionnée
  pour un besoin qui, aujourd'hui, ne le justifie pas.
- Si un jour le besoin business évolue (packages personnalisés par client, paliers
  configurables dynamiquement par le Super Admin), CE fichier est le seul endroit à
  migrer vers un modèle de données — toute la logique applicative qui consomme
  `tenant_a_acces_module()` n'aura pas à changer.

Pour ajouter/retirer un module d'un palier : modifier uniquement MODULES_PAR_PALIER
ci-dessous. Aucune migration, aucun redéploiement de la logique de contrôle d'accès.
"""

# =====================================================================
# 1. IDENTIFIANTS DE MODULES
# =====================================================================
# Chaque clé correspond à une app Django (TENANT_APPS), sauf 'vitrine' qui
# représente le site public du tenant (pas une app au sens Django, mais un
# périmètre fonctionnel à part entière — toujours accessible, voir plus bas).

MODULE_VITRINE = 'vitrine'              # Site public (horaires, prestations, contact) — TOUJOURS inclus
MODULE_CLIENTS = 'clients'              # Fiches clientes
MODULE_RENDEZ_VOUS = 'rendez_vous'      # Agenda, prestations, réservation
MODULE_CAISSE = 'caisse'                # Encaissement (cash, mobile money, en ligne)
MODULE_COUPONS = 'coupons'              # Codes promo et réductions
MODULE_PRODUITS = 'produits'            # Catalogue produits (vente en boutique)
MODULE_STOCK = 'stock'                  # Gestion des mouvements de stock
MODULE_COMMANDES = 'commandes'          # Commandes en ligne + livraison
MODULE_PERSONNEL = 'personnel'          # Suivi de performance du personnel
MODULE_JOURNAL = 'journal'              # Consultation de l'historique/audit détaillé
MODULE_ARDOISES = 'ardoises'            # Crédit client ("ardoise")

# NOTE IMPORTANTE : l'app Django `apps.rapports` mélange en réalité DEUX besoins
# de nature très différente (voir apps/rapports/views.py) :
#   1. Un tableau de bord + rapports financiers/impayés de base — un salon,
#      même le plus petit, a besoin de savoir combien il a encaissé et qui
#      lui doit de l'argent. Ce n'est pas un "plus", c'est une nécessité.
#   2. Des campagnes marketing SMS — un outil d'acquisition/rétention avancé,
#      qui a un coût opérationnel réel (envoi SMS) et s'adresse à des salons
#      déjà structurés qui investissent dans leur croissance.
# Ces deux besoins ne doivent PAS être gatés au même palier. On les distingue
# donc en deux modules séparés, bien qu'ils vivent dans la même app Django.
MODULE_TABLEAU_BORD = 'tableau_bord'          # Dashboard + rapport financier + impayés
MODULE_RAPPORTS_AVANCES = 'rapports_avances'  # Rapport clients (inactivité) + rapport stock
MODULE_SMS_MARKETING = 'sms_marketing'        # Campagnes SMS

TOUS_LES_MODULES = [
    MODULE_CLIENTS, MODULE_RENDEZ_VOUS, MODULE_CAISSE, MODULE_COUPONS,
    MODULE_PRODUITS, MODULE_STOCK, MODULE_COMMANDES, MODULE_PERSONNEL,
    MODULE_JOURNAL, MODULE_ARDOISES,
    MODULE_TABLEAU_BORD, MODULE_RAPPORTS_AVANCES, MODULE_SMS_MARKETING,
]

# =====================================================================
# 2. DÉFINITION DES PALIERS
# =====================================================================
# Chaque palier hérite implicitement du précédent dans la logique commerciale
# (Basic+ = Basic + ajouts, Pro = Basic+ + ajouts, Full = Pro + tout), mais est
# déclaré explicitement ici pour éviter toute ambiguïté de calcul en cascade.

MODULES_PAR_PALIER = {

    # ESSAI : accès complet, temporaire (30 jours par défaut).
    # Objectif : laisser le prospect vivre la valeur COMPLÈTE du produit,
    # pour maximiser la conversion vers un palier payant à l'expiration.
    'essai': TOUS_LES_MODULES,

    # BASIC : le strict nécessaire pour qu'un salon indépendant (souvent
    # mono-utilisateur) sorte du cahier papier / WhatsApp et digitalise
    # sa prise de rendez-vous et ses encaissements. On y inclut le tableau
    # de bord de base : savoir combien on a encaissé n'est pas un luxe,
    # c'est le minimum pour qu'un salon fasse confiance à l'outil.
    'basic': [
        MODULE_CLIENTS,
        MODULE_RENDEZ_VOUS,
        MODULE_CAISSE,
        MODULE_TABLEAU_BORD,
    ],

    # BASIC+ : ajoute la fidélisation. Un salon qui commence à avoir une
    # clientèle régulière a besoin d'outils pour la retenir (coupons/promos).
    'basic_plus': [
        MODULE_CLIENTS,
        MODULE_RENDEZ_VOUS,
        MODULE_CAISSE,
        MODULE_TABLEAU_BORD,
        MODULE_COUPONS,
    ],

    # PRO : pour les salons qui vendent aussi des produits (cosmétiques,
    # perruques, etc.) et qui ont une équipe à gérer plutôt qu'un seul
    # propriétaire polyvalent. Ajoute la dimension "commerce" et "équipe",
    # ainsi que les rapports avancés (inactivité clients, valorisation
    # stock) qui n'ont de sens qu'une fois qu'on gère effectivement du
    # stock et une équipe.
    'pro': [
        MODULE_CLIENTS,
        MODULE_RENDEZ_VOUS,
        MODULE_CAISSE,
        MODULE_TABLEAU_BORD,
        MODULE_COUPONS,
        MODULE_PRODUITS,
        MODULE_STOCK,
        MODULE_COMMANDES,
        MODULE_PERSONNEL,
        MODULE_RAPPORTS_AVANCES,
    ],

    # FULL : établissement structuré qui a besoin d'outils marketing actifs
    # (campagnes SMS — qui ont un coût d'envoi réel, à réserver aux clients
    # les plus engagés), de traçabilité complète (journal d'audit
    # consultable, utile en cas de litige ou de contrôle interne) et de
    # gestion de la confiance client au comptoir (ardoises = crédit /
    # paiement différé, une pratique commerciale courante et sensible qui
    # mérite le palier le plus engagé, car elle expose le salon à un
    # risque financier direct).
    'full': TOUS_LES_MODULES,
}

# La vitrine publique (site web du salon) n'est JAMAIS filtrée par palier.
# Elle sert de argument commercial permanent, y compris pour un salon en
# 'essai' arrivé à expiration : le site reste visible, seul le backoffice
# de gestion se bloque (voir core/middleware.py). C'est volontaire : couper
# la vitrine publique d'un salon expiré nuirait à son image et compliquerait
# sa réactivation commerciale — le Super Admin doit pouvoir le relancer sans
# que le salon ait disparu d'internet entre-temps.


def modules_disponibles(formule: str) -> list[str]:
    """
    Retourne la liste des modules accessibles pour une formule donnée.
    Fallback prudent : une formule inconnue (donnée corrompue, valeur
    legacy) n'obtient AUCUN module plutôt qu'un accès complet par défaut —
    principe de sécurité "fail closed", pas "fail open".
    """
    return MODULES_PAR_PALIER.get(formule, [])


def tenant_a_acces_module(tenant, module: str) -> bool:
    """
    Vérifie si un tenant a accès à un module donné, selon sa `formule`
    actuelle (PAS `type_licence`, qui ne concerne que la cadence de
    facturation — voir tenants/models.py pour la distinction).
    Le module 'vitrine' retourne toujours True (voir note ci-dessus).
    """
    if module == MODULE_VITRINE:
        return True
    return module in modules_disponibles(tenant.formule)
