import pandas as pd
from tqdm import tqdm
import os
from collections import Counter


def get_name_pairs_from_dataframe(df):
    if 'FirstName' not in df.columns or 'LastName' not in df.columns:
        return []
    name_pairs = df[['FirstName', 'LastName']].values.tolist()
    return name_pairs


def get_list_spyses(folder_path):
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    spyes = []
    numbers = 0
    info_df = {}
    for file in tqdm(files, desc="Чтение файлов"):
        df_data = pd.read_csv(f"{folder_path}/{file}", sep=';')
        unique_spyses = [list(item) for item in set(tuple(item) for item in get_name_pairs_from_dataframe(df_data))]
        for info in unique_spyses:
            spyes.append(info)
        info_df[numbers] = unique_spyses
        for info in unique_spyses:
            spyes.append(info)
        numbers += 1
    return spyes,info_df, files


def add_summ(spyses, info_df, files):
    result_list = []
    for spy in tqdm(spyses):
        info_spy = spy
        dfs = set()
        for key, value in info_df.items():
            if spy in value:
                dfs.add(files[key])
        result_list.append(info_spy + list(dfs))
    return result_list

def main():
    folder_path = 'data_spy'
    spyses, info_df, files = get_list_spyses(folder_path)
    spyses = add_summ(spyses, info_df, files)
    max_elem = max(spyses, key=lambda x: len(x[2:]))
    spyses = list(filter(lambda x: len(x[2:]) == len(max_elem[2:]), spyses))
    with open("result_spy.txt", "w", encoding='utf-8') as file:
        for i in range(len(spyses)):
            file.write(f"{spyses[i]}\n")


if __name__ == "__main__":
    main()