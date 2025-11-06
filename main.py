import pandas as pd
import numpy as np
from column_names import Names
from  check_lastname import RussianSurnameDetector
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
from itertools import repeat
import os
from pathlib import Path

folder = Path(r"C:\Users\golub\PycharmProjects\data_since\YourBoardingPassDotAero")

def chek_last_name(name: str)->bool:
    surname_detector = RussianSurnameDetector()
    return surname_detector.is_russian_surname(name)


def find_value_position_optimized(df, value):
    for col in df.columns:
        mask = df[col] == value
        if mask.any():
            idx = df.index[mask][0]  # берем первый найденный индекс
            return [(idx, col)]
    return []



def find_in_df(df:pd.DataFrame, info: str)->tuple:
    positions = find_value_position_optimized(df, info)
    name = ""
    result_find = True
    if positions:
        name = df.loc[positions[0][0], "Standart"]
    else:
        result_find = False
    return (name, result_find)



def get_first_last_name(all_name: str, df_names: pd.DataFrame, df_surnames: pd.DataFrame)->tuple:
    all_name = all_name.replace("'", "")
    info = list(filter(lambda name: len(name) > 1, all_name.split()))
    name1 = info[0]
    name2 = info[1]
    find_name1 = find_in_df(df_names, name1)
    if find_name1[1]:
        find_name2 = find_in_df(df_surnames, name2)
        if not(find_name2[1]):
            print(f"Не найдено '{name2}'")
        return find_name1[0], find_name2[0]
    find_name1 = find_in_df(df_surnames, name1)
    find_name2 = find_in_df(df_names, name2)
    if not(find_name2[1]):
        print(f"Не найдено '{name2}'")
    if not(find_name1[1]):
        print(f"Не найдено '{name1}'")
    return find_name2, find_name1


def convert_sex(name: str)->str:
    if name == "MR":
        return "Male"
    return "Female"

def get_info(name,string):
    if name == "Sex":
        return convert_sex(string)
    return string


def sheet_processing(excel_file, number_sheet, names_column: dict, df_names: pd.DataFrame, df_surnames: pd.DataFrame)->dict:
    df = pd.read_excel(excel_file, sheet_name=number_sheet, header=None)
    sheet_string = {}
    for name in names_column.keys():
        if name == "Sequence":
            continue
        pos_x, pos_y = names_column[name]
        info = name.split()
        if len(info) == 1:
            sheet_string[name] = get_info(name,df.iat[pos_x,pos_y])
            continue
        first_name, last_name = get_first_last_name(str(df.iat[pos_x,pos_y]), df_names, df_surnames)
        sheet_string[info[0]] = first_name
        sheet_string[info[1]] = last_name
    return sheet_string

def processing_file(file_name: str, names_column: dict, df_names: pd.DataFrame, df_surnames: pd.DataFrame)->list:
    excel_file = pd.ExcelFile(file_name)
    strings_file = []
    for name in tqdm(excel_file.sheet_names):
        strings_file.append(sheet_processing(excel_file, name, names_column,df_names, df_surnames))
    return strings_file


def process(names_column: dict, files: list, df_names: pd.DataFrame, df_surnames: pd.DataFrame) -> pd.DataFrame:
    data_frames = []
    max_workers = min(len(files), os.cpu_count() or 1)

    with ProcessPoolExecutor(max_workers=max_workers) as ex:
        for rows in tqdm(ex.map(processing_file, files,repeat(names_column),repeat(df_names), repeat(df_surnames))):
            data_frames.append(pd.DataFrame(rows))

    result_df = pd.concat(data_frames, ignore_index=True)
    return result_df



if __name__ == "__main__":
    print(os.cpu_count())
    names = ["YourBoardingPassDotAero/" + p.name for p in folder.iterdir() if p.is_file()]
    #people_names = set(open("names.txt", "r").read().split())
    geter_names = Names("name_file2.txt", "YourBoardingPassDotAero/YourBoardingPassDotAero-2017-01-02.xlsx")
    rest = geter_names.get_cords()
    count_thread = os.cpu_count()
    df_names = pd.read_csv("info.csv", sep=";")
    df_surnames = pd.read_csv("huila.csv", sep=";")
    result_data_frame = process(rest,names, df_names, df_surnames)
    result_data_frame.to_csv("result_archive.csv",index=False, encoding="utf-8-sig", sep=";")

