from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

# Graph nomenclature deviceType-timeCovered-type


class DeviceTypes(models.IntegerChoices):
    none = 0, 'Not Defined',
    water = 1, 'Water',
    energy = 2, 'Energy'


class GraphsTypes(models.IntegerChoices):
    none = 0, 'Not Defined',
    allWMoteDevices24hRaw = 1, 'All WMote Devices | 24h | Raw',
    allEMoteDevices24hRaw = 2, 'All EMote Devices | 24h | Raw',


class ExtendUser(AbstractUser):
    profile_photo = models.ImageField(
        upload_to='profile/', default='defaults/profile_default.png')
    description = models.CharField(max_length=256, blank=True)
    is_advisor = models.BooleanField(default=False)

    def __str__(self):
        if (self.first_name) and (self.last_name):
            return f"{self.first_name} {self.last_name}"
        else:
            return self.username


class Device(models.Model):
    id = models.CharField(primary_key=True, max_length=255,
                          blank=False, null=False)
    name = models.CharField(max_length=255, null=True)
    type = models.IntegerField(
        choices=DeviceTypes.choices, default=DeviceTypes.none)
    mac_address = models.CharField(
        max_length=255, null=True, blank=True, unique=True)
    section = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    ip_address = models.GenericIPAddressField(
        max_length=255, null=True, blank=True)
    api_token = models.CharField(
        max_length=255, null=True, blank=True, unique=True)

    def __str__(self):
        if self.name:
            return self.name
        else:
            return "Unnamed"


class Data(models.Model):
    device = models.ForeignKey(
        Device, on_delete=models.CASCADE, null=True, blank=True)
    last_collection = models.FloatField(
        null=True, blank=True)  # Litros/Hora no último minuto
    total = models.FloatField(default=0)  # Listros totais
    collect_date = models.DateTimeField(auto_now_add=True)  # Data de coleta


class Graph(models.Model):
    device = models.ForeignKey(
        Device, on_delete=models.CASCADE, null=True, blank=True)
    type = models.IntegerField(
        choices=GraphsTypes.choices, default=GraphsTypes.none)
    file_path = models.CharField(max_length=255, blank=True, null=True)
