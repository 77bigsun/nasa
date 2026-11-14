# 任務權重的文件依據（提案 v1，2026-11-14）

> 目的：讓「每個任務要分配多少給每個類比種類」有可追溯的依據，而不是憑感覺。
> 狀態：**提案，尚未寫進 `config/missions.json`**。團隊確認後再改程式。
> 每一條條件都附出處（第 7 節）。

---

## 1. 七個類比種類（對應題目 Potential Considerations 列的面向）

| 代碼 | 類比種類 | 題目原本的面向 | 目前用的變數 | 狀態 |
|---|---|---|---|---|
| T | 地形 | Terrain, elevation, slope, roughness, craters | 坡度、粗糙度 | 有 |
| S | 地表物質與裸露 | Geology, mineralogy, surface materials | 岩性、熱慣量、無植被（原「荒蕪度」） | 有（岩性 0.5° 偏粗） |
| E | 環境極端 | Temperature, illumination, environmental extremes | 溫度、日溫差、乾燥度 | 有 |
| W | 水與冰 | Water, ice, permafrost, resources | 冰（永凍土） | 有 |
| D | 大氣與沙塵 | Dust, wind, erosion | 沙塵 | 有 |
| B | 生物與棲息性 | Biology, extremophiles, habitability, biosignatures | 規劃：土壤有機碳、土壤鹽度（紫外線之後補） | **待補資料** |
| C | 洞穴與地下 | Caves, lava tubes, subsurface | 無 | **沒有全球資料** |

「著陸、移動、機器人、人員作業」不是類比種類，而是任務本身，所以放在任務那一層。

### 1.1 生物面向在 GEE 上的現成資料（已查證）

| 變數 | GEE 資料 | 備註 |
|---|---|---|
| 土壤有機碳 | `ee.Image("projects/soilgrids-isric/soc_mean")`（SoilGrids 2.0，250 m，6 個深度，CC BY 4.0） | 社群資料集；GEE 上 SoilGrids 系列標示範圍約 56°S–84°N，南極預期沒有值 |
| 土壤鹽度 | `ee.ImageCollection("projects/sat-io/open-datasets/global_soil_salinity")`（1986–2016，CC BY 4.0） | 作者報告驗證準確度 67–70% |
| 地表紫外線 | **GEE 沒有現成的地表 UV 劑量**。Sentinel-5P 的 UV Aerosol Index 是氣膠指數，不是紫外線劑量，不能用 | 需另外下載：NASA OMI `OMUVBd`（1°，每日，GES DISC，需 Earthdata 登入），或已整理好的氣候平均 glUV（UFZ） |

火星端：有機物極低、紫外線極高可以設固定值；鹽類可用氯化物／硫酸鹽沉積分布，之後再接。

## 2. 方法：條件計數法

1. 對每個任務，找 NASA 選址文件裡**明確列出的條件**（工程限制或科學條件）。
2. 每一條條件給 **1 分**，歸到它對應的類比種類。
3. 同時涉及兩個類比種類的條件（例如「岩石多寡」同時是地形障礙和地表物質特性）**各給 0.5**。
4. **只有火星才有的條件不計分**，改列入「地球無法模擬」：例如「海拔要夠低，才有足夠大氣減速」——地球沒辦法複製火星的稀薄大氣。
5. 文件**明講「最重要」**的條件給 **2 分**（目前只有一條：載人基地的水資源）。
6. 某任務的權重 = 該類比種類得分 ÷ 總分。

這是刻意選的簡單規則：每一分都能指回某一份文件的某一條條件，評審問「為什麼是 0.42」時可以逐條回答。限制見第 6 節。

## 3. 各任務的條件與計分

### 3.1 著陸測試 `landing`

主要依據：Mars Science Laboratory（Curiosity）選址的工程限制（Golombek et al. 2012；MSL 工程限制使用者手冊）。Mars 2020 沿用大部分 MSL 的限制。

| # | 文件條件 | 類比種類 | 分數 |
|---|---|---|---|
| L1 | 緯度 ±30°，為了探測車與儀器的熱管理 | E | 1 |
| L2 | 海拔 < −1 km，才有足夠大氣減速 | （火星限定，不計） | 0 |
| L3 | 1–1000 m 尺度的起伏 < 100–130 m（下降時的控制與燃料） | T | 1 |
| L4 | 2–5 m 尺度的坡度 < 30°（著陸時穩定） | T | 1 |
| L5 | 岩石豐度中等，避免撞到機身底板 | T 0.5 + S 0.5 | 1 |
| L6 | 地表要能反射雷達、能承重、可通行；熱慣量 < 100 且反照率 > 0.25 的厚塵地表不適合 | S | 1 |
| L7 | 下降時的風（MSL 手冊的 EDL 風限制；MER 也列了低水平風、風切、亂流） | D | 1 |

總分 6 → **T 0.42、S 0.25、E 0.17、D 0.17**（W、B、C 為 0）

跨任務檢查：Pathfinder、MER、MSL、InSight 的選址條件都包含「低坡度」「岩石豐度」「能反射雷達／能承重的地表」，所以地形和地表物質是著陸的主軸。

### 3.2 探測車測試 `rover`

主要依據：Mars 2020 選址的可通行性分析（JPL，Ono et al.），把**地表類型、岩石豐度、坡度**換算成行駛估計；MSL 選址要求地表「能承重、可通行」；MSL 緯度限制是為了探測車熱管理。

| # | 文件條件 | 類比種類 | 分數 |
|---|---|---|---|
| R1 | 坡度 | T | 1 |
| R2 | 岩石豐度（尖銳岩石造成輪子磨損、障礙物） | T 0.5 + S 0.5 | 1 |
| R3 | 地表類型／可通行性（鬆沙、沙波造成打滑與下陷；地表要能承重） | S | 1 |
| R4 | 熱管理（緯度限制；探測車設計溫度範圍約 145–310 K） | E | 1 |

總分 4 → **T 0.375、S 0.375、E 0.25**（其他為 0）

實際操作經驗支持 R1–R3：Curiosity 曾遇到「23° 坡度＋滑沙＋輪子大小的岩石」最難的爬坡、尖銳岩石造成的輪子磨損、沙波區的高打滑。

註：Curiosity、Perseverance 是核動力，文件沒有把沙塵列為移動條件，所以 D = 0。太陽能探測車要另外考慮沙塵。

### 3.3 地質探勘 `geology`

主要依據：Mars 2020 選址的科學條件（Grant et al. 2018），以及 MSL 的科學條件（可評估過去的宜居環境，包含多樣性、地質脈絡、生命跡象保存）。

| # | 文件條件 | 類比種類 | 分數 |
|---|---|---|---|
| G1 | 地質背景與歷史可以被釐清 | S | 1 |
| G2 | 有古代宜居環境的證據 | B | 1 |
| G3 | 有生命跡象保存潛力高的岩石，而且可以到達 | S 0.5 + B 0.5 | 1 |
| G4 | 樣本的數量、多樣性、品質足夠 | S | 1 |
| G5 | 工程限制：緯度（熱管理）；海拔限制不計（火星限定） | E | 1 |
| G6 | 可通行性：探測車要能到達科學目標（Mars 2020 可通行性分析） | T 0.5 + S 0.5 | 1 |

總分 6 → **S 0.50、B 0.25、E 0.17、T 0.08**（W、D、C 為 0）

### 3.4 建基地取冰 `isru_base`

主要依據：NASA 2015 年第一次載人登陸點／探索區（Exploration Zone, EZ）研討會（HLS2）的條件，以及 NASA 後續說明。

| # | 文件條件 | 類比種類 | 分數 |
|---|---|---|---|
| I1 | 水資源（地下冰或含水礦物）——文件明講是**最重要**的條件 | W | 2 |
| I2 | 緯度限制 ±50°（降落與起飛技術、取冰偏好高緯度） | E | 1 |
| I3 | 海拔不高於 +2 km | （火星限定，不計） | 0 |
| I4 | 避開厚沙塵堆積（沙塵對設備有問題） | D | 1 |
| I5 | 土木工程：要有可以設置基礎設施的區域、多次起降的爆炸範圍（平坦地形） | T | 1 |
| I6 | 土木工程：表土可以用來做起降坪和道路 | S | 1 |
| I7 | 探索區內要有科學目標區（Science ROI） | S 0.5 + B 0.5 | 1 |

總分 7 → **W 0.29、S 0.21、T 0.14、E 0.14、D 0.14、B 0.07**（C 為 0）

## 4. 結果總表

| 任務 | 地形 T | 地表物質 S | 環境 E | 水冰 W | 沙塵 D | 生物 B | 洞穴 C |
|---|---|---|---|---|---|---|---|
| 著陸測試 | **0.42** | 0.25 | 0.17 | 0 | 0.17 | 0 | 0 |
| 探測車測試 | **0.375** | **0.375** | 0.25 | 0 | 0 | 0 | 0 |
| 地質探勘 | 0.08 | **0.50** | 0.17 | 0 | 0 | 0.25 | 0 |
| 建基地取冰 | 0.14 | 0.21 | 0.14 | **0.29** | 0.14 | 0.07 | 0 |

精確值（寫進 config 時用）：著陸 5/12、1/4、1/6、1/6；探測車 3/8、3/8、1/4；地質 1/12、1/2、1/6、1/4；取冰 1/7、3/14、1/7、2/7、1/7、1/14。

### 4.1 和原本先驗（`missions.json` 加總到類比種類）的比較

| 任務 | 原本先驗 | 文件推導 | 差異 |
|---|---|---|---|
| 著陸 | T 0.60、S 0.15、E 0.05、D 0.15、（無植被 0.05） | T 0.42、S 0.25、E 0.17、D 0.17 | 主軸一樣是地形；文件給地表承重、熱管理更多 |
| 探測車 | T 0.50、S 0.25、E 0.10、D 0.10、（無植被 0.05） | T 0.375、S 0.375、E 0.25 | 文件把地表類型（鬆沙）看得和坡度一樣重；沙塵為 0 |
| 地質 | S 0.45、T 0.15、E 0.15、（無植被 0.15）… | S 0.50、B 0.25、E 0.17、T 0.08 | 主軸一樣是地表物質；文件多了 0.25 的生物／宜居 |
| 取冰 | W 0.35、E 0.25、T 0.15、S 0.15… | W 0.29、S 0.21、T/E/D 各 0.14 | 主軸一樣是水冰；文件多了沙塵和土木工程 |

**主要的類比種類完全一致**，代表原本的先驗方向是對的；文件推導讓次要部分有了依據。

## 5. 對程式的影響（確認後才改）

- 計分公式不變（分層的幾何平均等同逐變數加權）。
- 生物 B、洞穴 C 目前沒有變數 → coverage = false → 依缺資料規則重新分配權重、信心度下降。例如地質探勘目前信心度上限 0.75，要補上生物變數才會回到 1。這是誠實的表現方式。
- 「無植被」從生物移到地表物質 S。
- 學權重只學「類比種類內部」各變數的比例；任務對類比種類的權重固定用本文件。

## 6. 限制

- **每條條件一樣重**是簡化。真實選址裡某些是硬性門檻、某些是加分項；我們只在文件明講「最重要」時加倍。
- **條件歸類有判斷成分**：例如「岩石豐度」拆成地形和地表物質各半。每一筆歸類都寫在表裡，可以討論修改。
- **文件不完整**：這裡用的是公開摘要、使用者手冊和研討會資料，不是完整的內部需求文件。
- **權重描述的是「火星任務需要什麼」，不是「地球上能不能測」**：例如火星大氣密度無法在地球模擬，所以不計分，改列在 gaps。
- 建議做 ±20% 敏感度測試，確認排名不會因為小調整而大變。

## 7. 參考資料

著陸、探測車：
- Golombek et al. (2012) Selection of the Mars Science Laboratory landing site. *Space Sci. Rev.* 170, 641–737. https://doi.org/10.1007/s11214-012-9916-y （USGS 摘要頁：https://pubs.usgs.gov/publication/70047380）
- NASA (2012) Gale Crater: Exploring the Mars Science Laboratory Landing Site. https://science.nasa.gov/resource/gale-crater-exploring-the-mars-science-laboratory-landing-site
- JPL MSL Project. MSL Landing Site Selection User's Guide to Engineering Constraints. https://marsoweb.nas.nasa.gov/landingsites/msl/memoranda/MSL_Eng_User_Guide_v2.pdf
- Golombek et al. (2003) Selection of the Mars Exploration Rover landing sites. *JGR* 108(E12). https://doi.org/10.1029/2003JE002074
- Golombek et al. (1997) Selection of the Mars Pathfinder landing site. *JGR* 102(E2). https://doi.org/10.1029/96JE03318
- Golombek et al. (2017) Selection of the InSight landing site. *Space Sci. Rev.* https://doi.org/10.1007/s11214-016-0321-9
- Ono et al. Data-Driven Surface Traversability Analysis for Mars 2020 Landing Site Selection. JPL. https://www-robotics.jpl.nasa.gov/media/documents/Data-driven%20surface%20traversability%20analysis%20for%20Mars%202020%20landing%20site%20selection.pdf
- NASA JPL (2023) NASA's Curiosity rover faces its toughest climb yet on Mars. https://www.jpl.nasa.gov/news/nasas-curiosity-rover-faces-its-toughest-climb-yet-on-mars/
- Arvidson et al. (2016) Curiosity rover mobility issues crossing Martian megaripple fields. LPSC. https://www-robotics.jpl.nasa.gov/media/documents/lpsc_2016_arvidson_ripple_crossing.pdf
- The Importance of Adaptive Decision-Making for Autonomous Long-Range Planetary Surface Mobility (2024). https://arxiv.org/pdf/2409.19455

地質探勘：
- Grant et al. (2018) The science process for selecting the landing site for the 2020 Mars rover. *Planet. Space Sci.* https://authors.library.caltech.edu/87552 （EPSC 摘要：https://meetingorganizer.copernicus.org/EPSC2018/EPSC2018-578.pdf）
- Mars 2020 工程限制（±30°、< +0.5 km、熱慣量 > 100–150）：https://pmc.ncbi.nlm.nih.gov/articles/PMC5859260

建基地取冰：
- NASA (2015) Human Landing Sites Study (HLS2) overview. https://www.nasa.gov/wp-content/uploads/2015/11/hls2-overview-v3tagged.pdf
- Hoffman et al. (2016) Exploration Zones, Regions of Interest. NTRS 20160002370. https://ntrs.nasa.gov/api/citations/20160002370/downloads/20160002370.pdf
- NASA Red Planet Dispatch (2022) Criteria for Landing Site Selection.
- The Planetary Society (2015) First Human Landing Sites/Exploration Zones workshop. https://www.planetary.org/articles/20151027-humans-mars-workshop
- Noctis Landing EZ proposal（ICE 工作組條件範例）. NTRS 20150021128. https://ntrs.nasa.gov/citations/20150021128

資料：
- SoilGrids on GEE: https://docs.isric.org/globaldata/soilgrids/access_on_gee.html
- Global Soil Salinity Maps (Ivushkin et al. 2019): https://gee-community-catalog.org/projects/global_salinity/
- OMI OMUVBd: https://www.earthdata.nasa.gov/es/data/catalog/ges-disc-omuvb-003 ；glUV: https://www.ufz.de/gluv/index.php?en=32423
