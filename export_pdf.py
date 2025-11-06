"""
export_pdf.py -- экспорт pdf в csv
"""

import fitz
import re
import csv
import sys
from tqdm import tqdm

PDF_PATH = sys.argv[1]
OUTPUT_PATH = sys.argv[2]

HEADER_PATTERN = re.compile(
    r'FROM:\s*(?P<from_city>.*?),\s*'
    r'(?P<from_country>.*?)\n'
    r'(?P<from_code>[A-Z]{3})\s*\n'
    r'TO:\s*(?P<to_city>.*?),\s*'
    r'(?P<to_country>.*?)\n'
    r'(?P<to_code>[A-Z]{3})',
    re.I
)

LINE_PATTERN = re.compile(
    r'(?P<valid_from>\d{2} \w{3})\s*-\s*(?P<valid_to>\d{2} \w{3})\s*'
    r'(?P<days>[0-7\s]+)\s*'
    r'(?P<dep>\d{2}:\d{2}(?:\+[1-9])?)\s*'
    r'(?P<arr>\d{2}:\d{2}(?:\+[1-9])?)\s*'
    r'(?P<flight>[A-Z0-9]+(?:\*)?)\s*'
    r'(?P<aircraft>[A-Z0-9]+)\s*'
    r'(?P<travel_time>\d+H\d+M)\s*',
    re.I
)

HEADER = [
    'CITY_FROM',
    'COUNTRY_FROM',
    'CODE_FROM',
    'CITY_TO',
    'COUNTRY_TO',
    'CODE_TO',
    'VALIDITY_FROM',
    'VALIDITY_TO',
    'DAYS',
    'DEP_TIME',
    'ARR_TIME',
    'FLIGHT',
    'AIRCRAFT',
    'TRAVEL_TIME'
]

def main():
    print(f"Обрабатываем {PDF_PATH} ...")
    doc = fitz.open(PDF_PATH)

    data = []

    header_left = []
    header_right = []

    for page in tqdm(doc):
        page_text = page.get_text()
        headers_iter = list(HEADER_PATTERN.finditer(page_text))

        if len(headers_iter) == 2:
            h0 = headers_iter[0]
            h1 = headers_iter[1]

            header_left = [
                h0.group('from_city').strip(),
                h0.group('from_country').strip(),
                h0.group('from_code').strip(),
                h0.group('to_city').strip(),
                h0.group('to_country').strip(),
                h0.group('to_code').strip()
            ]

            header_right = [
                h1.group('from_city').strip(),
                h1.group('from_country').strip(),
                h1.group('from_code').strip(),
                h1.group('to_city').strip(),
                h1.group('to_country').strip(),
                h1.group('to_code').strip()
            ]

        page_text_blocks = page.get_text("blocks")
        for blk in page_text_blocks:
            line_text = blk[4].replace("\n", " ")
            match = LINE_PATTERN.search(line_text)
            if match:
                if blk[0] < 250:
                    header = header_left
                else:
                    header = header_right

                row = header + [
                    match.group('valid_from').strip(),
                    match.group('valid_to').strip(),
                    match.group('days').strip(),
                    match.group('dep').strip(),
                    match.group('arr').strip(),
                    match.group('flight').strip(),
                    match.group('aircraft').strip(),
                    match.group('travel_time').strip(),
                ]
                data.append(row)

    data.sort(key=lambda x: x[0].lower())

    print(f"Сохраняем в {OUTPUT_PATH} ...")
    with open(OUTPUT_PATH, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(HEADER)
        writer.writerows(data)

    print(f"Готово! Найдено {len(data)} строк.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Использование: python script.py input.pdf output.csv")
    else:
        main()

