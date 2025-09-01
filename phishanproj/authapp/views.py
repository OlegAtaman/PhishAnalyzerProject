from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse

from authapp.forms import CustomUserCreationForm
from authapp.models import CustomUser


def login_user(request):
    print(request.user)
    user = None
    if request.method == 'POST':
        email=request.POST['email']
        password=request.POST['password']
        user=authenticate(request, email=email, password=password)
    
    if user is not None:
        login(request, user)
        return redirect('mainpage')
    else:
        pass

    return render(request, 'authapp/login.html')

def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('mainpage')

def register_user(request):
    print(request.user)
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            email = request.GET.get('email')
            password = form.cleaned_data['password1']
            user=authenticate(request, email=email, password=password)
            login(request, user)
        
        return redirect('mainpage')

    provided_email = request.GET.get('email')
    form = CustomUserCreationForm()
    return render(request, 'authapp/register.html', {'form':form, 'provided_email': provided_email})

def enter_email(request):
    if request.method == 'POST':
        return redirect('confirm_email')
    return render(request, 'authapp/emailsend.html')

def confirm_email(request):
    if request.method == 'POST':
        url = reverse('register_user')
        return redirect(url + '?email=' + request.POST['code'])
    return render(request, 'authapp/emailconfirm.html')

def profile_user(request, name):
    if not request.user.is_authenticated:
        return('Цей профіль приватний')

    user = CustomUser.objects.filter(username=name)

    if not user:
        return HttpResponse('Користувача не знайдено')
    
    if request.user != user[0]:
        return HttpResponse('Цей профіль приватний')
    
    user_scans = user[0].up_emails.all()

    return render(request, 'authapp/profile.html', {'emails':user_scans})