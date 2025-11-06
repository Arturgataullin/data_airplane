import datetime

import iuliia
import csv

'''
парсинг файлов .tcb & .csv
на выходе получаем tcb.csv & csv.csv
'''

def parse_tab():
    notes = []

    with open("Sirena-export-fixed.tab", "r", encoding="utf-8") as f:
        for line in f:               # line содержит строку с завершающим \n
            cells = []
            cells = line[:126].split() # name -- flightCode
            cells.extend(line[126:150].split()) # YES/NO -- code
            cells.extend(line[150:166].split()) # e-ticket

            cells.append(line[168:179]) # passport #
            cells[len(cells)-1].replace(' ', '')

            cells.extend(line[180:184].split()) # seat

            meal = line[186:190].split() # meal
            if len(meal) == 0:
                cells.append('N/A')
            else:
                cells.append(meal[0])

            cells.extend(line[192:204].split()) # TrcCls -- fare

            baggage = line[204:211].split() # baggage
            if len(baggage) == 0:
                cells.append('N/A')
            else:
                cells.append(baggage[0])

            i = line[216:239].split()
            cells.append(" ".join(i)) # PaxAdditionalInfo
            info = line[240:276].split()
            if len(info) == 0:
                cells.append('N/A')
            else:
                cells.append(" ".join(info))

            site = line[276:334].split()  # site
            if len(site) == 0:
                cells.append('N/A')
            else:
                cells.append(site[0])

            if cells[3] != 'N/A': # changing dates
                cells[3] = datetime.datetime.strptime(cells[3], "%Y-%m-%d").strftime("%d.%m.%Y")
            cells[4] = datetime.datetime.strptime(cells[4], "%Y-%m-%d").strftime("%d.%m.%Y")
            cells[6] = datetime.datetime.strptime(cells[6], "%Y-%m-%d").strftime("%d.%m.%Y")

            for i in range(3): #changing names
                cells[i] = iuliia.translate(cells[i], schema=iuliia.ICAO_DOC_9303).upper()
            cells[0], cells[1] = cells[1], cells[0]
            cells[1], cells[2] = cells[2], cells[1]

            cells.extend(['N/A', 'N/A', 'N/A', 'N/A'])
            #cells[24] = 'N/A' # city
            #cells[25] = 'N/A' # other bag
            #cells[26] = 'N/A' # sex

            notes.append(cells)
        return notes

def read_csv():
    rows = []
    with open("BoardingData.csv", "r", encoding="latin-1", newline="") as f:
        reader = csv.reader(f, delimiter=";")  # по умолчанию delimiter=","
        # reader = csv.reader(f, delimiter=";")
        for row in reader:
            if row[4].find('/'):
                row[4] = datetime.datetime.strptime(row[4], "%m/%d/%Y").strftime("%d.%m.%Y")
            if row[9].find('-'):
                row[9] = datetime.datetime.strptime(row[9], "%Y-%m-%d").strftime("%d.%m.%Y")
            if row[7] == "Not presented":
                row[7] = 0

            #                               др
            note = [row[0], row[1], row[2], row[4], row[9], row[10], 'N/A', 'N/A', row[11], 'N/A',
                    'N/A', 'N/A', row[6], row[7], row[5], 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A',
                    'N/A', 'N/A', row[8], row[13], row[3], row[12]]
            rows.append(note)  # row — это list[str]
    return rows #ticket number = 8


def append_csv(path, rows, headers=None, delimiter=";", encoding="utf-8-sig", first_chunk=False):
    mode = "w" if first_chunk else "a"
    with open(path, mode, encoding=encoding, newline="") as f:
        w = csv.writer(f, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL)
        if first_chunk and headers:
            w.writerow(headers)
        w.writerows(rows)


rows1 = parse_tab()
rows2 = read_csv()

old_headers = ['FirstName', 'SecondName', 'LastName', 'BirthDate', 'DepartDate', 'DepartTime',
           'ArrivalDate', 'ArrivalTime', 'FlightNumber', 'CodeSh', 'From', 'Dest', 'Fare', 'e-Ticket', #From - код аэропорт,б Dest - код аэропрота, Code - 6 букв
           'TravelDoc', 'Seat', 'Meal', 'TravelClass', 'Fare', 'Baggage', 'AdditionalInfo1', 'AdditionalInfo2',
           'AgentInfo', 'TimeInRoute', 'DestCity', 'OtherBaggage', 'Sex']

headers = ['FirstName', 'SecondName', 'LastName', 'BirthDate', 'DepartDate',
           'DepartTime', 'ArrivalDate', 'ArrivalTime', 'FlightNumber', 'CodeSh',
           'From', 'Dest', 'Fare', 'CountryTo', 'CountryFrom',
           'CityTo', 'CityFrom', 'ETicketNumber', 'TravelClass', 'CardNumber']
rows1.insert(0, old_headers)


append_csv("tab.csv", rows1, first_chunk=True)
append_csv("out.csv", rows2)
