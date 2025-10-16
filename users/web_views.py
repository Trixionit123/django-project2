from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model


User = get_user_model()


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email', '')
        if not username or not password:
            messages.error(request, 'Введите логин и пароль')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь уже существует')
        else:
            user = User.objects.create_user(username=username, password=password, email=email)
            login(request, user)
            return redirect('home')
    return render(request, 'users/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        messages.error(request, 'Неверные учётные данные')
    return render(request, 'users/login.html')


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        user.email = request.POST.get('email', user.email)
        user.phone = request.POST.get('phone', getattr(user, 'phone', ''))
        user.address = request.POST.get('address', getattr(user, 'address', ''))
        user.save()
        messages.success(request, 'Профиль обновлён')
        return redirect('profile')
    return render(request, 'users/profile.html', {'user_obj': user})


