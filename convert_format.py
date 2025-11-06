import pandas as pd
from tqdm import tqdm
import os

def find_value_position_optimized(df, value):
    for col in df.columns:
        mask = df[col] == value
        if mask.any():
            idx = df.index[mask][0]  # берем первый найденный индекс
            return [(idx, col)]
    return []



def change(df_data: pd.DataFrame, df_name: pd.DataFrame, column: str, index: int, file)->tuple:
    name = df_data.loc[index, column]
    positions = find_value_position_optimized(df_name, name)
    if positions:
        df_data.loc[index, column] = df_name.loc[positions[0][0], "Standart"]
        return True, name
    else:
        file.write(name + "\n")
        return False, name





if __name__ == "__main__":
    folder_path = 'data'
    name_column1 = "FirstName"
    name_column2 = "LastName"
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    df_names = pd.read_csv("info (2).csv", sep=";")
    df_surnames = pd.read_csv("huila (2).csv", sep=";")

    with open("unknow_names.txt", "w", encoding="utf-8") as unknow_names, \
         open("unknow_surnames.txt", "w", encoding="utf-8") as unknow_surnames:

        for file in files:
            print(f"Обработка файла: {file}")
            flag = file != "result_archive.csv"
            df_data = pd.read_csv(f"{folder_path}/{file}", sep=';')
            otsos_name_set = set()
            otsos_surname_set = set()
            for i in tqdm(range(len(df_data)), desc="Обработка данных"):
                if flag:
                    change(df_data, df_names, name_column1, i, unknow_names)
                    change(df_data, df_surnames, name_column2, i, unknow_surnames)
                    continue
                change_name = change(df_data, df_names, name_column1, i, unknow_names)
                if change_name[0]:
                    check_lastname = change(df_data, df_surnames, name_column2, i, unknow_surnames)
                    if not(check_lastname[0]):
                        surname_success = change(df_data, df_surnames, name_column1, i, unknow_surnames)
                        name_success = change(df_data, df_names, name_column2, i, unknow_names)
                        if not(surname_success and name_success):
                            otsos_name_set.add(df_data.loc[i, name_column1])
                            otsos_surname_set.add(df_data.loc[i, name_column2])
                    continue
                check_lastname = change(df_data, df_surnames, name_column1, i, unknow_surnames)
                if check_lastname[0]:
                    change_name = change(df_data, df_names, name_column2, i, unknow_names)
                    if not(change_name[0]):
                        otsos_name_set.add(df_data.loc[i, name_column1])
                        otsos_surname_set.add(df_data.loc[i, name_column2])
                    continue

                otsos_name_set.add(df_data.loc[i, name_column1])
                otsos_surname_set.add(df_data.loc[i, name_column2])

            df_data.to_csv(f"new_{file}.csv", index=False, sep=";")
            continue
