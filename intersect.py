"""
intersect.py - найти пересечение значений по определенному параметру для двух датасетов
"""

import csv

file1 = "file1.csv"      
file2 = "file2.csv"         
outfile = "matched.csv"        

# === Настройки ===
KEYS = ["ETicketNumber"]
sep = ";"                                   

require_nonempty_keys = True

def norm(x: str) -> str:
    return x.strip()

def make_key(row: dict, keys: list[str]) -> tuple:
    vals = []
    for k in keys:
        v = row.get(k, "")
        v = "" if v is None else str(v)
        vals.append(norm(v))
    return tuple(vals)


with open(file2, newline="", encoding="utf-8") as f2:
    reader2 = csv.DictReader(f2, delimiter=sep)

    missing2 = [k for k in KEYS if k not in reader2.fieldnames]
    if missing2:
        raise ValueError(f"В файле {file2} нет столбцов: {', '.join(missing2)}")

    keys2 = set()
    total2 = 0
    for row in reader2:
        total2 += 1
        key_tuple = make_key(row, KEYS)
        if require_nonempty_keys and any(v == "" for v in key_tuple):
            continue
        keys2.add(key_tuple)

print(f"Во втором файле найдено {len(keys2)} уникальных ключей из {total2} строк")

with open(file1, newline="", encoding="utf-8") as f1, \
     open(outfile, "w", newline="", encoding="utf-8") as fout:

    reader1 = csv.DictReader(f1, delimiter=sep)

    missing1 = [k for k in KEYS if k not in reader1.fieldnames]
    if missing1:
        raise ValueError(f"В файле {file1} нет столбцов: {', '.join(missing1)}")

    writer = csv.DictWriter(fout, fieldnames=reader1.fieldnames, delimiter=sep)
    writer.writeheader()

    count = 0
    scanned = 0
    for row in reader1:
        scanned += 1
        key_tuple = make_key(row, KEYS)
        if require_nonempty_keys and any(v == "" for v in key_tuple):
            continue
        if key_tuple in keys2:
            writer.writerow(row)
            count += 1

print(f"Просканировано строк в первом файле: {scanned}")
print(f"Совпавших строк: {count}")
print(f"Результат сохранён в {outfile}")
