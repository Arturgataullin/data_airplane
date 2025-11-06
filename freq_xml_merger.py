#cлияние данных из xml и freq файла, в результирующем датасете все колонки из xml и freq

import pandas as pd
import numpy as np
from pathlib import Path

FILE_TAB = "new_frequent_flyer_forum.csv"
FILE_CSV = "new_xml_correct_data.csv"
OUT_FILE = "merged_freq_xml.csv"
SEP = ";"   
NA_VALUES = ["N/A", "NA", "", " ", "N\\A", "None"]

def read_clean(path):
    df = pd.read_csv(path, sep=SEP, dtype="string", keep_default_na=False)
    df = df.replace(NA_VALUES, pd.NA)

    for c in df.columns:
        if pd.api.types.is_string_dtype(df[c]):
            df[c] = df[c].str.strip()
            df[c] = df[c].str.replace(r"\s{2,}", " ", regex=True)
    
    for c in ["FirstName", "LastName", "From", "Dest", "FlightNumber"]:
        if c in df.columns and pd.api.types.is_string_dtype(df[c]):
            df[c] = df[c].str.upper()
    
    return df

df_tab = read_clean(FILE_TAB)
df_csv = read_clean(FILE_CSV)

print(f"Таблица 1: {len(df_tab)} строк, колонки: {list(df_tab.columns)}")
print(f"Таблица 2: {len(df_csv)} строк, колонки: {list(df_csv.columns)}")

merged = pd.merge(
    df_tab, 
    df_csv, 
    on=["FirstName", "LastName", "From", "Dest", "FlightNumber"], 
    how="outer", 
    suffixes=("_tab", "_csv")
)

final_data = {}

for col in ["FirstName", "LastName", "From", "Dest", "FlightNumber"]:
    final_data[col] = merged[col]

for col in merged.columns:
    if col in ["FirstName", "LastName", "From", "Dest", "FlightNumber"]:
        continue 
    
    if col.endswith('_tab') or col.endswith('_csv'):
        base_col = col[:-4]  #убираю _tab или _csv
        suffix = col[-3:]    #получаю _tab или _csv
        
        if base_col not in final_data:
            other_suffix = "_csv" if suffix == "_tab" else "_tab"
            other_col = base_col + other_suffix
            
            if other_col in merged.columns:
                final_data[base_col] = merged[col].combine_first(merged[other_col])
            else:
                final_data[base_col] = merged[col]
    else:
        final_data[col] = merged[col]

out = pd.DataFrame(final_data)

for col in df_tab.columns:
    if col not in out.columns and col not in ["FirstName", "LastName", "From", "Dest", "FlightNumber"]:
        col_tab = col + "_tab"
        if col_tab in merged.columns:
            out[col] = merged[col_tab]
        else:
            out[col] = ""

for col in df_csv.columns:
    if col not in out.columns and col not in ["FirstName", "LastName", "From", "Dest", "FlightNumber"]:
        col_csv = col + "_csv"
        if col_csv in merged.columns:
            out[col] = merged[col_csv]
        else:
            out[col] = ""

preferred_order = [
    "FirstName", "LastName", "From", "Dest", "FlightNumber", 
    "Fare", "Bonus", "Class", "DepartDate", 
    "CardNumber", "UID", "Sex", "Codeshare",
    "CityFrom", "CityTo", "CountryFrom", "CountryTo",
    "LoyaltyLevelSU", "LoyaltyNumberSU", "LoyaltyLevelDT", "LoyaltyNumberDT",
    "LoyaltyLevelKE", "LoyaltyNumberKE", "LoyaltyLevelFB", "LoyaltyNumberFB"
]

final_order = [col for col in preferred_order if col in out.columns] + \
              [col for col in out.columns if col not in preferred_order]

out = out[final_order]

out = out.fillna("")

out.to_csv(OUT_FILE, sep=SEP, index=False)
