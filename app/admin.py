from django.contrib import admin
from .models import Device, Data

# Register your models here.


class DevicesAdmin(admin.ModelAdmin):
    list_display = ['name', 'type',
                    'section', 'location', 'mac_address', 'ip_address']


class DataAdmin(admin.ModelAdmin):
    list_display = ['id', 'device', 'last_collection', 'total', 'collect_date']


admin.site.register(Device, DevicesAdmin)
admin.site.register(Data, DataAdmin)
