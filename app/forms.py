from django import forms
from .models import Device, DeviceTypes

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
            'api_token',
            'voltage'
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
            'voltage': 'Tensão',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control', 'id': 'device-type-select'}),
            'is_authorized': forms.Select(attrs={'class': 'form-control'}),
            'mac_address': forms.TextInput(attrs={'class': 'form-control'}),
            'section': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'ip_address': forms.TextInput(attrs={'class': 'form-control'}),
            'api_token': forms.TextInput(attrs={'class': 'form-control'}),
            'voltage': forms.Select(attrs={'class': 'form-control', 'id': 'voltage-select'}),
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
        self.fields['voltage'].required = False
        
        if self.instance and self.instance.pk:
            if self.instance.type != DeviceTypes.energy:
                self.fields['voltage'].widget = forms.HiddenInput()
        else:
            self.fields['voltage'].widget.attrs['style'] = 'display: none;'
    
    def clean(self):
        cleaned_data = super().clean()
        device_type = cleaned_data.get('type')
        voltage = cleaned_data.get('voltage')
        if device_type == DeviceTypes.energy and not voltage:
            self.add_error('voltage', 'Este campo é obrigatório para dispositivos de energia.')
        
        return cleaned_data