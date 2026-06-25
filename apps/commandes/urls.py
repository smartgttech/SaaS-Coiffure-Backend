from django.urls import path
from .views import (
    CommandeListCreateView, CommandeDetailView,
    CommandeChangerStatutView
)

urlpatterns = [
    path('', CommandeListCreateView.as_view(), name='commande-list-create'),
    path('<int:commande_id>/', CommandeDetailView.as_view(), name='commande-detail'),
    path('<int:commande_id>/statut/', CommandeChangerStatutView.as_view(), name='commande-statut'),
]