from django import forms
from .models import Device

class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = [
            'name', 
            'type', 
            'is_authorized', 
            'mac_address', 
            'section', 
            'location', 
            'ip_address', 
            'api_token'
        ]
        labels = {
            'name': 'Nome',
            'type': 'Tipo',
            'is_authorized': 'Autorizado',
            'mac_address': 'Endereço MAC',
            'section': 'Seção',
            'location': 'Localização',
            'ip_address': 'Endereço IP',
            'api_token': 'Token da API',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'is_authorized': forms.Select(attrs={'class': 'form-control'}),
            'mac_address': forms.TextInput(attrs={'class': 'form-control'}),
            'section': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'ip_address': forms.TextInput(attrs={'class': 'form-control'}),
            'api_token': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(DeviceForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['type'].required = True
        self.fields['is_authorized'].required = True
        self.fields['section'].required = True
        self.fields['location'].required = True
        self.fields['ip_address'].required = False
        self.fields['mac_address'].required = False
        self.fields['api_token'].required = False

