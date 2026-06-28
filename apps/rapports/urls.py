from django.urls import path
from .views import (
    TableauDeBordView, RapportFinancierView,
    RapportImpayesView, RapportClientsView,
    RapportStockView, RapportSMSCampagneView
)

urlpatterns = [
    path('tableau-de-bord/', TableauDeBordView.as_view(), name='tableau-de-bord'),
    path('financier/', RapportFinancierView.as_view(), name='rapport-financier'),
    path('impayes/', RapportImpayesView.as_view(), name='rapport-impayes'),
    path('clients/', RapportClientsView.as_view(), name='rapport-clients'),
    path('stock/', RapportStockView.as_view(), name='rapport-stock'),
    path('sms/', RapportSMSCampagneView.as_view(), name='rapport-sms'),
]