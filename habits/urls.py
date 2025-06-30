from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('import/', views.upload_csv, name='upload_csv'),
    path('add/',    views.add_habit,    name='add_habit'),
    path('analysis/', views.habit_analysis, name='habit_analysis'),
]