from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Device, DeviceLog, Data, ExtendUser, ProcessedData, Graph, New

# Register your models here.


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        *UserAdmin.fieldsets,  # original form fieldsets, expanded
        (                      # new fieldset added on to the bottom
            # group heading of your choice; set to None for a blank space instead of a header
            'Aditional Info',
            {
                'fields': (
                    'profile_photo',
                    'description',
                    'is_advisor',
                    'lattes_url'
                ),
            },
        ),
    )


class DevicesAdmin(admin.ModelAdmin):
    list_display = ['name', 'type',
                    'section', 'location', 'mac_address', 'ip_address', 'api_token', 'is_authorized']
    
class DeviceLogsAdmin(admin.ModelAdmin):
    list_display = ['device', 'mac_address', 'ip_address', 'api_token', 'is_authorized', 'created_at']


class DataAdmin(admin.ModelAdmin):
    list_display = ['id', 'device', 'type', 'last_collection', 'total', 'collect_date']

class ProcessedDataAdmin(admin.ModelAdmin):
    list_display = ['id', 'device', 'interval', 'mean', 'median', 'std', 'cv', 'max', 'min', 'fq', 'tq', 'created_at']

class GraphsAdmin(admin.ModelAdmin):
    list_display = ['id', 'device', 'type', 'file_path']


class NewsAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'message', 'created_at']


admin.site.register(ExtendUser, CustomUserAdmin)
admin.site.register(Device, DevicesAdmin)
admin.site.register(DeviceLog, DeviceLogsAdmin)
admin.site.register(Data, DataAdmin)
admin.site.register(ProcessedData, ProcessedDataAdmin)
admin.site.register(Graph, GraphsAdmin)
admin.site.register(New, NewsAdmin)
