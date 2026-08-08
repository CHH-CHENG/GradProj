# -*- coding: utf-8 -*-
"""检查 Access 数据库(.accdb)的表结构：表名、行数、字段、样例。

用法：
    D:/A_PDE/miniconda3/envs/GradProj/python.exe utils/inspect_accdb.py <db_path> [--rows N]
"""
import sys
import pyodbc

DRIVER = "Microsoft Access Driver (*.mdb, *.accdb)"


def connect(db_path):
    conn_str = r"DRIVER={%s};DBQ=%s;" % (DRIVER, db_path)
    return pyodbc.connect(conn_str)


def list_tables(cursor):
    tables = []
    for row in cursor.tables():
        # 只取用户表，跳过系统表(以 MSys 开头)
        if row.table_type == "TABLE" and not row.table_name.startswith("MSys"):
            tables.append(row.table_name)
    return tables


def inspect(db_path, max_rows=5):
    print("=" * 70)
    print("DB:", db_path)
    conn = connect(db_path)
    cur = conn.cursor()
    tables = list_tables(cur)
    print("表数量:", len(tables))
    for t in tables:
        print("-" * 70)
        print("表:", t)
        try:
            cur.execute(f'SELECT COUNT(*) FROM "{t}"')
            n = cur.fetchone()[0]
            print("  行数:", n)
        except Exception as e:
            print("  行数获取失败:", e)
            n = None
        # 字段
        cols = []
        try:
            cols = [(c.column_name, c.type_name, c.column_size)
                    for c in cur.columns(table=t)]
            for name, typ, size in cols:
                print(f"    - {name}  ({typ}{'('+str(size)+')' if size else ''})")
        except Exception as e:
            print("  字段获取失败:", e)
            continue
        # 样例
        if n and n > 0:
            col_names = [c[0] for c in cols]
            try:
                cur.execute(f'SELECT TOP {max_rows} * FROM "{t}"')
                rows = cur.fetchall()
                print("  前%d行样例:" % min(max_rows, n))
                print("    ", col_names)
                for r in rows:
                    try:
                        print("    ", list(r))
                    except Exception as e:
                        print("    样例解码失败:", e)
                        break
            except Exception as e:
                print("  样例获取失败:", e)
    conn.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    db = sys.argv[1]
    n = int(sys.argv[sys.argv.index("--rows") + 1]) if "--rows" in sys.argv else 5
    inspect(db, n)
