from django.db import models
from auth_app.models import User


class Doctor(models.Model):
    name = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to='profiles/')
    speciality = models.CharField(max_length=100)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Appointment(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)

    # def __str__(self):
    #     return f"{self.doctor} - {self.date} {self.start_time}"