from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

# Graph nomenclature deviceType-timeCovered-type


class DeviceTypes(models.IntegerChoices):
    none = 0, 'Not Defined',
    water = 1, 'Water',
    energy = 2, 'Energy',
    gas = 3, 'Gas'

class GraphsTypes(models.IntegerChoices):
    none = 0, 'Not Defined',
    allWMoteDevices24hRaw = 1, 'All WMote Devices | 24h | Raw',
    allEMoteDevices24hRaw = 2, 'All EMote Devices | 24h | Raw',
    allGMoteDevices24hRaw = 3, 'All GMote Devices | 24h | Raw'

class AuthTypes(models.IntegerChoices):
    pending = 0, 'Pending',
    notAuthorized = 1, 'Not Authorized',
    Authorized = 2, 'Authorized',

class DataTypes(models.IntegerChoices):
    notSelected = 0, "Not Selected"
    volume = 1, "Volume (L)"
    kwh = 2, "kWh"
    watt = 3, "Watt"
    ampere = 4, "Ampere"
    
class IntervalTypes(models.IntegerChoices):
    notSelected = 0, 'Not Selected',
    hourly = 1, "Hourly"


class ExtendUser(AbstractUser):
    profile_photo = models.ImageField(
        upload_to='profile_photo/', default='defaults/profile_default.png', blank=True)
    description = models.CharField(max_length=256, blank=True)
    is_advisor = models.BooleanField(default=False)
    lattes_url = models.URLField(max_length=200, blank=True, null=True)
    email = models.CharField(max_length=200, blank=False, null=False, unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._meta.get_field('first_name').blank = False
        self._meta.get_field('last_name').blank = False
        self._meta.get_field('first_name').null = False
        self._meta.get_field('last_name').null = False

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        if (self.first_name) and (self.last_name):
            return f"{self.first_name} {self.last_name}"
        else:
            return self.email


class Device(models.Model):
    name = models.CharField(max_length=255, null=True)
    type = models.IntegerField(
        choices=DeviceTypes.choices, default=DeviceTypes.none)
    is_authorized = models.IntegerField(choices=AuthTypes.choices, default=AuthTypes.pending)
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
    type = models.IntegerField(default=DataTypes.notSelected, choices=DataTypes.choices)
    last_collection = models.FloatField(
        null=True, blank=True)  # Litros/Hora no último minuto
    total = models.FloatField(default=0)  # Listros totais
    collect_date = models.DateTimeField(auto_now_add=True)  # Data de coleta

class ProcessedData(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, blank=True)
    interval = models.IntegerField(default=IntervalTypes.notSelected, choices=IntervalTypes.choices)
    mean = models.FloatField(blank=True, null=True)
    median = models.FloatField(blank=True, null=True)
    std = models.FloatField(blank=True, null=True) # standard deviation
    cv = models.FloatField(blank=True, null=True) # coefficient of variation
    max = models.FloatField(blank=True, null=True)
    min = models.FloatField(blank=True, null=True)
    fq = models.FloatField(blank=True, null=True) # first quartile
    tq = models.FloatField(blank=True, null=True) # third quartile
    created_at = models.DateTimeField(auto_now_add=True)

class Graph(models.Model):
    device = models.ForeignKey(
        Device, on_delete=models.CASCADE, null=True, blank=True)
    type = models.IntegerField(
        choices=GraphsTypes.choices, default=GraphsTypes.none)
    file_path = models.CharField(max_length=255, blank=True, null=True)


class New(models.Model):
    user = models.ForeignKey(
        ExtendUser, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
