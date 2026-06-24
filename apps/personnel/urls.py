from django.urls import path
from .views import (
    PersonnelPointsAjouterView, PersonnelPointsRetirerView,
    PersonnelPointsHistoriqueView, PersonnelRecapitulatifView,
    PersonnelRecapitulatifTousView
)

urlpatterns = [
    path('<int:personnel_id>/points/ajouter/', PersonnelPointsAjouterView.as_view(), name='personnel-points-ajouter'),
    path('<int:personnel_id>/points/retirer/', PersonnelPointsRetirerView.as_view(), name='personnel-points-retirer'),
    path('<int:personnel_id>/points/historique/', PersonnelPointsHistoriqueView.as_view(), name='personnel-points-historique'),
    path('<int:personnel_id>/recapitulatif/', PersonnelRecapitulatifView.as_view(), name='personnel-recapitulatif'),
    path('recapitulatif/', PersonnelRecapitulatifTousView.as_view(), name='personnel-recapitulatif-tous'),
]