from django.urls import path
from .views import (
    ProduitListCreateView, ProduitDetailView,
    StockApprovisionnerView, StockAlertesView,
    StockMouvementsView, StockValeurTotaleView
)

urlpatterns = [
    path('produits/', ProduitListCreateView.as_view(), name='produit-list-create'),
    path('produits/<int:produit_id>/', ProduitDetailView.as_view(), name='produit-detail'),
    path('produits/<int:produit_id>/approvisionner/', StockApprovisionnerView.as_view(), name='stock-approvisionner'),
    path('produits/<int:produit_id>/mouvements/', StockMouvementsView.as_view(), name='stock-mouvements-produit'),
    path('alertes/', StockAlertesView.as_view(), name='stock-alertes'),
    path('mouvements/', StockMouvementsView.as_view(), name='stock-mouvements'),
    path('valeur/', StockValeurTotaleView.as_view(), name='stock-valeur'),
]