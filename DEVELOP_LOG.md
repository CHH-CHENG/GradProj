# 开发日志

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
