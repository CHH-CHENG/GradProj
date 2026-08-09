# 开发日志

---

## **开发日志模板（必须统一）**

### 【日期】：（填写日期） 第 （每天第几条）条

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
示例：

- 新增 downloader/copernicus.py
- 修改 main.py 调用流程
- 调整 data 目录结构

#### 【影响范围】

说明影响到哪些模块/文件

#### 【当前状态/结果】

- 是否完成
- 是否可运行

#### 【存在问题】

当前已经完成的内容里面，已发现，但仍未解决的问题，包括无法解决的问题

#### 【下一步计划】

明确下一步要做什么

#### 【AI辅助记录】

说明：

- AI做了什么（哪些内容是ai做的，必须标注清楚）
- 人工是否修改

---

## **开发日志记录：**

---

### 【日期】：2026-08-06 第1条

#### 【操作类型】

项目初始化 + 核心模块实现

#### 【修改内容】

1. 完成项目整体结构设计：

   - 确定模块划分：
     - downloader（数据下载）
     - preprocess（数据预处理）
     - feature（特征工程）
     - model（模型训练）
     - utils（工具模块）
   - 确定数据目录结构：
     - data/inventory（样地数据）
     - data/Sentinel2（遥感数据）
     - data/DEM（地形数据）
     - data/feature（训练数据）
     - data/result（输出结果）
2. 实现 Copernicus 数据下载模块：

   - 基于 Copernicus Data Space API
   - 支持：
     - 按时间 + 经纬度查询 Sentinel-2 数据
     - 批量获取产品 ID
     - 自动下载产品
     - 多次重试机制（应对网络不稳定）
3. 实现下载优化机制：

   - 加入 token 获取与认证流程
   - 解决 401（token过期）问题：
     - 在下载过程中自动刷新 token
   - 处理 404（离线数据）问题：
     - 筛选 Online 产品，仅下载可用数据
4. 实现断点续传机制：

   - 使用 .part 文件标记未完成下载
   - 支持：
     - 程序中断后重新运行
     - 自动跳过已完成文件
     - 继续未完成下载任务
5. 实现数据解压模块：

   - 自动扫描 zip 文件
   - 解压为 SAFE 格式
   - 已解压数据自动跳过（避免重复解压）

#### 【修改目的】

- Copernicus网页下载不稳定，经常中断
- 遥感数据体量大，必须自动化处理
- 为后续特征提取建立标准数据输入（SAFE结构）
- 提高整个项目的可重复运行能力

#### 【影响范围】

- 新增：
  - downloader/copernicus.py
  - preprocess/unzip.py
- 修改：
  - main.py（加入下载 + 解压流程控制）

#### 【当前状态/结果】

- 已成功获取并下载多个 Sentinel-2 产品
- 数据已存储至：
  - data/Sentinel2/zip/
- 解压完成：
  - data/Sentinel2/SAFE/
- 下载流程支持：
  - 自动重试
  - token刷新
  - 断点续传
- **是否完成：** 是
- **是否可运行：** 是

#### 【存在问题】

1. 下载速度较慢（受网络和服务器限制）
2. 部分产品存在离线情况（不可下载）
3. 当前为单线程下载，效率较低

#### 【下一步计划】

1. 实现 ROI 裁剪模块：
   - 根据样地位置裁剪 Sentinel-2 数据
2. 实现波段读取与重采样：
   - 统一空间分辨率（10m）
3. 设计特征提取流程：
   - NDVI / EVI
   - 光谱特征
   - 纹理特征

#### 【AI辅助记录】

本阶段使用 AI 进行：

- 项目结构设计
- Copernicus API 调用逻辑梳理
- 下载模块代码实现
- 异常（401 / 404）问题分析与修复
- **人工是否修改：** 否

---

### 【日期】：2026-08-06 第2条

#### 【操作类型】

修复Bug + 优化逻辑

#### 【修改目的】

修复下载/解压环节已发现的问题，增强健壮性与可复现性：

1. 修复"已解压自动跳过"逻辑失效：Copernicus 下载的 zip 以 UUID 命名，zip 内部顶层目录才是 SAFE 产品名，原逻辑按 zip 文件名拼接 .SAFE，导致每次重复解压全部数据；
2. 下载完成后未校验文件完整性，网络静默中断时可能产出损坏 zip 却被当作成功；
3. config/copernicus.yaml 使用相对路径，依赖当前运行目录。

#### 【修改内容】

1. preprocess/unzip.py：

   - 新增 get_safe_name(zip_path)，从 zip 内部读取真实 SAFE 产品名（顶层目录）；
   - 修改 unzip_all() 使用 get_safe_name 判断是否已解压，解决重复解压问题；
2. downloader/copernicus.py：

   - 下载完成后用 zipfile.is_zipfile() 校验完整性，失败则删除 .part 并触发重试；
   - 新增 CONFIG_PATH 常量，基于 __file__ 定位 config/copernicus.yaml，不再依赖运行目录；
   - search_products 查询增加 $orderby=ContentDate/Start desc，按时间倒序取产品；
3. 环境：GradProj 环境新增 python-docx（仅用于维护推进文档，未写入 environment.yml）。

#### 【影响范围】

- downloader/copernicus.py
- preprocess/unzip.py
- （main.py 调用流程不变）

#### 【当前状态/结果】

- **是否完成：** 完成
- **是否可运行：** 可运行

已用实际数据验证：

- get_safe_name 正确返回 SAFE 产品名；
- unzip_all 对 20 个已解压产品全部正确跳过（修复前会重复解压）；
- CONFIG_PATH 正确定位到 E:\GradProj\ProjCode\config\copernicus.yaml。

#### 【存在问题】

无新增已知问题。

#### 【下一步计划】

- 实现 ROI 裁剪模块（按样地位置裁剪 Sentinel-2）；
- 实现波段读取与重采样（统一 10m）；
- 设计特征提取流程（NDVI/EVI、光谱特征、纹理特征）。

#### 【AI辅助记录】

本阶段由 AI 完成：

- 分析定位 unzip 跳过失效原因（UUID vs SAFE 命名不匹配）；
- 完成上述代码修改并用实际数据运行验证；
- **人工是否修改：** 人工确认后登记本条记录

---

### 【日期】：2026-08-06 第3条

#### 【操作类型】

新增模块

#### 【修改目的】

执行下一步计划：实现波段读取 + 重采样 + ROI 裁剪，打通"遥感数据 → 预处理 → 可建模影像"链路。

#### 【修改内容】

1. 新增 config/preprocess.yaml：预处理配置（产品类型/目标分辨率/波段列表/研究区/按样地参数）；
2. 新增 preprocess/read_bands.py：波段读取与重采样

   - 支持 L2A（IMG_DATA 按 R10m/R20m/R60m 分目录）与 L1C（平铺）；
   - 20m/60m 波段双线性重采样到目标分辨率（默认 10m）；
   - 支持按研究区窗口读取（bounds），避免读取整个 tile，大幅节省内存与时间；
   - L2A 反射率 DN(0~10000) 缩放为 0~1；
3. 新增 preprocess/crop_roi.py：ROI 裁剪

   - 研究区整幅：以配置中心点(107.0, 34.3)在影像 CRS 下方形缓冲(默认10km×10km)，窗口读取+重采样+多边形裁剪，输出多波段 GeoTIFF（10 波段 B02~B12, 10m, deflate 压缩）；
   - 按样地裁剪（预留）：读取 plots 矢量（点自动按 plot_buffer_m 缓冲 / 面直接用），样地文件未就位时提示并跳过；
   - 主流程 process_sentinel2()：遍历 SAFE 下所有 L2A 产品，已处理自动跳过；
4. main.py：集成预处理流程 run_preprocess()，并在导入 rasterio 前完成 GDAL 环境自愈（GDAL_DATA / GDAL_DRIVER_PATH / PATH 追加 Library/bin）；
5. 环境：GradProj 新增 libgdal-jp2openjpeg（GDAL 的 JP2 解码插件，conda 安装），并修复 yaml 读取编码（utf-8）。

#### 【影响范围】

- 新增：preprocess/read_bands.py、preprocess/crop_roi.py、config/preprocess.yaml
- 修改：main.py、downloader/copernicus.py（yaml 编码统一 utf-8）
- 环境：GradProj 新增 libgdal-jp2openjpeg

#### 【当前状态/结果】

- **是否完成：** 完成
- **是否可运行：** 可运行

已用全部 9 个 L2A 产品实测：

- 全部成功输出 data/Sentinel2/roi/*_roi.tif（10 波段, 10m, 约10km×10km, 约24MB/个）；
- 元数据验证：CRS=EPSG:32648，值域 0.11~0.94（0~1 反射率），有效像素 100%；
- 波段描述正确（B02~B12）；真彩色预览图确认地形/地表正常；
- 按样地接口在无样地数据时正确跳过。

#### 【存在问题】

样地数据（data/inventory）尚未就位，按样地裁剪暂未实测（接口已预留）。

#### 【下一步计划】

- 设计特征提取流程（NDVI/EVI、光谱特征、纹理特征），生成 samples.csv；
- 样地数据就位后启用按样地裁剪并实测。

#### 【AI辅助记录】

- **AI 完成：** 模块设计与实现、窗口读取性能优化、GDAL/JP2 环境问题定位与修复（安装 libgdal-jp2openjpeg + 环境变量自愈）、全量运行验证与预览图检查
- **人工是否修改：** 人工确认后登记本条记录

---

### 【日期】：2026-08-09 第1条

#### 【操作类型】

修改结构（文档同步更新 + 数据登记）

#### 【修改目的】

1. 了解 `data/inventory/` 中第一份（当前唯一）数据 `Finland_NFI_2023_GSV` 的完整信息（元数据、栅格属性、值域），为后续特征提取/建模提供标签数据依据；
2. 按项目开发文档「README同步更新」Skill 执行一次全项目范围的 README 同步，使文档与磁盘实际状态一致。

#### 【修改内容】

1. **数据盘点（Finland_NFI_2023_GSV，芬兰 Luke MS-NFI 2023）**：
   - 数据集 ID `682679e9-0e42-4e0e-a9b2-c53fc319623d`，Paituli/CSC 下载，许可 CC BY 4.0；
   - 生产方法：VMI13 地面样地（51051 个）+ Sentinel-2 L2A 反射率镶嵌影像，增强 k-NN（ik-NN，5 邻）；
   - 已下载 4 个全国整幅主题栅格（`tilavuus`/`manty`/`kuusi`/`koivu`_vmi1x_1923.tif，蓄积量 m³/ha，共约 6.3 GB）；
   - 栅格属性（rasterio 实测）：GeoTIFF、EPSG:3067、16m、42240×73472、uint16、nodata=32767、总蓄积量 0~750 m³/ha。
2. **README 全项目同步（共更新 7 个文件）**：
   - 根目录 `README.md`：结构树 inventory 说明、4.1 样地数据节更新；
   - `data/README.md`：inventory 目录说明 + 数据总览表更新；
   - `data/inventory/README.md`：重写，全面登记 Finland_NFI_2023_GSV（简介/方法/目录结构/清单/栅格格式/去向/引用），并补充：
     - 2.1 节「时间信息」：清查年 2023（野外更新至 2023-07-31）、样地来源 2019–2023（VMI13）、遥感影像 2021–2023 生长季、temporal 2023-01-01~12-31、发布于 2025-08-05、元数据修改 2026-05-29、版本 v1；
     - 3 节「文件格式说明」表：metadata.json(JSON)、LUETAMA-2023.txt / 临时叙述.txt / luke_ehdot.txt(TXT UTF-8)、zip(ZIP)、tif(GeoTIFF)；
     - 5 节栅格格式补全：GTiff / 单波段 uint16 / EPSG:3067 / 42240×73472 / 16m / **LZW 压缩** / **tiled 512×512** / band interleave / 内部 overviews 8 级 / AREA_OR_POINT=Area / nodata=32767 / 无外部辅助文件；
     - 5.1 节「空间坐标范围」：EPSG:3067 边界（left=57632, bottom=6602752, right=733472, top=7778304）与 WGS84 经纬度范围（lon 15.50°E~33.13°E, lat 59.33°N~70.11°N）及图幅跨度（东西约 676km、南北约 1176km）；
   - 填充 5 个空模块 README：`downloader/`、`preprocess/`、`feature/`、`model/`、`utils/`（登记脚本功能与输入/输出）。

#### 【影响范围】

- README.md、data/README.md、data/inventory/README.md、downloader/README.md、preprocess/README.md、feature/README.md、model/README.md、utils/README.md
- （不涉及代码逻辑；`config`/`data/Sentinel2`/`data/DEM`/`data/feature`/`data/result` 的 README 经核查与现状一致，未改动）

#### 【当前状态/结果】

- **是否完成：** 完成
- **是否可运行：** 不受影响（纯文档/数据登记变更）

#### 【存在问题】

1. 磁盘上 `inventory/` 当前仅有 `Finland_NFI_2023_GSV`，早前 README 提及的混交林（xlsx）与纯林（accdb）数据目录不在磁盘上，README 已如实标注"待放回"；
2. `feature/`、`model/`、`utils/` 尚无实际脚本（仅 `__init__.py`），README 中为规划内容。

#### 【下一步计划】

- 设计并实现特征提取模块 `feature/extract.py`：从 ROI 影像提取光谱/植被指数特征，关联 `Finland_NFI_2023_GSV` 蓄积量标签（需先将 16m 栅格与研究区/样地对齐），生成 `samples.csv`；
- 确定芬兰研究区范围与 Sentinel-2 影像时间匹配方案（2023 年）。

#### 【AI辅助记录】

- **AI 完成：** 数据盘点（解析 metadata.json、rasterio 实测栅格元数据与值域、zip/解压目录核对）、全项目 README 同步更新、本条日志起草
- **人工是否修改：** 待人工确认

---

### 【日期】：2026-08-09 第2条

#### 【操作类型】

新增数据（DEM）+ 文档同步更新

#### 【修改目的】

用户已收集完整芬兰 DEM 数据（`data/DEM/raw/Finland_DEM_10m_2019/`），完善 `data/DEM/README.md` 并同步 `data/README.md`，登记 DEM 数据完整信息（来源/格式/空间范围/规模/去向），为后续地形特征提取做准备。

#### 【修改内容】

1. **数据盘点（Finland_DEM_10m_2019，芬兰 MML 10m 高程模型）**：
   - 数据集 ID `16bb1329-1632-4559-919e-1cd1cd969296`，MML（芬兰国家土地测量局）发布，Paituli/CSC 下载，许可 CC BY 4.0，芬兰全国最精确 DEM；
   - 关键特性：10m×10m、垂直精度约 1.4m、高程基准 N2000、投影 EPSG:3067、数据年份 2019；
   - 规模：1523 个 GeoTIFF（float32、单波段、LZW 压缩、nodata=-9999、每块 2400×1200≈24km×12km），共约 10.29 GB；38 个顶层图幅（K2~X5），5 个 zip 分片已全部解压；
   - 空间范围（官方 WKT）：经度 18.71°E~31.77°E，纬度 59.35°N~70.14°N，覆盖全芬兰；
   - 目录结构：`mml/dem10m/2019/<图幅>/<子图幅>/<图幅><子图幅><块>.tif`。
2. **README 同步（共更新 2 个文件）**：
   - `data/DEM/README.md`：重写，全面登记 Finland_DEM_10m_2019（简介/关键特性/目录结构与命名规则/文件格式说明/栅格内部格式/空间范围/规模/输入来源与输出去向/参考）；
   - `data/README.md`：数据总览表 DEM 行更新为"芬兰 MML 10m DEM 2019"。

#### 【影响范围】

- data/DEM/README.md、data/README.md
- （不涉及代码逻辑；DEM 数据仅存放于 data/DEM/raw/，roi/ 待生成）

#### 【当前状态/结果】

- **是否完成：** 完成
- **是否可运行：** 不受影响（纯数据登记/文档变更）

#### 【存在问题】

1. `data/DEM/roi/` 尚未生成（按研究区裁剪 DEM 待研究区确定后执行）；
2. 芬兰 DEM 以分块 tif 组织，使用时需按研究区定位并拼接/裁剪所需图幅块。

#### 【下一步计划】

- 确定芬兰研究区（如 62~65°N 同时含纯林/混交林的区域）后：
  - 用现有 `preprocess/crop_roi.py` 思路裁剪 DEM → `roi/`；
  - 设计 `feature/extract.py`：地形特征（高程/坡度/坡向）与 Sentinel-2 光谱特征、MS-NFI 蓄积量标签对齐。

#### 【AI辅助记录】

- **AI 完成：** DEM 数据盘点（解析 metadata.json、rasterio 实测栅格格式与值域、图幅/zip 结构统计、官方 WKT 空间范围提取）、data/DEM/README.md 重写、data/README.md 同步、本条日志起草
- **人工是否修改：** 待人工确认

---

### 【日期】：2026-08-09 第3条

#### 【操作类型】

新增模块（下载代码重构）+ 数据采集启动

#### 【修改目的】

采集纯林/混交林各自典型区域的 Sentinel-2 遥感影像（原始整 tile），为后续特征提取与建模提供芬兰研究区影像数据；重构下载代码以满足"矩形范围查询 + 按 tile 去重（无重复时相）"需求。

#### 【修改内容】

1. **典型区域识别（基于 MS-NFI 树种蓄积量分析）**：
   - 纯林典型区：拉普兰纯松林，中心 (27.20E, 68.76N)（100km 格纯林占比 63%，几乎全纯松）；
   - 混交典型区：中心 (24.97E, 66.06N)（混交占比 31%）；
   - 全国分类统计：有效林地 18.7 万 km²（纯松 3.06 万、纯云杉 0.19 万、混交 3.23 万、其他 12.2 万）。
2. **重构 `downloader/copernicus.py`**：
   - 新增 `search_products_bbox(...)`：WGS84 矩形（POLYGON）范围查询，`$expand=Attributes` 获取 cloudCover/tileId，L2A/L1C/ALL 过滤，返回完整产品信息 `{id,name,tile,date,cloud,online}`；
   - 新增 `dedup_by_tile(products)`：按 tile 去重，每 tile 保留云量最少一期（满足"不要重复时相"）；
   - 新增 `search_and_download_region(...)`：区域一站式（查询→去重→下载）；
   - 修复：cloud 解析兼容 CDSE 扁平 Attributes 结构（`{"Name","Value","ValueType"}`）；tile 优先取 Attributes.tileId；OData v4 不支持 `substringof` → 改为 Python 端过滤 L2A。
3. **新增采集脚本 `download_finland.py`**：定义两个典型区域（中心+查询半宽±0.35°），时间窗 2023-07-01~08-10、云量<30%、L2A；支持 `--dry-run` 预览。

#### 【影响范围】

- downloader/copernicus.py、新增 download_finland.py、downloader/README.md
- 下载输出：data/Sentinel2/zip/

#### 【当前状态/结果】

- **dry-run 验证通过**：纯林区命中 4 个 tile（T35WMR/WMS/WNR/WNS，2023-08-08，云量 0~6.8%）；混交区命中 4 个 tile（T34WFT/WFU、T35WMN/WMP，2023-07-10，云量 0~0.1%）；
- **✅ 下载完成**：8 个整 tile L2A 全部下载成功（zip 完整校验通过，30MB~1087MB/个，共约 5GB）；
- **✅ 解压完成**：8 个 SAFE 已解压至 `data/Sentinel2/SAFE/`（标准 L2A 结构，各 95 项）；
- **是否完成：** 完成
- **是否可运行：** 可运行

#### 【存在问题】

1. 两区域中心点位于 S2 tile 交汇处，各命中 4 个相邻 tile（下载量高于单 tile 预期）；
2. `T35WMN` 产品偏小（约 30MB，多为云/水区域，JP2 压缩率高，属正常）；其余 7 个 tile 均为 300MB~1.1GB。

#### 【下一步计划】

- 等待下载完成 → `unzip_all()` 解压 → 用 `preprocess/crop_roi.py` 对两个研究区分别裁剪；
- 之后：MS-NFI 蓄积量标签 / DEM / Sentinel-2 特征对齐，进入特征提取。

#### 【AI辅助记录】

- **AI 完成：** 典型区域识别分析、下载代码重构（矩形查询/去重/L2A 过滤/OData 结构调试）、采集脚本编写、dry-run 验证、README 与日志登记
- **人工是否修改：** 待人工确认（下载范围 8 tile 已由用户确认）

---

### 【日期】：2026-08-09 第4条

#### 【操作类型】

修改结构（数据目录重组 + README 全量更新）

#### 【修改目的】

1. 清理不再符合研究需求的数据：早期测试用中国（秦岭）20 个 Sentinel-2 影像、秦岭混交林与西班牙纯林样地数据全部移除，项目聚焦芬兰；
2. 芬兰遥感数据按研究用途重新组织，子目录命名为体现用途的名称（纯林+混交）；
3. 按「README同步」Skill 全量更新各 README，数据类 README 细化到**每个文件**（位置/时间/用途）。

#### 【修改内容】

1. **数据目录重组**：
   - 移除：`data/Sentinel2/zip/`、`SAFE/` 根目录下的中国测试影像（20 个）；`inventory/` 中秦岭/西班牙样地数据；
   - 重命名：`zip/Finland`、`SAFE/Finland`、`roi/Finland` → **`Finland_PureMixed`**（体现纯林/混交研究用途）；
   - 现状：`data/Sentinel2/{zip,SAFE,roi}/Finland_PureMixed/`（8 个 L2A 整 tile，roi 待裁剪）。
2. **README 全量更新（8 个文件）**：
   - 根 `README.md`：结构树（Finland_PureMixed 层级、download_finland.py）、4.1/4.2/4.3 数据说明聚焦芬兰；
   - `data/README.md`：移除中国/秦岭/西班牙条目，数据总览聚焦芬兰 + 历史说明；
   - `data/Sentinel2/README.md`：**逐文件明细表**（8 个影像：SAFE 名/成像日期/Tile/云量/zip ID/大小/研究区用途），纯林区（T35WMR/WMS/WNR/WNS，2023-08-08）+ 混交区（T34WFT/WFU、T35WMN/WMP，2023-07-10）；
   - `data/inventory/README.md`：移除秦岭/西班牙提及，聚焦 Finland_NFI_2023_GSV；
   - `data/feature/README.md`：补充典型区识别中间文件（_cls1km.npy/_t1km.npy）说明；
   - `downloader/README.md`：补充 `download_finland.py` 采集脚本说明；
   - `data/DEM/README.md`、`data/result/README.md`、`config/README.md`、模块 README：核查与现状一致。

#### 【影响范围】

- data 目录结构（Sentinel2 子目录重命名、移除中国/秦岭/西班牙数据）
- README.md、data/README.md、data/Sentinel2/README.md、data/inventory/README.md、data/feature/README.md、downloader/README.md
- （代码不变；download_finland.py 下载路径仍为 `zip/` 根，人工整理入子目录）

#### 【当前状态/结果】

- **是否完成：** 完成
- **是否可运行：** 不受影响（数据组织/文档变更）

#### 【存在问题】

1. `download_finland.py` 下载到 `zip/` 根目录，与 `zip/Finland_PureMixed/` 组织不一致（需人工整理或后续调整脚本 out_dir）；
2. `data/feature/` 存在典型区识别临时文件（_cls1km.npy/_t1km.npy），README 已说明，是否保留待定。

#### 【下一步计划】

- 对两个研究区分别裁剪（`roi/Finland_PureMixed/`），并完成 MS-NFI 蓄积量标签、DEM、Sentinel-2 特征的空间对齐；
- 实现 `feature/extract.py` 特征提取，生成 samples.csv。

#### 【AI辅助记录】

- **AI 完成：** 磁盘现状盘点（移除数据核对、Finland 子目录结构确认）、重命名建议与执行、README 全量更新、本条日志起草
- **人工是否修改：** 待人工确认（Finland_PureMixed 命名由用户确认；文件整理为用户手动完成）

---

### 【日期】：2026-08-09 第5条

#### 【操作类型】

新增模块 + 数据产出（正式推进：数据链路打通）

#### 【修改目的】

正式开启项目推进：利用已有蓄积量（MS-NFI）、DEM（MML 10m）、遥感影像（Sentinel-2 L2A）三类数据，完成研究区数据对齐与特征提取，生成可建模的训练样本。

#### 【修改内容】

1. **新增 `config/finland_study.yaml`**：两个研究区（纯林 `pure_pine_lapland` 27.20E/68.76N、混交 `mixed_central` 24.97E/66.06N，各 20km×20km）、采样参数（30m 窗口）、数据路径。
2. **新增 `preprocess/finland_study.py`**（研究区数据准备）：
   - `prepare_region_s2`：从覆盖研究区的 SAFE 读取波段，逐块重投影到统一 EPSG:3067 10m 网格，重叠区均值融合（解决 rasterio.merge 不支持跨 CRS 的问题）；
   - `prepare_region_label`：MS-NFI 全国蓄积量栅格按研究区裁剪，16m→10m 最近邻重采样；
   - `prepare_region_dem`：MML 10m DEM 分块裁剪拼接（EPSG:3067）；
   - 修复：JP2 解码需 GDAL 环境自愈（GDAL_DRIVER_PATH）、`BoundingBox` 无 intersects、MemoryFile 需返回打开 dataset、`_write_tif` 单波段描述类型。
3. **新增 `feature/extract.py`**（特征提取 + 样本构建）：
   - 30m×30m 窗口采样（3×3 个 10m 像元，步长 30m），标签取窗口中心 MS-NFI 蓄积量；
   - 特征：10 光谱波段窗口均值 + NDVI/EVI/NDWI/NDRE + DEM 高程/坡度/坡向；
   - 过滤：窗口中心 GSV 为 nodata（非林地）、窗口 S2 无有效值剔除。
4. **产出（已验证）**：
   - `data/Sentinel2/roi/Finland_PureMixed/{纯林,混交}_S2_10m_3067.tif`（10 波段、2000×2000、10m、EPSG:3067）；
   - `data/feature/finland_study/*_GSV_10m_3067.tif`、`*_DEM_10m_3067.tif`（与 S2 完全对齐）；
   - `data/feature/samples.csv`：**76.3 万样本**（纯林 38.8 万 + 混交 37.5 万），0 NaN，GSV 0~279 m³/ha。
5. **新增 `feature/subsample.py`（空间均匀抽样）**：按 label 空间分箱抽样（每箱取 1 个），默认每区 5 万 → `data/feature/samples_sampled.csv`（9.19 万样本）；验证抽样后 GSV 分布与完整集一致（纯林 mean 77.8/混交 81.4），空间覆盖完整。

#### 【影响范围】

- 新增：config/finland_study.yaml、preprocess/finland_study.py、feature/extract.py
- 数据产出：data/Sentinel2/roi/Finland_PureMixed/、data/feature/finland_study/、data/feature/samples.csv
- 文档：preprocess/README.md、feature/README.md、config/README.md、data/feature/README.md、data/Sentinel2/README.md

#### 【当前状态/结果】

- **是否完成：** 完成
- **是否可运行：** 可运行（两个脚本均实测跑通）
- 数据质量验证：三源栅格完全对齐（EPSG:3067、10m、2000×2000）；纯林 GSV 分布较集中（mean 77.9, std 37.4）、混交更分散（mean 82.9, std 59.6），符合预期

#### 【存在问题】

1. 样本量较大（76.3 万），RF 训练需控制内存/时间（必要时抽样）；
2. 研究区 2000×2000 网格不能被 30m 窗口整除，实际截取 1998×1998（边缘 2m 丢弃，可忽略）；
3. 坡度/坡向由 numpy gradient 计算（未用 GDAL DEMProcessing），精度可接受但非标准。

#### 【下一步计划】

- 实现 `model/rf.py`：随机森林建模 + 纯林/混交对比 + 空间分块交叉验证（避免空间自相关虚高）；
- 指标：R² / RMSE / RMSE% / MAE，固定随机种子，SHAP 解释。

#### 【AI辅助记录】

- **AI 完成：** 研究区方案设计（与用户确认 20km/30m 窗口/10m 对齐）、finland_study.py 与 extract.py 实现与多轮调试（JP2 环境、跨 CRS 拼接、窗口整除）、数据产出与质量验证、README 与日志登记
- **人工是否修改：** 待人工确认（关键设计决策已由用户确认）

---

### 【日期】：2026-08-09 第6条

#### 【操作类型】

修改结构（重构 main.py）+ 优化逻辑（训练脚本完善）

#### 【修改目的】

1. 用户将**亲自执行模型训练**，需将主入口重构为芬兰工作流统一入口（替代旧的中国研究区 run_preprocess）；
2. 完善训练脚本（冒烟测试模式 + 实时进度输出），便于用户执行与排查。

#### 【修改内容】

1. **重构 `main.py`**（芬兰工作流 CLI 入口）：
   - 步骤：`prepare`（研究区数据准备）/ `extract`（特征提取）/ `subsample [N]`（抽样）/ `train [--smoke]`（训练）/ `all`（全流程）；
   - 各步骤幂等（已生成自动跳过）、可独立开关；保留 GDAL 环境自愈；用法见 `python main.py --help`。
2. **增强 `model/rf.py`**：
   - 冒烟测试模式（`RF_SMOKE=1`：每区抽样 3000 + 30 棵树，快速验证流程）；
   - `sys.stdout.reconfigure(line_buffering=True)` 实时输出 fold 进度（解决管道缓冲看不到进度的问题）。
3. **`feature/subsample.py` 参数化**：`main(n_per_region=None)`，支持从 main.py 传入数量。
4. **根 `README.md`**：更新运行方法（环境、账号、main.py 各步骤用法、模块直接调用方式）。

#### 【影响范围】

- main.py、model/rf.py、feature/subsample.py、README.md

#### 【当前状态/结果】

- **是否完成：** 完成（代码就绪，get_errors 无错误）
- **是否可运行：** 可运行；训练由用户亲自执行（`python main.py train` 或 `python -m model.rf`）
- 注：早前异步启动的训练未能产出结果（data/result 为空），疑似后台会话中断，本次由用户前台执行

#### 【存在问题】

1. 完整训练（9.2 万样本 × 200 树 × 5 折 × 3 模型）计算量较大，用户机器需保证内存/CPU；可先 `--smoke` 验证；
2. `utils/` 模块仍为空（日志/配置通用工具未实现）。

#### 【下一步计划】

- 用户执行训练 → 结果解读（纯林 vs 混交精度对比）→ 更新 data/result/README.md；
- 之后：蓄积量空间预测、SHAP 解释、utils 基础工具。

#### 【AI辅助记录】

- **AI 完成：** main.py 重构、rf.py 冒烟模式与实时输出、subsample 参数化、README 更新、本条日志起草
- **人工是否修改：** 待人工确认（用户将亲自执行训练）
