# -*- coding: utf-8 -*-
"""验证 Sig_09.accdb / Ifn3p09.accdb 是否满足蓄积量建模需求。"""
import pyodbc

DRIVER = "Microsoft Access Driver (*.mdb, *.accdb)"
IFN = "data/inventory/pureforest/Ifn3p09.accdb"
SIG = "data/inventory/pureforest/Sig_09.accdb"


def conn(p):
    return pyodbc.connect(rf"DRIVER={{{DRIVER}}};DBQ={p};")


c_ifn = conn(IFN).cursor()
c_sig = conn(SIG).cursor()

print("### 1. Parcelas_exs 样地/树种/径阶数量与 VCC 汇总 ###")
c_sig.execute('SELECT COUNT(*) FROM (SELECT DISTINCT "Estadillo" FROM "Parcelas_exs")')
print("不同样地(Estadillo)数:", c_sig.fetchone()[0])
c_sig.execute('SELECT COUNT(*) FROM (SELECT DISTINCT "Estadillo","Cla","Subclase" FROM "Parcelas_exs")')
print("不同样地(Estadillo+Cla+Subclase)数:", c_sig.fetchone()[0])
c_sig.execute('SELECT COUNT(*) FROM (SELECT DISTINCT "Especie" FROM "Parcelas_exs")')
print("不同树种数:", c_sig.fetchone()[0])
c_sig.execute('SELECT COUNT(*) FROM (SELECT DISTINCT "CD" FROM "Parcelas_exs")')
print("不同径阶(CD)数:", c_sig.fetchone()[0])

print("\n### 2. 单个样地(Estadillo=0001)按物种×径阶 VCC, 验证 m³/ha 归一化 ###")
c_sig.execute('SELECT "Especie","CD","NPies","ABas","VCC" FROM "Parcelas_exs" WHERE "Estadillo"=\'0001\' AND "Cla"=\'A\' ORDER BY "Especie","CD"')
rows = c_sig.fetchall()
for r in rows:
    print(f"  种{r[0]} 径阶{r[1]}: NPies={r[2]:.2f}/ha  ABas={r[3]:.3f}m2/ha  VCC={r[4]:.3f}m3/ha")
tot = sum(r[4] for r in rows)
n = sum(r[2] for r in rows)
print(f"  -> 样地0001 总蓄积 VCC ≈ {tot:.2f} m³/ha, 总株数 ≈ {n:.2f} 株/ha")

print("\n### 3. Mayores_exs 每木蓄积样例 + Fac(扩展因子) ###")
c_sig.execute('SELECT TOP 3 "Estadillo","Especie","Dn1","Ht","G","VCC","Fac" FROM "Mayores_exs"')
for r in c_sig.fetchall():
    print(f"  样地{r[0]} 种{r[1]}: D={r[2]}mm H={r[3]}m G={r[4]:.4f}m2 VCC={r[5]:.2f}dm3 Fac={r[6]}")

print("\n### 4. TarifasIFN3 方程数量(按 VCC/VSC) ###")
c_sig.execute('SELECT "CPARAM", COUNT(*) FROM "TarifasIFN3" GROUP BY "CPARAM"')
for r in c_sig.fetchall():
    print("  ", r)

print("\n### 5. Estrato 定义(地层/优势树种/样地数) ###")
c_sig.execute('SELECT "Estrato","NPar","IdEspDom" FROM "Estratos" ORDER BY "Estrato"')
for r in c_sig.fetchall():
    print(f"  地层{r[0]}: 样地数={r[1]}")

print("\n### 6. 坐标来源: Listado Definitivo (UTM) ###")
c_ifn.execute('SELECT TOP 5 "Orden","Clase","SubClase","CoorX","CoorY","FccArb" FROM "Listado Definitivo"')
for r in c_ifn.fetchall():
    print(f"  Orden={r[0]} Clase={r[1]} SubClase={r[2]} CoorX={r[3]} CoorY={r[4]} FccArb={r[5]}")

print("\n### 7. 关联键检查: PCParcelas.Estadillo 与 Parcelas_exs.Estadillo 是否对应 ###")
c_ifn.execute('SELECT TOP 5 "Estadillo","Cla","Subclase","FccTot","FccArb" FROM "PCParcelas"')
for r in c_ifn.fetchall():
    print(f"  PCParcelas: Estadillo={r[0]} Cla={r[1]} Subclase={r[2]} FccTot={r[3]} FccArb={r[4]}")

print("\n### 8. 样地内 VCC 是否为正/可汇总(抽10个样地) ###")
c_sig.execute('''SELECT TOP 10 "Estadillo", ROUND(SUM("VCC"),2), ROUND(SUM("VSC"),2), ROUND(SUM("ABas"),2)
                 FROM "Parcelas_exs" GROUP BY "Estadillo" ORDER BY "Estadillo"''')
for r in c_sig.fetchall():
    print(f"  样地{r[0]}: VCC合计={r[1]} m3/ha, VSC={r[2]}, ABas={r[3]} m2/ha")
