from django.contrib import admin

from b2_utils import models

admin.site.register(models.Address)
admin.site.register(models.City)
admin.site.register(models.Phone)
