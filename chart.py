import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import rcParams

# Настройка стиля для русских шрифтов
rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

# Загрузка данных из CSV
df = pd.read_csv("document_collisions_detailed.csv", sep=";")

print("📊 АНАЛИЗ ДАННЫХ ИЗ ФАЙЛА:")
print(f"Всего записей: {len(df)}")
print(f"Колонки: {df.columns.tolist()}")
print(f"\nПервые 5 строк:")
print(df.head())

# Создаем фигуру с несколькими subplots
fig = plt.figure(figsize=(20, 15))
fig.suptitle('АНАЛИЗ КОЛЛИЗИЙ ДОКУМЕНТОВ ПАССАЖИРОВ', fontsize=16, fontweight='bold')

# 1. Распределение по типам коллизий (круговая диаграмма)
plt.subplot(2, 3, 1)
collision_counts = df['Collision_Type'].value_counts()
colors = ['#ff9999', '#66b3ff']
plt.pie(collision_counts.values, labels=collision_counts.index, autopct='%1.1f%%',
        colors=colors, startangle=90)
plt.title('Распределение по типам коллизий', fontweight='bold')

# 2. Размеры групп коллизий (столбчатая диаграмма)
plt.subplot(2, 3, 2)
group_size_distribution = df.groupby('Group_Size').size()
plt.bar(group_size_distribution.index, group_size_distribution.values, color='skyblue')
plt.xlabel('Размер группы')
plt.ylabel('Количество групп')
plt.title('Распределение по размеру групп', fontweight='bold')
plt.grid(axis='y', alpha=0.3)

# 3. Топ-10 самых частых документов с коллизиями
plt.subplot(2, 3, 3)
top_documents = df['Document_Value'].value_counts().head(10)
plt.barh(range(len(top_documents)), top_documents.values, color='lightcoral')
plt.yticks(range(len(top_documents)), top_documents.index)
plt.xlabel('Количество коллизий')
plt.title('Топ-10 документов с коллизиями', fontweight='bold')
plt.gca().invert_yaxis()

# 4. Количество коллизий по типам документов и размерам групп
plt.subplot(2, 3, 4)
pivot_data = df.pivot_table(index='Collision_Type', columns='Group_Size',
                           values='FirstName', aggfunc='count', fill_value=0)
sns.heatmap(pivot_data, annot=True, fmt='d', cmap='YlOrRd', cbar_kws={'label': 'Количество'})
plt.title('Коллизии по типам и размерам групп', fontweight='bold')
plt.ylabel('Тип коллизии')
plt.xlabel('Размер группы')

# 5. Распределение пассажиров по коллизиям (скatter plot)
plt.subplot(2, 3, 5)
# Создаем числовые значения для типов коллизий
df['Collision_Type_Num'] = df['Collision_Type'].map({'РОССИЙСКИЙ ДОКУМЕНТ': 0, 'МЕЖДУНАРОДНЫЙ ДОКУМЕНТ': 1})

# Случайные смещения для лучшей визуализации
import numpy as np
np.random.seed(42)
jitter = np.random.normal(0, 0.05, len(df))

plt.scatter(df['Collision_Type_Num'] + jitter, df['Group_Size'],
           alpha=0.6, c=df['Group_Size'], cmap='viridis', s=50)
plt.yticks(range(2, df['Group_Size'].max() + 1))
plt.xticks([0, 1], ['Российские', 'Международные'])
plt.xlabel('Тип документа')
plt.ylabel('Размер группы')
plt.title('Распределение коллизий', fontweight='bold')
plt.colorbar(label='Размер группы')

# 6. Кумулятивное распределение
plt.subplot(2, 3, 6)
cumulative_data = []
for group_size in sorted(df['Group_Size'].unique()):
    count = (df['Group_Size'] >= group_size).sum()
    cumulative_data.append((group_size, count))

cumulative_sizes, cumulative_counts = zip(*cumulative_data)
plt.plot(cumulative_sizes, cumulative_counts, marker='o', linewidth=2, markersize=6)
plt.xlabel('Минимальный размер группы')
plt.ylabel('Количество коллизий')
plt.title('Кумулятивное распределение', fontweight='bold')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('document_collisions_analysis.png', dpi=300, bbox_inches='tight')
plt.show()