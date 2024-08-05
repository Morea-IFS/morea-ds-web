from datetime import timedelta
import datetime
import plotly.express as px
import pandas as pd
from .models import Device, Data, Graph
from django.conf import settings


def generateAllMotes24hRaw():
    for n in range(1, 4):
        idList = list(Device.objects.filter(
            type=n, is_authorized=True).values_list('id', flat=True))
        dataFrameList = []

        mediaRoot = settings.MEDIA_ROOT
        if n == 1:
            mediaPath = f'graphs/allWMoteDevices24hRaw.html'
            collectionUnit = 'Consumo(L)'
        elif n == 2:
            mediaPath = f'graphs/allEMoteDevices24hRaw.html'
            collectionUnit = 'Consumo(Watts)'
        else:
            mediaPath = 'graphs/allGMoteDevices24hRaw.html'
            collectionUnit = 'Consumo(m³)'

        for i in idList:
            counter = 0
            dateFrom = datetime.datetime.now() - timedelta(days=1)
            infoList = Device.objects.get(id=str(i))
            dataList = list(Data.objects.filter(
                device=i, collect_date__gte=dateFrom).values_list('last_collection', flat=True))
            datetimeList = list(Data.objects.filter(
                device=i, collect_date__gte=dateFrom).values_list('collect_date', flat=True))

            for collection in dataList:
                tempList = [infoList.name, collection,
                            (datetimeList[counter] - timedelta(hours=3)).strftime('%H:%M')]
                counter += 1
                dataFrameList.append(tempList)

        df = pd.DataFrame(dataFrameList, columns=[
                          'Dispositivo', collectionUnit, 'Hora'])

        config = {'displayModeBar': False}

        fig = px.line(df, x='Hora', y=collectionUnit,
                      color='Dispositivo', markers=True)
        fig.update_layout(dragmode=False, margin=dict(
            l=0, r=0, t=0, b=0), xaxis_title=None)
        fig.update_traces(textposition="bottom right")
        fig.write_html(f'{mediaRoot}{mediaPath}', config)

        if not (Graph.objects.all().filter(type=n).exists()):
            createGraph = Graph(type=n, file_path=mediaPath)
            createGraph.save()
