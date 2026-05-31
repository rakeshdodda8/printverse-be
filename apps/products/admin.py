from django.contrib import admin
from .models import Category, Product, ProductImage, ProductVariant, Review, WishlistItem

admin.site.register([Category, Product, ProductImage, ProductVariant, Review, WishlistItem])

