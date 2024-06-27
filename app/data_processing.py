from app.models import Device, Data, ProcessedData
from django.utils import timezone
from datetime import timedelta
import numpy

def hourlyDataProcessing():
    processData(1)

def processData(time):
    timeCounter = timezone.now() - timedelta(hours=time)
    devices = Device.objects.all()

    for device in devices:
        try:
            deviceData = list(Data.objects.values_list('last_collection', flat=True).filter(
                device=device, collect_date__gte=timeCounter))
            # Função __gte = greater than or equal, compara a data.
            
            if deviceData is not None:
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
                # processedData = ProcessedData(device=device, mean=0, median=0, std=0, cv=0, max=0, min=0, fq=0, tq=0)
                # processedData.save()
                pass
                
        except:
            print('error')
            pass