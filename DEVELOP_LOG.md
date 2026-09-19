# 开发日志

> 📌 本文件记录**当前（西班牙 IFN4）阶段**的开发日志。
> 历史日志（2026-08-06 ~ 2026-09-18，项目初始化 / 中国测试 / 芬兰阶段）已归档至
> [`DEVELOP_LOG_ARCHIVE.md`](./DEVELOP_LOG_ARCHIVE.md)。

---

## **开发日志模板（必须统一）**

### 【日期】：（填写日期） 第{}条

#### 【操作类型】

（必须选择）

- 新增模块
- 修改结构
- 修复Bug
- 优化逻辑

#### 【修改目的】

说明为什么要做这个修改

#### 【修改内容】

具体改了什么（文件 + 内容）

#### 【影响范围】

说明影响到哪些模块/文件

#### 【当前状态/结果】

- 是否完成
- 是否可运行

#### 【存在问题】

当前已经完成的内容里面，已发现，但仍未解决的问题

#### 【下一步计划】

明确下一步要做什么

#### 【AI辅助记录】

- AI做了什么（必须标注清楚）
- 人工是否修改

---

## **开发日志记录：**

### 2026-09-18 第1条

#### 【操作类型】

- 修改结构

#### 【修改目的】

项目正式开展前的重构整备：研究区由**芬兰**切换至**西班牙 IFN4**，清理芬兰阶段数据/代码残留，
修正被散落的脚本目录归属，归档历史日志，统一文档与信息索引。

#### 【修改内容】

**代码归位与去芬兰化：**

- `download_spain.py` → `downloader/spain.py`；`estimate_s2_size.py` → `downloader/estimate.py`
  （导入路径改为基于项目根，用法改为 `python -m downloader.spain` / `python -m downloader.estimate`）
- 删除芬兰专用：`download_finland.py`、`preprocess/finland_study.py`、`config/finland_study.yaml`
- `feature/extract.py` 重写为**西班牙版骨架**（移除对已删 `finland_study` 的依赖，
  保留通用函数 `calc_indices` / `compute_slope_aspect`，`build_all()` 待数据就绪后实现）
- `main.py` 重写为**西班牙工作流 CLI**：`download / unzip / roi / extract / subsample / train / all`
- `feature/subsample.py`、`model/rf.py` 去芬兰化：
  分组列 `label`（纯林/混交）→ `province`（省份）；坐标列 `x_3067/y_3067` → `x/y`；
  模型矩阵改为**分省（leon/burgos/lugo）+ 全局**（对比分省/合并建模）
- 新增 `config/spain_study.yaml`（三省调查年/S2 年份/EPSG/bbox/样地数、采样参数、数据路径）、
  `config/copernicus.example.yaml`（无凭据模板）
- `config/preprocess.yaml` 研究区中心改为西班牙 León（初步占位，待样地分布统计后确定）

**文档整理：**

- `DEVELOP_LOG.md`：历史日志归档至 `DEVELOP_LOG_ARCHIVE.md`，本日志归零（保留统一模板）
- `项目开发文档.docx.md` → **`项目开发文档.md`**（弃用 .docx 展示）；更新结构树、download/feature
  模块脚本说明、第 7 节；第 8 节追加 8.9（研究区切换西班牙决策）与 8.10（决策汇总）
- 全量更新 README：根目录 / `config/` / `downloader/` / `preprocess/` / `feature/` / `model/` /
  `data/` 及 `data/Sentinel2`、`data/inventory`、`data/DEM`、`data/feature` 子目录

#### 【影响范围】

- 根目录、`config/`、`downloader/`、`preprocess/`、`feature/`、`model/`、`data/**/README.md`、
  `DEVELOP_LOG.md`、`DEVELOP_LOG_ARCHIVE.md`、`项目开发文档.md`
- 所有脚本调用方式：根目录散落脚本统一为 `python -m <模块>.<脚本>`

#### 【当前状态/结果】

- ✅ 完成；`python -m compileall`（exit=0）与全模块 import 验证通过（ALL IMPORTS OK）
- `roi` 与 `extract` 步骤为**待实现**状态（分别依赖研究区范围确定、DEM 与样地蓄积量）

#### 【存在问题】

- 西班牙 DEM 尚未获取；IFN4 样地蓄积量需按官方材积公式由 `PCMayores` 计算
- 研究区范围未最终确定（`config/preprocess.yaml` 中为中心占位值）

#### 【下一步计划】

1. 计算 IFN4 样地蓄积量（`PCMayores` → 材积公式）
2. 获取西班牙 DEM（IGN/CNIG MDT 或 Copernicus DEM）
3. 确定研究区范围 → ROI 裁剪（`python main.py roi`）
4. 实现 `feature/extract.py`（样地缓冲窗口 → 17 特征 + GSV → `samples.csv`）
5. `python -m feature.subsample` → `python -m model.rf`（可先 `--smoke`）

#### 【AI辅助记录】

- AI：完成上述全部代码归位/清理、config 与文档全量更新、语法与导入验证
- 人工是否修改：待人工确认

### 2026-09-18 第2条

#### 【操作类型】

- 修改结构

#### 【修改目的】

确定项目解释器环境：由系统环境 `GradProj`（Python 3.10）迁移为**项目本地 `.conda`**（Python 3.13，与代码同目录、自包含），并安装研究方案所需依赖。

#### 【修改内容】

- `.conda`（原为空环境、零依赖）安装全套依赖：
  - 科学计算/机器学习：numpy 2.5.3、pandas 3.0.6、scipy 1.18.1、scikit-learn 1.9.1、xgboost 3.4.1、lightgbm 4.7.0、shap 0.52.0、scikit-image 0.26.0（GLCM）、matplotlib、joblib
  - 遥感/空间：rasterio 1.5.1（自带 GDAL 3.12.4 + `JP2OpenJPEG`）、geopandas 1.1.4、shapely 2.1.2、pyproj 3.8.0、pyogrio 0.13.0
  - 数据读取/网络：pyodbc 5.3.0、pyyaml、requests
- 安装方式说明：`conda install -c conda-forge` 求解失败（Python 3.13 + win-64 下 `libgdal-jp2openjpeg` 与 `libgdal-core`/`libexpat` 冲突）→ 改用 **pip**（rasterio 官方 wheel 自带 GDAL 与 JP2 驱动）
- `environment.yaml` 重写为**精简依赖定义**（原文件为空环境的导出，不含项目依赖）
- 文档同步：`README.md` 5.1 节与第 8 节、`项目开发文档.md` 第 4 节第 5 条（环境规定 → 项目本地 `.conda`）
- 修复 Windows GBK 控制台编码问题：`main.py` / `model/rf.py` / `feature/subsample.py` /
  `downloader/spain.py` / `downloader/estimate.py` 增加 `sys.stdout.reconfigure(errors="replace")`，
  避免输出 `⏳`/`→` 等符号时抛 `UnicodeEncodeError`

#### 【影响范围】

- `.conda`（本地环境）、`environment.yaml`、`README.md`、`项目开发文档.md`

#### 【当前状态/结果】

- ✅ 验证通过：
  - JP2 解码：`JP2OpenJPEG` 驱动可用，成功读取真实 S2 波段（10980×10980、uint16）
  - 项目模块全部导入 OK；重投影 4326→25830 正常
  - ODBC：Microsoft Access Driver 可用（读 `.accdb`）
- ⚠️ 实测发现：S2 产品 CRS 为 **EPSG:32629/32630**（WGS84 / UTM），而 IFN4 样地为 **EPSG:25829/25830**（ETRS89 / UTM）→ 对齐时需做 datum 转换（差异 <1m，但应显式处理）

#### 【存在问题】

- `.conda` 依赖由 pip 管理，conda 不追踪（`conda env export` 会告警）——已用精简 `environment.yaml` 固化
- Python 3.13 / pandas 3.0 为新版本：现有脚本已在新环境验证可导入，运行期 API 差异需在正式跑数据时留意

#### 【下一步计划】

同第 1 条"下一步计划"。

#### 【AI辅助记录】

- AI：环境诊断（发现 `.conda` 为零依赖空环境）、pip 安装全套依赖、JP2/ODBC/重投影实测、`environment.yaml` 重写、文档同步
- 人工是否修改：待确认

### 2026-09-19 第3条

#### 【操作类型】

- 修改结构

#### 【修改目的】

将收敛后的**研究方案 v1**（特征体系与创新点）固化为项目依据，并同步代码/README，
消除"方案 — 代码 — 文档"三者不一致。

#### 【修改内容】

- `项目开发文档.md`：新增 **8.11 研究方案 v1**，含：
  方案定位（Method Enhancement / 特征工程优化型）、模型框架、**21 特征表**、
  3 条创新点（结构信息引入 / 多尺度受控设计 / 数据约束下的特征设计）、
  实验设计（含单变量消融修正）、答辩常见质疑应对、落地前置条件
- `feature/extract.py`：docstring 与特征常量按 v1 重写
  - 21 特征分组定义：`SPECTRAL_BANDS` / `INDEX_FEATURES` / `MULTISCALE_FEATURES` /
    `TEXTURE_FEATURES` / `NEIGHBOR_FEATURES` / `TERRAIN_FEATURES` → `FEATURES`
  - `calc_indices` 由 10 波段（含 B11/B12、EVI）改为 **8 波段**，返回 `(NDVI, NDWI, NDRE)`
  - 标注待确认项：SWIR（B11/B12）是否纳入
- `feature/README.md`：特征清单由 17 → **21**（对齐 v1，含尺度依据说明）
- `model/rf.py`：`FEATURES` 改为 `from feature.extract import FEATURES`
  （**单一来源**，避免特征定义在两处维护）

#### 【影响范围】

- `项目开发文档.md`（8.11）、`feature/extract.py`、`feature/README.md`、`model/rf.py`

#### 【当前状态/结果】

- 完成；`compileall` 与模块导入验证通过（`FEATURES` 共 21 个）
- 特征定义现由 `feature/extract.py` **单一维护**，`model/rf.py` 引用之

#### 【存在问题】

- 特征清单仍有 **2 处待确认**：
  1. **SWIR（B11/B12）是否纳入** —— v1 方案未列，但文献中 SWIR 对生物量/蓄积量贡献显著；
  2. **100m 邻域**（超出 IFN4 样地 25m 半径）的合理性需在论文中论证
- ⛔ 蓄积量标签 y 仍未计算（唯一真实阻塞）

#### 【下一步计划】

1. 计算 IFN4 样地蓄积量 y（`PCMayores` → 官方材积公式）
2. 确认特征清单（含 B11/B12 取舍）与消融策略
3. 实现 `feature/extract.py`

#### 【AI辅助记录】

- AI：整理方案决策与创新点入开发文档 8.11、同步 `extract.py`/`rf.py`/`feature README`、语法与导入校验
- 人工是否修改：待确认

### 2026-09-19 第4条

#### 【操作类型】

- 修改结构

#### 【修改目的】

① 落地 **SWIR 决策（选择 B：纳入 B11/B12）**；
② 全面整理文档与代码归位，消除所有"方案 — 代码 — 文档"不一致。

#### 【修改内容】

**SWIR 决策（B）落地：**

- `feature/extract.py`：`SPECTRAL_BANDS` 加入 `B11`/`B12` → 基础光谱 10 个，`FEATURES` 由 21 → **23 个**
- `项目开发文档.md` 8.11：C 表①改为 10 波段、合计改 23；新增"SWIR 决策"说明；G 表第 2 条标记为**已确认**
- `feature/README.md`、`data/feature/README.md`：特征清单同步为 23（含分组明细）
- `model/rf.py` docstring、`model/README.md`：特征描述由旧 17（含 EVI）更新为 v1 的 **23 特征**

**文档整理与归位：**

- 根目录 `方案探讨.txt` → **`docs/研究方案_探讨记录.md`**（新建 `docs/` 目录，附 `README.md`）；
  8.11 来源注与根 README 结构树同步更新
- 根 `README.md`：第 2 节路线图特征部分改为 v1 的 6 组特征；修正"11 已就绪"错字；
  加入 8.11 研究方案索引；结构树补充 `docs/`
- `项目开发文档.md` 3.2 节：`feature/extract.py` 特征类型改为 v1 的 23 特征分组
  （删除过时的 EVI、"可选纹理"表述）
- 清除全部 `__pycache__`（含已删芬兰模块 `finland_study.cpython-310.pyc` 残留）

#### 【影响范围】

- 根 `README.md`、`项目开发文档.md`、`docs/`、`feature/*`、`model/*`、`data/feature/README.md`

#### 【当前状态/结果】

- ✅ **文档 — 代码 — 磁盘结构三者一致**
- ✅ `FEATURES` = 23（`SPECTRAL_BANDS` 含 B11/B12），`model/rf.py` 经 `from feature.extract import FEATURES` 单一引用
- ✅ 根目录仅保留 7 个文件（无散落脚本）：`.gitignore`、`environment.yaml`、`main.py`、
  `README.md`、`项目开发文档.md`、`DEVELOP_LOG.md`、`DEVELOP_LOG_ARCHIVE.md`

#### 【存在问题】

- ⛔ **蓄积量标签 y 仍未计算**（唯一真实阻塞）
- 100m 邻域（超出 IFN4 样地 25m 半径）的合理性仍需论文论证
- `utils/` 仍为空模块（待后续补充通用工具）

#### 【下一步计划】

1. 计算 IFN4 样地蓄积量 y（`PCMayores` → 官方材积公式）
2. 实现 `feature/extract.py`（23 特征提取）
3. 获取西班牙 DEM（启用地形特征）

#### 【AI辅助记录】

- AI：SWIR 决策落地、全项目文档核对与修正、探讨稿归位、编译缓存清理、结构与导入验证
- 人工是否修改：待确认

<!-- 新阶段日志从此处开始记录 -->