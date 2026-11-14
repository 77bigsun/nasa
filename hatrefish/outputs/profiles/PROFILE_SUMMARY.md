# 類比剖面總表（自動產生）

> 產生時間 2026-11-14 15:12。由 `scripts/make_profiles.py` 產生，數字以 `outputs/profiles/*.json` 為準。
> 面向分數 = 面向內變數的等權重幾何平均；整體 = 面向的等權重幾何平均 × 100；不依任務加權。
> 尚未評估的面向：生物與棲息性、洞穴與地下（沒有變數）。
> 排名只用「面向」和「變數」都至少 80% 有資料的格子；每個面向的前 5 名只用該面向變數全部有資料的格子；地點彼此至少相距 150 km。
> 日溫差不計入任何面向（火星日溫差主要來自稀薄大氣，地球無法模擬），只在 breaks 裡當參考。
> 冰的目標值 = clip(SWIM Ci, 0, 1)：Ci ≤ 0 視為沒有冰。

## Jezero Crater（18.4, 77.5）

**各面向「分數 ≥ 0.9」的陸地比例**：地形 31.7%、地表物質與裸露 0.1%、環境極端 0.0%、水與冰 86.9%、大氣與沙塵 20.0%；整體 ≥ 90 分：0.00%

### 整體相似度前 10 名

| # | 地點 | 座標 | 整體 | 地形 | 地表物質與裸露 | 環境極端 | 水與冰 | 大氣與沙塵 | 最弱面向 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 33 km from Urdgol (MN) | 48.05, 92.95 | 90.4 | 0.98 | 0.91 | 0.82 | 1.00 | 0.83 | 環境極端 | 否（新候選） |
| 2 | 203 km from Turkmenbasy (TM) | 41.65, 54.05 | 90.4 | 0.99 | 0.86 | 0.72 | 1.00 | 0.99 | 環境極端 | 否（新候選） |
| 3 | 30 km from Jetaral (CN) | 47.15, 87.05 | 89.7 | 0.93 | 0.91 | 0.78 | 1.00 | 0.88 | 環境極端 | 否（新候選） |
| 4 | 136 km from Sekseuil (KZ) | 46.25, 59.85 | 88.5 | 0.90 | 0.90 | 0.74 | 1.00 | 0.90 | 環境極端 | 否（新候選） |
| 5 | 130 km from Tewulike (CN) | 41.35, 87.85 | 88.0 | 0.97 | 0.76 | 0.77 | 1.00 | 0.94 | 地表物質與裸露 | 否（新候選） |
| 6 | near Mynaral (KZ) | 45.45, 73.65 | 87.8 | 0.91 | 0.82 | 0.75 | 1.00 | 0.93 | 環境極端 | 否（新候選） |
| 7 | 62 km from Turkmenbasy (TM) | 39.55, 53.35 | 87.7 | 0.81 | 0.93 | 0.70 | 1.00 | 0.99 | 環境極端 | 否（新候選） |
| 8 | 43 km from Sayotesh (KZ) | 44.05, 53.15 | 87.6 | 0.95 | 0.78 | 0.72 | 1.00 | 0.98 | 環境極端 | 否（新候選） |
| 9 | 152 km from Sanlei (CN) | 39.95, 103.55 | 87.6 | 1.00 | 0.72 | 0.74 | 1.00 | 0.96 | 地表物質與裸露 | 否（新候選） |
| 10 | near Dabancheng (CN) | 43.35, 88.15 | 87.5 | 0.98 | 0.76 | 0.72 | 1.00 | 0.95 | 環境極端 | 否（新候選） |

### 每個面向最像的前 5 名

- **地形**：near Urdgol (MN)（1.00，整體 89）；152 km from Sanlei (CN)（1.00，整體 88）；98 km from Altay sumu (MN)（1.00，整體 88）；near Jetaral (CN)（1.00，整體 87）；77 km from Yiwu (CN)（1.00，整體 87）
- **地表物質與裸露**：68 km from Jisegumen (CN)（0.96，整體 36）；158 km from Maqian (CN)（0.96，整體 33）；45 km from Laotai (CN)（0.95，整體 20）；near Karabulak (CN)（0.94，整體 14）；87 km from Tumxuk (CN)（0.94，整體 14）
- **環境極端**：127 km from Nur (CN)（0.92，整體 24）；109 km from Layka (CN)（0.91，整體 14）；1416 km from Gjoa Haven (CA)（0.90，整體 30）；77 km from Zangkaxa (CN)（0.90，整體 14）；34 km from Aqqan (CN)（0.89，整體 28）
- **水與冰**：33 km from Urdgol (MN)（1.00，整體 90）；203 km from Turkmenbasy (TM)（1.00，整體 90）；30 km from Jetaral (CN)（1.00，整體 90）；136 km from Sekseuil (KZ)（1.00，整體 88）；130 km from Tewulike (CN)（1.00，整體 88）
- **大氣與沙塵**：139 km from Balkanabat (TM)（0.99，整體 86）；near Adrasmon (TJ)（0.99，整體 86）；106 km from Gumdag (TM)（1.00，整體 86）；near Taxtako'pir (UZ)（1.00，整體 86）；102 km from Qo'ng'irot Shahri (UZ)（1.00，整體 85）

### 已知類比地的剖面（標給這個目標的）

| 類比地 | 整體 | 全球前 % | 地形 | 地表物質與裸露 | 環境極端 | 水與冰 | 大氣與沙塵 | 最強 | 最弱 |
|---|---|---|---|---|---|---|---|---|---|
| Mars Desert Research Station Hanksville (Utah) | 73.2 | 5.4 | 0.97 | 0.53 | 0.69 | 1.00 | 0.60 | 水與冰 | 地表物質與裸露 |
| Black Point Lava Flow (Arizona) | 71.2 | 6.9 | 0.93 | 0.53 | 0.65 | 1.00 | 0.60 | 水與冰 | 地表物質與裸露 |
| Lavic Lake and Sunshine volcanic field Mojave Desert (California) | 69.3 | 8.6 | 0.95 | 0.55 | 0.53 | 1.00 | 0.69 | 水與冰 | 環境極端 |
| Lake Salda (Turkey) | 59.9 | 19.5 | 0.80 | 0.19 | 0.61 | 1.00 | 0.84 | 水與冰 | 地表物質與裸露 |
| Matanumadh jarosite locality Kachchh (India) | 55.1 | 27.7 | 0.92 | 0.18 | 0.32 | 1.00 | 0.97 | 水與冰 | 地表物質與裸露 |
| Lonar crater (India) | 49.8 | 38.1 | 0.91 | 0.13 | 0.29 | 1.00 | 0.89 | 水與冰 | 地表物質與裸露 |
| Ries impact crater (Germany) | 47.8 | 42.7 | 0.96 | 0.10 | 0.44 | 1.00 | 0.65 | 水與冰 | 地表物質與裸露 |
| Dresser Formation stromatolites Pilbara (Australia) | 46.5 | 45.6 | 0.98 | 0.55 | 0.15 | 1.00 | 0.29 | 水與冰 | 環境極端 |
| Askja lava fields Vikrahraun (Iceland) | 44.0 | 51.7 | 0.93 | 0.55 | 0.13 | 0.99 | 0.27 | 水與冰 | 環境極端 |
| Haughton impact crater Devon Island (Canada) | 25.3 | 86.1 | 0.93 | 0.88 | 0.49 | 0.01 | 0.28 | 地形 | 水與冰 |
| Pavilion Lake (British Columbia) | 19.1 | 92.4 | 0.01 | 0.10 | 0.60 | 1.00 | 0.41 | 水與冰 | 地形 |
| Bockfjorden Volcanic Complex Svalbard (Norway) | 8.9 | 99.8 | 0.01 | 0.89 | 0.14 | 0.01 | 0.28 | 地表物質與裸露 | 水與冰 |

## Gale Crater（-5.4, 137.8）

**各面向「分數 ≥ 0.9」的陸地比例**：地形 6.3%、地表物質與裸露 0.1%、環境極端 0.0%、水與冰 87.5%、大氣與沙塵 20.0%；整體 ≥ 90 分：0.00%

### 整體相似度前 10 名

| # | 地點 | 座標 | 整體 | 地形 | 地表物質與裸露 | 環境極端 | 水與冰 | 大氣與沙塵 | 最弱面向 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | near Altanteel (MN) | 47.05, 92.85 | 88.2 | 0.99 | 0.68 | 0.83 | 0.99 | 0.96 | 地表物質與裸露 | 否（新候選） |
| 2 | 111 km from Barkol (CN) | 43.75, 91.65 | 87.7 | 1.00 | 0.75 | 0.78 | 0.94 | 0.95 | 地表物質與裸露 | 否（新候選） |
| 3 | near Bayinbaolige (CN) | 41.05, 106.95 | 86.6 | 0.97 | 0.77 | 0.74 | 0.94 | 0.93 | 環境極端 | 否（新候選） |
| 4 | near Aksuat (KZ) | 48.85, 83.55 | 86.6 | 0.98 | 0.77 | 0.70 | 0.94 | 0.98 | 環境極端 | 否（新候選） |
| 5 | near Bayansayr (MN) | 45.45, 99.25 | 86.5 | 0.99 | 0.69 | 0.76 | 0.94 | 0.99 | 地表物質與裸露 | 否（新候選） |
| 6 | 84 km from Altay sumu (MN) | 45.05, 92.45 | 86.5 | 0.98 | 0.71 | 0.76 | 0.94 | 0.98 | 地表物質與裸露 | 否（新候選） |
| 7 | near Dabancheng (CN) | 43.25, 88.25 | 86.5 | 0.97 | 0.78 | 0.73 | 0.94 | 0.93 | 環境極端 | 否（新候選） |
| 8 | near Takeshiken (CN) | 46.25, 91.15 | 86.3 | 0.99 | 0.70 | 0.76 | 0.94 | 0.97 | 地表物質與裸露 | 否（新候選） |
| 9 | near Togrog (MN) | 45.85, 94.65 | 86.2 | 0.98 | 0.66 | 0.79 | 0.94 | 0.99 | 地表物質與裸露 | 否（新候選） |
| 10 | near Har-Us (MN) | 48.35, 91.15 | 86.2 | 0.96 | 0.69 | 0.78 | 0.99 | 0.93 | 地表物質與裸露 | 否（新候選） |

### 每個面向最像的前 5 名

- **地形**：111 km from Barkol (CN)（1.00，整體 88）；near Uyenchi Somon (MN)（1.00，整體 87）；72 km from Bayangol (MN)（1.00，整體 86）；32 km from Altai (MN)（1.00，整體 86）；near Bayinbaolige (CN)（1.00，整體 86）
- **地表物質與裸露**：68 km from Jisegumen (CN)（0.95，整體 42）；113 km from Cuozheqiangma (CN)（0.95，整體 41）；45 km from Laotai (CN)（0.95，整體 23）；near Karabulak (CN)（0.95，整體 21）；87 km from Tumxuk (CN)（0.95，整體 21）
- **環境極端**：127 km from Nur (CN)（0.92，整體 44）；109 km from Layka (CN)（0.91，整體 19）；1416 km from Gjoa Haven (CA)（0.90，整體 39）；77 km from Zangkaxa (CN)（0.90，整體 33）；120 km from Zhabu (CN)（0.89，整體 30）
- **水與冰**：near Altanteel (MN)（1.00，整體 85）；near Bugat (MN)（1.00，整體 84）；near Dzadgay (MN)（1.00，整體 84）；41 km from Duobagou (CN)（0.99，整體 82）；near Har-Us (MN)（1.00，整體 81）
- **大氣與沙塵**：33 km from Xalxikay (CN)（1.00，整體 86）；near Tiechanggou (CN)（1.00，整體 85）；30 km from Orgon (MN)（1.00，整體 85）；near Burenhayrhan (MN)（1.00，整體 84）；47 km from Bayan-Ovoo (MN)（1.00，整體 84）

### 已知類比地的剖面（標給這個目標的）

| 類比地 | 整體 | 全球前 % | 地形 | 地表物質與裸露 | 環境極端 | 水與冰 | 大氣與沙塵 | 最強 | 最弱 |
|---|---|---|---|---|---|---|---|---|---|
| Navajo Sandstone hematite concretions southern Utah | 71.1 | 1.0 | 0.82 | 0.56 | 0.69 | 0.94 | 0.69 | 水與冰 | 地表物質與裸露 |
| Lavic Lake and Sunshine volcanic field Mojave Desert (California) | 66.8 | 1.9 | 0.64 | 0.57 | 0.53 | 0.94 | 0.82 | 水與冰 | 環境極端 |
| Pilot Valley paleolake playa (Utah) | 66.4 | 2.1 | 0.52 | 0.59 | 0.72 | 0.94 | 0.80 | 水與冰 | 地形 |
| Mars Desert Research Station Hanksville (Utah) | 65.2 | 2.4 | 0.46 | 0.55 | 0.69 | 0.94 | 0.74 | 水與冰 | 地形 |
| Badwater Basin Death Valley (California) | 60.7 | 4.7 | 0.29 | 0.72 | 0.49 | 0.94 | 0.81 | 水與冰 | 地形 |
| Rio Tinto acid river headwaters (Spain) | 59.7 | 5.5 | 0.94 | 0.19 | 0.57 | 0.94 | 0.98 | 大氣與沙塵 | 地表物質與裸露 |
| Dalangtan saline playa Qaidam Basin (China) | 57.6 | 7.4 | 0.20 | 0.46 | 0.79 | 0.94 | 0.90 | 水與冰 | 地形 |
| Atacama Desert Yungay core (Chile) | 51.2 | 16.2 | 0.65 | 0.43 | 0.46 | 0.94 | 0.36 | 水與冰 | 大氣與沙塵 |
| White Sands gypsum dunes and Lake Lucero (New Mexico) | 49.3 | 19.5 | 0.16 | 0.50 | 0.62 | 0.94 | 0.63 | 水與冰 | 地形 |
| Matanumadh jarosite locality Kachchh (India) | 41.2 | 40.3 | 0.26 | 0.19 | 0.32 | 0.94 | 0.84 | 水與冰 | 地表物質與裸露 |
| Askja lava fields Vikrahraun (Iceland) | 40.9 | 41.5 | 0.44 | 0.55 | 0.13 | 0.94 | 0.40 | 水與冰 | 環境極端 |
| AMADEE-18 field site Marmul area Dhofar (Oman) | 40.7 | 42.2 | 0.17 | 0.50 | 0.17 | 0.94 | 0.81 | 水與冰 | 地形 |
| Lonar crater (India) | 38.6 | 49.3 | 0.25 | 0.13 | 0.29 | 0.94 | 0.97 | 大氣與沙塵 | 地表物質與裸露 |
| Dallol geothermal area Afar (Ethiopia) | 38.1 | 51.2 | 0.15 | 0.76 | 0.09 | 0.94 | 0.84 | 水與冰 | 環境極端 |
| Ka'u Desert Kilauea (Hawaii) | 34.6 | 64.5 | 0.80 | 0.09 | 0.21 | 0.94 | 0.36 | 水與冰 | 地表物質與裸露 |
| Mauna Kea upper slopes palagonitic tephra (Hawaii) | 31.6 | 75.4 | 0.38 | 0.14 | 0.47 | 0.94 | 0.37 | 水與冰 | 地表物質與裸露 |

## Arcadia Planitia (shallow ground ice)（47.2, -175.7）

**各面向「分數 ≥ 0.9」的陸地比例**：地形 55.1%、地表物質與裸露 0.1%、環境極端 0.0%、水與冰 1.7%、大氣與沙塵 20.0%；整體 ≥ 90 分：0.00%

### 整體相似度前 10 名

| # | 地點 | 座標 | 整體 | 地形 | 地表物質與裸露 | 環境極端 | 水與冰 | 大氣與沙塵 | 最弱面向 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 46 km from Urdgol (MN) | 48.25, 92.65 | 83.2 | 1.00 | 0.71 | 0.79 | 1.00 | 0.72 | 地表物質與裸露 | 否（新候選） |
| 2 | 208 km from Pevek (RU) | 67.85, 170.95 | 81.6 | 0.98 | 0.67 | 0.66 | 0.93 | 0.90 | 環境極端 | 否（新候選） |
| 3 | 131 km from Jumla (NP) | 30.25, 82.95 | 81.2 | 1.00 | 0.51 | 0.72 | 0.98 | 0.98 | 地表物質與裸露 | 否（新候選） |
| 4 | 138 km from Chernyshevskiy (RU) | 63.95, 110.65 | 81.1 | 0.98 | 0.54 | 0.67 | 0.99 | 0.98 | 地表物質與裸露 | 否（新候選） |
| 5 | 193 km from Yagodnoye (RU) | 64.25, 149.25 | 80.2 | 0.95 | 0.57 | 0.74 | 0.91 | 0.91 | 地表物質與裸露 | 否（新候選） |
| 6 | 622 km from Flin Flon (CA) | 60.35, -102.65 | 79.9 | 0.99 | 0.67 | 0.63 | 0.96 | 0.82 | 環境極端 | 否（新候選） |
| 7 | 143 km from Kotzebue (US) | 66.45, -159.55 | 79.9 | 1.00 | 0.56 | 0.68 | 0.96 | 0.89 | 地表物質與裸露 | 否（新候選） |
| 8 | 195 km from Tura (RU) | 64.45, 104.25 | 79.8 | 1.00 | 0.51 | 0.66 | 1.00 | 0.97 | 地表物質與裸露 | 否（新候選） |
| 9 | near Evensk (RU) | 62.05, 159.65 | 79.6 | 0.96 | 0.59 | 0.63 | 0.94 | 0.96 | 地表物質與裸露 | 否（新候選） |
| 10 | 99 km from Rutog (CN) | 33.75, 78.65 | 79.6 | 0.86 | 0.64 | 0.82 | 0.79 | 0.89 | 地表物質與裸露 | 否（新候選） |

### 每個面向最像的前 5 名

- **地形**：46 km from Urdgol (MN)（1.00，整體 83）；131 km from Jumla (NP)（1.00，整體 81）；143 km from Kotzebue (US)（1.00，整體 80）；195 km from Tura (RU)（1.00，整體 80）；622 km from Flin Flon (CA)（1.00，整體 79）
- **地表物質與裸露**：67 km from La Consulta (AR)（1.00，整體 26）；193 km from Qimantage (CN)（0.97，整體 76）；87 km from Colbun (CL)（0.97，整體 43）；88 km from Karakenja (TJ)（0.97，整體 30）；37 km from Pahalgam (IN)（0.96，整體 34）
- **環境極端**：127 km from Nur (CN)（0.92，整體 41）；109 km from Layka (CN)（0.91，整體 27）；1337 km from Gjoa Haven (CA)（0.90，整體 64）；77 km from Zangkaxa (CN)（0.90，整體 28）；57 km from Thang (IN)（0.89，整體 29）
- **水與冰**：46 km from Urdgol (MN)（1.00，整體 83）；141 km from Chernyshevskiy (RU)（1.00，整體 81）；140 km from Xagmakajor (CN)（1.00，整體 80）；195 km from Tura (RU)（1.00，整體 80）；623 km from Flin Flon (CA)（1.00，整體 78）
- **大氣與沙塵**：near Chernyshevskiy (RU)（1.00，整體 80）；142 km from Tura (RU)（1.00，整體 75）；211 km from Yerbogachen (RU)（1.00，整體 74）；86 km from Sangar (RU)（1.00，整體 74）；43 km from Arco (US)（0.99，整體 73）

### 已知類比地的剖面（標給這個目標的）

| 類比地 | 整體 | 全球前 % | 地形 | 地表物質與裸露 | 環境極端 | 水與冰 | 大氣與沙塵 | 最強 | 最弱 |
|---|---|---|---|---|---|---|---|---|---|
| Pilot Valley paleolake playa (Utah) | 61.4 | 5.4 | 0.72 | 0.50 | 0.72 | 0.47 | 0.88 | 大氣與沙塵 | 水與冰 |
| Lanzarote volcanic fields (Spain) | 56.7 | 13.3 | 0.62 | 0.64 | 0.55 | 0.47 | 0.60 | 地表物質與裸露 | 水與冰 |
| Haughton impact crater Devon Island (Canada) | 50.1 | 24.9 | 0.57 | 0.31 | 0.49 | 0.53 | 0.74 | 大氣與沙塵 | 地表物質與裸露 |
| HI-SEAS habitat Mauna Loa (Hawaii) | 38.6 | 54.1 | 0.31 | 0.80 | 0.47 | 0.47 | 0.68 | 地表物質與裸露 | 地形 |
| Lost Hammer cold saline spring Axel Heiberg Island (Canada) | 24.1 | 86.0 | 0.01 | 0.32 | 0.68 | 0.53 | 0.72 | 大氣與沙塵 | 地形 |
| Mauna Kea upper slopes palagonitic tephra (Hawaii) | 24.1 | 86.0 | 0.02 | 0.30 | 0.47 | 0.47 | 0.69 | 大氣與沙塵 | 地形 |
| McMurdo Dry Valleys (Antarctica) | 22.9 | 87.6 | 0.01 | 0.20 | 1.00 | 0.53 | 0.59 | 環境極端 | 地形 |
| Beacon Valley ancient buried ice (Antarctica) | 22.9 | 87.6 | 0.01 | 0.20 | 1.00 | 0.53 | 0.59 | 環境極端 | 地形 |
| Bockfjorden Volcanic Complex Svalbard (Norway) | 18.2 | 92.3 | 0.01 | 0.32 | 0.14 | 0.53 | 0.73 | 大氣與沙塵 | 地形 |

## Oxia Planum (ExoMars Rosalind Franklin landing site)（18.2, -24.55）

> 岩性類別用文獻覆寫為 `sedimentary_carbonate_clay`（全球地質圖 1:20M 分不出這裡的礦物）：Literature override: SIM3292 maps lNh (highland, impact breccia) at 1:20M, but the rover target is the Fe/Mg clay-bearing layered unit; Quantin-Nataf et al. 2021, Astrobiology 21(3):345, doi:10.1089/ast.2019.2191

**各面向「分數 ≥ 0.9」的陸地比例**：地形 61.0%、地表物質與裸露 0.0%、環境極端 0.0%、水與冰 86.9%、大氣與沙塵 13.9%；整體 ≥ 90 分：0.00%

### 整體相似度前 10 名

| # | 地點 | 座標 | 整體 | 地形 | 地表物質與裸露 | 環境極端 | 水與冰 | 大氣與沙塵 | 最弱面向 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 125 km from Shumanay Shahri (UZ) | 41.85, 57.85 | 90.9 | 1.00 | 0.91 | 0.73 | 1.00 | 0.94 | 環境極端 | 否（新候選） |
| 2 | 58 km from Turkmenbasy (TM) | 39.55, 53.25 | 90.5 | 1.00 | 0.96 | 0.70 | 1.00 | 0.90 | 環境極端 | 否（新候選） |
| 3 | near Gazojak (TM) | 41.15, 61.45 | 89.9 | 1.00 | 0.87 | 0.72 | 1.00 | 0.94 | 環境極端 | 否（新候選） |
| 4 | 149 km from Balkanabat (TM) | 40.85, 54.35 | 89.9 | 0.99 | 0.92 | 0.70 | 1.00 | 0.92 | 環境極端 | 否（新候選） |
| 5 | 58 km from Priozersk (KZ) | 46.45, 74.15 | 89.8 | 0.99 | 0.94 | 0.77 | 1.00 | 0.81 | 環境極端 | 否（新候選） |
| 6 | 30 km from Jetaral (CN) | 47.15, 87.05 | 89.2 | 0.98 | 0.94 | 0.78 | 1.00 | 0.79 | 環境極端 | 否（新候選） |
| 7 | 76 km from Kalpin (CN) | 39.85, 78.95 | 89.1 | 0.99 | 0.77 | 0.77 | 1.00 | 0.96 | 地表物質與裸露 | 否（新候選） |
| 8 | 201 km from Mo'ynoq Shahri (UZ) | 45.55, 58.55 | 89.1 | 0.99 | 0.93 | 0.74 | 1.00 | 0.82 | 環境極端 | 否（新候選） |
| 9 | 177 km from Zhanaozen (KZ) | 41.75, 52.75 | 88.8 | 1.00 | 0.86 | 0.72 | 1.00 | 0.90 | 環境極端 | 否（新候選） |
| 10 | 51 km from Ayteke Bi (KZ) | 46.15, 61.65 | 88.5 | 1.00 | 0.88 | 0.76 | 1.00 | 0.81 | 環境極端 | 否（新候選） |

### 每個面向最像的前 5 名

- **地形**：125 km from Shumanay Shahri (UZ)（1.00，整體 91）；58 km from Turkmenbasy (TM)（1.00，整體 90）；near Gazojak (TM)（1.00，整體 90）；near Mynaral (KZ)（1.00，整體 90）；177 km from Zhanaozen (KZ)（1.00，整體 89）
- **地表物質與裸露**：170 km from Turkmenbasy (TM)（0.92，整體 90）；near Mynaral (KZ)（0.92，整體 90）；near Jiajuedibu (CN)（0.92，整體 51）；79 km from Deltana (US)（0.92，整體 18）；125 km from Shumanay Shahri (UZ)（0.91，整體 91）
- **環境極端**：127 km from Nur (CN)（0.92，整體 19）；109 km from Layka (CN)（0.91，整體 13）；1337 km from Gjoa Haven (CA)（0.90，整體 28）；77 km from Zangkaxa (CN)（0.90，整體 12）；34 km from Aqqan (CN)（0.89，整體 29）
- **水與冰**：125 km from Shumanay Shahri (UZ)（1.00，整體 91）；58 km from Turkmenbasy (TM)（1.00，整體 90）；near Gazojak (TM)（1.00，整體 90）；149 km from Balkanabat (TM)（1.00，整體 90）；58 km from Priozersk (KZ)（1.00，整體 90）
- **大氣與沙塵**：52 km from Yuli (CN)（1.00，整體 88）；91 km from Nouadhibou (MR)（0.99，整體 86）；49 km from Dakhla (EH)（1.00，整體 84）；37 km from Al Hayy (IQ)（1.00，整體 83）；36 km from Kalpin (CN)（1.00，整體 83）

### 已知類比地的剖面（沒有標給這個目標的；列出全部已知類比地中全球排名最前的 8 個，供參考）

| 類比地 | 整體 | 全球前 % | 地形 | 地表物質與裸露 | 環境極端 | 水與冰 | 大氣與沙塵 | 最強 | 最弱 |
|---|---|---|---|---|---|---|---|---|---|
| Lanzarote volcanic fields (Spain) | 69.1 | 6.6 | 0.70 | 0.49 | 0.55 | 1.00 | 0.85 | 水與冰 | 地表物質與裸露 |
| Pilot Valley paleolake playa (Utah) | 68.7 | 6.8 | 0.79 | 0.50 | 0.72 | 1.00 | 0.57 | 水與冰 | 地表物質與裸露 |
| Dalangtan saline playa Qaidam Basin (China) | 67.9 | 7.5 | 0.99 | 0.21 | 0.79 | 1.00 | 0.87 | 水與冰 | 地表物質與裸露 |
| Black Point Lava Flow (Arizona) | 66.8 | 8.3 | 0.98 | 0.41 | 0.65 | 1.00 | 0.51 | 水與冰 | 地表物質與裸露 |
| Mars Desert Research Station Hanksville (Utah) | 64.1 | 10.8 | 0.85 | 0.42 | 0.69 | 1.00 | 0.51 | 水與冰 | 地表物質與裸露 |
| White Sands gypsum dunes and Lake Lucero (New Mexico) | 60.7 | 14.9 | 0.99 | 0.38 | 0.62 | 1.00 | 0.40 | 水與冰 | 地表物質與裸露 |
| Lavic Lake and Sunshine volcanic field Mojave Desert (California) | 59.9 | 15.9 | 0.68 | 0.44 | 0.53 | 1.00 | 0.59 | 水與冰 | 地表物質與裸露 |
| AMADEE-18 field site Marmul area Dhofar (Oman) | 57.2 | 20.5 | 1.00 | 0.37 | 0.17 | 1.00 | 0.96 | 水與冰 | 環境極端 |

## Meridiani Planum (Opportunity landing site, Eagle crater)（-1.95, -5.53）

> 岩性類別用文獻覆寫為 `evaporite_sulfate_clastic`（全球地質圖 1:20M 分不出這裡的礦物）：Literature override: SIM3292 maps HNhu (highland undivided) at 1:20M, but Opportunity found sulfate-rich sandstones with hematite spherules; Squyres et al. 2004, Science 306:1709, doi:10.1126/science.1104559

**各面向「分數 ≥ 0.9」的陸地比例**：地形 68.6%、地表物質與裸露 0.0%、環境極端 0.0%、水與冰 87.3%、大氣與沙塵 20.0%；整體 ≥ 90 分：0.00%

### 整體相似度前 10 名

| # | 地點 | 座標 | 整體 | 地形 | 地表物質與裸露 | 環境極端 | 水與冰 | 大氣與沙塵 | 最弱面向 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 127 km from Mazongshan (CN) | 42.85, 97.65 | 89.6 | 1.00 | 0.82 | 0.75 | 0.97 | 0.98 | 環境極端 | 否（新候選） |
| 2 | 92 km from Wentugaole (CN) | 42.25, 102.05 | 89.6 | 1.00 | 0.82 | 0.75 | 0.97 | 0.97 | 環境極端 | 否（新候選） |
| 3 | near Takeshiken (CN) | 45.95, 90.65 | 89.4 | 0.98 | 0.86 | 0.76 | 0.97 | 0.93 | 環境極端 | 否（新候選） |
| 4 | 45 km from Bayan-Ovoo (MN) | 44.85, 94.45 | 89.4 | 1.00 | 0.84 | 0.76 | 0.97 | 0.93 | 環境極端 | 否（新候選） |
| 5 | 55 km from Lenghu (CN) | 38.85, 93.95 | 89.3 | 0.98 | 0.74 | 0.83 | 0.97 | 0.97 | 地表物質與裸露 | 否（新候選） |
| 6 | 41 km from Mo'ynoq Shahri (UZ) | 44.15, 59.05 | 89.3 | 0.92 | 0.91 | 0.70 | 0.97 | 1.00 | 環境極端 | 否（新候選） |
| 7 | near Sa'erhusong (CN) | 47.45, 87.25 | 89.1 | 1.00 | 0.84 | 0.76 | 0.97 | 0.92 | 環境極端 | 否（新候選） |
| 8 | 53 km from Sharbulag (MN) | 48.35, 92.95 | 89.0 | 1.00 | 0.83 | 0.79 | 0.98 | 0.87 | 環境極端 | 否（新候選） |
| 9 | near Balqash (KZ) | 46.95, 74.95 | 88.9 | 0.99 | 0.83 | 0.75 | 0.97 | 0.93 | 環境極端 | 否（新候選） |
| 10 | 216 km from Mo'ynoq Shahri (UZ) | 45.65, 59.75 | 88.8 | 0.93 | 0.89 | 0.73 | 0.97 | 0.96 | 環境極端 | 否（新候選） |

### 每個面向最像的前 5 名

- **地形**：127 km from Mazongshan (CN)（1.00，整體 90）；92 km from Wentugaole (CN)（1.00，整體 90）；45 km from Bayan-Ovoo (MN)（1.00，整體 89）；60 km from Takeshiken (CN)（1.00，整體 89）；near Sa'erhusong (CN)（1.00，整體 89）
- **地表物質與裸露**：77 km from Colchani (BO)（1.00，整體 60）；58 km from Letlhakane (BW)（0.97，整體 57）；41 km from Cruz de Machacamarca (BO)（0.94，整體 59）；near Tozeur (TN)（0.92，整體 78）；near Zahedan (IR)（0.92，整體 56）
- **環境極端**：127 km from Nur (CN)（0.92，整體 31）；109 km from Layka (CN)（0.91，整體 16）；1417 km from Gjoa Haven (CA)（0.90，整體 38）；77 km from Zangkaxa (CN)（0.90，整體 18）；34 km from Aqqan (CN)（0.89，整體 28）
- **水與冰**：near Ulaantolgoy (MN)（1.00，整體 87）；31 km from Harhiraa (MN)（1.00，整體 86）；50 km from Tavin (MN)（1.00，整體 85）；52 km from Sharga (MN)（1.00，整體 85）；118 km from Wutumeiren (CN)（1.00，整體 84）
- **大氣與沙塵**：41 km from Mo'ynoq Shahri (UZ)（1.00，整體 89）；90 km from Taushyq (KZ)（1.00，整體 88）；52 km from Mazongshan (CN)（1.00，整體 88）；near Gasi (CN)（1.00，整體 88）；110 km from Yiwu (CN)（1.00，整體 88）

### 已知類比地的剖面（沒有標給這個目標的；列出全部已知類比地中全球排名最前的 8 個，供參考）

| 類比地 | 整體 | 全球前 % | 地形 | 地表物質與裸露 | 環境極端 | 水與冰 | 大氣與沙塵 | 最強 | 最弱 |
|---|---|---|---|---|---|---|---|---|---|
| Dalangtan saline playa Qaidam Basin (China) | 85.3 | 0.4 | 0.95 | 0.63 | 0.79 | 0.97 | 0.99 | 大氣與沙塵 | 地表物質與裸露 |
| Lanzarote volcanic fields (Spain) | 77.9 | 4.7 | 0.84 | 0.69 | 0.55 | 0.97 | 0.99 | 大氣與沙塵 | 環境極端 |
| Pilot Valley paleolake playa (Utah) | 77.1 | 5.3 | 0.87 | 0.64 | 0.72 | 0.97 | 0.71 | 水與冰 | 地表物質與裸露 |
| Mars Desert Research Station Hanksville (Utah) | 75.5 | 6.5 | 0.95 | 0.62 | 0.69 | 0.97 | 0.65 | 水與冰 | 地表物質與裸露 |
| Black Point Lava Flow (Arizona) | 75.0 | 6.8 | 0.99 | 0.59 | 0.65 | 0.97 | 0.65 | 地形 | 地表物質與裸露 |
| White Sands gypsum dunes and Lake Lucero (New Mexico) | 70.7 | 10.6 | 0.93 | 0.57 | 0.62 | 0.97 | 0.54 | 水與冰 | 大氣與沙塵 |
| Lavic Lake and Sunshine volcanic field Mojave Desert (California) | 69.7 | 11.5 | 0.83 | 0.64 | 0.53 | 0.97 | 0.73 | 水與冰 | 環境極端 |
| AMADEE-18 field site Marmul area Dhofar (Oman) | 61.9 | 18.3 | 0.94 | 0.63 | 0.17 | 0.97 | 0.91 | 水與冰 | 環境極端 |

## Protonilus Mensae (candidate human exploration zone, buried glacial ice)（41.905, 48.548）

**各面向「分數 ≥ 0.9」的陸地比例**：地形 8.2%、地表物質與裸露 0.1%、環境極端 0.0%、水與冰 2.2%、大氣與沙塵 20.0%；整體 ≥ 90 分：0.00%

### 整體相似度前 10 名

| # | 地點 | 座標 | 整體 | 地形 | 地表物質與裸露 | 環境極端 | 水與冰 | 大氣與沙塵 | 最弱面向 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 93 km from Maindong (CN) | 30.95, 84.55 | 89.9 | 0.94 | 0.87 | 0.78 | 0.96 | 0.96 | 環境極端 | 否（新候選） |
| 2 | 81 km from Zhabu (CN) | 32.45, 82.95 | 88.7 | 0.94 | 0.88 | 0.80 | 1.00 | 0.82 | 環境極端 | 否（新候選） |
| 3 | 80 km from Jiajuedibu (CN) | 31.35, 87.95 | 87.9 | 0.96 | 0.82 | 0.73 | 0.98 | 0.94 | 環境極端 | 否（新候選） |
| 4 | near Zangkaxa (CN) | 33.75, 80.65 | 86.1 | 0.97 | 0.75 | 0.82 | 0.98 | 0.80 | 地表物質與裸露 | 否（新候選） |
| 5 | 30 km from Rock Springs (US) | 41.65, -108.85 | 85.2 | 1.00 | 0.75 | 0.73 | 0.84 | 0.97 | 環境極端 | 否（新候選） |
| 6 | 128 km from Maindong (CN) | 32.45, 85.75 | 85.1 | 0.97 | 0.78 | 0.80 | 0.89 | 0.83 | 地表物質與裸露 | 否（新候選） |
| 7 | near Qinglung (CN) | 31.05, 90.55 | 85.1 | 0.99 | 0.70 | 0.69 | 0.99 | 0.95 | 環境極端 | 否（新候選） |
| 8 | 75 km from Bar Nunn (US) | 43.25, -107.15 | 84.5 | 1.00 | 0.73 | 0.72 | 0.84 | 0.98 | 環境極端 | 否（新候選） |
| 9 | 54 km from Las Heras (AR) | -32.45, -69.15 | 84.2 | 0.99 | 0.79 | 0.71 | 0.84 | 0.91 | 環境極端 | 否（新候選） |
| 10 | near Tsetsegnuur (MN) | 46.55, 93.45 | 84.1 | 1.00 | 0.77 | 0.84 | 0.99 | 0.66 | 大氣與沙塵 | 否（新候選） |

### 每個面向最像的前 5 名

- **地形**：67 km from Zhabu (CN)（1.00，整體 85）；30 km from Rock Springs (US)（1.00，整體 85）；75 km from Bar Nunn (US)（1.00，整體 84）；67 km from Tamberias (AR)（1.00，整體 84）；near Tsetsegnuur (MN)（1.00，整體 84）
- **地表物質與裸露**：37 km from Khandud (AF)（0.96，整體 32）；44 km from Zongga (CN)（0.96，整體 27）；57 km from Thang (IN)（0.96，整體 26）；126 km from Layka (CN)（0.96，整體 24）；65 km from Tumxuk (CN)（0.96，整體 22）
- **環境極端**：127 km from Nur (CN)（0.92，整體 50）；109 km from Layka (CN)（0.91，整體 20）；1416 km from Gjoa Haven (CA)（0.90，整體 58）；77 km from Zangkaxa (CN)（0.90，整體 37）；120 km from Zhabu (CN)（0.89，整體 33）
- **水與冰**：81 km from Zhabu (CN)（1.00，整體 89）；55 km from Maindong (CN)（1.00，整體 86）；near Jiaqiong (CN)（1.00，整體 85）；near Hohtolgoy (MN)（1.00，整體 84）；144 km from Maindong (CN)（1.00，整體 84）
- **大氣與沙塵**：near Rawlins (US)（1.00，整體 85）；near Jiajuedibu (CN)（1.00，整體 82）；near Waterflow (US)（1.00，整體 82）；39 km from Mammoth Lakes (US)（1.00，整體 81）；near Laguna (US)（1.00，整體 81）

### 已知類比地的剖面（沒有標給這個目標的；列出全部已知類比地中全球排名最前的 8 個，供參考）

| 類比地 | 整體 | 全球前 % | 地形 | 地表物質與裸露 | 環境極端 | 水與冰 | 大氣與沙塵 | 最強 | 最弱 |
|---|---|---|---|---|---|---|---|---|---|
| Navajo Sandstone hematite concretions southern Utah | 75.0 | 0.4 | 0.77 | 0.66 | 0.69 | 0.84 | 0.93 | 大氣與沙塵 | 地表物質與裸露 |
| Mars Desert Research Station Hanksville (Utah) | 74.5 | 0.5 | 0.66 | 0.69 | 0.69 | 0.84 | 0.89 | 大氣與沙塵 | 地形 |
| Pilot Valley paleolake playa (Utah) | 71.8 | 1.0 | 0.71 | 0.72 | 0.72 | 0.84 | 0.83 | 水與冰 | 地形 |
| Lavic Lake and Sunshine volcanic field Mojave Desert (California) | 71.7 | 1.0 | 0.81 | 0.70 | 0.53 | 0.84 | 0.81 | 水與冰 | 環境極端 |
| Lanzarote volcanic fields (Spain) | 67.0 | 2.7 | 0.80 | 0.70 | 0.55 | 0.84 | 0.55 | 水與冰 | 大氣與沙塵 |
| Black Point Lava Flow (Arizona) | 66.8 | 2.7 | 0.45 | 0.71 | 0.65 | 0.84 | 0.89 | 大氣與沙塵 | 地形 |
| White Sands gypsum dunes and Lake Lucero (New Mexico) | 62.7 | 5.2 | 0.28 | 0.63 | 0.62 | 0.84 | 1.00 | 大氣與沙塵 | 地形 |
| Atacama Desert Yungay core (Chile) | 62.2 | 5.6 | 0.77 | 0.65 | 0.46 | 0.84 | 0.74 | 水與冰 | 環境極端 |

## Arcadia Planitia AP-105 (SkyFall design reference landing site)（43.3295, -161.4772）

**各面向「分數 ≥ 0.9」的陸地比例**：地形 55.0%、地表物質與裸露 0.1%、環境極端 0.0%、水與冰 1.7%、大氣與沙塵 20.0%；整體 ≥ 90 分：0.00%

### 整體相似度前 10 名

| # | 地點 | 座標 | 整體 | 地形 | 地表物質與裸露 | 環境極端 | 水與冰 | 大氣與沙塵 | 最弱面向 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 46 km from Urdgol (MN) | 48.25, 92.65 | 88.7 | 1.00 | 0.83 | 0.79 | 0.94 | 0.90 | 環境極端 | 否（新候選） |
| 2 | near Kosh-Agach (RU) | 49.95, 88.65 | 85.0 | 0.99 | 0.70 | 0.80 | 0.82 | 0.97 | 地表物質與裸露 | 否（新候選） |
| 3 | 49 km from Zhabu (CN) | 33.45, 82.95 | 85.0 | 0.97 | 0.57 | 0.83 | 0.98 | 0.98 | 地表物質與裸露 | 否（新候選） |
| 4 | 46 km from Erzin (RU) | 49.85, 95.15 | 84.1 | 0.91 | 0.65 | 0.76 | 0.99 | 0.95 | 地表物質與裸露 | 否（新候選） |
| 5 | 62 km from Hoshoot (MN) | 48.55, 88.55 | 82.5 | 0.90 | 0.57 | 0.79 | 0.98 | 0.96 | 地表物質與裸露 | 否（新候選） |
| 6 | 234 km from Zhabu (CN) | 34.85, 84.75 | 81.7 | 0.92 | 0.88 | 0.86 | 0.58 | 0.91 | 水與冰 | 否（新候選） |
| 7 | 191 km from Qimantage (CN) | 35.75, 89.45 | 81.6 | 0.94 | 0.93 | 0.80 | 0.58 | 0.90 | 水與冰 | 否（新候選） |
| 8 | near Qimantage (CN) | 37.35, 90.25 | 81.6 | 0.99 | 0.57 | 0.83 | 0.94 | 0.82 | 地表物質與裸露 | 否（新候選） |
| 9 | 199 km from Koramlik (CN) | 35.65, 86.35 | 81.5 | 0.98 | 0.88 | 0.83 | 0.58 | 0.86 | 水與冰 | 否（新候選） |
| 10 | 121 km from Murghob (TJ) | 39.15, 73.35 | 81.4 | 0.96 | 0.76 | 0.76 | 0.76 | 0.86 | 地表物質與裸露 | 否（新候選） |

### 每個面向最像的前 5 名

- **地形**：46 km from Urdgol (MN)（1.00，整體 89）；55 km from Tsetserleg (MN)（1.00，整體 83）；near Kosh-Agach (RU)（1.00，整體 82）；near Qimantage (CN)（1.00，整體 82）；175 km from Qimantage (CN)（1.00，整體 81）
- **地表物質與裸露**：74 km from Assab (ER)（0.97，整體 39）；91 km from Karakenja (TJ)（0.97，整體 32）；180 km from Qimantage (CN)（0.95，整體 78）；39 km from Pahalgam (IN)（0.96，整體 36）；79 km from Colbun (CL)（0.95，整體 25）
- **環境極端**：127 km from Nur (CN)（0.92，整體 45）；109 km from Layka (CN)（0.91，整體 29）；1337 km from Gjoa Haven (CA)（0.90，整體 62）；77 km from Zangkaxa (CN)（0.90，整體 30）；57 km from Thang (IN)（0.89，整體 31）
- **水與冰**：30 km from Qimantage (CN)（1.00，整體 80）；56 km from Qiangma (CN)（1.00，整體 78）；51 km from Jargalant (MN)（1.00，整體 77）；43 km from Evensk (RU)（0.99，整體 76）；near Altan (MN)（1.00，整體 76）
- **大氣與沙塵**：90 km from Luring (CN)（1.00，整體 75）；31 km from Vlaa Vula (MN)（1.00，整體 73）；77 km from Kyzyl-Khaya (RU)（1.00，整體 71）；123 km from Jisegumen (CN)（1.00，整體 70）；72 km from Cuozheqiangma (CN)（1.00，整體 70）

### 已知類比地的剖面（沒有標給這個目標的；列出全部已知類比地中全球排名最前的 8 個，供參考）

| 類比地 | 整體 | 全球前 % | 地形 | 地表物質與裸露 | 環境極端 | 水與冰 | 大氣與沙塵 | 最強 | 最弱 |
|---|---|---|---|---|---|---|---|---|---|
| Dalangtan saline playa Qaidam Basin (China) | 65.2 | 1.8 | 0.99 | 0.54 | 0.79 | 0.42 | 0.76 | 地形 | 水與冰 |
| Mars Desert Research Station Hanksville (Utah) | 63.1 | 3.4 | 0.78 | 0.51 | 0.69 | 0.42 | 0.88 | 大氣與沙塵 | 水與冰 |
| White Sands gypsum dunes and Lake Lucero (New Mexico) | 62.8 | 3.7 | 1.00 | 0.49 | 0.62 | 0.42 | 0.77 | 地形 | 水與冰 |
| Black Point Lava Flow (Arizona) | 62.2 | 4.7 | 0.94 | 0.44 | 0.65 | 0.42 | 0.88 | 地形 | 水與冰 |
| Pilot Valley paleolake playa (Utah) | 61.9 | 5.1 | 0.72 | 0.53 | 0.72 | 0.42 | 0.94 | 大氣與沙塵 | 水與冰 |
| Lavic Lake and Sunshine volcanic field Mojave Desert (California) | 58.5 | 10.2 | 0.60 | 0.55 | 0.53 | 0.42 | 0.96 | 大氣與沙塵 | 水與冰 |
| Lanzarote volcanic fields (Spain) | 58.0 | 11.0 | 0.62 | 0.67 | 0.55 | 0.42 | 0.78 | 大氣與沙塵 | 水與冰 |
| Askja lava fields Vikrahraun (Iceland) | 49.0 | 27.2 | 0.80 | 1.00 | 0.13 | 0.42 | 0.54 | 地表物質與裸露 | 環境極端 |
