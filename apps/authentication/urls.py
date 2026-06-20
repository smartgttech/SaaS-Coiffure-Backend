from django.urls import path
from .views import LoginView, InscriptionPersonnelView, LogoutView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('inscription/', InscriptionPersonnelView.as_view(), name='inscription-personnel'),
    path('refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
