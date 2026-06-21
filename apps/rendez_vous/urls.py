from django.urls import path
from .views import (
    PrestationListCreateView, PrestationDetailView,
    RendezVousListCreateView, RendezVousDetailView, RendezVousChangerStatutView
)

urlpatterns = [
    path('prestations/', PrestationListCreateView.as_view(), name='prestation-list-create'),
    path('prestations/<int:prestation_id>/', PrestationDetailView.as_view(), name='prestation-detail'),
    path('', RendezVousListCreateView.as_view(), name='rdv-list-create'),
    path('<int:rdv_id>/', RendezVousDetailView.as_view(), name='rdv-detail'),
    path('<int:rdv_id>/statut/', RendezVousChangerStatutView.as_view(), name='rdv-changer-statut'),
]