#парсит jspn документ с данными в csv
import json
import pandas as pd
from datetime import datetime

name_translations = {
    'ALEXANDR': 'ALEKSANDR',
    'ALEXANDRA': 'ALEKSANDRA',
    'OXANA': 'OKSANA',
    'XENIYA': 'KSENIYA',
    'ALEXEY': 'ALEKSEY',
    'MAXIM': 'MAKSIM'
}
surname_translations = {
    'MAXIMOVA': 'MAKSIMOVA',
    'ALEXEEV': 'ALEKSEEV',
    'ALEXANDROVA': 'ALEKSANDROVA',
    'MAXIMOV': 'MAKSIMOV',
    'AXENOVA': 'AKSENOVA',
    'ALEXEEVA': 'ALEKSEEVA',
    'AXENOV': 'AKSENOV',
    'ALEXANDROV': 'ALEKSANDROV'
}

def json_to_csv_simple(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    all_records = []
    
    for profile in data["Forum Profiles"]:

        if profile.get('Real Name', {}).get('First Name', '') == None or profile.get('Real Name', {}).get('Last Name', '') == None:
            continue

        first_name = profile.get('Real Name', {}).get('First Name', '').replace("'", "").strip()
        first_name = name_translations.get(first_name, first_name)
        last_name = profile.get('Real Name', {}).get('Last Name', '').replace("'", "").strip()
        last_name = surname_translations.get(last_name, last_name)
        
        for flight in profile.get('Registered Flights', []):
            date_str = flight.get('Date', '')
            try:
                formatted_date = datetime.strptime(date_str, '%Y-%m-%d').strftime('%d.%m.%Y')
            except:
                formatted_date = date_str
            
            record = {
                'Sex': profile.get('Sex', ''),
                'FirstName': first_name,
                'LastName': last_name,
                'DepartDate': formatted_date,
                'FlightNumber': flight.get('Flight', ''),
                'Codeshare': flight.get('Codeshare', False),
                'CityFrom': flight.get('Departure', {}).get('City', '').upper(),
                'From': flight.get('Departure', {}).get('Airport', '').upper(),
                'CountryFrom': flight.get('Departure', {}).get('Country', '').upper(),
                'CityTo': flight.get('Arrival', {}).get('City', '').upper(),
                'Dest': flight.get('Arrival', {}).get('Airport', '').upper(),
                'CountryTo': flight.get('Arrival', {}).get('Country', '').upper()
            }
            
            for prog in profile.get('Loyality Programm', []):
                program_name = prog.get('programm', '')
                record[f"LoyaltyLevel{program_name}"] = prog.get('Status', '')
                record[f"LoyaltyNumber{program_name}"] = program_name + prog.get('Number', '')
            
            all_records.append(record)
    
    if all_records:
        df = pd.DataFrame(all_records)
        df.to_csv(output_file, index=False, encoding='utf-8', sep=';')
        print(f"Сохранено {len(all_records)} записей в {output_file}")

if __name__ == "__main__":
    json_to_csv_simple("FrequentFlyerForum-Profiles.json", "frequent_flyer_forum.csv")