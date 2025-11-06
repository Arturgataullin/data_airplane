#вспомогательные функции для получения конкретной информации из датастов, например уникальных стран

import pandas as pd
import numpy as np

def country_getter():
    df = pd.read_csv('frequent_flyer_forum.csv', delimiter=';')

    countryFrom = 'CountryFrom'
    countryTo = 'CountryTo'

    unique_values1 = df[countryFrom].dropna().unique()
    unique_values2 = df[countryTo].dropna().unique()

    all_countries_series = pd.concat([
        pd.Series(unique_values1, name='Country'),
        pd.Series(unique_values2, name='Country')
    ], ignore_index=True).drop_duplicates()

    with open('countries.txt', 'w', encoding='utf-8') as f:
        for country in all_countries_series:
            f.write(f"{country}\n")

def agent_getter():
    df = pd.read_csv('correct_tab.csv', delimiter=';')

    agents = 'AgentInfo'

    unique_values1 = df[agents].dropna().unique()
    with open('agents.txt', 'w', encoding='utf-8') as f:
        for agent in unique_values1:
            f.write(f"{agent}\n")

def name_getter():
    df = pd.read_csv('correct_tab.csv', delimiter=';')

    first = 'FirstName'
    last = 'LastName'

    unique_values1 = df[first].dropna().unique()
    unique_values2 = df[last].dropna().unique()

    with open('tab_first.txt', 'w', encoding='utf-8') as f:
        for agent in unique_values1:
            f.write(f"{agent}\n")
    with open('tab_last.txt', 'w', encoding='utf-8') as f:
        for agent in unique_values2:
            f.write(f"{agent}\n")

def dif_name():
    df1 = pd.read_csv('3merged.csv', sep=';')
    df2 = pd.read_csv('correct_merged_freq_xml.csv', sep=';')
    only_in_df1 = set(df1['FirstName']) - set(df2['FirstName'])
    print(only_in_df1)
    print('----------------------------------------------')

    only_in_df2 = set(df2['FirstName']) - set(df1['FirstName'])
    print(only_in_df2)
    print(f"Только в первом: {len(only_in_df1)} имен")
    print(f"Только во втором: {len(only_in_df2)} имен")
    
dif_name()