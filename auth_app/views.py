from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import SignupForm
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    user = request.user
    if user.user_type == 'patient':
        request.session['user_role'] = 'Patient'
        details = user
        user_type = 'Patient'
    elif user.user_type == 'doctor':
        request.session['user_role'] = 'Doctor'
        details = user
        user_type = 'Doctor'
    else:
        details = None
        user_type = None

    if request.method == 'POST' and 'logout' in request.POST:
        logout(request)
        return redirect('login_process')

    return render(request, 'dashboard.html', {
        'user_type': user_type,
        'details': details,
    })

def logout_process(request):
    logout(request)
    return redirect('login_process')

def signup_process(request):
    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            if 'profile_picture' in request.FILES:
                form.instance.profile_picture = request.FILES['profile_picture']
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})

def login_process(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')