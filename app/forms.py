from django import forms
from .models import Device

class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = [
            'id',  
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
            'id': 'ID', 
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
            'id': forms.TextInput(attrs={'placeholder': 'Digite o ID', 'class': 'form-control'}), 
            'name': forms.TextInput(attrs={'placeholder': 'Digite o nome', 'class': 'form-control'}),
            'type': forms.Select(choices=[
                ('1', 'Água'),
                ('2', 'Energia')
            ], attrs={'class': 'form-control'}),
            'mac_address': forms.TextInput(attrs={'placeholder': 'Digite o endereço MAC', 'class': 'form-control'}),
            'section': forms.TextInput(attrs={'placeholder': 'Digite a seção', 'class': 'form-control'}),
            'location': forms.TextInput(attrs={'placeholder': 'Digite a localização', 'class': 'form-control'}),
            'ip_address': forms.TextInput(attrs={'placeholder': 'Digite o endereço IP', 'class': 'form-control'}),
            'api_token': forms.TextInput(attrs={'placeholder': 'Digite o token da API', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(DeviceForm, self).__init__(*args, **kwargs)
        self.fields['id'].required = True  
        self.fields['name'].required = True
        self.fields['type'].required = True
        self.fields['is_authorized'].required = False
        self.fields['section'].required = True
        self.fields['location'].required = True
        self.fields['ip_address'].required = False
        self.fields['mac_address'].required = False
        self.fields['api_token'].required = False
