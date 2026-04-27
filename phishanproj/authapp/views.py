import os

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse

from authapp.forms import CustomUserCreationForm
from authapp.models import CustomUser, ConfirmationEmail
from authapp.utils import generate_code
from authapp.postmanager import send_code


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

        email = request.GET.get('email')
        email_obj = CustomUser.objects.filter(email=email)
        if email_obj:
            return HttpResponse('The email has been taken')
        
        if form.is_valid():
            form.save()
            if not email:
                return HttpResponse('No email provided')

            password = form.cleaned_data['password1']
            user=authenticate(request, email=email, password=password)
            login(request, user)
        
        return redirect('mainpage')

    provided_email = request.GET.get('email')
    form = CustomUserCreationForm()
    return render(request, 'authapp/register.html', {'form':form, 'provided_email': provided_email})

def enter_email(request):
    if request.method == 'POST':
        try:
            mail_to_confirm = ConfirmationEmail(email=request.POST.get('email'), code=generate_code())
            mail_to_confirm.save()
        except:
            return HttpResponse('This email has been taken')
        url = reverse('confirm_email')
        completed_url = url + '?email=' + request.POST['email']
        send_code(mail_to_confirm.email,
                  mail_to_confirm.code,
                  'test.phish.analyzer@gmail.com',
                  os.getenv('GOOGLEE_APP_PASSWORD'),
                  completed_url)
        return redirect(completed_url)
    return render(request, 'authapp/emailsend.html')

def confirm_email(request):
    email = request.GET.get('email')
    if not email:
        return HttpResponse('Access denied')

    if request.method == 'POST':
        email_obj = ConfirmationEmail.objects.filter(email=email)
        if not email_obj:
            return HttpResponse('Email was not provided')
        email_obj = email_obj[0]

        sub_code = int(request.POST.get('code'))
        real_code = email_obj.code

        if sub_code == real_code:
            email_obj.is_verified = True
            email_obj.save()
            url = reverse('register_user')
            return redirect(url + '?email=' + email)
        else:
            return redirect('enter_email')

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