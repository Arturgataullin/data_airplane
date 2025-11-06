#считает в датесете количество Elite/Elite+ уровней привилегий для людей в датасете
#строит график количество людей/количество Elite/Elite+ программ

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('new_mgrd.csv', sep=';', low_memory=False)

loyalty_columns = [
    'LoyaltyLevelDT', 'LoyaltyLevelFB', 'LoyaltyLevelKE', 'LoyaltyLevelSU'
]

def has_elite_level(level):
    if pd.isna(level) or level == "":
        return False
    return 'ELITE' in str(level).upper()

results = []

for _, row in df.iterrows():
    total_programs = 0
    elite_programs = 0
    
    for col in loyalty_columns:
        if col in df.columns and not pd.isna(row[col]) and row[col] != "":
            total_programs += 1
            if has_elite_level(row[col]):
                elite_programs += 1
    
    if total_programs > 0 and elite_programs >= total_programs / 2:
        results.append({
            'FirstName': row['FirstName'],
            'LastName': row['LastName'],
            'TotalPrograms': total_programs,
            'ElitePrograms': elite_programs,
            'ElitePercentage': (elite_programs / total_programs) * 100
        })


result_df = pd.DataFrame(results)
result_df = result_df.sort_values('ElitePrograms', ascending=False)


result_df.to_csv('loyal_level_check_result.csv', sep=';', index=False)



plt.figure(figsize=(10, 6))
sns.histplot(data=result_df, x='ElitePrograms', bins=range(0, 5), discrete=True)
plt.title('Распределение людей по количеству Elite программ')
plt.xlabel('Количество Elite программ')
plt.ylabel('Количество людей')
plt.xticks(range(0, 5))
plt.grid(axis='y', alpha=0.3)
plt.show()