# apps/journal/urls.py
from django.urls import path
from .views import JournalListeView, JournalRessourceView

urlpatterns = [
    path('', JournalListeView.as_view(), name='journal-liste'),
    path('<str:ressource>/<int:ressource_id>/', JournalRessourceView.as_view(), name='journal-ressource'),
]