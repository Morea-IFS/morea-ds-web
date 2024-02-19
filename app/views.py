from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import uuid

# Graphs
from datetime import timedelta, time
import datetime
import plotly.express as px
import pandas as pd
from .models import Device, Data

# Create your views here.

# Render


def index(request):
    return render(request, 'home.html')


def dashboard(request):

    # dataList = list(Data.objects.values_list('last_collection', flat=True))
    # datetimeList = list(Data.objects.values_list('collect_date', flat=True))
    # timeList = []

    # for i in datetimeList:
    #     brTimeZone = i + timedelta(hours=-3)
    #     time = brTimeZone.strftime('%H:%M')

    #     timeList.append(time)

    idList = list(Device.objects.filter(type=1).values_list('id', flat=True))
    dataFrameList = []

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
                      'Dispositivo', 'Consumo(L)', 'Hora'])

    print(df)

    config = {'displayModeBar': False}

    fig = px.line(df, x='Hora', y="Consumo(L)", color='Dispositivo')
    fig.update_layout(dragmode=False)
    fig.write_html('static/graphs/first_figure.html', config)

    return render(request, 'dashboard.html')


def members(request):
    return render(request, 'members.html')


def news(request):
    return render(request, 'news.html')

# API


@api_view(['POST'])
def identifyDevice(request):
    if request.method == 'POST':
        macAddress = request.POST['macAddress']

        if Device.objects.all().filter(mac_address=macAddress).exists():
            apiToken = uuid.uuid4()

            device = Device.objects.get(mac_address=macAddress)
            device.api_token = str(apiToken)
            device.save()

            return Response({'id': device.id, 'api_token': apiToken}, status=status.HTTP_200_OK)
        else:
            id = uuid.uuid4()
            apiToken = uuid.uuid4()

            try:
                newDevice = Device(
                    id=id, mac_address=macAddress, api_token=apiToken)
                newDevice.save()
            except:
                return Response({'error': 'something went wrong.'}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'id': id, 'api_token': apiToken}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def getDeviceIp(request):
    if request.method == "POST":
        deviceId = request.POST["deviceId"]
        deviceIp = request.POST["deviceIp"]
        apiToken = request.POST["apiToken"]

    if Device.objects.all().filter(id=deviceId).exists():
        if Device.objects.get(id=deviceId).api_token == apiToken:
            if deviceId and deviceIp:
                deviceObject = Device.objects.get(id=deviceId)
                deviceObject.ip_address = str(deviceIp)
                deviceObject.save()

                print(deviceObject.name)

                return Response({'message': 'ip received.', 'deviceName': deviceObject.name}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'ip not received.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'api token does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'message': 'device does not exist.'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def getDeviceData(request):
    if request.method == "POST":
        deviceId = request.POST["deviceId"]
        apiToken = request.POST["apiToken"]
        volume = request.POST["volume"]

    if Device.objects.all().filter(id=deviceId).exists():
        if Device.objects.get(id=deviceId).api_token == apiToken:
            if deviceId and volume:
                device = Device.objects.get(id=str(deviceId))
                total = Data.objects.all().filter(
                    device=str(deviceId)).order_by('id').reverse()

                if (total):
                    saveData = Data(device=device,
                                    last_collection=float(volume), total=(float(total[0].total) + float(volume)))
                    saveData.save()
                else:
                    saveData = Data(device=device,
                                    last_collection=float(volume), total=float(volume))
                    saveData.save()

                return Response({'message': 'data received.'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'data not received.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'api token does not exist.'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response({'message': 'device does not exist.'}, status=status.HTTP_404_NOT_FOUND)
