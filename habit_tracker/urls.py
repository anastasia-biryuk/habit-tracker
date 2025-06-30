from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),  # Добавляем маршруты пользователей
    path('', include('habits.urls')),
]