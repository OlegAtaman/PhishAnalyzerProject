import os

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse

from authapp.forms import CustomUserCreationForm
from authapp.models import CustomUser, ConfirmationEmail
from authapp.utils import generate_code, get_client_ip
from authapp.postmanager import send_code
from authapp.security_check import count_login_attempt, set_zero_attempts, try_code
from phishanalyzer.tasks import delete_confirmation


def login_user(request):
    user = None
    if request.method == 'POST':
        email=request.POST['email']
        password=request.POST['password']
        user_ip = get_client_ip(request)
        result, exp = count_login_attempt(email, user_ip)
        if result == True:
            user=authenticate(request, email=email, password=password)
        else:
            messages.error(request, exp)
            return redirect('login_user')
    
        if user is not None:
            login(request, user)
            set_zero_attempts(email)
            return redirect('mainpage')
        else:
            messages.error(request, "! Incorrect credentials")
            return redirect('login_user')
    
    return render(request, 'authapp/login.html')

def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('mainpage')

def register_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        email = request.GET.get('email')
        old_user = CustomUser.objects.filter(email=email)
        if old_user:
            messages.error(request, '! This email has been taken')
            return redirect(reverse('register_user') + '?email=' + email)
        
        if form.is_valid():
            form.save()
            if not email:
                messages.error(request, '! No email provided')
                return redirect(reverse('register_user') + '?email=' + email)

            password = form.cleaned_data['password1']
            user=authenticate(request, email=email, password=password)
            login(request, user)
        else:
            messages.error(request, "! Please, fix errors below")
            return render(request, 'authapp/register.html', {
                    'form': form,
                    'provided_email': email
                })

        return redirect('mainpage')

    provided_email = request.GET.get('email')
    form = CustomUserCreationForm()
    return render(request, 'authapp/register.html', {'form':form, 'provided_email': provided_email})

def enter_email(request):
    if request.method == 'POST':
        try:
            random_code = generate_code()
            mail_to_confirm = ConfirmationEmail(email=request.POST.get('email'), code=random_code)
            mail_to_confirm.save()
            delete_confirmation.apply_async(args=[mail_to_confirm.id], countdown=15 * 60)
        except Exception as exc:
            messages.error(request, "! This email is already taken")
            return redirect('enter_email')
        url = reverse('confirm_email')
        mini_url = url + '?email=' + request.POST['email']
        send_code(mail_to_confirm.email,
                  mail_to_confirm.code,
                  'phishanalyzer.dev@gmail.com',
                  os.getenv('GOOGLEE_APP_PASSWORD'),
                  mini_url)
        return redirect(mini_url)
    return render(request, 'authapp/emailsend.html')

def confirm_email(request):
    ctx = {}
    email = request.GET.get('email')
    code = request.GET.get('code')
    # if code:
    #     ctx.update({'code':code})

    if not email:
        return HttpResponse('Access denied')

    if request.method == 'POST':
        email_obj = ConfirmationEmail.objects.filter(email=email)
        if not email_obj:
            return HttpResponse('Email was not provided')
        email_obj = email_obj[0]

        try:
            sub_code = int(request.POST.get('code'))
        except:
            messages.error(request, '! Invalid format')
            return redirect(f"{reverse('confirm_email')}?email={email}")

        result, message = try_code(sub_code, email_obj)

        if result == True:
            email_obj.is_verified = True
            email_obj.save()
            url = reverse('register_user')
            return redirect(url + '?email=' + email)
        else:
            messages.error(request, message)
            return redirect(f"{reverse('confirm_email')}?email={email}")

    return render(request, 'authapp/emailconfirm.html', ctx)

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