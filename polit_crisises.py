import pandas as pd

'''
Все пассажиры, прилетевшие за месяц до четырёх важных экономических или политических 
событий в соотвествующие города проведения этих событий - потенциальные шпионы
'''

df = pd.read_csv("../new_mgrd.csv", sep=';', dtype="string", keep_default_na=False)

df["DepartDate_dt"] = pd.to_datetime(df["DepartDate"], dayfirst=True, errors="coerce")

df["CityTo_norm"] = (
    df["CityTo"]
    .astype("string")
    .str.strip()
    .str.title()
)

events = [
    ("14.04.2017", "14.05.2017", "Beijing"), # 14-15 мая: Саммит «Один пояс — один путь» (Пекин, Китай)
    ("02.05.2017", "02.06.2017", "Saint Petersburg"), # 1-2 июня: Форум в Санкт-Петербурге (СПбМЭФ, Россия)
    ("30.10.2017", "30.11.2017", "Sochi"), # 30 ноября: Саммит СНГ (Сочи, Россия)
    ("21.07.2017", "21.08.2017", "Minsk"), # 21 августа - 26 сентября: Совместные учения России и Беларуси "Запад-2017"
]

mask = pd.Series(False, index=df.index)
for start, end, city in events:
    start_dt = pd.to_datetime(start, dayfirst=True)
    end_dt = pd.to_datetime(end, dayfirst=True)
    mask |= df["DepartDate_dt"].between(start_dt, end_dt, inclusive="both") & df["CityTo_norm"].eq(city)

dates_df = df.loc[mask].copy()
dates_df.drop(columns=["DepartDate_dt", "CityTo_norm"], inplace=True, errors="ignore")

dates_df.to_csv("political_crisises.csv", sep=";", index=False)
print(f"Записей:", len(dates_df))
