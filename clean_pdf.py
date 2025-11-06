"""
clean_pdf.py -- предварительная очистка ненужных страниц в pdf
"""

import fitz  # PyMuPDF
import re
import csv
import sys
from tqdm import tqdm

PDF_PATH = sys.argv[1]
CLEANED_PDF_PATH = 'cleaned' + PDF_PATH

BLOCK_PATTERN = re.compile(
    r'FROM:\s*(.*?)\s*\nTO:\s*(.*?)\s*\n(.*?)(?=(?:FROM:|$))',
    re.S | re.I
)

FLIGHT_PATTERN = re.compile(
    r'(\d{2} +\w{3} +- +\d{2} +\w{3})\s+'
    r'([\d\s]+)\s+'
    r'(\d{2}:\d{2}(\+[1-9])?)\s+'
    r'(\d{2}:\d{2}(\+[1-9])?)\s+'
    r'([A-Z0-9]+(\*)?)\s+'
    r'([A-Z0-9]+)\s+'
    r'([A-Z0-9]+)\s*',
    re.I
)

def check_page(page: str):
    match = FLIGHT_PATTERN.search(page)
    if match:
        return True
    else:
        return False

def main(): 
    print(f"Обрабатываем {PDF_PATH} ...")
    doc = fitz.open(PDF_PATH)
    
    correct = 0
    broken = 0
    wrong = []
    
    i = 0
    for page in tqdm(doc):
        text = page.get_text()
        flag = check_page(text)
        # print(text)
        # print("--------------------------------")
        if flag:
            correct += 1
        else:
            broken += 1
            wrong.append(i)

        # print(f"{i + 1} - {flag}") 
        i += 1

    if broken != 0:
        doc.delete_page(wrong)
        doc.save(CLEANED_PDF_PATH)
    
    doc.close()

    print("-------------------------")
    print(f"Total pages: {i}")
    print(f"Correct pages: {correct}")
    print(f"Broken pages: {broken}") 
    print(wrong)
    if broken != 0:
        print(f"Сохранено: {CLEANED_PDF_PATH}")
    print("-------------------------")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: python convert_final.py input.pdf")
    else:
        main()
