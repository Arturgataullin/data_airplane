"""
plots.py -- визуализация анализа, произведенного с помощью home_airports.py
"""

import pandas as pd
import matplotlib.pyplot as plt

# === настройки ===
FILE = "input.csv"
SEP = ";"

df = pd.read_csv(FILE, sep=SEP)

df = df.dropna(subset=["n_unique_from", "top1_ratio"])
df["n_unique_from"] = df["n_unique_from"].astype(int)
df["top1_ratio"] = df["top1_ratio"].astype(float)

# === график 1: распределение количества уникальных аэропортов ===
plt.figure(figsize=(8,5))
plt.hist(df["n_unique_from"], bins=range(1, df["n_unique_from"].max()+2), edgecolor="black")
plt.title("Распределение количества уникальных аэропортов вылета", fontsize=13)
plt.xlabel("Количество уникальных аэропортов (From)")
plt.ylabel("Количество пассажиров")
plt.grid(alpha=0.4)
plt.tight_layout()
plt.show()

# === график 2: распределение доли самого частого аэропорта ===
plt.figure(figsize=(8,5))
plt.hist(df["top1_ratio"], bins=30, color="lightblue", edgecolor="black")
plt.title("Распределение доли полётов из самого частого аэропорта", fontsize=13)
plt.xlabel("Доля полётов из топ-1 аэропорта (top1_ratio)")
plt.ylabel("Количество пассажиров")
plt.grid(alpha=0.4)
plt.tight_layout()
plt.show()

# === график 3: диаграмма рассеяния с выделением подозрительных ===
plt.figure(figsize=(8,6))
normal = df[df["no_home_airport"] == False]
suspect = df[df["no_home_airport"] == True]

plt.scatter(normal["n_unique_from"], normal["top1_ratio"],
            s=20, c="gray", alpha=0.5, label="Обычные пассажиры")
plt.scatter(suspect["n_unique_from"], suspect["top1_ratio"],
            s=40, c="red", alpha=0.7, label="Нет домашнего аэропорта")

plt.title("Гипотеза: отсутствие «домашнего» аэропорта", fontsize=13)
plt.xlabel("Количество уникальных аэропортов (From)")
plt.ylabel("Доля полётов из самого частого аэропорта (top1_ratio)")
plt.legend()
plt.grid(alpha=0.4)
plt.tight_layout()
plt.show()
