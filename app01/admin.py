from django.contrib import admin

# Register your models here.
from .models import Welcome, Mine
admin.site.register(Welcome)
admin.site.register(Mine)
