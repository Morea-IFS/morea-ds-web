from datetime import timedelta
import datetime
import plotly.express as px
import pandas as pd
from .models import Device, Data, Graph


def generateAllMotes24hRaw():
    for n in range(1, 3):
        idList = list(Device.objects.filter(
            type=n).values_list('id', flat=True))
        dataFrameList = []

        mediaRoot = 'media/'
        if (n == 1):
            mediaPath = f'graphs/allWMoteDevices24hRaw.html'
            collectionUnit = 'Consumo(L)'
        else:
            mediaPath = f'graphs/allEMoteDevices24hRaw.html'
            collectionUnit = 'Consumo(Watts)'

        for i in idList:
            counter = 0
            dateFrom = datetime.datetime.now() - timedelta(days=1)
            infoList = Device.objects.get(id=str(i))
            dataList = list(Data.objects.filter(
                device=i, collect_date__gte=dateFrom).values_list('last_collection', flat=True))
            datetimeList = list(Data.objects.filter(
                device=i, collect_date__gte=dateFrom).values_list('collect_date', flat=True))
            timeList = []

            for time in datetimeList:
                brTimeZone = time + timedelta(hours=-3)
                formatTime = brTimeZone.strftime('%H:%M')
                timeList.append(formatTime)

            for collection in dataList:
                tempList = [infoList.name, collection, timeList[counter]]
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
