from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from django.shortcuts import render, redirect, get_object_or_404
from social_core.backends.google import GoogleOAuth2
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Appointment
from .forms import AppointmentForm, DoctorForm
from .models import Doctor
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from .models import Appointment
import datetime
from datetime import timedelta
from social_django.models import UserSocialAuth
from django.conf import settings
from social_django.utils import get_strategy
from social_django.models import DjangoStorage
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from social_django.utils import load_strategy
from social_django.models import UserSocialAuth
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google_auth_oauthlib.flow import Flow

# from social_core.backends.utils import load_backend

from social_django.utils import load_strategy, load_backend

# from social_core.backends.google import GoogleOAuth2
# from social_core.backends.utils import load_backend

# from blog_project import settings

# from .credentials import get_credential

# from django.conf import settings
# SOCIALACCOUNT_PROVIDERS = getattr(settings, 'SOCIALACCOUNT_PROVIDERS')


@login_required
def doctor_list(request):
    doctors = Doctor.objects.all()
    return render(request, 'appointment/doctor_list.html', {'doctors': doctors})

def can_add_doctor(request):
    if request.user.is_authenticated and request.user.user_type == 'doctor':
        # check if the user has already signed up as a doctor
        if not Doctor.objects.filter(user=request.user).exists():
            return True
        else:
            return False
    else:
        return False
    

@login_required
def add_doctor(request):

    # Check if the user is a doctor
    if not request.user.groups.filter(name='doctor').exists():
        return HttpResponseForbidden("You do not have permission to access this page.")

    # Check if the doctor has already signed up
    if Doctor.objects.filter(user=request.user).exists():
        return HttpResponseBadRequest("You have already signed up as a doctor.")

    if request.method == 'POST':
        form = DoctorForm(request.POST, request.FILES)
        if form.is_valid():
            # Check if a Doctor object already exists for the current user
            if hasattr(request.user, 'doctor'):
                messages.warning(request, 'You have already registered as a doctor.')
                return redirect('appointment:doctor_list')

            doctor = form.save(commit=False)
            doctor.user = request.user
            doctor.save()
            messages.success(request, 'Doctor added successfully!')
            return redirect('appointment:doctor_list')
    else:
        form = DoctorForm()
    return render(request, 'appointment/add_doctor.html', {'form': form})



@login_required
def book_appointment(request, doctor_id):
    # get doctor instance by doctor_id
    doctor = get_object_or_404(Doctor, id=doctor_id)

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            patient = request.user
            # speciality = form.cleaned_data['speciality']
            start_time = datetime.datetime.combine(form.cleaned_data['date'], form.cleaned_data['start_time'])

            # calculate end time
            end_time = start_time + datetime.timedelta(minutes=45)
            
            flow = Flow.from_client_config(
                client_config={
                    "client_id": settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
                    "client_secret": settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
                    "redirect_uri": "http://127.0.0.1:8000/social-auth/complete/google-oauth2/",
                    "scope": ["https://www.googleapis.com/auth/calendar"],
                },
                scopes=["https://www.googleapis.com/auth/calendar"],
            )
            auth_code = request.GET.get('code')

            # Exchange the authorization code for credentials
            creds = flow.fetch_token(code=auth_code)

            
            # Check if the credentials have expired and refresh them if necessary
            if not creds.valid:
                if creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    raise Exception('Google credentials are invalid')

            # Build the credentials info dictionary
            creds_info = {
                'token': creds.token,
                'refresh_token': creds.refresh_token,
                'token_uri': creds.token_uri,
                'client_id': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
                'client_secret': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
                'scopes': ['https://www.googleapis.com/auth/calendar']
            }
            creds = Credentials.from_authorized_user_info(info=creds_info)
            access_token = creds.token

            # Refresh the access token if it has expired
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())

            # Use the credentials object for API calls
            # Example: Get the user's Google Calendar events
            from googleapiclient.discovery import build
            service = build('calendar', 'v3', credentials=creds)
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            access_token = credentials.token
            service = build('calendar', 'v3', credentials=credentials)

            # create calendar event
            event = {
                'summary': 'Appointment with Dr. {} - {}'.format(doctor.user.first_name, speciality),
                'location': doctor.clinic_address,
                'description': 'Appointment with Dr. {} - {}'.format(doctor.user.first_name, speciality),
                'start': {
                    'dateTime': dateutil.parser.parse(str(date.date()) + ' ' + str(start_time)).strftime('%Y-%m-%dT%H:%M:%S'),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': dateutil.parser.parse(str(date.date()) + ' ' + str(end_time)).strftime('%Y-%m-%dT%H:%M:%S'),
                    'timeZone': 'UTC',
                },
                'reminders': {
                    'useDefault': True,
                },
            }
            event = service.events().insert(calendarId='primary', body=event).execute()

            # create appointment object
            appointment = Appointment.objects.create(
                doctor=doctor,
                patient=patient,
                # speciality=speciality,
                date=date,
                start_time=start_time,
                end_time=end_time,
                # google_event_id=event['id'],
            )

            # redirect to appointment details page
            return render(request, 'appointment/patients_appointments.html', {'appointments': appointments})
    else:
        form = AppointmentForm()

    return render(request, 'appointment/book_appointment.html', {'doctor': doctor, 'form': form})


@login_required
def doctor_appointments(request):
    appointments = Appointment.objects.filter(doctor=request.user.doctor)
    return render(request, 'appointment/doctor_appointments.html', {'appointments': appointments})

@login_required
def patient_appointments(request):
    appointments = Appointment.objects.filter(patient=request.user)
    return render(request, 'appointment/patients_appointments.html', {'appointments': appointments})



#     from google.oauth2.credentials import Credentials
# from googleapiclient.errors import HttpError
# from googleapiclient.discovery import build
# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from django.utils import timezone
# from .models import Appointment
# from .forms import AppointmentForm
# from .credentials import get_credentials

# @login_required
# def appointment_new(request):
#     if request.method == "POST":
#         form = AppointmentForm(request.POST)
#         if form.is_valid():
#             appointment = form.save(commit=False)
#             appointment.patient = request.user.patient
#             appointment.save()
#             messages.success(request, 'Appointment booked successfully!')

#             # Create an event in Google Calendar
#             try:
#                 credentials = get_credentials(request.user)
#                 service = build('calendar', 'v3', credentials=credentials)
#                 event = {
#                     'summary': 'Appointment with Dr. ' + appointment.doctor.user.get_full_name(),
#                     'location': appointment.doctor.office_address,
#                     'description': appointment.reason_for_visit,
#                     'start': {
#                         'dateTime': timezone.localtime(appointment.start_time).isoformat(),
#                         'timeZone': timezone.get_current_timezone().zone,
#                     },
#                     'end': {
#                         'dateTime': timezone.localtime(appointment.start_time + timezone.timedelta(minutes=45)).isoformat(),
#                         'timeZone': timezone.get_current_timezone().zone,
#                     },
# #                 }
#                 calendar_id = 'primary'  # Default calendar for the authenticated user
#                 event = service.events().insert(calendarId=calendar_id, body=event).execute()
#                 print(f"Event created: {event.get('htmlLink')}")
#             except HttpError as error:
#                 print(f"An error occurred: {error}")
#                 messages.warning(request, 'Could not create calendar event')

#             return redirect('appointment_list')
#     else:
#         form = AppointmentForm()
#     return render(request, 'appointment_new.html', {'form': form})
# Get the google oauth2 credentials for the patient
            # storage = DjangoStorage()
            # strategy = load_strategy(request)
            # backend = load_backend(strategy, 'oauth2', redirect_uri=None)
            # access_token = backend.get_access_token(storage)

            # creds_info = {
            #     'token': access_token,
            #     'refresh_token': storage.user.get_social_auth(provider='google-oauth2').extra_data['refresh_token'],
            #     'token_uri': GoogleOAuth2.token_url,
            #     'client_id': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
            #     'client_secret': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
            #     'scopes': ['https://www.googleapis.com/auth/calendar']
            # }
            # credentials = Credentials.from_authorized_user_info(info=creds_info)

            # storage = DjangoStorage()
            # access_token = storage.user.get_social_auth(provider='google-oauth2').access_token

            # creds_info = {
            #     'token': access_token,
            #     'token_uri': GoogleOAuth2.token_url,
            #     'client_id': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
            #     'client_secret': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
            #     'scopes': ['https://www.googleapis.com/auth/calendar']
            # }

            # credentials = Credentials.from_authorized_user_info(info=creds_info)


            # storage = DjangoStorage()
            # strategy = load_strategy(request)
            # backend = load_backend(strategy, 'google-oauth2', redirect_uri=None)
            # # access_token = backend.get_access_token(storage)

            # # Get the user's refresh token
            # social_auth = request.user.social_auth.get(provider='google-oauth2')
            # creds = Credentials.from_authorized_user_info(info=social_auth.extra_data)



            # @login_required
# def book_appointment(request, doctor_id):
#     doctor = Doctor.objects.get(pk=doctor_id)
    
#     if request.method == 'POST':
#         form = AppointmentForm(request.POST)
#         if form.is_valid():
#             appointment = form.save(commit=False)
#             appointment.patient = request.user
#             appointment.doctor = doctor
#             appointment.end_time = (datetime.combine(datetime.min, appointment.start_time) + timedelta(minutes=45)).time()
#             appointment.save()

#             # create a calendar event
#             try:
#                 # credentials = Credentials.from_authorized_user_info(request.user.social_auth.get(provider='google-oauth2').extra_data['access_token'])
#                 # extra_data = request.user.social_auth.get(provider='google-oauth2').extra_data
#                 # print(type(extra_data), extra_data)
#                 # credentials = Credentials.from_authorized_user_info(extra_data['access_token'])
#                 # print(credentials)
#                 # extra_data = request.user.social_auth.get(provider='google-oauth2').extra_data
#                 # credentials = Credentials.from_authorized_user_info(
#                 #    
#                 # )
#                 # extra_data = request.user.social_auth.get(provider='google-oauth2').extra_data
#                 # creds_info = {
#                 #     'client_id': SOCIALACCOUNT_PROVIDERS['google']['APP']['client_id'],
#                 #     'client_secret': SOCIALACCOUNT_PROVIDERS['google']['APP']['secret'],
#                 #     'refresh_token': extra_data['refresh_token'],
#                 #     'token_uri': 'https://oauth2.googleapis.com/token',
#                 #     'scopes': ['https://www.googleapis.com/auth/calendar'],
#                 # }

#                 # extra_data = request.user.social_auth.get(provider='google-oauth2').extra_data
#                 # refresh_token = extra_data.get('refresh_token')
                
#                 # creds_info = {
#                 # 'client_id': SOCIALACCOUNT_PROVIDERS['google']['APP']['client_id'],
#                 # 'client_secret': SOCIALACCOUNT_PROVIDERS['google']['APP']['secret'],
#                 # 'refresh_token': refresh_token,
#                 # 'token_uri': 'https://oauth2.googleapis.com/token',
#                 # 'scopes': ['https://www.googleapis.com/auth/calendar'],
#                 # }
#                 # credentials = Credentials.from_authorized_user_info(info=creds_info)
               
#                     # # Redirect the user to the authentication URL with access_type=offline parameter
#                     # storage = DjangoStorage()
#                     # strategy = get_strategy('google-oauth2', storage=storage)
#                     # auth_url = strategy.get_authorization_url(
#                     #     {'access_type': 'offline', 'prompt': 'select_account'}
#                     # )
#                     # return redirect(auth_url)

#                 user_social_auth = UserSocialAuth.objects.get(provider='google-oauth2', user=request.user)
#                 strategy = load_strategy(request)
#                 backend = strategy.get_backend()
#                 access_token = user_social_auth.get_access_token(backend)
#                 # create credentials object
#                 credentials = Credentials.from_authorized_user_info(user_social_auth.extra_data)
                
#                 service = build('calendar', 'v3', credentials=credentials)
#                 start = datetime.combine(appointment.date, appointment.start_time).isoformat()
#                 end = datetime.combine(appointment.date, appointment.end_time).isoformat()
#                 event = {
#                     'summary': f"Appointment with {doctor.name}",
#                     'location': f"{doctor.speciality}",
#                     'description': f"Booked by {request.user.username}",
#                     'start': {
#                         'dateTime': start,
#                         'timeZone': 'Asia/Kolkata',
#                     },
#                     'end': {
#                         'dateTime': end,
#                         'timeZone': 'Asia/Kolkata',
#                     },
#                 }
#                 try:
#                     event = service.events().insert(calendarId='primary', body=event).execute()
#                 except HttpError as error:
#                     print(f'An error occurred: {error}')
#                     messages.error(request, 'An error occurred while booking the appointment. Please try again later.')

#                 messages.success(request, 'Your appointment has been booked successfully!')
#                 return redirect('appointment:doctor_list')
#             except UserSocialAuth.DoesNotExist:
#                 messages.warning(request, 'You have not authorized the app to access your Google Calendar. Please authorize the app to continue.')
#                 return redirect('social:begin', 'google-oauth2')


#     else:
#         form = AppointmentForm()
#     return render(request, 'appointment/book_appointment.html', {'form': form, 'doctor': doctor})