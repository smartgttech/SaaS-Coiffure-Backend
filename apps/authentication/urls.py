from django.urls import path
from .views import LoginView, InscriptionPersonnelView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('inscription/', InscriptionPersonnelView.as_view(), name='inscription-personnel')
]
