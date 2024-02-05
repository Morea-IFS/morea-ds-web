from django.contrib import admin
from .models import Device

# Register your models here.


class DevicesAdmin(admin.ModelAdmin):
    list_display = ['name', 'type',
                    'section', 'location', 'mac_address', 'ip_address']


admin.site.register(Device, DevicesAdmin)
