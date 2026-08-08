# -*- coding: utf-8 -*-
"""最终关联验证：坐标(Orden) 与 蓄积(Estadillo) 关联 + 样本量统计。"""
import pyodbc
import pandas as pd

D = "Microsoft Access Driver (*.mdb, *.accdb)"
c1 = pyodbc.connect(rf"DRIVER={{{D}}};DBQ=data/inventory/pureforest/Ifn3p09.accdb;").cursor()
c2 = pyodbc.connect(rf"DRIVER={{{D}}};DBQ=data/inventory/pureforest/Sig_09.accdb;").cursor()

c1.execute('SELECT "Orden","CoorX","CoorY","FccArb" FROM "Listado Definitivo"')
rows = c1.fetchall()
ldf = pd.DataFrame([list(r) for r in rows], columns=[d[0] for d in c1.description])
print("ldf shape:", ldf.shape)

c2.execute('SELECT "Estrato","Estadillo","Cla","Subclase","Especie","CD","NPies","ABas","VCC","VSC","IAVC","VLE" FROM "Parcelas_exs"')
rows2 = c2.fetchall()
pdf = pd.DataFrame([list(r) for r in rows2], columns=[d[0] for d in c2.description])

print("坐标表(Listado Definitivo)行数:", len(ldf))
print("蓄积表(Parcelas_exs)行数:", len(pdf), " 不同样地:", pdf["Estadillo"].nunique())

# 样地总蓄积
plot_v = pdf.groupby("Estadillo")[["VCC", "VSC", "ABas"]].sum().reset_index()
plot_v["Estadillo_i"] = plot_v["Estadillo"].astype(int)

# 坐标表 Ordente 关联
ldf["Orden_i"] = ldf["Orden"].astype(int)
m = plot_v.merge(ldf[["Orden_i", "CoorX", "CoorY", "FccArb"]], left_on="Estadillo_i", right_on="Orden_i", how="inner")
print("能关联到坐标的蓄积样地数:", m.shape[0])
print("有蓄积(总VCC>0)样地数:", (plot_v["VCC"] > 0).sum())
print("纯林(仅1树种有蓄积)样地数:", pdf[pdf.VCC > 0].groupby("Estadillo")["Especie"].nunique().eq(1).sum())
print("样地总VCC m3/ha: min=%.1f max=%.1f mean=%.1f" % (
    plot_v.VCC.min(), plot_v.VCC.max(), plot_v.VCC.mean()))
print("\n关联示例(前5):")
print(m.head()[["Estadillo", "CoorX", "CoorY", "VCC", "FccArb"]].to_string(index=False))
print("\nCoorX/CoorY 分布(UTM 米):")
print(m[["CoorX", "CoorY"]].agg(["min", "max"]).to_string())
