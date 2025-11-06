import warnings

warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
from column_names import Names
from check_lastname import RussianSurnameDetector
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
from itertools import repeat
import os
from pathlib import Path


import re


def translit_ru_to_en_passport2(name: str, upper: bool = True) -> str:

    s = name.strip().lower()

    def _word(w: str) -> str:
        if not w:
            return w

        rules = [
            # 1) концовки с й/я/ю и др.
            (r"ия\b",  "iia"),   # Мария → mariia; София → sof iia
            (r"ий\b",  "ii"),    # Валерий → valerii
            (r"ый\b",  "y"),     # (редко в именах)
            (r"ей\b",  "ei"),    # Сергей → sergei
            (r"ья",    "ya"),    # Дарья → darya

            # 2) общие бидиграфы
            (r"щ",     "shch"),
            (r"ж",     "zh"),
            (r"ч",     "ch"),
            (r"ш",     "sh"),
            (r"ц",     "tc"),
            (r"х",     "kh"),

            # 3) й после гласных/в общем случае
            (r"й",     "i"),

            # 4) одиночные буквы
            (r"ё",     "e"),
            (r"ю",     "iu"),
            (r"я",     "ia"),
            (r"э",     "e"),
            (r"ъ",     ""),      # выпадает
            (r"ь",     ""),      # выпадает

            (r"а", "a"), (r"б", "b"), (r"в", "v"), (r"г", "g"), (r"д", "d"),
            (r"е", "e"), (r"з", "z"), (r"и", "i"), (r"к", "k"), (r"л", "l"),
            (r"м", "m"), (r"н", "n"), (r"о", "o"), (r"п", "p"), (r"р", "r"),
            (r"с", "s"), (r"т", "t"), (r"у", "u"), (r"ф", "f"), (r"ы", "y"),
            (r"й", "i"), # дублируем на случай, если что-то осталось
        ]

        out = w
        for pat, rep in rules:
            out = re.sub(pat, rep, out)
        return out

    parts = re.split(r"([-\s]+)", s)  # чтобы сохранить дефисы/пробелы
    parts = [_word(p) if not re.fullmatch(r"[-\s]+", p) else p for p in parts]
    res = "".join(parts)
    return res.upper() if upper else res





def translit_ru_to_en_passport(name: str, upper: bool = True) -> str:

    s = name.strip().lower()

    def _word(w: str) -> str:
        if not w:
            return w

        rules = [
            # 1) концовки с й/я/ю и др.
            (r"ия\b",  "iia"),   # Мария → mariia; София → sof iia
            (r"ий\b",  "ii"),    # Валерий → valerii
            (r"ый\b",  "y"),     # (редко в именах)
            (r"ей\b",  "ei"),    # Сергей → sergei
            (r"ья",    "ya"),    # Дарья → darya

            # 2) общие бидиграфы
            (r"щ",     "shch"),
            (r"ж",     "zh"),
            (r"ч",     "ch"),
            (r"ш",     "sh"),
            (r"ц",     "ts"),
            (r"х",     "kh"),

            # 3) й после гласных/в общем случае
            (r"й",     "i"),

            # 4) одиночные буквы
            (r"ё",     "e"),
            (r"ю",     "iu"),
            (r"я",     "ia"),
            (r"э",     "e"),
            (r"ъ",     ""),      # выпадает
            (r"ь",     ""),      # выпадает

            (r"а", "a"), (r"б", "b"), (r"в", "v"), (r"г", "g"), (r"д", "d"),
            (r"е", "e"), (r"з", "z"), (r"и", "i"), (r"к", "k"), (r"л", "l"),
            (r"м", "m"), (r"н", "n"), (r"о", "o"), (r"п", "p"), (r"р", "r"),
            (r"с", "s"), (r"т", "t"), (r"у", "u"), (r"ф", "f"), (r"ы", "y"),
            (r"й", "i"), # дублируем на случай, если что-то осталось
        ]

        out = w
        for pat, rep in rules:
            out = re.sub(pat, rep, out)
        return out

    parts = re.split(r"([-\s]+)", s)  # чтобы сохранить дефисы/пробелы
    parts = [_word(p) if not re.fullmatch(r"[-\s]+", p) else p for p in parts]
    res = "".join(parts)
    return res.upper() if upper else res


def translit_ru_to_en_passport3(name: str, upper: bool = True) -> str:

    s = name.strip().lower()

    def _word(w: str) -> str:
        if not w:
            return w

        rules = [
            # 1) концовки с й/я/ю и др.
            (r"ия\b",  "iia"),   # Мария → mariia; София → sof iia
            (r"ий\b",  "ii"),    # Валерий → valerii
            (r"ый\b",  "y"),     # (редко в именах)
            (r"ей\b",  "ei"),    # Сергей → sergei
            (r"ья",    "ya"),    # Дарья → darya
            (r"кс", "x"),  # Оксана -> oxana
            # 2) общие бидиграфы
            (r"щ",     "shch"),
            (r"ж",     "zh"),
            (r"ч",     "ch"),
            (r"ш",     "sh"),
            (r"ц",     "ts"),
            (r"х",     "kh"),

            # 3) й после гласных/в общем случае
            (r"й",     "i"),

            # 4) одиночные буквы
            (r"ё",     "e"),
            (r"ю",     "iu"),
            (r"я",     "ya"),
            (r"э",     "e"),
            (r"ъ",     ""),      # выпадает
            (r"ь",     ""),      # выпадает

            (r"а", "a"), (r"б", "b"), (r"в", "v"), (r"г", "g"), (r"д", "d"),
            (r"е", "e"), (r"з", "z"), (r"и", "i"), (r"к", "k"), (r"л", "l"),
            (r"м", "m"), (r"н", "n"), (r"о", "o"), (r"п", "p"), (r"р", "r"),
            (r"с", "s"), (r"т", "t"), (r"у", "u"), (r"ф", "f"), (r"ы", "y"),
            (r"й", "i"), # дублируем на случай, если что-то осталось
        ]

        out = w
        for pat, rep in rules:
            out = re.sub(pat, rep, out)
        return out

    parts = re.split(r"([-\s]+)", s)  # чтобы сохранить дефисы/пробелы
    parts = [_word(p) if not re.fullmatch(r"[-\s]+", p) else p for p in parts]
    res = "".join(parts)
    return res.upper() if upper else res

def translit_ru_to_en_passport4(name: str, upper: bool = True) -> str:

    s = name.strip().lower()

    def _word(w: str) -> str:
        if not w:
            return w

        rules = [
            # 1) концовки с й/я/ю и др.
            (r"ия\b",  "iya"),   # Мария → mariia; София → sof iia
            (r"ий\b",  "ii"),    # Валерий → valerii
            (r"ый\b",  "y"),     # (редко в именах)
            (r"ей\b",  "ei"),    # Сергей → sergei
            (r"ья",    "ya"),    # Дарья → darya
            (r"кс", "x"),  # Оксана -> oxana
            # 2) общие бидиграфы
            (r"щ",     "shch"),
            (r"ж",     "zh"),
            (r"ч",     "ch"),
            (r"ш",     "sh"),
            (r"ц",     "ts"),
            (r"х",     "kh"),

            # 3) й после гласных/в общем случае
            (r"й",     "i"),

            # 4) одиночные буквы
            (r"ё",     "e"),
            (r"ю",     "iu"),
            (r"я",     "ya"),
            (r"э",     "e"),
            (r"ъ",     ""),      # выпадает
            (r"ь",     ""),      # выпадает

            (r"а", "a"), (r"б", "b"), (r"в", "v"), (r"г", "g"), (r"д", "d"),
            (r"е", "e"), (r"з", "z"), (r"и", "i"), (r"к", "k"), (r"л", "l"),
            (r"м", "m"), (r"н", "n"), (r"о", "o"), (r"п", "p"), (r"р", "r"),
            (r"с", "s"), (r"т", "t"), (r"у", "u"), (r"ф", "f"), (r"ы", "y"),
            (r"й", "i"), # дублируем на случай, если что-то осталось
        ]

        out = w
        for pat, rep in rules:
            out = re.sub(pat, rep, out)
        return out

    parts = re.split(r"([-\s]+)", s)  # чтобы сохранить дефисы/пробелы
    parts = [_word(p) if not re.fullmatch(r"[-\s]+", p) else p for p in parts]
    res = "".join(parts)
    return res.upper() if upper else res




def manual_transliteration(name):
    """Ручная транслитерация по ГОСТ 16876-71"""
    translit_map = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
        'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i',
        'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
        'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
        'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch',
        'ш': 'sh', 'щ': 'shch', 'ъ': '', 'ы': 'y', 'ь': '',
        'э': 'e', 'ю': 'yu', 'я': 'ya'
    }

    result = []
    for char in name.lower():
        if char in translit_map:
            result.append(translit_map[char])
        else:
            result.append(char)

    return ''.join(result).title()

def surname_transliteration(name):
    """Транслитерация по стандарту ISO 9"""
    iso9_map = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
        'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i',
        'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
        'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
        'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'tc', 'ч': 'ch',
        'ш': 'sh', 'щ': 'shch', 'ъ': '', 'ы': 'y', 'ь': '',
        'э': 'e', 'ю': 'iu', 'я': 'ia', 'ья': 'ia', 'ий': 'ii', 'ей': 'ei'
    }

    result = []
    for char in name.lower():
        if char in iso9_map:
            result.append(iso9_map[char])
        else:
            result.append(char)

    return ''.join(result).title()


def iso9_transliteration(name):
    """Транслитерация по стандарту ISO 9"""
    iso9_map = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
        'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i',
        'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
        'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
        'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch',
        'ш': 'sh', 'щ': 'shch', 'ъ': '', 'ы': 'y', 'ь': '',
        'э': 'e', 'ю': 'yu', 'я': 'ia', 'ья': 'ya', 'ий': 'iy', 'ей': 'ey'
    }

    result = []
    for char in name.lower():
        if char in iso9_map:
            result.append(iso9_map[char])
        else:
            result.append(char)

    return ''.join(result).title()

def my_dop_transliteration(name):
    """Транслитерация по стандарту ISO 9"""
    iso9_map = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
        'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i',
        'й': 'i', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
        'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
        'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch',
        'ш': 'sh', 'щ': 'shch', 'ъ': '', 'ы': 'y', 'ь': '',
        'э': 'e', 'ю': 'iu', 'я': 'ia', 'ья': 'ia', 'ий': 'ii', 'ей': 'ei'
    }

    result = []
    for char in name.lower():
        if char in iso9_map:
            result.append(iso9_map[char])
        else:
            result.append(char)

    return ''.join(result).title()





def translate_russian_name(name):
    translations = set()

    name = name.strip().title()

    try:
        import transliterate
        translit1 = transliterate.translit(name, 'ru', reversed=True)
        clean_trans = clean_translation(translit1)
        if clean_trans:
            translations.add(clean_trans.title())
    except:
        pass

    # 2. Используем библиотеку iuliia (множество стандартов транслитерации)
    try:
        import iuliia
        # Используем разные схемы транслитерации из iuliia
        schemes = [
            'gost_779',  # ГОСТ 779-2000 (российский стандарт)
            'icao',  # ICAO (международный для документов)
            'wikipedia',  # Схема Википедии (широко распространена)
            'mosmetro',  # Схема Московского метро (популярна в России)
            'telegram',  # Схема Telegram (современный мессенджер)
            'gost_52535',  # ГОСТ Р 52535.1-2006 (для загранпаспортов)
            'iso_9_1968',  # ISO 9:1968 (международный стандарт)
        ]

        for scheme in schemes:
            try:
                transliterated = iuliia.translate(name, scheme)
                clean_trans = clean_translation(transliterated)
                if clean_trans:
                    translations.add(clean_trans.title())
            except:
                continue

    except Exception as e:
        print(f"Iuliia error: {e}")

    # 3. Используем googletrans (Google Translate API)
    try:
        from googletrans import Translator
        translator = Translator()
        google_trans = translator.translate(name, src='ru', dest='en').text
        # Очищаем результат от лишних слов
        clean_trans = clean_translation(google_trans)
        if clean_trans:
            translations.add(clean_trans.title())
    except:
        pass

    # 5. Используем библиотеку translators (универсальный переводчик)
    try:
        import translators as ts
        # Пробуем разные сервисы
        services = ['google', 'yandex', 'bing', 'sogou']
        for service in services:
            try:
                trans_result = ts.translate_text(name, from_language='ru', to_language='en', translator=service)
                clean_trans = clean_translation(trans_result)
                if clean_trans:
                    translations.add(clean_trans.title())
            except:
                continue
    except:
        pass
    translations.add(iso9_transliteration(name))
    translations.add(manual_transliteration(name))
    translations.add(my_dop_transliteration(name))
    translations.add(translit_ru_to_en_passport(name))
    translations.add(surname_transliteration(name))
    translations.add(translit_ru_to_en_passport2(name))
    translations.add(translit_ru_to_en_passport3(name))
    translations.add(translit_ru_to_en_passport4(name))
    return translations


def clean_translation(text):
    """Очищает перевод от лишних слов и оставляет только имя"""
    # Убираем слова, которые могут добавить переводчики
    unwanted_words = ['name', 'named', 'is called', 'the name', 'first name',
                      'my name is', 'his name is', 'her name is', 'called']

    text = str(text).strip()

    # Если переводчик добавил "Name" или подобное
    for word in unwanted_words:
        if text.lower().startswith(word + ' '):
            text = text[len(word):].strip()
        if text.lower().endswith(' ' + word):
            text = text[:-len(word)].strip()

    # Убираем кавычки, точки, скобки
    text = text.strip('"\'().,;:!?[]{}')

    # Проверяем, что это похоже на имя (только буквы и пробелы/дефисы)
    if all(c.isalpha() or c.isspace() or c == '-' for c in text):
        # Разделяем на слова и проверяем каждое
        words = text.split()
        clean_words = []
        for word in words:
            # Убираем слова, которые не являются именами
            if word.replace('-', '').isalpha():
                clean_words.append(word)
        if clean_words:
            return ' '.join(clean_words)

    return None




# Дополнительная функция для просмотра всех схем iuliia
def show_iuliia_schemes():
    """Показывает все доступные схемы транслитерации в iuliia"""
    try:
        import iuliia
        schemes = iuliia.schemes()
        print("Доступные схемы транслитерации iuliia:")
        for scheme in schemes:
            print(f"  - {scheme}")
        return schemes
    except:
        print("Библиотека iuliia не установлена")
        return []


def process_single_name(name):
    """Обрабатывает одно имя и возвращает результат"""
    translates = list(map(lambda x: str(x).upper(),translate_russian_name(name)))
    if len(translates) < 10:
        for i in range(10 - len(translates)):
            translates.append("N/A")
    translates.append(translates[0] if translates else "N/A")
    return translates


def generate_from_files_parallel(file, max_workers=20):
    names = set(open(file, "r", encoding="UTF-8").read().split())
    result_translate = []

    print(f"Обрабатывается {len(names)} имен с использованием {max_workers} процессов...")

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_to_name = {executor.submit(process_single_name, name): name for name in names}

        for future in tqdm(as_completed(future_to_name), total=len(names), desc="Обработка имен"):
            try:
                result = future.result()
                result_translate.append(result)
            except Exception as e:
                print(f"Ошибка при обработке имени: {e}")
                result_translate.append(["N/A"] * 7)

    return result_translate


def generate_from_files_parallel_chunked(file, max_workers=20, chunk_size=100):
    """Параллельная обработка с разбивкой на чанки для лучшей производительности"""
    names = list(set(open(file, "r", encoding="UTF-8").read().split()))
    result_translate = []

    print(f"Обрабатывается {len(names)} имен с использованием {max_workers} процессов...")

    # Разбиваем на чанки
    chunks = [names[i:i + chunk_size] for i in range(0, len(names), chunk_size)]

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Обрабатываем чанки параллельно
        futures = [executor.submit(process_chunk, chunk) for chunk in chunks]

        for future in tqdm(as_completed(futures), total=len(chunks), desc="Обработка чанков"):
            try:
                chunk_result = future.result()
                result_translate.extend(chunk_result)
            except Exception as e:
                print(f"Ошибка при обработке чанка: {e}")

    return result_translate


def process_chunk(names_chunk):
    """Обрабатывает чанк имен"""
    chunk_result = []
    for name in names_chunk:
        try:
            result = process_single_name(name)
            chunk_result.append(result)
        except Exception as e:
            print(f"Ошибка при обработке имени {name}: {e}")
            chunk_result.append(["N/A"] * 7)
    return chunk_result


def generate_from_files(file):
    """Оригинальная последовательная версия для сравнения"""
    names = set(open(file, "r", encoding="UTF-8").read().split())
    result_translate = []
    for name in tqdm(names):
        translates = list(translate_russian_name(name))
        if len(translates) < 10:
            for i in range(10 - len(translates)):
                translates.append("N/A")
        translates.append(translates[0] if translates else "N/A")
        result_translate.append(translates)
    return result_translate


def create_data_frame(file_name, use_parallel=True, max_workers=20):
    names_column = [f"Translate{i}" for i in range(10)]
    names_column.append("Standart")

    if use_parallel:
        translated_names_data = generate_from_files_parallel(file_name, max_workers)
    else:
        translated_names_data = generate_from_files(file_name)

    df_names = pd.DataFrame(translated_names_data, columns=names_column)
    return df_names

# def change_standart(old_file_name, new_file_name):
#     df_old = pd.read_csv(old_file_name, sep=";")
#     df_new = pd.read_csv(new_file_name, sep=";")
#     old_standart = df_old["Standart"]
#     df_new["Standart"] = old_standart
#     df_new.to_csv(f"{names[:-4]}.csv", index=False, encoding="utf-8-sig", sep=";")

if __name__ == "__main__":
    names = "info.txt"
    surname = "huila.txt"
    #print(translate_russian_name("Ксения"))
    #Используем параллельную обработку с 20 процессами
    df_names = create_data_frame(names, use_parallel=True, max_workers=os.cpu_count())
    df_lasts = create_data_frame(surname, use_parallel=True, max_workers=os.cpu_count())

    df_names.to_csv(f"{names[:-4]}.csv", index=False, encoding="utf-8", sep=";")
    df_lasts.to_csv(f"{surname[:-4]}.csv", index=False, encoding="utf-8", sep=";")

    print("Обработка завершена!")