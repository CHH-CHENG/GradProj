# 纯林样地调查数据目录

放置纯林样地调查数据（西班牙 IFN3 — 第3次国家森林清查，布尔戈斯省 Burgos，省码 09）。

## 放置的数据

| 文件            | 说明                      |
| ----------------- | --------------------------- |
| `Ifn3p09.accdb` | IFN3 野外调查**原始数据库**（每木检尺、样地因子，**无蓄积量**） |
| `Sig_09.accdb`  | IFN3 **处理结果数据库**（含样地/每木蓄积量 VCC/VSC、材积方程 TarifasIFN3） |

## 数据类型

- Access 数据库（ACCDB），可用 `pyodbc` + `Microsoft Access Driver (*.mdb, *.accdb)` 读取
- 注意：此 pandas(2.3) 会把 `pyodbc.Row` 当标量，构建 DataFrame 需 `[list(r) for r in rows]`

## 数据内部格式（经核查）

### 编号与单位规则
- **`Estadillo`**：样地编号（4 位字符串，如 `'0001'`），其整数值 = `Listado Definitivo.Orden`（作为两库关联键）。
- **`Cla`**：样地类别（`A` 等；`PCDetTabla` 中 0=正常样地、1=不可达）。
- **`Subclase`**：样地亚类（`1`、`4` 等）。
- **`Especie`**：3~4 位西班牙树种代码（本库出现：002/003/004/011/021/028/041/042/050/071/090 等；`EspDominante` 含主要优势树种的拉丁名，完整代码对照需官方 IFN3 树种表）。
- **`CD`**：径阶（cm，胸径分档），共 13 档：10,15,20,…,70（每 5 cm 一档）。
- **单位约定**：胸径 `Dn1/Dn2`=mm、树高 `Ht`=m、株数 `NPies`=株/ha、断面积 `ABas`/`G`=m²/ha（`G` 在 Mayores_exs 为单株 m²）、蓄积 `VCC/VSC`=m³/ha（Parcelas_exs）或 dm³（Mayores_exs 每木）、`IAVC`=年蓄积生长量、`VLE`=薪材/剩余材积、`Fac`=公顷扩展因子。

### Ifn3p09.accdb —— 野外调查原始库（14 表）

#### 关键表字段
| 表 | 行数 | 字段明细 |
| --- | --- | --- |
| `PCMayores`（每木检尺） | 53780 | Estadillo, Cla, Subclase, nArbol, OrdenIf3, OrdenIf2, Rumbo, Distanci, Especie, **Dn1, Dn2（胸径 mm）, Ht（树高 m）**, Calidad, Forma, ParEsp, Agente, Import, Elemento, Compara |
| `PCParcelas`（样地因子） | 2970 | Provincia, Estadillo, Cla, Subclase, Tipo, Vuelo1/2, Pasada1/2, Foto1/2, **Ano（清查年份）**, INE, Nivel1/2/3, **FccTot, FccArb（冠层盖度）**, DisEsp, ComEsp, Rocosid, Textura, MatOrg, PhSuelo, FechaPh, HoraPh, TipSuelo1/2/3, MErosiva, ModComb, EspCMue, PresReg, EfecReg, CortaReg, MejVue1/2, MejSue1/2, **Orienta1/2, MaxPend1/2（朝向/坡度）**, Localiza, Acceso, Levanta, Obser, Equipo, JefeEq, FechaIni, HoraIni, FechaFin, HoraFin, Tiempo, Resid, RumboF1/2, DistFoto, CarFoto1/2, NumFoto1/2, ConFoto1/2, Estado, Tecnico |
| `Listado Definitivo`（坐标） | 2916 | Provincia, **Orden（=样地编号）**, Clase, SubClase, Hoja, Pasada, Foto, Vuelo, **CoorX, CoorY（UTM 30N，米）**, Ine, Nivel1, **FccArb**, DistEsp, CompEsp, Especie1/2/3, Ocupa1/2/3, Estado1/2/3 |
| `PCEspParc`（样地树种组成） | 5300 | Estadillo, Cla, Subclase, PosEsp, Especie, Ocupa, Estado, FPMasa, **Edad**, FInfor, Fiabil, Barrena1/2/3, AltPer, OrgMasa1/2, TratMasa |
| `PCTablaEsp`（树种参数） | 95 | Especie, **DnMin, DnMax, DifDnMax, HtMin, HtMax, DnHtMin, DnHtMax**, HmRegMax, LForma |

#### 其他表
`PCDetTabla`(1055, 码表 CodTabla/Valor/DenValor)、`PCEspMapa`(5495, 图上树种)、`PCMatorral`(10614, 灌丛 Fcc/Hm)、`PCRegenera`(17495, 更新)、`PCMayores2`(34024, 每木字符串版)、`PCNueEsp`(13165)、`PCDatosMap`(2916, 样地定位)、`Uso2Nivel1`(7)、`Errores de conversión`(3, 旧库转换日志，可忽略)。

> 注：`PCDatosMap` 字段名含特殊字符，`pyodbc` 的 `cursor.columns()` 读取该表列信息会报 `utf-16-le` 解码错误，但 `SELECT` 正常，用 `cursor.description` 取列名即可。

### Sig_09.accdb —— 处理结果库（11 表）—— **蓄积量在此库**

#### 关键表字段
| 表 | 行数 | 字段明细 |
| --- | --- | --- |
| `Parcelas_exs`（**样地级蓄积**） | 13387 | Estrato, Estadillo, Cla, Subclase, Especie, CD, **NPies(株/ha), ABas(m²/ha), VCC(带皮 m³/ha), VSC(去皮 m³/ha), IAVC, VLE** |
| `Mayores_exs`（**每木蓄积**） | 47288 | Estadillo, Cla, Subclase, nArbol, OrdenIf3, OrdenIf2, Rumbo, Distanci, Especie, EspecieOriginal, Dn1, Dn2, Ht, Calidad, Forma, ParEsp, Agente, Import, Elemento, Estrato, CD, **G(单株断面积 m²), VCC, VSC, IAVC, VLE, Fac(公顷扩展因子)** |
| `Estratos_exs`（地层汇总） | 1457 | Estrato, Especie, CD, NPies, ABas, VCC, VSC, IAVC, VLE |
| `TarifasIFN3`（**材积方程**） | 1136 | PROVINCIA, ESPECIE, FORMA, PARAMET, **CPARAM(VCC/VSC/IAVC/VLE)**, CALIDAD, CLASE, MODELO, CUADRO, SISTGEOG, PARESP, APLIC, OBSERV, NUM, R2, R2A, **AA~TT（方程系数）**, ESTR（方程来源，如 `IFN2;P09;E076;F1`） |
| `Estratos`（地层定义） | 31 | Estrato, NPar, Superficie, IdEspDom |
| `EspDominante` | 14 | IdEspDom, EspDom（如 `Pinus sylvestris`、`Pinus pinaster`） |

#### 示例行（Estadillo=0001，样地总蓄积 ≈ 179.9 m³/ha）
| Especie | CD | NPies(株/ha) | ABas(m²/ha) | VCC(m³/ha) |
| --- | --- | --- | --- | --- |
| 028 | 30 | 14.15 | 0.977 | 5.94 |
| 042 | 50 | 20.37 | 3.996 | 19.15 |
| 071 | 15 | 63.66 | 1.071 | 4.47 |
| 090 | 20 | 31.83 | 0.846 | 2.31 |

#### 其他表
`CambioEspecie`(83)、`CambioEspecieReg`(82)（树种代码变更映射）、`Poligon`(23451)、`Parcpoly`(2829)（多边形/样地归属，字段名同样含特殊字符）、`Errores de conversión`(1)。

## 关键结论（蓄积量数据可用性核查）

- ✅ **样地级蓄积量(m³/ha) 现成可用**：`Sig_09.accdb → Parcelas_exs` 按样地+树种+径阶给出 VCC/VSC，单位已归一化为每公顷（NPies=株/ha），按样地求和即得样地总蓄积。
- ✅ **坐标可关联**：`Listado Definitivo.Orden ↔ Estadillo`（整数一致），2449 个样地同时具备坐标+蓄积。
- ✅ **样本量充足**：蓄积>0 样地 2449 个；纯林（仅 1 树种有蓄积）1339 个；样地总蓄积范围 0.6~594 m³/ha，均值约 92 m³/ha。
- ⚠️ **时间错位**：清查年份约 2003（PCParcelas.Ano），与本项目 2023 年 Sentinel-2 影像相差约 20 年。
- ⚠️ **地点错位**：数据在西班牙布尔戈斯（UTM 30N），与当前中国研究区（107°E, 34.3°N）不重合，无法直接用于现有 ROI 影像建模。
- ℹ️ `Ifn3p09.accdb` 无蓄积量；如需从原始每木(胸径/树高)自行计算，可用 `TarifasIFN3` 方程。
