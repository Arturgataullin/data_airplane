# -*- coding: utf-8 -*-
"""
home_airports.py
Отбор пассажиров без «домашнего» аэропорта
и выгрузка их исходных строк в отдельный CSV.

Запуск:
    python home_airports.py
"""
import os
import pandas as pd
import numpy as np
from collections import defaultdict

# ===================== НАСТРОЙКИ =====================
IN_FILE = "input.csv"
OUT_SUSP_ROWS = "output_rows.csv"
OUT_SUSP_IDENT = "output_metrics.csv"

SEP = ";"
CHUNKSIZE = 2000000
MIN_FLIGHTS_FOR_ANALYSIS = 2

# Пороговые условия «нет домашнего аэропорта»
MIN_TOP1_RATIO = 0.2       # если доля топ-1 < 0.6 -> подозрительно
MAX_UNIQUE_FROM = 20        # если уникальных From > 2 -> подозрительно

# Приоритетные идентификаторы
ID_PRIORITY = [
    "ETicketNumber",
    "LoyaltyNumberDT","LoyaltyNumberFB","LoyaltyNumberKE","LoyaltyNumberSU",
    "PassengerDocument_RU","PassengerDocument_INTL",
    "CardNumber"
]

FALLBACK_COLS = ["FirstName", "LastName", "BirthDate"]
# =====================================================

def normalize_str_series(s: pd.Series) -> pd.Series:
    return s.astype(str).str.strip().replace({"": pd.NA, "NA": pd.NA, "N/A": pd.NA, "None": pd.NA})

def build_identity_vectorized(df: pd.DataFrame) -> pd.Series:
    s = pd.Series(pd.NA, index=df.index, dtype="object")
    for col in ID_PRIORITY:
        if col in df.columns:
            colval = normalize_str_series(df[col])
            mask = s.isna() & colval.notna()
            s.loc[mask] = col + "::" + colval.loc[mask].astype(str)
    fallback_mask = s.isna()
    if fallback_mask.any():
        f = df.get(FALLBACK_COLS[0], "").astype(str).str.strip().replace({"": pd.NA})
        for c in FALLBACK_COLS[1:]:
            f = f.fillna("") + "_" + df.get(c, "").astype(str).str.strip().replace({"": ""})
        f = f.str.strip("_").replace({"": pd.NA})
        s.loc[fallback_mask & f.notna()] = "NAME::" + f.loc[fallback_mask & f.notna()].astype(str)
    return s

def pass1_collect_stats(in_file: str, sep: str, chunksize: int):
    total = defaultdict(int)
    from_counts = defaultdict(int)

    fn_counts = defaultdict(lambda: defaultdict(int))
    ln_counts = defaultdict(lambda: defaultdict(int))

    usecols = None
    it = pd.read_csv(in_file, sep=sep, dtype=str, keep_default_na=False,
                     chunksize=chunksize, usecols=usecols)

    for chunk in it:
        chunk["__identity"] = build_identity_vectorized(chunk)

        chunk = chunk[chunk["__identity"].notna()]
        if chunk.empty:
            continue

        from_valid = chunk["From"].astype(str).str.strip()
        mask_from = from_valid.astype(bool)

        for ident, cnt in chunk["__identity"].value_counts().items():
            total[ident] += int(cnt)
        sub = chunk.loc[mask_from, ["__identity", "From"]].copy()
        if not sub.empty:
            sub["From"] = sub["From"].astype(str).str.strip()
            vc = sub.groupby(["__identity", "From"]).size()
            for (ident, frm), cnt in vc.items():
                from_counts[(ident, frm)] += int(cnt)
        if "FirstName" in chunk.columns:
            for ident, s in chunk.groupby("__identity")["FirstName"]:
                m = s.mode()
                key = m.iat[0] if not m.empty else ""
                fn_counts[ident][key] += 1
        if "LastName" in chunk.columns:
            for ident, s in chunk.groupby("__identity")["LastName"]:
                m = s.mode()
                key = m.iat[0] if not m.empty else ""
                ln_counts[ident][key] += 1

    def pick_mode(counter_dict):

        out = {}
        for ident, subd in counter_dict.items():
            if not subd:
                out[ident] = ""
                continue
            out[ident] = max(subd.items(), key=lambda kv: kv[1])[0]
        return out

    first_mode = pick_mode(fn_counts)
    last_mode  = pick_mode(ln_counts)

    return total, from_counts, first_mode, last_mode

def compute_metrics_and_flag(total, from_counts, first_mode, last_mode):
    per_ident = defaultdict(list)
    for (ident, frm), cnt in from_counts.items():
        per_ident[ident].append((frm, cnt))

    rows = []
    for ident, tot in total.items():
        pairs = per_ident.get(ident, [])
        pairs.sort(key=lambda x: x[1], reverse=True)
        n_unique = len(pairs)
        top1 = pairs[0][0] if n_unique >= 1 else ""
        top1_count = pairs[0][1] if n_unique >= 1 else 0
        top1_ratio = round(top1_count / tot, 3) if tot > 0 else 0.0

        no_home = (n_unique > MAX_UNIQUE_FROM) or (top1_ratio < MIN_TOP1_RATIO)
        rows.append({
            "identity": ident,
            "FirstName": first_mode.get(ident, ""),
            "LastName": last_mode.get(ident, ""),
            "total_flights": tot,
            "n_unique_from": n_unique,
            "top1": top1,
            "top1_count": top1_count,
            "top1_ratio": top1_ratio,
            "no_home_airport": no_home
        })

    df = pd.DataFrame(rows)
    if df.empty:
        return df, set()

    df = df[df["total_flights"] >= MIN_FLIGHTS_FOR_ANALYSIS].copy()
    suspicious = df[
        (df["n_unique_from"] > MAX_UNIQUE_FROM) | (df["top1_ratio"] < MIN_TOP1_RATIO)
    ].copy()

    id_set = set(suspicious["identity"]) if not suspicious.empty else set()
    return suspicious.sort_values(["no_home_airport","total_flights"], ascending=[False, False]), id_set

def pass2_dump_rows(in_file: str, sep: str, chunksize: int, id_set: set, out_path: str):
    if not id_set:
        head = pd.read_csv(in_file, sep=sep, nrows=0, dtype=str, keep_default_na=False)
        head.to_csv(out_path, sep=sep, index=False)
        return

    write_header = True
    it = pd.read_csv(in_file, sep=sep, dtype=str, keep_default_na=False, chunksize=chunksize)
    for chunk in it:
        chunk["__identity"] = build_identity_vectorized(chunk)
        mask = chunk["__identity"].isin(id_set)
        part = chunk.loc[mask].drop(columns=["__identity"])
        if part.empty:
            continue
        part.to_csv(out_path, sep=sep, index=False, mode="w" if write_header else "a",
                    header=write_header)
        write_header = False

def main():
    if not os.path.exists(IN_FILE):
        raise FileNotFoundError(f"Не найден входной файл: {IN_FILE}")

    print("Проход 1: считаем метрики...")
    total, from_counts, first_mode, last_mode = pass1_collect_stats(IN_FILE, SEP, CHUNKSIZE)
    print(f"Уникальных identity: {len(total)}")

    print("Формируем таблицу подозрительных...")
    susp_df, id_set = compute_metrics_and_flag(total, from_counts, first_mode, last_mode)

    susp_df.to_csv(OUT_SUSP_IDENT, sep=SEP, index=False)
    print(f"Сохранено: {OUT_SUSP_IDENT} (подозрительных: {len(id_set)})")

    print("Проход 2: выгружаем строки исходного CSV для подозрительных identity...")
    pass2_dump_rows(IN_FILE, SEP, CHUNKSIZE, id_set, OUT_SUSP_ROWS)
    print(f"Готово: {OUT_SUSP_ROWS}")

if __name__ == "__main__":
    main()
