import pandas as pd
from tqdm import tqdm
import os

df = pd.read_csv("new_mgrd.csv", sep=";", low_memory=False)

loyalty_columns = [
    'LoyaltyNumberDT', 'LoyaltyNumberFB',
    'LoyaltyNumberKE', 'LoyaltyNumberSU'
]

existing_loyalty_cols = [col for col in loyalty_columns if col in df.columns]
print(f"Используются столбцы лояльности: {existing_loyalty_cols}")

all_loyalty_values = set()
for col in existing_loyalty_cols:
    if col in df.columns:
        all_loyalty_values.update(df[col].dropna().astype(str).unique())

print(f"Всего уникальных значений в столбцах лояльности: {len(all_loyalty_values)}")


condition1 = df['CardNumber'].notna()


condition2 = ~df['CardNumber'].astype(str).isin(all_loyalty_values)


condition3 = df[existing_loyalty_cols].notna().any(axis=1)


mask = condition1 & condition2 & condition3
mismatch_rows = df[mask]

result_columns = ['FirstName', 'LastName', 'CardNumber'] + existing_loyalty_cols
names_info = mismatch_rows[result_columns]

print(names_info.head(10))


names_info.to_csv("mismatch_names_.csv", index=False, sep=';')