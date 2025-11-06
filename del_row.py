"""
del_row.py — удаление столбцов из датасета
"""

import pandas as pd


inp = "data/correct_csv.csv"
out = "data/csv_deleted.csv"
sep = ";"

# === список колонок, которые нужно удалить ===
cols_to_drop = ["Sex", "SecondName", "BirthDate", "literal"]

df = pd.read_csv(inp, sep=sep, dtype=str)
df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])
df.to_csv(out, sep=sep, index=False)

print(f"Удалено: {cols_to_drop} → результат в {out}")
