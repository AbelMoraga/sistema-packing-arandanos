from django import forms
from .models import Pallet

class PalletForm(forms.ModelForm):
    class Meta:
        model = Pallet
        fields = ['productor', 'variedad', 'tipo_envase', 'cantidad_cajas', 'peso_neto']
        widgets = {
            'productor': forms.Select(attrs={'class': 'form-control'}),
            'variedad': forms.Select(attrs={'class': 'form-control'}),
            'tipo_envase': forms.Select(attrs={'class': 'form-control'}),
            'cantidad_cajas': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cantidad de cajas'}),
            'peso_neto': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Peso neto (kg)'}),
        }
