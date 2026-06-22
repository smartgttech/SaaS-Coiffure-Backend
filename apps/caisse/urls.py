from django.urls import path
from .views import (
    PaiementListCreateView, PaiementDetailView,
    ArdoiseListView, ArdoiseClienteView, ArdoiseReglerView,
    CaisseTableauDuJourView
)

urlpatterns = [
    path('paiements/', PaiementListCreateView.as_view(), name='paiement-list-create'),
    path('paiements/<int:paiement_id>/', PaiementDetailView.as_view(), name='paiement-detail'),
    path('ardoises/', ArdoiseListView.as_view(), name='ardoise-list'),
    path('ardoises/cliente/<int:cliente_id>/', ArdoiseClienteView.as_view(), name='ardoise-cliente'),
    path('ardoises/<int:paiement_id>/regler/', ArdoiseReglerView.as_view(), name='ardoise-regler'),
    path('tableau-du-jour/', CaisseTableauDuJourView.as_view(), name='caisse-tableau-jour'),
]