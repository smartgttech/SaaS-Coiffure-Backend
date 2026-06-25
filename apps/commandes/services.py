from decimal import Decimal
from apps.journal.services import JournalService
from apps.clients.repository import ClienteRepository
from apps.stock.repository import ProduitRepository, MouvementStockRepository
from apps.coupons.services import CouponService
from .repository import CommandeRepository, LigneCommandeRepository


TRANSITIONS_COMMANDE = {
    'en_preparation': ['prete', 'annulee'],
    'prete': ['livree', 'annulee'],
    'livree': [],
    'annulee': [],
}


class CommandeService:

    def __init__(self):
        self.commande_repo = CommandeRepository()
        self.ligne_repo = LigneCommandeRepository()
        self.produit_repo = ProduitRepository()
        self.mouvement_repo = MouvementStockRepository()
        self.cliente_repo = ClienteRepository()
        self.journal = JournalService()

    def lister(self, **filtres):
        return self.commande_repo.liste(**filtres)

    def obtenir(self, commande_id):
        commande = self.commande_repo.par_id(commande_id)
        if commande is None:
            raise ValueError("Commande introuvable.")
        return commande

    def creer(self, data, utilisateur=None):
        lignes = data.get('lignes', [])
        if not lignes:
            raise ValueError("Une commande doit contenir au moins un produit.")

        # Vérifier le stock et calculer le montant total
        montant_total = Decimal('0')
        lignes_validees = []

        for ligne in lignes:
            produit = self.produit_repo.par_id(ligne['produit_id'])
            if produit is None:
                raise ValueError(f"Produit introuvable (id: {ligne['produit_id']}).")

            if produit.quantite_stock < ligne['quantite']:
                raise ValueError(
                    f"Stock insuffisant pour '{produit.nom}'. "
                    f"Disponible : {produit.quantite_stock}."
                )

            # Prix figé au moment de la commande — section 6.4 du CDC
            prix_unitaire = produit.prix_vente
            montant_total += prix_unitaire * ligne['quantite']
            lignes_validees.append({
                'produit': produit,
                'quantite': ligne['quantite'],
                'prix_unitaire': prix_unitaire
            })

        # Appliquer le coupon si fourni
        reduction = Decimal('0')
        coupon_id = data.get('coupon_id') or None
        cliente_id = data.get('cliente_id') 

        if coupon_id and cliente_id:
            coupon_service = CouponService()
            try:
                resultat = coupon_service.valider_et_appliquer(
                    code=data['coupon_code'],
                    cliente_id=cliente_id,
                    utilisateur=utilisateur
                )
                if resultat['type'] == 'montant_fixe':
                    reduction = Decimal(str(resultat['reduction']))
                else:
                    reduction = montant_total * Decimal(str(resultat['valeur'])) / 100
            except ValueError:
                pass  # Coupon invalide — on continue sans réduction

        montant_final = max(montant_total - reduction, Decimal('0'))

        # Créer la commande
        commande_data = {
            'cliente_id': cliente_id,
            'coupon_id': coupon_id,
            'montant_total': montant_final,
            'mode_livraison': data['mode_livraison'],
            'adresse_livraison': data.get('adresse_livraison'),
        }
        commande = self.commande_repo.creer(commande_data)

        # Créer les lignes et décrémenter le stock
        for ligne in lignes_validees:
            self.ligne_repo.creer(
                commande=commande,
                produit=ligne['produit'],
                quantite=ligne['quantite'],
                prix_unitaire=ligne['prix_unitaire']
            )

            # Décrémentation automatique du stock — section 2.3 du CDC
            quantite_avant = ligne['produit'].quantite_stock
            quantite_apres = quantite_avant - ligne['quantite']
            self.produit_repo.modifier(ligne['produit'], {'quantite_stock': quantite_apres})
            self.mouvement_repo.creer(
                produit=ligne['produit'],
                type='sortie',
                motif='vente_en_ligne',
                quantite=ligne['quantite'],
                quantite_avant=quantite_avant,
                quantite_apres=quantite_apres
            )

        self.journal.enregistrer(
            utilisateur=utilisateur,
            type_action='creation_commande',
            ressource='Commande',
            ressource_id=commande.id,
            details_apres={
                'montant_total': str(montant_final),
                'mode_livraison': data['mode_livraison'],
                'nb_lignes': len(lignes_validees)
            }
        )
        return commande

    def changer_statut(self, commande_id, nouveau_statut, utilisateur=None):
        commande = self.obtenir(commande_id)

        # L'annulation est réservée à la propriétaire
        if nouveau_statut == 'annulee':
            if utilisateur and utilisateur.role not in ['proprietaire', 'super_admin']:
                raise ValueError("Seule la propriétaire peut annuler une commande.")

        transitions_possibles = TRANSITIONS_COMMANDE.get(commande.statut, [])
        if nouveau_statut not in transitions_possibles:
            raise ValueError(
                f"Impossible de passer du statut '{commande.statut}' à '{nouveau_statut}'."
            )

        ancien_statut = commande.statut
        commande_modifiee = self.commande_repo.modifier_statut(commande, nouveau_statut)

        # Si annulation, on remet le stock
        if nouveau_statut == 'annulee':
            for ligne in commande.lignes.all():
                produit = ligne.produit
                quantite_avant = produit.quantite_stock
                quantite_apres = quantite_avant + ligne.quantite
                self.produit_repo.modifier(produit, {'quantite_stock': quantite_apres})
                self.mouvement_repo.creer(
                    produit=produit,
                    type='entree',
                    motif='correction',
                    quantite=ligne.quantite,
                    quantite_avant=quantite_avant,
                    quantite_apres=quantite_apres,
                    note=f"Annulation commande #{commande.id}"
                )

        self.journal.enregistrer(
            utilisateur=utilisateur,
            type_action='changement_statut_commande',
            ressource='Commande',
            ressource_id=commande.id,
            details_avant={'statut': ancien_statut},
            details_apres={'statut': nouveau_statut}
        )
        return commande_modifiee