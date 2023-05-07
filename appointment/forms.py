from django import forms
from .models import Appointment
from .models import Doctor


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'start_time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
        }

class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ('name', 'speciality', 'clinic_address', 'profile_picture',)

    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    speciality = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    clinic_address = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    profile_picture = forms.ImageField(required=False)