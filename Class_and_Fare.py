import pandas as pd

'''
сравнение Class и первой буквы Fare. Любое несоответствие или использование редкого префикса (как A )
- повод присмотреться к пассажиру внимательнее
'''

df = pd.read_csv("merged.csv", sep=';')

def isNA(row, col):
    if row[col] == 'N/A' or row[col] == '':
        return True
    return False

def check(row):
    if (row['Fare'].astype('string').str[1] == 'A' or row['TravelClass'] == 'A'):
        return True

    if not isNA(row, 'TravelClass') and not isNA(row, 'Fare'):
        if row['TravelClass'] != row['Fare'].astype('string').str[1]:
            return True
        return False
    return False

dates_df = df[df.apply(check, axis=1)].copy()

dates_df.to_csv('check_class_fare.csv', sep=';')