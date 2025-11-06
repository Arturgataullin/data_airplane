import pandas as pd
from tqdm import tqdm
import os
#FirstName;LastName;SecondName;Sex;BirthDate;PassengerDocument_RU;PassengerDocument_INTL;CardNumber;ETicketNumber;TravelClass;DepartDate;DepartTime;ArrivalDate;ArrivalTime;FlightNumber;From;Dest;Fare;FareBasisCode;CodeShare;CityFrom;CityTo;CountryFrom;CountryTo;AgentInfo;Bonus;LoyaltyLevelDT;LoyaltyNumberDT;LoyaltyLevelFB;LoyaltyNumberFB;LoyaltyLevelKE;LoyaltyNumberKE;LoyaltyLevelSU;LoyaltyNumberSU;Codeshare
df = pd.read_csv("mrgd.csv", sep=";",low_memory=False)
df = df.dropna(subset=['FirstName', 'LastName'])
N = 20
#CountryFrom;CountryTo
columns_to_check1 = ['FareBasisCode', 'CodeShare', 'SecondName']
df = df.drop(columns_to_check1, axis=1)
df_cleaned = df.dropna(thresh=len(df.columns) - N + 1)
column1 = "CountryTo"
column2 = "CountryFrom"
df.loc[df[column1] == 'RUSSIAN', column1] = 'RUSSIAN FEDERATION'
df.loc[df[column2] == 'RUSSIAN', column2] = 'RUSSIAN FEDERATION'
df.loc[df[column1] == 'UNITED STATES OF', column1] = 'UNITED STATES'
df.loc[df[column2] == 'UNITED STATES OF', column2] = 'UNITED STATES'
df.to_csv("new_mgrd.csv", index=False, sep=';')
