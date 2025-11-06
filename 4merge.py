#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
4merge.py -- универсальное слияние CSV
Пример:
  python3 4merge.py data/csv.csv data/tab.csv merged.csv --keys ETicketNumber
"""

import argparse
import pandas as pd
import numpy as np
import re

try:
    from tqdm.auto import tqdm
except Exception:
    class _DummyTqdm:
        def __init__(self, iterable=None, **kwargs): self.iterable = iterable
        def __iter__(self): return iter(self.iterable) if self.iterable is not None else iter(())
        def update(self, *_, **__): pass
        def close(self): pass
    def tqdm(iterable=None, **kwargs): return _DummyTqdm(iterable, **kwargs)

SEP = ";"
NA_VALUES = ["N/A", "NA", "", " ", "N\\A", "None"]

DESIRED_ORDER = [
    "FirstName","LastName","SecondName","Sex","BirthDate",
    "PassengerDocument_RU","PassengerDocument_INTL",
    "CardNumber","ETicketNumber","TravelClass",
    "DepartDate","DepartTime","ArrivalDate","ArrivalTime",
    "FlightNumber","From","Dest","Fare","FareBasisCode","CodeShare",
    "CityFrom","CityTo","CountryFrom","CountryTo","AgentInfo",
    "Bonus", "LoyaltyLevelDT", "LoyaltyNumberDT", "LoyaltyLevelFB",
    "LoyaltyNumberFB", "LoyaltyLevelKE", "LoyaltyNumberKE", 
    "LoyaltyLevelSU", "LoyaltyNumberSU",
]

def _is_na(x):
    return pd.isna(x) or (isinstance(x, str) and x.strip() == "")

def ci_equal(a, b):
    if _is_na(a) or _is_na(b):
        return False
    return str(a).strip().lower() == str(b).strip().lower()

# Нормализация e-ticket
_ETKT_DIGITS = re.compile(r"\D+")

def normalize_eticket(x: object) -> object:
    """Оставляем только цифры. '0' или пусто -> NA."""
    if _is_na(x): return pd.NA
    s = re.sub(_ETKT_DIGITS, "", str(x))
    if not s or set(s) == {"0"}:
        return pd.NA
    return s

# Имена / фамилии / отчества с сокращениями 
def _norm_name_token(s: str) -> str:
    s = re.sub(r"\s+", " ", s.strip())
    s = s.replace("—", "-").replace("–", "-")
    return s.lower()

def _is_abbrev_token(tok_short: str, tok_full: str) -> bool:
    ts, tf = tok_short.rstrip("."), tok_full
    return ts and tf.startswith(ts)

def name_abbrev_equal(a, b):
    """I. ~ Ivan; Iv. ~ Ivan; дефисы и регистр игнорируются."""
    if _is_na(a) or _is_na(b):
        return False
    A = _norm_name_token(str(a)); B = _norm_name_token(str(b))
    split_tokens = lambda s: re.split(r"[\s\-]+", s)
    ta, tb = split_tokens(A), split_tokens(B)
    for sa, sb in zip(ta, tb):
        if sa == sb: continue
        if sa.endswith(".") and _is_abbrev_token(sa, sb): continue
        if sb.endswith(".") and _is_abbrev_token(sb, sa): continue
        return False
    return True

# Паспорта
_RU_PASSPORT_RE   = re.compile(r"^\s*(\d{4})\s*(\d{6})\s*$")   # 1234 567890
_INTL_PASSPORT_RE = re.compile(r"^\s*(\d{2})\s*(\d{7})\s*$")   # 12 3456789

def _norm_ru_passport(x):
    m = _RU_PASSPORT_RE.match(str(x)) if not _is_na(x) else None
    return f"{m.group(1)} {m.group(2)}" if m else None

def _norm_intl_passport(x):
    m = _INTL_PASSPORT_RE.match(str(x)) if not _is_na(x) else None
    return f"{m.group(1)} {m.group(2)}" if m else None

def _doc_type(x):
    if _is_na(x): return None
    s = str(x)
    if _RU_PASSPORT_RE.match(s):   return "RU"
    if _INTL_PASSPORT_RE.match(s): return "INTL"
    return "OTHER"

def split_passport_columns(series: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Из одной колонки с документами выделяем RU и INTL, с нормализацией формата."""
    ru_vals, intl_vals = [], []
    for v in series.astype("string"):
        t = _doc_type(v)
        if t == "RU":
            ru_vals.append(_norm_ru_passport(v)); intl_vals.append(pd.NA)
        elif t == "INTL":
            intl_vals.append(_norm_intl_passport(v)); ru_vals.append(pd.NA)
        else:
            ru_vals.append(pd.NA); intl_vals.append(pd.NA)
    return pd.Series(ru_vals, dtype="string"), pd.Series(intl_vals, dtype="string")

def resolve_default(series_left, series_right):
    return series_left.combine_first(series_right)

def resolve_secondname(series_left, series_right):
    def normlen(x):
        if _is_na(x): return -1
        return len(str(x).replace(".", "").strip())
    out = []
    for a, b in zip(series_left, series_right):
        if _is_na(a): out.append(b)
        elif _is_na(b): out.append(a)
        else: out.append(a if normlen(a) >= normlen(b) else b)
    return pd.Series(out, dtype="string")

def to_upper_or_na(x):
    if _is_na(x): return x
    return str(x).upper()

NAME_COLS = ["FirstName", "LastName", "SecondName"]
GEO_COLS  = ["CityFrom", "CityTo", "CountryFrom", "CountryTo"]
AIR_COLS  = ["From", "Dest", "CodeShare", "FareBasisCode", "TravelClass", "AgentInfo"]

FORMATTERS = {
    **{c: to_upper_or_na for c in NAME_COLS},
    **{c: to_upper_or_na for c in GEO_COLS},
    **{c: to_upper_or_na for c in AIR_COLS},
    "Sex": to_upper_or_na,
}

RULES = {
    "FirstName":   name_abbrev_equal,
    "LastName":    name_abbrev_equal,
    "SecondName":  name_abbrev_equal,
}

RESOLVERS = {
    "SecondName":        resolve_secondname,
}

def read_clean(path):
    df = pd.read_csv(path, sep=SEP, dtype="string", keep_default_na=False, index_col=None)
    df = df.replace(NA_VALUES, pd.NA)

    for c in tqdm(df.columns, desc=f"Чистим и форматируем: {path}", leave=False):
        if pd.api.types.is_string_dtype(df[c]):
            df[c] = df[c].str.strip().str.replace(r"\s{2,}", " ", regex=True)
            if "date" in c.lower():  # DepartDate/ArrivalDate/BirthDate
                parsed = pd.to_datetime(df[c], errors="coerce", dayfirst=True)
                df[c] = parsed.dt.strftime("%d.%m.%Y").replace("NaT", pd.NA)

    if "ETicketNumber" in df.columns:
        df["ETicketNumber"] = df["ETicketNumber"].map(normalize_eticket).astype("string")

    if "PassengerDocument" in df.columns:
        ru, intl = split_passport_columns(df["PassengerDocument"])
        df["PassengerDocument_RU"]   = ru
        df["PassengerDocument_INTL"] = intl
        df = df.drop(columns=["PassengerDocument"])

    return df

def compare_value(col, a, b):
    func = RULES.get(col)
    try:
        if func is None:
            return ci_equal(a, b)
        res = func(a, b)
        if res is None or res is NotImplemented:
            return ci_equal(a, b)
        return bool(res)
    except Exception:
        return ci_equal(a, b)

def merge_datasets(df1, df2, key_cols):
    cols1 = [c for c in df1.columns if c not in key_cols]
    cols2 = [c for c in df2.columns if c not in key_cols]
    base_cols   = sorted(set(cols1) | set(cols2))
    common_cols = sorted(set(cols1) & set(cols2))

    df1r = df1.rename(columns={c: f"{c}__tab" for c in cols1})
    df2r = df2.rename(columns={c: f"{c}__csv" for c in cols2})
    for k in key_cols:
        df1r[k] = df1[k]
        df2r[k] = df2[k]

    merged = pd.merge(df1r, df2r, on=key_cols, how="outer")
    conflict_mask = pd.Series(False, index=merged.index)

    for c in tqdm(common_cols, desc="Проверка конфликтов", leave=False):
        ct, cc = f"{c}__tab", f"{c}__csv"
        both = merged[ct].notna() & merged[cc].notna()
        if both.any():
            same = merged.loc[both].apply(lambda r: compare_value(c, r[ct], r[cc]), axis=1)
            conflict_mask.loc[both] |= ~same

    conflict_keys = merged.loc[conflict_mask, key_cols].drop_duplicates()

    # исключаем конфликтные ключи из результата
    if not conflict_keys.empty:
        nonconf = merged.merge(conflict_keys.assign(_flag=1), on=key_cols, how="left")
        nonconf = nonconf[nonconf["_flag"].isna()].drop(columns="_flag")
    else:
        nonconf = merged.copy()

    out = pd.DataFrame({k: nonconf[k] for k in key_cols})
    for c in tqdm(base_cols, desc="Коалесценс полей", leave=False):
        ct, cc = f"{c}__tab", f"{c}__csv"
        resolver = RESOLVERS.get(c, resolve_default)
        if ct in nonconf and cc in nonconf:
            out[c] = resolver(nonconf[ct], nonconf[cc])
        elif ct in nonconf:
            out[c] = nonconf[ct]
        elif cc in nonconf:
            out[c] = nonconf[cc]
        else:
            out[c] = pd.NA

    # форматирование
    for col, fmt in FORMATTERS.items():
        if col in out.columns:
            out[col] = out[col].map(fmt)

    return out, conflict_keys, merged

def apply_desired_order(df: pd.DataFrame) -> pd.DataFrame:
    for c in DESIRED_ORDER:
        if c not in df.columns:
            df[c] = pd.NA
    head = [c for c in DESIRED_ORDER if c in df.columns]
    tail = [c for c in df.columns if c not in DESIRED_ORDER]
    return df[head + tail]

def main():
    ap = argparse.ArgumentParser(description="Слияние CSV с локальными правилами/нормализацией.")
    ap.add_argument("file1", help="Первый CSV")
    ap.add_argument("file2", help="Второй CSV")
    ap.add_argument("outfile", help="Итоговый файл")
    ap.add_argument("--keys", nargs="+", required=True, help="Ключевые колонки для объединения")
    ap.add_argument("--conflict1", default="conflict_1.csv", help="Файл конфликтов из первого источника")
    ap.add_argument("--conflict2", default="conflict_2.csv", help="Файл конфликтов из второго источника")
    args = ap.parse_args()

    df1 = read_clean(args.file1)
    df2 = read_clean(args.file2)

    miss1 = [c for c in args.keys if c not in df1.columns]
    miss2 = [c for c in args.keys if c not in df2.columns]
    if miss1 or miss2:
        raise SystemExit(f"Нет ключей: в {args.file1} отсутствуют {miss1}, в {args.file2} отсутствуют {miss2}")

    out, conflict_keys, _ = merge_datasets(df1, df2, args.keys)

    out = apply_desired_order(out)

    out = out.fillna("N/A")
    out.to_csv(args.outfile, sep=SEP, index=False)

    if not conflict_keys.empty:
        ktuple = conflict_keys[args.keys].fillna("").astype(str).agg("|".join, axis=1)
        df1_conf = df1[df1[args.keys].fillna("").astype(str).agg("|".join, axis=1).isin(ktuple)]
        df2_conf = df2[df2[args.keys].fillna("").astype(str).agg("|".join, axis=1).isin(ktuple)]
    else:
        df1_conf = df1.iloc[0:0].copy()
        df2_conf = df2.iloc[0:0].copy()

    df1_conf.to_csv(args.conflict1, sep=SEP, index=False)
    df2_conf.to_csv(args.conflict2, sep=SEP, index=False)

    print("Готово.")
    print(f"  Итог без конфликтов: {args.outfile} — {len(out)} строк.")
    print(f"  Конфликтных ключей: {len(conflict_keys)}")
    print(f"  См. {args.conflict1} и {args.conflict2}")

if __name__ == "__main__":
    main()
