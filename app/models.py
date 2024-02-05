from django.db import models

# Create your models here.


class DeviceTypes(models.IntegerChoices):
    none = 0, 'Not Defined',
    water = 1, 'Water',
    energy = 2, 'Energy'


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
        return self.name
