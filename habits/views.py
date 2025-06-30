import requests
import locale
from datetime import date, timedelta
from io import BytesIO
import base64

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import Habit, HabitLog
from .forms import CSVUploadForm, HabitForm
from .csv_import import import_habits

def get_motivational_quote():
    url = "https://zenquotes.io/api/random"
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        return r.json()[0]["q"]
    except:
        return "Не удалось загрузить цитату. Попробуйте позже."

@login_required
def dashboard(request):
    if request.method == "POST":
        if "delete_habit" in request.POST:
            Habit.objects.filter(
                id=request.POST["habit_id"],
                user=request.user
            ).delete()
            return redirect("dashboard")
        if "habit_id" in request.POST and "date" in request.POST:
            hid = int(request.POST["habit_id"])
            d = date.fromisoformat(request.POST["date"])
            completed = request.POST.get("completed") == "on"
            habit = Habit.objects.get(id=hid, user=request.user)
            logs = HabitLog.objects.filter(
                habit=habit,
                date=d,
                user=request.user
            )
            if completed:
                if logs.exists():
                    logs.update(completed=True)
                    if logs.count() > 1:
                        logs.exclude(pk=logs.first().pk).delete()
                else:
                    HabitLog.objects.create(
                        habit=habit,
                        date=d,
                        completed=True,
                        user=request.user
                    )
            else:
                logs.delete()
            return redirect("dashboard")

    habits = Habit.objects.filter(user=request.user)
    today = date.today()
    days = [today + timedelta(days=i) for i in range(-3, 4)]
    logs = HabitLog.objects.filter(
        habit__user=request.user,
        user=request.user,
        date__in=days,
        completed=True
    )
    records = {}
    for l in logs:
        records.setdefault(l.habit_id, set()).add(l.date)

    habit_rows = []
    for h in habits:
        entries = [{"date": d, "done": d in records.get(h.id, set())} for d in days]
        habit_rows.append({"habit": h, "entries": entries})

    return render(request, "dashboard.html", {
        "quote": get_motivational_quote(),
        "days": days,
        "habit_rows": habit_rows,
    })

@login_required
def upload_csv(request):
    if request.method == "POST":
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            import_habits(request.user, request.FILES["file"])
            return redirect("dashboard")
    else:
        form = CSVUploadForm()
    return render(request, "upload_csv.html", {"form": form})

@login_required
def add_habit(request):
    if request.method == "POST":
        form = HabitForm(request.POST)
        if form.is_valid():
            h = form.save(commit=False)
            h.user = request.user
            h.save()
            return redirect("dashboard")
    else:
        form = HabitForm()
    return render(request, "add_habit.html", {"form": form})

@login_required
def habit_analysis(request):
    today = date.today()
    dates = [today + timedelta(days=i) for i in range(-3, 4)]
    habits = Habit.objects.filter(user=request.user)
    data = {}
    rates = {}

    for habit in habits:
        logs = {
            log.date: log.completed
            for log in HabitLog.objects.filter(
                habit=habit,
                user=request.user,
                date__in=dates
            )
        }
        vals = [1 if logs.get(d, False) else 0 for d in dates]
        data[habit.name] = vals
        rates[habit.name] = np.mean(vals) * 100

    if not data:
        return render(request, "habit_analysis.html", {
            "message": "Нет данных для графика. Отметьте привычки на дашборде."
        })

    fig, ax = plt.subplots(figsize=(10, 6))
    for name, vals in data.items():
        ax.plot(dates, vals, marker="o", label=name)
    ax.set_title("Прогресс по привычкам")
    ax.set_xlabel("Дата")
    ax.set_ylabel("Выполнено (1) / Не выполнено (0)")
    ax.legend(loc="upper left")

    buf = BytesIO()
    fig.autofmt_xdate()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    graph_image = base64.b64encode(buf.read()).decode()

    return render(request, "habit_analysis.html", {
        "graph_image": graph_image,
        "dates": dates,
        "rates": rates,
    })