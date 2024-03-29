from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Device, Data, ExtendUser, Graph, New

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
                    'is_advisor'
                ),
            },
        ),
    )


class DevicesAdmin(admin.ModelAdmin):
    list_display = ['name', 'type',
                    'section', 'location', 'mac_address', 'ip_address']


class DataAdmin(admin.ModelAdmin):
    list_display = ['id', 'device', 'last_collection', 'total', 'collect_date']


class GraphsAdmin(admin.ModelAdmin):
    list_display = ['id', 'device', 'type', 'file_path']


class NewsAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'message', 'created_at']


admin.site.register(ExtendUser, CustomUserAdmin)
admin.site.register(Device, DevicesAdmin)
admin.site.register(Data, DataAdmin)
admin.site.register(Graph, GraphsAdmin)
admin.site.register(New, NewsAdmin)
