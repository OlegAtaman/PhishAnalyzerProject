from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from authapp.forms import CustomUserCreationForm


def login_user(request):
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
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            user=authenticate(request, email=email, password=password)
            login(request, user)
        
        return redirect('mainpage')

    form = CustomUserCreationForm()
    return render(request, 'authapp/register.html', {'form':form})
