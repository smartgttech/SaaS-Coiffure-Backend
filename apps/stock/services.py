from apps.journal.services import JournalService
from .repository import ProduitRepository, MouvementStockRepository

# Logique métier de cette app
# Utilise le repository pour accéder aux données


class StockService:

    def __init__(self):
        self.produit_repo = ProduitRepository()
        self.mouvement_repo = MouvementStockRepository()
        self.journal = JournalService()

    def lister_produits(self):
        return self.produit_repo.liste_actifs()

    def obtenir_produit(self, produit_id):
        produit = self.produit_repo.par_id(produit_id)
        if produit is None:
            raise ValueError("Produit introuvable.")
        return produit

    def creer_produit(self, data, utilisateur=None):
        if self.produit_repo.par_reference(data.get('reference')):
            raise ValueError("Un produit existe déjà avec cette référence.")

        produit = self.produit_repo.creer(data)

        self.journal.enregistrer(
            utilisateur=utilisateur,
            type_action='creation_produit',
            ressource='Produit',
            ressource_id=produit.id,
            details_apres={'nom': produit.nom, 'reference': produit.reference}
        )
        return produit

    def modifier_produit(self, produit_id, data, utilisateur=None):
        produit = self.obtenir_produit(produit_id)

        details_avant = {
            champ: str(getattr(produit, champ, None))
            for champ in data.keys()
        }

        produit_modifie = self.produit_repo.modifier(produit, data)

        self.journal.enregistrer(
            utilisateur=utilisateur,
            type_action='modification_produit',
            ressource='Produit',
            ressource_id=produit.id,
            details_avant=details_avant,
            details_apres={k: str(v) for k, v in data.items()}
        )
        return produit_modifie

    def archiver_produit(self, produit_id, utilisateur=None):
        produit = self.obtenir_produit(produit_id)
        produit_archive = self.produit_repo.archiver(produit)

        self.journal.enregistrer(
            utilisateur=utilisateur,
            type_action='archivage_produit',
            ressource='Produit',
            ressource_id=produit.id
        )
        return produit_archive

    def approvisionner(self, produit_id, quantite, note=None, utilisateur=None):
        """
        Entrée de stock — approvisionnement manuel.
        """
        if quantite <= 0:
            raise ValueError("La quantité doit être supérieure à zéro.")

        produit = self.obtenir_produit(produit_id)
        quantite_avant = produit.quantite_stock
        quantite_apres = quantite_avant + quantite

        self.produit_repo.modifier(produit, {'quantite_stock': quantite_apres})
        self.mouvement_repo.creer(
            produit=produit,
            type='entree',
            motif='approvisionnement',
            quantite=quantite,
            quantite_avant=quantite_avant,
            quantite_apres=quantite_apres,
            note=note
        )

        self.journal.enregistrer(
            utilisateur=utilisateur,
            type_action='approvisionnement_stock',
            ressource='Produit',
            ressource_id=produit.id,
            details_avant={'quantite_stock': quantite_avant},
            details_apres={'quantite_stock': quantite_apres}
        )
        return produit

    def decrementer(self, produit_id, quantite, motif='vente_physique', utilisateur=None):
        """
        Sortie de stock — vente physique ou en ligne.
        Appelé automatiquement depuis le module Caisse lors d'une vente.
        """
        if quantite <= 0:
            raise ValueError("La quantité doit être supérieure à zéro.")

        produit = self.obtenir_produit(produit_id)

        if produit.quantite_stock < quantite:
            raise ValueError(f"Stock insuffisant. Stock disponible : {produit.quantite_stock}.")

        quantite_avant = produit.quantite_stock
        quantite_apres = quantite_avant - quantite

        self.produit_repo.modifier(produit, {'quantite_stock': quantite_apres})
        self.mouvement_repo.creer(
            produit=produit,
            type='sortie',
            motif=motif,
            quantite=quantite,
            quantite_avant=quantite_avant,
            quantite_apres=quantite_apres
        )
        return produit

    def alertes_stock(self):
        """
        Retourne les produits dont le stock est sous le seuil d'alerte.
        """
        return self.produit_repo.sous_seuil_alerte()

    def historique_mouvements(self, produit_id=None):
        return self.mouvement_repo.historique(produit_id=produit_id)

    def valeur_totale_stock(self):
        """
        Valeur totale du stock en temps réel — section 3.7 du CDC.
        """
        produits = self.produit_repo.liste_actifs()
        return sum(p.quantite_stock * p.prix_achat for p in produits)
