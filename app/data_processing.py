from app.models import Device, Data, ProcessedData
from django.utils import timezone
from datetime import timedelta
import numpy

def run():
    processData(1)

def processData(time):
    timeCounter = timezone.now() - timedelta(hours=time)
    devices = Device.objects.all().filter(is_authorized=2)

    for device in devices:
        try:
            deviceData = list(Data.objects.values_list('last_collection', flat=True).filter(
                device=device, collect_date__gte=timeCounter))
            # Função __gte = greater than or equal, compara a data.
            
            if len(deviceData) != 0:
                mean = numpy.mean(deviceData)
                median = numpy.median(deviceData)
                std = numpy.std(deviceData)
                cv = std / mean
                max = numpy.amax(deviceData)
                min = numpy.amin(deviceData)
                fq = numpy.quantile(deviceData, 0.25)
                tq = numpy.quantile(deviceData, 0.75)

                processedData = ProcessedData(device=device, mean=mean, median=median, std=std, cv=cv, max=max, min=min, fq=fq, tq=tq)
                processedData.save()
            else:
                processedData = ProcessedData(device=device, mean=None, median=None, std=None, cv=None, max=None, min=None, fq=None, tq=None)
                processedData.save()
                
        except:
            print('data processing error')
            pass