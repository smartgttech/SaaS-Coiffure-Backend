from django.contrib import admin
from .models import Coupon, CouponUtilisation

admin.site.register(Coupon)
admin.site.register(CouponUtilisation)