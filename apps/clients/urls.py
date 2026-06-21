from django.urls import path
from .views import (
    ClienteListCreateView, ClienteDetailView,
    ClientePointsAjouterView, ClientePointsRetirerView,
    ClientePointsHistoriqueView
)

urlpatterns = [
    path('', ClienteListCreateView.as_view(), name='client-list-create'),
    path('<int:cliente_id>/', ClienteDetailView.as_view(), name='client-details'),
    path('<int:cliente_id>/points/', ClientePointsHistoriqueView.as_view(), name='client-points-historique'),
    path('<int:cliente_id>/points/ajouter/', ClientePointsAjouterView.as_view(), name='client-points-ajouter'),
    path('<int:cliente_id>/points/retirer/', ClientePointsRetirerView.as_view(), name='client-points-retirer'),
]
