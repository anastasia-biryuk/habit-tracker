from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required

def register_user(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # После успешной регистрации автоматически авторизуем пользователя
            user = form.save()
            login(request, user)
            return redirect('dashboard')  # Перенаправляем на главную страницу
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)  # Проверка пользователя
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Перенаправляем на главную страницу
        else:
            return render(request, 'login.html', {'error': 'Неверный логин или пароль'})
    return render(request, 'login.html')

@login_required
def logout_user(request):
    logout(request)
    return redirect('login')  # После выхода перенаправляем на страницу логина