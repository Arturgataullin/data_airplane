import pandas as pd

'''
добавляем каждому, у кого есть код аэропорта, навзание
страны и города
'''

FILE_MAIN = "merged_arch_freq_xml.csv" # файл с билетами
FILE_REF = "Skyteam_Timetable.csv" # файл с расписанием
OUT_FILE = "arch_freq_xml_geo.csv"
SEP = ";" # разделитель

df = pd.read_csv(FILE_MAIN, sep=SEP, dtype="string")
ref = pd.read_csv(FILE_REF,  sep=SEP, dtype="string")

ref_from = (ref.dropna(subset=["CODE_FROM"]).drop_duplicates(subset=["CODE_FROM"], keep="first")) # удаляем дубликаты
ref_to = (ref.dropna(subset=["CODE_TO"]).drop_duplicates(subset=["CODE_TO"], keep="first"))

city_from_map = ref_from.set_index("CODE_FROM")["CITY_FROM"] if "CITY_FROM" in ref_from.columns else None # словари код -> город/страна
country_from_map = ref_from.set_index("CODE_FROM")["COUNTRY_FROM"] if "COUNTRY_FROM" in ref_from.columns else None
city_to_map = ref_to.set_index("CODE_TO")["CITY_TO"] if "CITY_TO" in ref_to.columns else None
country_to_map = ref_to.set_index("CODE_TO")["COUNTRY_TO"] if "COUNTRY_TO" in ref_to.columns else None


if city_to_map is not None: # заполняем куда по Dest
    df["CityTo"] = df["CityTo"].combine_first(df["Dest"].map(city_to_map))
if country_to_map is not None:
    df["CountryTo"] = df["CountryTo"].combine_first(df["Dest"].map(country_to_map))

if "From" in df.columns and city_from_map is not None: # заполняем откуда по From
    df["CityFrom"] = df["CityFrom"].combine_first(df["From"].map(city_from_map))
if "From" in df.columns and country_from_map is not None:
    df["CountryFrom"] = df["CountryFrom"].combine_first(df["From"].map(country_from_map))

for col in ["CityFrom", "CountryFrom", "CityTo", "CountryTo"]:
    if col in df.columns:
        df[col] = (
            df[col]
            .astype("string")
            .str.strip()
            .str.upper()
        )

df.to_csv(OUT_FILE, sep=SEP, index=False)
print("Готово")
