from django import forms
from .models import Habit

class HabitForm(forms.ModelForm):
    class Meta:
        model = Habit
        fields = ['name', 'category', 'description']
        labels = {
            'name': 'Привычка:',  # Изменим название поля на "Привычка"
            'category': 'Категория:',  # Оставляем название как есть
            'description': 'Описание:',  # Оставляем название как есть
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class CSVUploadForm(forms.Form):
    file = forms.FileField()