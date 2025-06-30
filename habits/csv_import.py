import csv
from datetime import date
from .models import Habit, HabitLog

def import_habits(user, file):
    text = file.read().decode('utf-8').splitlines()
    reader = csv.DictReader(text)

    for row in reader:
        name = row.get('habit_name', '').strip()
        if not name:
            continue

        # пытаемся получить или создать привычку
        try:
            habit, created = Habit.objects.get_or_create(
                user=user,
                name=name,
                defaults={
                    'category': row.get('category', '').strip(),
                    'description': row.get('description', '').strip(),
                }
            )
        except Habit.MultipleObjectsReturned:
            # если несколько дублей — берём первый
            habit = Habit.objects.filter(user=user, name=name).first()

        # обрабатываем поля date и completed, только если они есть
        date_str = row.get('date', '').strip()
        completed_str = row.get('completed', '').strip().lower()
        if date_str:
            try:
                log_date = date.fromisoformat(date_str)
            except ValueError:
                # невалидная дата — пропускаем строку
                continue

            completed = completed_str in ('1', 'true', 'on', 'yes')
            HabitLog.objects.update_or_create(
                habit=habit,
                date=log_date,
                defaults={'completed': completed, 'user': user}
            )