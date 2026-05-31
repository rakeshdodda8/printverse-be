from django.contrib import admin
from .models import Cart, CartItem, Coupon, Order, OrderItem, Shipment, OrderStatusHistory

admin.site.register([Cart, CartItem, Coupon, Order, OrderItem, Shipment, OrderStatusHistory])

