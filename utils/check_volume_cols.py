# -*- coding: utf-8 -*-
"""深度检查两表是否含蓄积量(volume)字段，以及关键表的蓄积相关列。"""
import pyodbc

DRIVER = "Microsoft Access Driver (*.mdb, *.accdb)"
PATHS = [
    "data/inventory/pureforest/Ifn3p09.accdb",
    "data/inventory/pureforest/Sig_09.accdb",
]
VOL_KEYWORDS = ["vol", "vcc", "vsc", "abi", "area", "exist", "fcc"]


def cols_of(cur, table):
    cur.execute(f'SELECT TOP 1 * FROM "{table}"')
    return [d[0] for d in cur.description]


for p in PATHS:
    print("=" * 70)
    print("DB:", p)
    conn = pyodbc.connect(rf"DRIVER={{{DRIVER}}};DBQ={p};")
    cur = conn.cursor()
    tables = [r.table_name for r in cur.tables()
              if r.table_type == "TABLE" and not r.table_name.startswith("MSys")]
    print("表:", tables)
    # 检查每个表里是否有蓄积量相关字段
    for t in tables:
        try:
            cols = cols_of(cur, t)
        except Exception as e:
            print(f"  表 {t}: 读取失败 {e}")
            continue
        hits = [c for c in cols if any(k in c.lower() for k in VOL_KEYWORDS)]
        if hits:
            print(f"  表 {t} 含蓄积相关字段: {hits}")
    conn.close()
