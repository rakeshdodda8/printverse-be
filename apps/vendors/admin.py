from django.contrib import admin
from .models import VendorProfile, CommissionRule, Payout

admin.site.register([VendorProfile, CommissionRule, Payout])

