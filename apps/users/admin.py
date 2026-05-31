from django.contrib import admin
from .models import User, Profile, Address, SocialAccount, ImportedPhoto

admin.site.register([User, Profile, Address, SocialAccount, ImportedPhoto])

