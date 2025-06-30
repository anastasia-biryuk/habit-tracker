import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_data(habit, logs):
    dates = [log.date for log in logs]
    values = [1 if log.completed else 0 for log in logs]
    if not values:
        return None
    avg = np.mean(values)
    trend = np.polyfit(range(len(values)), values, 1)[0]
    window = 5 if len(values) >= 5 else 2
    mov_avg = np.convolve(values, np.ones(window)/window, mode='valid')
    plt.figure(figsize=(10,4))
    sns.lineplot(x=range(len(values)), y=values)
    sns.lineplot(x=range(window-1, len(values)), y=mov_avg)
    plt.title(f'{habit.name}: тренд={trend:.2f}, среднее={avg:.2f}')
    path = f'static/plot_{habit.id}.png'
    plt.savefig(path)
    plt.close()
    return f'/{path}'