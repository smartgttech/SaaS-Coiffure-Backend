from django.urls import path
from .views import (
    CouponListCreateView, CouponDetailView,
    CouponValiderView, CouponHistoriqueView
)

urlpatterns = [
    path('', CouponListCreateView.as_view(), name='coupon-list-create'),
    path('<int:coupon_id>/', CouponDetailView.as_view(), name='coupon-detail'),
    path('valider/', CouponValiderView.as_view(), name='coupon-valider'),
    path('<int:coupon_id>/historique/', CouponHistoriqueView.as_view(), name='coupon-historique'),
]