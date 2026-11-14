# 類比剖面總表（自動產生）

> 產生時間 2026-11-14 23:51。由 `scripts/make_profiles.py` 產生，數字以 `outputs/profiles/*.json` 為準。
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
| 1 | 92 km from Wutumeiren (CN) | 37.45, 93.95 | 88.4 | 0.72 | 0.96 | 0.83 | 1.00 | 0.94 | 地形 | 否（新候選） |
| 2 | near Dabancheng (CN) | 43.35, 88.15 | 88.2 | 0.98 | 0.78 | 0.73 | 1.00 | 0.95 | 環境極端 | 否（新候選） |
| 3 | 152 km from Sanlei (CN) | 39.95, 103.55 | 87.4 | 1.00 | 0.71 | 0.74 | 1.00 | 0.96 | 地表物質與裸露 | 否（新候選） |
| 4 | 113 km from Mori (CN) | 43.55, 91.55 | 87.1 | 0.99 | 0.75 | 0.74 | 1.00 | 0.92 | 環境極端 | 否（新候選） |
| 5 | near Lasengmiao (CN) | 39.45, 106.95 | 87.0 | 1.00 | 0.73 | 0.71 | 1.00 | 0.95 | 環境極端 | 否（新候選） |
| 6 | near Chijin (CN) | 40.15, 97.45 | 86.9 | 1.00 | 0.68 | 0.74 | 1.00 | 0.99 | 地表物質與裸露 | 否（新候選） |
| 7 | 167 km from Mazongshan (CN) | 42.95, 98.35 | 86.9 | 0.99 | 0.70 | 0.77 | 1.00 | 0.93 | 地表物質與裸露 | 否（新候選） |
| 8 | near Todok (CN) | 44.35, 83.75 | 86.8 | 0.99 | 0.72 | 0.72 | 1.00 | 0.95 | 地表物質與裸露 | 否（新候選） |
| 9 | 77 km from Yiwu (CN) | 42.95, 95.55 | 86.8 | 1.00 | 0.68 | 0.76 | 1.00 | 0.96 | 地表物質與裸露 | 否（新候選） |
| 10 | 80 km from Yiwu (CN) | 43.85, 94.15 | 86.6 | 1.00 | 0.70 | 0.74 | 1.00 | 0.94 | 地表物質與裸露 | 否（新候選） |

### 每個面向最像的前 5 名

- **地形**：152 km from Sanlei (CN)（1.00，整體 87）；near Lasengmiao (CN)（1.00，整體 87）；near Chijin (CN)（1.00，整體 87）；149 km from Bulgan (MN)（1.00，整體 87）；77 km from Yiwu (CN)（1.00，整體 87）
- **地表物質與裸露**：92 km from Wutumeiren (CN)（0.96，整體 88）；54 km from Tumxuk (CN)（0.95，整體 14）；46 km from Bofeng (CN)（0.94，整體 14）；near Kyzyl-Khaya (RU)（0.93，整體 14）；216 km from Prudhoe Bay (US)（0.93，整體 12）
- **環境極端**：1417 km from Gjoa Haven (CA)（0.90，整體 29）；120 km from Nur (CN)（0.90，整體 25）；95 km from Layka (CN)（0.89，整體 20）；127 km from Jisegumen (CN)（0.89，整體 13）；107 km from Guma (CN)（0.89，整體 13）
- **水與冰**：92 km from Wutumeiren (CN)（1.00，整體 88）；near Dabancheng (CN)（1.00，整體 88）；152 km from Sanlei (CN)（1.00，整體 87）；113 km from Mori (CN)（1.00，整體 87）；near Lasengmiao (CN)（1.00，整體 87）
- **大氣與沙塵**：near Adrasmon (TJ)（0.99，整體 86）；103 km from Hami (CN)（0.99，整體 85）；64 km from A'yi Take (CN)（1.00，整體 85）；47 km from Xiba (CN)（1.00，整體 84）；near Hankazi (CN)（1.00，整體 84）

### 每個變數最像的前 5 名（一張圖看：`board_jezero.png`）

> 括號內：該變數的分數、地球的值、整體相似度。只有一個變數的面向（水與冰、大氣與沙塵）和上面的面向排名相同，不重複列。

- **坡度**（火星 2.24°）：152 km from Sanlei (CN)（1.00，2.18°，整體 87）；near Lasengmiao (CN)（0.99，1.94°，整體 87）；near Chijin (CN)（1.00，2.31°，整體 87）；149 km from Bulgan (MN)（1.00，2.07°，整體 87）；77 km from Yiwu (CN)（1.00，2.31°，整體 87）
- **粗糙度**（火星 10.6 m）：152 km from Sanlei (CN)（1.00，9.7 m，整體 87）；113 km from Mori (CN)（1.00，11.2 m，整體 87）；near Lasengmiao (CN)（1.00，10.1 m，整體 87）；near Todok (CN)（1.00，11.7 m，整體 87）；149 km from Bulgan (MN)（1.00，11.3 m，整體 87）
- **岩性**（火星 clastic）：92 km from Wutumeiren (CN)（0.90，ss，整體 88）；near Dabancheng (CN)（0.90，ss，整體 88）；152 km from Sanlei (CN)（0.90，ss，整體 87）；113 km from Mori (CN)（0.90，ss，整體 87）；near Lasengmiao (CN)（0.90，ss，整體 87）
- **熱慣量**（火星 第 88 百分位）：52 km from Kupino (RU)（1.00，第 88 百分位，整體 76）；37 km from Jati (PK)（1.00，第 88 百分位，整體 75）；near Sants-Montjuic (ES)（1.00，第 87 百分位，整體 74）；near Qian'an (CN)（0.99，第 87 百分位，整體 73）；near Karachi (PK)（1.00，第 88 百分位，整體 73）
- **無植被**（火星 NDVI 0.00）：92 km from Wutumeiren (CN)（1.00，NDVI -0.01，整體 88）；235 km from Qilanbulak (CN)（1.00，NDVI -0.04，整體 86）；40 km from Xitieshan (CN)（1.00，NDVI -0.02，整體 85）；164 km from Beyneu (KZ)（1.00，NDVI -0.01，整體 85）；47 km from Tieganlike (CN)（0.99，NDVI 0.00，整體 84）
- **溫度**（火星 -49.5 °C）：772 km from Clyde River (CA)（1.00，-19.0 °C，整體 66）；1303 km from Clyde River (CA)（1.00，-18.8 °C，整體 64）；281 km from Clyde River (CA)（1.00，-17.6 °C，整體 42）；897 km from Kugluktuk (CA)（1.00，-19.0 °C，整體 30）；1416 km from Gjoa Haven (CA)（1.00，-19.2 °C，整體 30）
- **乾燥度**（火星 最乾）：83 km from Al Kharijah (EG)（1.00，乾燥指數 0.001，整體 77）；120 km from Abu Sunbul (EG)（1.00，乾燥指數 0.000，整體 76）；near Paracas (PE)（0.99，乾燥指數 0.001，整體 75）；near Al Badari (EG)（1.00，乾燥指數 0.000，整體 74）；62 km from Qasr al Farafirah (EG)（1.00，乾燥指數 0.001，整體 74）

### 已知類比地的剖面（標給這個目標的）

| 類比地 | 整體 | 全球前 % | 地形 | 地表物質與裸露 | 環境極端 | 水與冰 | 大氣與沙塵 | 最強 | 最弱 |
|---|---|---|---|---|---|---|---|---|---|
| Mars Desert Research Station Hanksville (Utah) | 72.4 | 5.8 | 0.97 | 0.50 | 0.69 | 1.00 | 0.60 | 水與冰 | 地表物質與裸露 |
| Black Point Lava Flow (Arizona) | 70.2 | 7.6 | 0.93 | 0.50 | 0.65 | 1.00 | 0.60 | 水與冰 | 地表物質與裸露 |
| Lavic Lake and Sunshine volcanic field Mojave Desert (California) | 69.1 | 8.6 | 0.95 | 0.55 | 0.52 | 1.00 | 0.69 | 水與冰 | 環境極端 |
| Lake Salda (Turkey) | 58.9 | 20.9 | 0.80 | 0.17 | 0.61 | 1.00 | 0.84 | 水與冰 | 地表物質與裸露 |
| Matanumadh jarosite locality Kachchh (India) | 56.1 | 25.8 | 0.92 | 0.19 | 0.33 | 1.00 | 0.97 | 水與冰 | 地表物質與裸露 |
| Lonar crater (India) | 50.4 | 37.1 | 0.91 | 0.13 | 0.31 | 1.00 | 0.89 | 水與冰 | 地表物質與裸露 |
| Ries impact crater (Germany) | 47.7 | 42.7 | 0.96 | 0.10 | 0.44 | 1.00 | 0.65 | 水與冰 | 地表物質與裸露 |
| Dresser Formation stromatolites Pilbara (Australia) | 47.2 | 43.9 | 0.98 | 0.56 | 0.16 | 1.00 | 0.29 | 水與冰 | 環境極端 |
| Askja lava fields Vikrahraun (Iceland) | 44.5 | 50.6 | 0.93 | 0.55 | 0.15 | 0.99 | 0.27 | 水與冰 | 環境極端 |
| Haughton impact crater Devon Island (Canada) | 25.3 | 86.1 | 0.93 | 0.87 | 0.48 | 0.01 | 0.28 | 地形 | 水與冰 |
| Pavilion Lake (British Columbia) | 19.1 | 92.5 | 0.01 | 0.10 | 0.61 | 1.00 | 0.41 | 水與冰 | 地形 |
| Bockfjorden Volcanic Complex Svalbard (Norway) | 9.0 | 99.8 | 0.01 | 0.89 | 0.14 | 0.01 | 0.28 | 地表物質與裸露 | 水與冰 |

## Gale Crater（-5.4, 137.8）

**各面向「分數 ≥ 0.9」的陸地比例**：地形 6.3%、地表物質與裸露 0.1%、環境極端 0.0%、水與冰 87.5%、大氣與沙塵 20.0%；整體 ≥ 90 分：0.00%

### 整體相似度前 10 名

| # | 地點 | 座標 | 整體 | 地形 | 地表物質與裸露 | 環境極端 | 水與冰 | 大氣與沙塵 | 最弱面向 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | near Altanteel (MN) | 47.05, 92.85 | 87.4 | 0.99 | 0.68 | 0.80 | 0.99 | 0.96 | 地表物質與裸露 | 否（新候選） |
| 2 | 95 km from Altay sumu (MN) | 44.95, 92.25 | 87.2 | 0.98 | 0.76 | 0.74 | 0.94 | 0.96 | 環境極端 | 否（新候選） |
| 3 | near Bayansayr (MN) | 45.45, 99.25 | 87.1 | 0.99 | 0.71 | 0.77 | 0.94 | 0.99 | 地表物質與裸露 | 否（新候選） |
| 4 | near Araltobe (CN) | 46.45, 90.15 | 87.0 | 0.97 | 0.73 | 0.76 | 0.94 | 0.99 | 地表物質與裸露 | 否（新候選） |
| 5 | 79 km from Barkol (CN) | 43.45, 92.05 | 86.8 | 1.00 | 0.74 | 0.75 | 0.94 | 0.95 | 地表物質與裸露 | 否（新候選） |
| 6 | near Togrog (MN) | 45.85, 94.65 | 86.3 | 0.98 | 0.68 | 0.77 | 0.94 | 0.99 | 地表物質與裸露 | 否（新候選） |
| 7 | 192 km from Dzalaa (MN) | 42.85, 98.75 | 86.2 | 1.00 | 0.71 | 0.77 | 0.94 | 0.93 | 地表物質與裸露 | 否（新候選） |
| 8 | near Hovd (MN) | 44.55, 102.15 | 86.2 | 0.99 | 0.65 | 0.76 | 0.99 | 0.99 | 地表物質與裸露 | 否（新候選） |
| 9 | near Dabancheng (CN) | 43.25, 88.25 | 86.0 | 0.97 | 0.76 | 0.73 | 0.94 | 0.93 | 環境極端 | 否（新候選） |
| 10 | near Har-Us (MN) | 48.35, 91.15 | 85.9 | 0.96 | 0.69 | 0.77 | 0.99 | 0.93 | 地表物質與裸露 | 否（新候選） |

### 每個面向最像的前 5 名

- **地形**：111 km from Barkol (CN)（1.00，整體 87）；near Altanteel (MN)（1.00，整體 86）；32 km from Altai (MN)（1.00，整體 86）；192 km from Dzalaa (MN)（1.00，整體 86）；near Saynshand (MN)（1.00，整體 86）
- **地表物質與裸露**：92 km from Wutumeiren (CN)（0.96，整體 62）；54 km from Tumxuk (CN)（0.96，整體 20）；46 km from Bofeng (CN)（0.95，整體 20）；72 km from Khandud (AF)（0.93，整體 31）；near Bokombayevskoye (KG)（0.93，整體 21）
- **環境極端**：120 km from Nur (CN)（0.90，整體 49）；1417 km from Gjoa Haven (CA)（0.90，整體 36）；103 km from Layka (CN)（0.89，整體 22）；127 km from Jisegumen (CN)（0.89，整體 20）；107 km from Guma (CN)（0.89，整體 18）
- **水與冰**：near Altanteel (MN)（1.00，整體 86）；near Bugat (MN)（1.00，整體 84）；near Dzadgay (MN)（1.00，整體 84）；near Dzuunhovoo (MN)（1.00，整體 81）；near Har-Us (MN)（1.00，整體 81）
- **大氣與沙塵**：near Burenhayrhan (MN)（1.00，整體 86）；33 km from Xalxikay (CN)（1.00，整體 85）；near Hovd (MN)（1.00，整體 85）；near Tiechanggou (CN)（1.00，整體 84）；47 km from Bayan-Ovoo (MN)（1.00，整體 84）

### 每個變數最像的前 5 名（一張圖看：`board_gale.png`）

> 括號內：該變數的分數、地球的值、整體相似度。只有一個變數的面向（水與冰、大氣與沙塵）和上面的面向排名相同，不重複列。

- **坡度**（火星 5.46°）：79 km from Barkol (CN)（1.00，5.38°，整體 87）；near Altanteel (MN)（1.00，5.31°，整體 86）；87 km from Altay sumu (MN)（1.00，5.36°，整體 86）；32 km from Altai (MN)（1.00，5.19°，整體 86）；192 km from Dzalaa (MN)（1.00，5.56°，整體 86）
- **粗糙度**（火星 27.3 m）：near Altanteel (MN)（1.00，27.5 m，整體 87）；95 km from Altay sumu (MN)（1.00，28.4 m，整體 87）；93 km from Barkol (CN)（1.00，28.2 m，整體 87）；near Takeshiken (CN)（1.00，28.2 m，整體 86）；32 km from Altai (MN)（1.00，26.7 m，整體 86）
- **岩性**（火星 clastic）：near Bayansayr (MN)（0.90，ss，整體 87）；111 km from Barkol (CN)（0.90，ss，整體 87）；32 km from Altai (MN)（0.90，ss，整體 86）；near Dabancheng (CN)（0.90，ss，整體 86）；39 km from Luntai (CN)（0.90，ss，整體 86）
- **熱慣量**（火星 第 84 百分位）：128 km from Jeminay (CN)（1.00，第 84 百分位，整體 78）；180 km from Ust-Maya (RU)（1.00，第 84 百分位，整體 70）；53 km from Comandante Luis Piedra Buena (AR)（1.00，第 84 百分位，整體 68）；47 km from Kulachi (PK)（0.99，第 85 百分位，整體 68）；62 km from Dukat (RU)（1.00，第 84 百分位，整體 67）
- **無植被**（火星 NDVI 0.00）：233 km from Dillingham (US)（1.00，NDVI -0.03，整體 76）；1346 km from Clyde River (CA)（1.00，NDVI -0.06，整體 70）；704 km from Clyde River (CA)（1.00，NDVI -0.08，整體 68）；69 km from Valdez (US)（1.00，NDVI -0.01，整體 65）；93 km from Sand Point (US)（1.00，NDVI -0.01，整體 62）
- **溫度**（火星 -50.9 °C）：1346 km from Clyde River (CA)（1.00，-20.4 °C，整體 70）；765 km from Clyde River (CA)（1.00，-16.5 °C，整體 68）；281 km from Clyde River (CA)（1.00，-17.6 °C，整體 56）；1407 km from Gjoa Haven (CA)（1.00，-19.1 °C，整體 45）；1058 km from Upernavik (GL)（1.00，-16.6 °C，整體 45）
- **乾燥度**（火星 最乾）：41 km from Santiago (PE)（0.99，乾燥指數 0.001，整體 73）；73 km from Tocopilla (CL)（1.00，乾燥指數 0.000，整體 70）；near Antofagasta (CL)（1.00，乾燥指數 0.001，整體 70）；45 km from Al Kharijah (EG)（1.00，乾燥指數 0.001，整體 69）；69 km from Abu Sunbul (EG)（1.00，乾燥指數 0.000，整體 67）

### 已知類比地的剖面（標給這個目標的）

| 類比地 | 整體 | 全球前 % | 地形 | 地表物質與裸露 | 環境極端 | 水與冰 | 大氣與沙塵 | 最強 | 最弱 |
|---|---|---|---|---|---|---|---|---|---|
| Navajo Sandstone hematite concretions southern Utah | 71.1 | 1.0 | 0.82 | 0.54 | 0.69 | 0.94 | 0.69 | 水與冰 | 地表物質與裸露 |
| Lavic Lake and Sunshine volcanic field Mojave Desert (California) | 66.9 | 1.9 | 0.64 | 0.56 | 0.52 | 0.94 | 0.82 | 水與冰 | 環境極端 |
| Pilot Valley paleolake playa (Utah) | 66.1 | 2.1 | 0.52 | 0.56 | 0.71 | 0.94 | 0.80 | 水與冰 | 地形 |
| Mars Desert Research Station Hanksville (Utah) | 64.9 | 2.5 | 0.46 | 0.52 | 0.69 | 0.94 | 0.74 | 水與冰 | 地形 |
| Rio Tinto acid river headwaters (Spain) | 59.5 | 5.5 | 0.94 | 0.19 | 0.57 | 0.94 | 0.98 | 大氣與沙塵 | 地表物質與裸露 |
| Badwater Basin Death Valley (California) | 59.2 | 5.8 | 0.29 | 0.74 | 0.49 | 0.94 | 0.81 | 水與冰 | 地形 |
| Dalangtan saline playa Qaidam Basin (China) | 57.7 | 7.2 | 0.20 | 0.46 | 0.80 | 0.94 | 0.90 | 水與冰 | 地形 |
| Atacama Desert Yungay core (Chile) | 51.4 | 15.8 | 0.65 | 0.43 | 0.48 | 0.94 | 0.36 | 水與冰 | 大氣與沙塵 |
| White Sands gypsum dunes and Lake Lucero (New Mexico) | 48.0 | 21.7 | 0.16 | 0.45 | 0.62 | 0.94 | 0.63 | 水與冰 | 地形 |
| Matanumadh jarosite locality Kachchh (India) | 41.9 | 37.9 | 0.26 | 0.19 | 0.33 | 0.94 | 0.84 | 水與冰 | 地表物質與裸露 |
| Askja lava fields Vikrahraun (Iceland) | 40.9 | 41.4 | 0.44 | 0.55 | 0.15 | 0.94 | 0.40 | 水與冰 | 環境極端 |
| AMADEE-18 field site Marmul area Dhofar (Oman) | 40.8 | 41.6 | 0.17 | 0.49 | 0.17 | 0.94 | 0.81 | 水與冰 | 地形 |
| Lonar crater (India) | 39.3 | 47.1 | 0.25 | 0.13 | 0.31 | 0.94 | 0.97 | 大氣與沙塵 | 地表物質與裸露 |
| Dallol geothermal area Afar (Ethiopia) | 38.1 | 51.3 | 0.15 | 0.75 | 0.09 | 0.94 | 0.84 | 水與冰 | 環境極端 |
| Ka'u Desert Kilauea (Hawaii) | 35.0 | 63.0 | 0.80 | 0.06 | 0.20 | 0.94 | 0.36 | 水與冰 | 地表物質與裸露 |
| Mauna Kea upper slopes palagonitic tephra (Hawaii) | 29.7 | 80.9 | 0.38 | 0.04 | 0.46 | 0.94 | 0.37 | 水與冰 | 地表物質與裸露 |

## Arcadia Planitia (shallow ground ice)（47.2, -175.7）

**各面向「分數 ≥ 0.9」的陸地比例**：地形 55.1%、地表物質與裸露 0.1%、環境極端 0.0%、水與冰 1.7%、大氣與沙塵 20.0%；整體 ≥ 90 分：0.00%

### 整體相似度前 10 名

| # | 地點 | 座標 | 整體 | 地形 | 地表物質與裸露 | 環境極端 | 水與冰 | 大氣與沙塵 | 最弱面向 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 138 km from Chernyshevskiy (RU) | 63.95, 110.65 | 81.7 | 0.98 | 0.57 | 0.67 | 0.99 | 0.98 | 地表物質與裸露 | 否（新候選） |
| 2 | 131 km from Jumla (NP) | 30.25, 82.95 | 80.9 | 1.00 | 0.50 | 0.73 | 0.98 | 0.98 | 地表物質與裸露 | 否（新候選） |
| 3 | 193 km from Yagodnoye (RU) | 64.25, 149.25 | 80.9 | 0.95 | 0.59 | 0.74 | 0.91 | 0.91 | 地表物質與裸露 | 否（新候選） |
| 4 | near Evensk (RU) | 62.05, 159.65 | 80.4 | 0.96 | 0.62 | 0.62 | 0.94 | 0.96 | 地表物質與裸露 | 否（新候選） |
| 5 | 195 km from Tura (RU) | 64.45, 104.25 | 80.3 | 1.00 | 0.52 | 0.66 | 1.00 | 0.97 | 地表物質與裸露 | 否（新候選） |
| 6 | 46 km from Urdgol (MN) | 48.25, 92.65 | 79.9 | 1.00 | 0.57 | 0.80 | 1.00 | 0.72 | 地表物質與裸露 | 否（新候選） |
| 7 | 208 km from Pevek (RU) | 67.85, 170.95 | 79.9 | 0.98 | 0.60 | 0.66 | 0.93 | 0.90 | 地表物質與裸露 | 否（新候選） |
| 8 | 48 km from Erzin (RU) | 49.85, 94.95 | 79.8 | 0.98 | 0.62 | 0.77 | 0.92 | 0.76 | 地表物質與裸露 | 否（新候選） |
| 9 | near Kosh-Agach (RU) | 49.95, 88.65 | 79.8 | 0.99 | 0.67 | 0.80 | 0.76 | 0.79 | 地表物質與裸露 | 否（新候選） |
| 10 | 410 km from Yerbogachen (RU) | 64.95, 107.25 | 79.1 | 0.96 | 0.55 | 0.66 | 0.94 | 0.96 | 地表物質與裸露 | 否（新候選） |

### 每個面向最像的前 5 名

- **地形**：131 km from Jumla (NP)（1.00，整體 81）；195 km from Tura (RU)（1.00，整體 80）；46 km from Urdgol (MN)（1.00，整體 80）；103 km from Colchani (BO)（1.00，整體 78）；55 km from Tsetserleg (MN)（1.00，整體 78）
- **地表物質與裸露**：68 km from Tupungato (AR)（0.99，整體 26）；46 km from Karakenja (TJ)（0.97，整體 32）；39 km from Pahalgam (IN)（0.96，整體 34）；77 km from Cochrane (CL)（0.95，整體 46）；117 km from Edd (ER)（0.95，整體 44）
- **環境極端**：1417 km from Gjoa Haven (CA)（0.90，整體 63）；120 km from Nur (CN)（0.90，整體 35）；106 km from Zangguy (CN)（0.89，整體 28）；127 km from Jisegumen (CN)（0.89，整體 27）；161 km from Rutog (CN)（0.88，整體 70）
- **水與冰**：134 km from Chernyshevskiy (RU)（1.00，整體 82）；140 km from Xagmakajor (CN)（1.00，整體 81）；195 km from Tura (RU)（1.00，整體 80）；46 km from Urdgol (MN)（1.00，整體 80）；623 km from Flin Flon (CA)（1.00，整體 78）
- **大氣與沙塵**：near Chernyshevskiy (RU)（1.00，整體 80）；142 km from Tura (RU)（1.00，整體 77）；211 km from Yerbogachen (RU)（1.00，整體 76）；168 km from Berdigestyakh (RU)（1.00，整體 74）；43 km from Arco (US)（0.99，整體 74）

### 每個變數最像的前 5 名（一張圖看：`board_arcadia.png`）

> 括號內：該變數的分數、地球的值、整體相似度。只有一個變數的面向（水與冰、大氣與沙塵）和上面的面向排名相同，不重複列。

- **坡度**（火星 0.21°）：131 km from Jumla (NP)（1.00，0.30°，整體 81）；195 km from Tura (RU)（1.00，0.31°，整體 80）；46 km from Urdgol (MN)（1.00，0.31°，整體 80）；103 km from Colchani (BO)（1.00，0.13°，整體 78）；55 km from Tsetserleg (MN)（1.00，0.42°，整體 78）
- **粗糙度**（火星 1.0 m）：131 km from Jumla (NP)（1.00，1.3 m，整體 81）；195 km from Tura (RU)（1.00，1.3 m，整體 80）；46 km from Urdgol (MN)（1.00，1.1 m，整體 80）；103 km from Colchani (BO)（1.00，0.7 m，整體 78）；83 km from Grantsville (US)（1.00，0.0 m，整體 78）
- **岩性**（火星 basalt）：138 km from Chernyshevskiy (RU)（1.00，vb，整體 82）；near Evensk (RU)（1.00，vb，整體 80）；195 km from Tura (RU)（1.00，vb，整體 80）；410 km from Yerbogachen (RU)（1.00，vb，整體 79）；280 km from Vanavara (RU)（1.00，vb，整體 79）
- **熱慣量**（火星 第 64 百分位）：37 km from Pico Truncado (AR)（1.00，第 64 百分位，整體 76）；231 km from Qimantage (CN)（1.00，第 64 百分位，整體 76）；100 km from San Julian (AR)（1.00，第 64 百分位，整體 73）；81 km from Gobernador Gregores (AR)（1.00，第 64 百分位，整體 73）；75 km from Wendover (US)（1.00，第 64 百分位，整體 72）
- **無植被**（火星 NDVI 0.00）：75 km from Colchani (BO)（1.00，NDVI -0.00，整體 78）；83 km from Grantsville (US)（1.00，NDVI -0.01，整體 78）；103 km from Luring (CN)（1.00，NDVI -0.03，整體 75）；1452 km from Gjoa Haven (CA)（1.00，NDVI -0.05，整體 72）；63 km from Milford (US)（1.00，NDVI -0.03，整體 72）
- **溫度**（火星 -75.9 °C）：526 km from Kugluktuk (CA)（0.99，-16.0 °C，整體 74）；1452 km from Gjoa Haven (CA)（1.00，-19.0 °C，整體 72）；995 km from Khatanga (RU)（1.00，-17.3 °C，整體 72）；1128 km from Rankin Inlet (CA)（1.00，-16.9 °C，整體 70）；707 km from Deputatsky (RU)（1.00，-17.6 °C，整體 68）
- **乾燥度**（火星 最乾）：near Paracas (PE)（0.99，乾燥指數 0.001，整體 61）；near San Juan de Marcona (PE)（1.00，乾燥指數 0.001，整體 61）；Atacama Desert Yungay core (Chile)（0.99，乾燥指數 0.001，整體 60）；365 km from Maradah (LY)（1.00，乾燥指數 0.001，整體 58）；87 km from Al Kharijah (EG)（1.00，乾燥指數 0.001，整體 58）

### 已知類比地的剖面（標給這個目標的）

| 類比地 | 整體 | 全球前 % | 地形 | 地表物質與裸露 | 環境極端 | 水與冰 | 大氣與沙塵 | 最強 | 最弱 |
|---|---|---|---|---|---|---|---|---|---|
| Pilot Valley paleolake playa (Utah) | 60.9 | 5.9 | 0.72 | 0.49 | 0.71 | 0.47 | 0.88 | 大氣與沙塵 | 水與冰 |
| Lanzarote volcanic fields (Spain) | 57.2 | 12.4 | 0.62 | 0.66 | 0.58 | 0.47 | 0.60 | 地表物質與裸露 | 水與冰 |
| Haughton impact crater Devon Island (Canada) | 50.0 | 25.0 | 0.57 | 0.31 | 0.48 | 0.53 | 0.74 | 大氣與沙塵 | 地表物質與裸露 |
| HI-SEAS habitat Mauna Loa (Hawaii) | 41.4 | 46.4 | 0.31 | 0.73 | 0.47 | 0.47 | 0.68 | 地表物質與裸露 | 地形 |
| Lost Hammer cold saline spring Axel Heiberg Island (Canada) | 24.0 | 86.2 | 0.01 | 0.30 | 0.69 | 0.53 | 0.72 | 大氣與沙塵 | 地形 |
| McMurdo Dry Valleys (Antarctica) | 22.9 | 87.6 | 0.01 | 0.20 | 1.00 | 0.53 | 0.59 | 環境極端 | 地形 |
| Beacon Valley ancient buried ice (Antarctica) | 22.9 | 87.6 | 0.01 | 0.20 | 1.00 | 0.53 | 0.59 | 環境極端 | 地形 |
| Mauna Kea upper slopes palagonitic tephra (Hawaii) | 19.8 | 90.7 | 0.02 | 0.09 | 0.46 | 0.47 | 0.69 | 大氣與沙塵 | 地形 |
| Bockfjorden Volcanic Complex Svalbard (Norway) | 18.5 | 92.0 | 0.01 | 0.32 | 0.14 | 0.53 | 0.73 | 大氣與沙塵 | 地形 |

## Oxia Planum (ExoMars Rosalind Franklin landing site)（18.2, -24.55）

> 岩性類別用文獻覆寫為 `sedimentary_carbonate_clay`（全球地質圖 1:20M 分不出這裡的礦物）：Literature override: SIM3292 maps lNh (highland, impact breccia) at 1:20M, but the rover target is the Fe/Mg clay-bearing layered unit; Quantin-Nataf et al. 2021, Astrobiology 21(3):345, doi:10.1089/ast.2019.2191

**各面向「分數 ≥ 0.9」的陸地比例**：地形 61.0%、地表物質與裸露 0.0%、環境極端 0.0%、水與冰 86.9%、大氣與沙塵 13.9%；整體 ≥ 90 分：0.00%

### 整體相似度前 10 名

| # | 地點 | 座標 | 整體 | 地形 | 地表物質與裸露 | 環境極端 | 水與冰 | 大氣與沙塵 | 最弱面向 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 92 km from Wutumeiren (CN) | 37.45, 93.95 | 88.9 | 0.98 | 0.81 | 0.83 | 1.00 | 0.84 | 地表物質與裸露 | 否（新候選） |
| 2 | 235 km from Qilanbulak (CN) | 40.45, 90.75 | 88.7 | 0.99 | 0.76 | 0.75 | 1.00 | 0.98 | 環境極端 | 否（新候選） |
| 3 | 47 km from Tieganlike (CN) | 39.45, 88.25 | 88.1 | 0.99 | 0.74 | 0.74 | 1.00 | 0.98 | 環境極端 | 否（新候選） |
| 4 | near Wuhai (CN) | 39.65, 106.75 | 87.6 | 1.00 | 0.83 | 0.72 | 1.00 | 0.87 | 環境極端 | 否（新候選） |
| 5 | 164 km from Beyneu (KZ) | 45.65, 57.25 | 87.3 | 0.98 | 0.87 | 0.72 | 1.00 | 0.83 | 環境極端 | 否（新候選） |
| 6 | 115 km from Qaraton (KZ) | 45.45, 53.95 | 86.9 | 0.99 | 0.80 | 0.71 | 1.00 | 0.89 | 環境極端 | 否（新候選） |
| 7 | near Gazojak (TM) | 41.15, 61.45 | 86.1 | 1.00 | 0.70 | 0.72 | 1.00 | 0.94 | 地表物質與裸露 | 否（新候選） |
| 8 | near Mynaral (KZ) | 45.45, 73.75 | 85.9 | 1.00 | 0.74 | 0.75 | 1.00 | 0.84 | 地表物質與裸露 | 否（新候選） |
| 9 | 146 km from Shumanay Shahri (UZ) | 41.65, 57.75 | 85.4 | 0.99 | 0.70 | 0.70 | 1.00 | 0.94 | 地表物質與裸露 | 否（新候選） |
| 10 | 52 km from Serdar (TM) | 38.85, 56.85 | 85.1 | 0.99 | 0.76 | 0.63 | 1.00 | 0.94 | 環境極端 | 否（新候選） |

### 每個面向最像的前 5 名

- **地形**：near Wuhai (CN)（1.00，整體 88）；near Gazojak (TM)（1.00，整體 86）；near Mynaral (KZ)（1.00，整體 86）；222 km from Serdar (TM)（1.00，整體 85）；138 km from Zhanaozen (KZ)（1.00，整體 85）
- **地表物質與裸露**：312 km from Fort McPherson (CA)（0.92，整體 12）；190 km from Prudhoe Bay (US)（0.92，整體 11）；212 km from Prudhoe Bay (US)（0.92，整體 11）；105 km from Kugluktuk (CA)（0.91，整體 28）；54 km from Gjoa Haven (CA)（0.91，整體 27）
- **環境極端**：1417 km from Gjoa Haven (CA)（0.90，整體 27）；120 km from Nur (CN)（0.90，整體 19）；95 km from Layka (CN)（0.89，整體 19）；107 km from Guma (CN)（0.89，整體 13）；127 km from Jisegumen (CN)（0.89，整體 12）
- **水與冰**：92 km from Wutumeiren (CN)（1.00，整體 89）；235 km from Qilanbulak (CN)（1.00，整體 89）；47 km from Tieganlike (CN)（1.00，整體 88）；near Wuhai (CN)（1.00，整體 88）；164 km from Beyneu (KZ)（1.00，整體 87）
- **大氣與沙塵**：near Dakhla (EH)（1.00，整體 83）；152 km from Nouadhibou (MR)（1.00，整體 83）；41 km from Kalpin (CN)（1.00，整體 82）；52 km from Yuli (CN)（1.00，整體 82）；176 km from Qilanbulak (CN)（1.00，整體 80）

### 每個變數最像的前 5 名（一張圖看：`board_oxia.png`）

> 括號內：該變數的分數、地球的值、整體相似度。只有一個變數的面向（水與冰、大氣與沙塵）和上面的面向排名相同，不重複列。

- **坡度**（火星 0.56°）：near Wuhai (CN)（1.00，0.35°，整體 88）；113 km from Qaraton (KZ)（1.00，0.30°，整體 87）；near Gazojak (TM)（1.00，0.35°，整體 86）；near Mynaral (KZ)（1.00，0.35°，整體 86）；52 km from Serdar (TM)（1.00，0.29°，整體 85）
- **粗糙度**（火星 2.8 m）：near Wuhai (CN)（1.00，1.8 m，整體 88）；near Gazojak (TM)（1.00，2.3 m，整體 86）；near Mynaral (KZ)（1.00，2.2 m，整體 86）；222 km from Serdar (TM)（1.00，1.8 m，整體 85）；138 km from Zhanaozen (KZ)（1.00，2.1 m，整體 85）
- **岩性**（火星 sedimentary_carbonate_clay）：164 km from Beyneu (KZ)（0.80，sm，整體 87）；115 km from Qaraton (KZ)（0.80，sm，整體 87）；near Gazojak (TM)（0.80，sm，整體 86）；near Mynaral (KZ)（0.80，sm，整體 86）；146 km from Shumanay Shahri (UZ)（0.80，sm，整體 85）
- **熱慣量**（火星 第 98 百分位）：36 km from Taiynsha (KZ)（1.00，第 98 百分位，整體 80）；61 km from Kupino (RU)（1.00，第 98 百分位，整體 79）；near Keti Bandar (PK)（0.99，第 99 百分位，整體 79）；61 km from Dayapar (IN)（1.00，第 98 百分位，整體 74）；near Shengli (CN)（1.00，第 98 百分位，整體 72）
- **無植被**（火星 NDVI 0.00）：92 km from Wutumeiren (CN)（1.00，NDVI -0.01，整體 89）；235 km from Qilanbulak (CN)（1.00，NDVI -0.04，整體 89）；47 km from Tieganlike (CN)（0.99，NDVI 0.00，整體 88）；164 km from Beyneu (KZ)（1.00，NDVI -0.01，整體 87）；40 km from Xitieshan (CN)（1.00，NDVI -0.02，整體 84）
- **溫度**（火星 -50.8 °C）：772 km from Clyde River (CA)（1.00，-19.0 °C，整體 58）；1303 km from Clyde River (CA)（1.00，-18.8 °C，整體 53）；281 km from Clyde River (CA)（1.00，-17.6 °C，整體 29）；627 km from Deputatsky (RU)（1.00，-17.7 °C，整體 28）；944 km from Kugluktuk (CA)（1.00，-19.1 °C，整體 28）
- **乾燥度**（火星 最乾）：52 km from Al Kharijah (EG)（1.00，乾燥指數 0.000，整體 77）；60 km from Al Qusiyah (EG)（0.99，乾燥指數 0.001，整體 76）；146 km from Qasr al Farafirah (EG)（0.99，乾燥指數 0.001，整體 74）；153 km from Al Kharijah (EG)（1.00，乾燥指數 0.000，整體 73）；32 km from Tahta (EG)（1.00，乾燥指數 0.000，整體 73）

### 已知類比地的剖面（沒有標給這個目標的；列出全部已知類比地中全球排名最前的 8 個，供參考）

| 類比地 | 整體 | 全球前 % | 地形 | 地表物質與裸露 | 環境極端 | 水與冰 | 大氣與沙塵 | 最強 | 最弱 |
|---|---|---|---|---|---|---|---|---|---|
| Lanzarote volcanic fields (Spain) | 69.3 | 6.2 | 0.70 | 0.52 | 0.58 | 1.00 | 0.85 | 水與冰 | 地表物質與裸露 |
| Dalangtan saline playa Qaidam Basin (China) | 67.7 | 7.4 | 0.99 | 0.21 | 0.80 | 1.00 | 0.87 | 水與冰 | 地表物質與裸露 |
| Pilot Valley paleolake playa (Utah) | 67.5 | 7.6 | 0.79 | 0.48 | 0.71 | 1.00 | 0.57 | 水與冰 | 地表物質與裸露 |
| Black Point Lava Flow (Arizona) | 66.3 | 8.6 | 0.98 | 0.41 | 0.65 | 1.00 | 0.51 | 水與冰 | 地表物質與裸露 |
| Mars Desert Research Station Hanksville (Utah) | 63.3 | 11.4 | 0.85 | 0.38 | 0.69 | 1.00 | 0.51 | 水與冰 | 地表物質與裸露 |
| Lavic Lake and Sunshine volcanic field Mojave Desert (California) | 60.7 | 14.6 | 0.68 | 0.44 | 0.52 | 1.00 | 0.59 | 水與冰 | 地表物質與裸露 |
| AMADEE-18 field site Marmul area Dhofar (Oman) | 57.9 | 19.1 | 1.00 | 0.37 | 0.17 | 1.00 | 0.96 | 水與冰 | 環境極端 |
| White Sands gypsum dunes and Lake Lucero (New Mexico) | 57.8 | 19.3 | 0.99 | 0.27 | 0.62 | 1.00 | 0.40 | 水與冰 | 地表物質與裸露 |

## Meridiani Planum (Opportunity landing site, Eagle crater)（-1.95, -5.53）

> 岩性類別用文獻覆寫為 `evaporite_sulfate_clastic`（全球地質圖 1:20M 分不出這裡的礦物）：Literature override: SIM3292 maps HNhu (highland undivided) at 1:20M, but Opportunity found sulfate-rich sandstones with hematite spherules; Squyres et al. 2004, Science 306:1709, doi:10.1126/science.1104559

**各面向「分數 ≥ 0.9」的陸地比例**：地形 68.6%、地表物質與裸露 0.0%、環境極端 0.0%、水與冰 87.3%、大氣與沙塵 20.0%；整體 ≥ 90 分：0.00%

### 整體相似度前 10 名

| # | 地點 | 座標 | 整體 | 地形 | 地表物質與裸露 | 環境極端 | 水與冰 | 大氣與沙塵 | 最弱面向 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 97 km from Mazongshan (CN) | 42.55, 97.65 | 89.9 | 0.99 | 0.84 | 0.75 | 0.97 | 0.98 | 環境極端 | 否（新候選） |
| 2 | 30 km from Jetaral (CN) | 47.15, 87.05 | 89.8 | 1.00 | 0.86 | 0.76 | 0.97 | 0.92 | 環境極端 | 否（新候選） |
| 3 | 81 km from Wentugaole (CN) | 42.15, 102.05 | 89.8 | 1.00 | 0.83 | 0.75 | 0.97 | 0.97 | 環境極端 | 否（新候選） |
| 4 | 37 km from Sharbulag (MN) | 49.15, 93.05 | 89.4 | 1.00 | 0.90 | 0.79 | 0.97 | 0.84 | 環境極端 | 否（新候選） |
| 5 | 61 km from Takeshiken (CN) | 45.65, 90.95 | 89.1 | 0.99 | 0.83 | 0.77 | 0.97 | 0.92 | 環境極端 | 否（新候選） |
| 6 | 52 km from Bayan-Ovoo (MN) | 44.85, 94.35 | 89.0 | 1.00 | 0.84 | 0.74 | 0.97 | 0.93 | 環境極端 | 否（新候選） |
| 7 | 100 km from Wutumeiren (CN) | 37.55, 93.95 | 89.0 | 0.94 | 0.77 | 0.82 | 0.97 | 0.97 | 地表物質與裸露 | 否（新候選） |
| 8 | near Balqash (KZ) | 46.95, 74.95 | 88.9 | 0.99 | 0.83 | 0.75 | 0.97 | 0.93 | 環境極端 | 否（新候選） |
| 9 | 157 km from Tahilt (MN) | 43.95, 96.35 | 88.5 | 1.00 | 0.77 | 0.76 | 0.97 | 0.96 | 環境極端 | 否（新候選） |
| 10 | 109 km from Yiwu (CN) | 42.65, 95.75 | 88.5 | 1.00 | 0.74 | 0.76 | 0.97 | 0.99 | 地表物質與裸露 | 否（新候選） |

### 每個面向最像的前 5 名

- **地形**：30 km from Jetaral (CN)（1.00，整體 90）；81 km from Wentugaole (CN)（1.00，整體 90）；93 km from Mazongshan (CN)（1.00，整體 90）；37 km from Sharbulag (MN)（1.00，整體 89）；52 km from Bayan-Ovoo (MN)（1.00，整體 89）
- **地表物質與裸露**：133 km from Cruz de Machacamarca (BO)（0.99，整體 60）；73 km from San Pedro de Atacama (CL)（0.93，整體 65）；near Zahedan (IR)（0.92，整體 57）；near Degache (TN)（0.91，整體 78）；58 km from Letlhakane (BW)（0.92，整體 59）
- **環境極端**：1417 km from Gjoa Haven (CA)（0.90，整體 38）；120 km from Nur (CN)（0.90，整體 30）；95 km from Layka (CN)（0.89，整體 20）；127 km from Jisegumen (CN)（0.89，整體 18）；104 km from Guma (CN)（0.89，整體 16）
- **水與冰**：near Ulaantolgoy (MN)（1.00，整體 86）；42 km from Bayanhoshuu (MN)（1.00，整體 86）；50 km from Tavin (MN)（1.00，整體 85）；39 km from Mugur-Aksy (RU)（0.99，整體 85）；52 km from Sharga (MN)（1.00，整體 85）
- **大氣與沙塵**：170 km from Mazongshan (CN)（1.00，整體 88）；102 km from Yiwu (CN)（1.00，整體 88）；90 km from Taushyq (KZ)（1.00，整體 88）；52 km from Mazongshan (CN)（1.00，整體 88）；near Liuyuan (CN)（1.00，整體 88）

### 每個變數最像的前 5 名（一張圖看：`board_meridiani.png`）

> 括號內：該變數的分數、地球的值、整體相似度。只有一個變數的面向（水與冰、大氣與沙塵）和上面的面向排名相同，不重複列。

- **坡度**（火星 1.28°）：102 km from Mazongshan (CN)（0.99，1.58°，整體 90）；30 km from Jetaral (CN)（1.00，1.17°，整體 90）；81 km from Wentugaole (CN)（1.00，1.24°，整體 90）；37 km from Sharbulag (MN)（1.00，1.23°，整體 89）；61 km from Takeshiken (CN)（1.00，1.53°，整體 89）
- **粗糙度**（火星 6.4 m）：30 km from Jetaral (CN)（1.00，5.7 m，整體 90）；81 km from Wentugaole (CN)（1.00，6.1 m，整體 90）；93 km from Mazongshan (CN)（1.00，5.9 m，整體 90）；37 km from Sharbulag (MN)（1.00，6.7 m，整體 89）；52 km from Bayan-Ovoo (MN)（1.00，6.2 m，整體 89）
- **岩性**（火星 evaporite_sulfate_clastic）：near Shahreza (IR)（1.00，ev，整體 87）；112 km from Mersa Matruh (EG)（1.00，ev，整體 86）；near Kuhbanan (IR)（1.00，ev，整體 85）；58 km from Djebilet Rosfa (DZ)（1.00，ev，整體 85）；69 km from Hajjiabad (IR)（1.00，ev，整體 84）
- **熱慣量**（火星 第 42 百分位）：near Sa'erhusong (CN)（1.00，第 43 百分位，整體 90）；36 km from Balqash (KZ)（1.00，第 43 百分位，整體 88）；64 km from Sekseuil (KZ)（1.00，第 42 百分位，整體 88）；77 km from Yiwu (CN)（1.00，第 42 百分位，整體 88）；38 km from Dagur (CN)（1.00，第 43 百分位，整體 87）
- **無植被**（火星 NDVI 0.00）：40 km from Xitieshan (CN)（1.00，NDVI -0.02，整體 88）；92 km from Wutumeiren (CN)（1.00，NDVI -0.01，整體 86）；178 km from Torghay (KZ)（0.99，NDVI 0.00，整體 85）；156 km from Beyneu (KZ)（1.00，NDVI -0.01，整體 85）；235 km from Qilanbulak (CN)（1.00，NDVI -0.04，整體 83）
- **溫度**（火星 -46.1 °C）：772 km from Clyde River (CA)（1.00，-19.0 °C，整體 64）；1303 km from Clyde River (CA)（1.00，-18.8 °C，整體 60）；594 km from Kugluktuk (CA)（1.00，-16.3 °C，整體 40）；1417 km from Gjoa Haven (CA)（1.00，-19.6 °C，整體 38）；748 km from Kugluktuk (CA)（0.99，-16.1 °C，整體 38）
- **乾燥度**（火星 最乾）：83 km from Al Kharijah (EG)（1.00，乾燥指數 0.001，整體 80）；79 km from Farshut (EG)（1.00，乾燥指數 0.000，整體 78）；232 km from Qasr al Farafirah (EG)（1.00，乾燥指數 0.001，整體 77）；88 km from Al Minya (EG)（0.99，乾燥指數 0.001，整體 77）；76 km from Qasr al Farafirah (EG)（1.00，乾燥指數 0.001，整體 77）

### 已知類比地的剖面（沒有標給這個目標的；列出全部已知類比地中全球排名最前的 8 個，供參考）

| 類比地 | 整體 | 全球前 % | 地形 | 地表物質與裸露 | 環境極端 | 水與冰 | 大氣與沙塵 | 最強 | 最弱 |
|---|---|---|---|---|---|---|---|---|---|
| Dalangtan saline playa Qaidam Basin (China) | 85.5 | 0.3 | 0.95 | 0.62 | 0.80 | 0.97 | 0.99 | 大氣與沙塵 | 地表物質與裸露 |
| Lanzarote volcanic fields (Spain) | 78.1 | 4.5 | 0.84 | 0.69 | 0.58 | 0.97 | 0.99 | 大氣與沙塵 | 環境極端 |
| Pilot Valley paleolake playa (Utah) | 76.6 | 5.6 | 0.87 | 0.65 | 0.71 | 0.97 | 0.71 | 水與冰 | 地表物質與裸露 |
| Mars Desert Research Station Hanksville (Utah) | 74.9 | 6.9 | 0.95 | 0.63 | 0.69 | 0.97 | 0.65 | 水與冰 | 地表物質與裸露 |
| Black Point Lava Flow (Arizona) | 74.6 | 7.1 | 0.99 | 0.58 | 0.65 | 0.97 | 0.65 | 地形 | 地表物質與裸露 |
| White Sands gypsum dunes and Lake Lucero (New Mexico) | 70.6 | 10.6 | 0.93 | 0.57 | 0.62 | 0.97 | 0.54 | 水與冰 | 大氣與沙塵 |
| Lavic Lake and Sunshine volcanic field Mojave Desert (California) | 70.5 | 10.7 | 0.83 | 0.64 | 0.52 | 0.97 | 0.73 | 水與冰 | 環境極端 |
| AMADEE-18 field site Marmul area Dhofar (Oman) | 62.0 | 18.1 | 0.94 | 0.63 | 0.17 | 0.97 | 0.91 | 水與冰 | 環境極端 |

## Protonilus Mensae (candidate human exploration zone, buried glacial ice)（41.905, 48.548）

**各面向「分數 ≥ 0.9」的陸地比例**：地形 8.2%、地表物質與裸露 0.1%、環境極端 0.0%、水與冰 2.2%、大氣與沙塵 20.0%；整體 ≥ 90 分：0.00%

### 整體相似度前 10 名

| # | 地點 | 座標 | 整體 | 地形 | 地表物質與裸露 | 環境極端 | 水與冰 | 大氣與沙塵 | 最弱面向 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 93 km from Maindong (CN) | 30.95, 84.55 | 86.6 | 0.94 | 0.72 | 0.78 | 0.96 | 0.96 | 地表物質與裸露 | 否（新候選） |
| 2 | 81 km from Zhabu (CN) | 32.45, 82.95 | 86.3 | 0.94 | 0.78 | 0.80 | 1.00 | 0.82 | 地表物質與裸露 | 否（新候選） |
| 3 | 80 km from Jiajuedibu (CN) | 31.35, 87.95 | 85.8 | 0.96 | 0.72 | 0.73 | 0.98 | 0.94 | 地表物質與裸露 | 否（新候選） |
| 4 | near Zangkaxa (CN) | 33.75, 80.65 | 85.6 | 0.97 | 0.72 | 0.83 | 0.98 | 0.80 | 地表物質與裸露 | 否（新候選） |
| 5 | near Rawlins (US) | 41.65, -107.35 | 85.3 | 0.99 | 0.75 | 0.72 | 0.84 | 1.00 | 環境極端 | 否（新候選） |
| 6 | 64 km from Las Heras (AR) | -32.35, -69.15 | 84.8 | 0.99 | 0.82 | 0.71 | 0.84 | 0.91 | 環境極端 | 否（新候選） |
| 7 | near Green River (US) | 41.65, -109.45 | 84.5 | 0.99 | 0.73 | 0.74 | 0.84 | 0.96 | 地表物質與裸露 | 否（新候選） |
| 8 | 148 km from Maindong (CN) | 32.25, 86.55 | 84.4 | 0.97 | 0.71 | 0.78 | 0.94 | 0.83 | 地表物質與裸露 | 否（新候選） |
| 9 | Mars Desert Research Station Hanksville (Utah) | 38.25, -111.15 | 84.3 | 0.98 | 0.78 | 0.70 | 0.84 | 0.94 | 環境極端 | 是 |
| 10 | near Delta (US) | 38.75, -108.25 | 84.2 | 0.99 | 0.75 | 0.68 | 0.84 | 0.99 | 環境極端 | 否（新候選） |

### 每個面向最像的前 5 名

- **地形**：79 km from Xagmakajor (CN)（1.00，整體 86）；30 km from Rock Springs (US)（1.00，整體 85）；53 km from Zhabu (CN)（0.99，整體 84）；near Delta (US)（0.99，整體 84）；81 km from Bar Nunn (US)（1.00，整體 84）
- **地表物質與裸露**：70 km from Gakuch (PK)（0.96，整體 29）；44 km from Zongga (CN)（0.96，整體 27）；57 km from Thang (IN)（0.95，整體 26）；near Lobujya (NP)（0.96，整體 26）；137 km from Layka (CN)（0.96，整體 24）
- **環境極端**：120 km from Nur (CN)（0.90，整體 55）；1417 km from Gjoa Haven (CA)（0.90，整體 55）；127 km from Jisegumen (CN)（0.89，整體 24）；106 km from Zangguy (CN)（0.89，整體 23）；111 km from Yeyik (CN)（0.88，整體 58）
- **水與冰**：81 km from Zhabu (CN)（1.00，整體 86）；144 km from Maindong (CN)（1.00，整體 84）；near Hohtolgoy (MN)（1.00，整體 84）；55 km from Maindong (CN)（1.00，整體 83）；near Dzuyl (MN)（1.00，整體 83）
- **大氣與沙塵**：near Rawlins (US)（1.00，整體 85）；32 km from Jiajuedibu (CN)（1.00，整體 83）；near Waterflow (US)（1.00，整體 82）；near Qinglung (CN)（1.00，整體 81）；36 km from Mammoth Lakes (US)（1.00，整體 81）

### 每個變數最像的前 5 名（一張圖看：`board_protonilus.png`）

> 括號內：該變數的分數、地球的值、整體相似度。只有一個變數的面向（水與冰、大氣與沙塵）和上面的面向排名相同，不重複列。

- **坡度**（火星 4.59°）：91 km from Maindong (CN)（1.00，4.68°，整體 86）；79 km from Xagmakajor (CN)（1.00，4.43°，整體 86）；near Rawlins (US)（1.00，4.32°，整體 85）；near Lumaka (CN)（1.00，4.31°，整體 85）；43 km from Zhabu (CN)（1.00，4.56°，整體 85）
- **粗糙度**（火星 22.6 m）：93 km from Maindong (CN)（1.00，21.5 m，整體 87）；80 km from Jiajuedibu (CN)（1.00，21.8 m，整體 86）；near Zangkaxa (CN)（1.00，21.5 m，整體 86）；67 km from Zhabu (CN)（1.00，23.8 m，整體 85）；near Rock Springs (US)（1.00，21.7 m，整體 85）
- **岩性**（火星 clastic）：93 km from Maindong (CN)（0.90，ss，整體 87）；80 km from Jiajuedibu (CN)（0.90，ss，整體 86）；near Rawlins (US)（0.90，ss，整體 85）；67 km from Zhabu (CN)（0.90，ss，整體 85）；64 km from Las Heras (AR)（0.90，ss，整體 85）
- **熱慣量**（火星 第 46 百分位）：near Lovell (US)（1.00，第 46 百分位，整體 84）；near Dillon (US)（1.00，第 46 百分位，整體 82）；near Rodeo (AR)（1.00，第 46 百分位，整體 82）；43 km from Ferron (US)（1.00，第 45 百分位，整體 82）；near Sierra Blanca (US)（1.00，第 46 百分位，整體 81）
- **無植被**（火星 NDVI 0.00）：233 km from Dillingham (US)（1.00，NDVI -0.03，整體 80）；1303 km from Clyde River (CA)（1.00，NDVI -0.06，整體 80）；704 km from Clyde River (CA)（1.00，NDVI -0.08，整體 74）；1396 km from Nar'yan-Mar (RU)（1.00，NDVI -0.08，整體 74）；69 km from Valdez (US)（1.00，NDVI -0.01，整體 70）
- **溫度**（火星 -71.2 °C）：1303 km from Clyde River (CA)（1.00，-18.8 °C，整體 80）；772 km from Clyde River (CA)（1.00，-19.0 °C，整體 73）；1407 km from Gjoa Haven (CA)（1.00，-18.5 °C，整體 63）；931 km from Kugluktuk (CA)（1.00，-17.7 °C，整體 62）；1059 km from Upernavik (GL)（1.00，-18.1 °C，整體 62）
- **乾燥度**（火星 最乾）：near Antofagasta (CL)（1.00，乾燥指數 0.001，整體 81）；73 km from Tocopilla (CL)（1.00，乾燥指數 0.000，整體 80）；41 km from Santiago (PE)（0.99，乾燥指數 0.001，整體 80）；31 km from Iquique (CL)（1.00，乾燥指數 0.001，整體 73）；near El Algarrobal (PE)（1.00，乾燥指數 0.001，整體 71）

### 已知類比地的剖面（沒有標給這個目標的；列出全部已知類比地中全球排名最前的 8 個，供參考）

| 類比地 | 整體 | 全球前 % | 地形 | 地表物質與裸露 | 環境極端 | 水與冰 | 大氣與沙塵 | 最強 | 最弱 |
|---|---|---|---|---|---|---|---|---|---|
| Navajo Sandstone hematite concretions southern Utah | 75.4 | 0.4 | 0.77 | 0.66 | 0.69 | 0.84 | 0.93 | 大氣與沙塵 | 地表物質與裸露 |
| Mars Desert Research Station Hanksville (Utah) | 74.7 | 0.5 | 0.66 | 0.69 | 0.69 | 0.84 | 0.89 | 大氣與沙塵 | 地形 |
| Pilot Valley paleolake playa (Utah) | 71.8 | 1.0 | 0.71 | 0.72 | 0.71 | 0.84 | 0.83 | 水與冰 | 地形 |
| Lavic Lake and Sunshine volcanic field Mojave Desert (California) | 71.8 | 1.0 | 0.81 | 0.71 | 0.52 | 0.84 | 0.81 | 水與冰 | 環境極端 |
| Lanzarote volcanic fields (Spain) | 67.2 | 2.5 | 0.80 | 0.70 | 0.58 | 0.84 | 0.55 | 水與冰 | 大氣與沙塵 |
| Black Point Lava Flow (Arizona) | 66.4 | 2.9 | 0.45 | 0.70 | 0.65 | 0.84 | 0.89 | 大氣與沙塵 | 地形 |
| Atacama Desert Yungay core (Chile) | 63.6 | 4.5 | 0.77 | 0.65 | 0.48 | 0.84 | 0.74 | 水與冰 | 環境極端 |
| HI-SEAS habitat Mauna Loa (Hawaii) | 62.9 | 5.0 | 0.79 | 0.48 | 0.47 | 0.84 | 0.74 | 水與冰 | 環境極端 |

## Arcadia Planitia AP-105 (SkyFall design reference landing site)（43.3295, -161.4772）

**各面向「分數 ≥ 0.9」的陸地比例**：地形 55.0%、地表物質與裸露 0.1%、環境極端 0.0%、水與冰 1.7%、大氣與沙塵 20.0%；整體 ≥ 90 分：0.00%

### 整體相似度前 10 名

| # | 地點 | 座標 | 整體 | 地形 | 地表物質與裸露 | 環境極端 | 水與冰 | 大氣與沙塵 | 最弱面向 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | near Kosh-Agach (RU) | 49.95, 88.65 | 86.1 | 0.99 | 0.75 | 0.80 | 0.82 | 0.97 | 地表物質與裸露 | 否（新候選） |
| 2 | 46 km from Erzin (RU) | 49.85, 95.15 | 85.4 | 0.91 | 0.70 | 0.76 | 0.99 | 0.95 | 地表物質與裸露 | 否（新候選） |
| 3 | 49 km from Zhabu (CN) | 33.45, 82.95 | 84.1 | 0.97 | 0.54 | 0.83 | 0.98 | 0.98 | 地表物質與裸露 | 否（新候選） |
| 4 | 57 km from Urdgol (MN) | 48.35, 92.65 | 83.7 | 0.95 | 0.84 | 0.78 | 0.73 | 0.90 | 水與冰 | 否（新候選） |
| 5 | 62 km from Hoshoot (MN) | 48.55, 88.55 | 82.7 | 0.90 | 0.58 | 0.79 | 0.98 | 0.96 | 地表物質與裸露 | 否（新候選） |
| 6 | near Qimantage (CN) | 37.35, 90.05 | 82.6 | 1.00 | 0.64 | 0.81 | 0.93 | 0.81 | 地表物質與裸露 | 否（新候選） |
| 7 | 202 km from Zhabu (CN) | 34.55, 84.65 | 81.8 | 0.97 | 0.83 | 0.86 | 0.58 | 0.91 | 水與冰 | 否（新候選） |
| 8 | near Jisegumen (CN) | 33.95, 80.85 | 81.6 | 0.97 | 0.57 | 0.86 | 0.78 | 0.97 | 地表物質與裸露 | 否（新候選） |
| 9 | 252 km from Qimantage (CN) | 35.05, 90.65 | 81.5 | 0.98 | 0.87 | 0.77 | 0.58 | 0.93 | 水與冰 | 否（新候選） |
| 10 | 121 km from Murghob (TJ) | 39.15, 73.35 | 81.2 | 0.96 | 0.75 | 0.75 | 0.76 | 0.86 | 地表物質與裸露 | 否（新候選） |

### 每個面向最像的前 5 名

- **地形**：near Qimantage (CN)（1.00，整體 83）；near Kosh-Agach (RU)（1.00，整體 82）；55 km from Tsetserleg (MN)（1.00，整體 82）；near Telmin Suma (MN)（1.00，整體 81）；114 km from Zhabu (CN)（1.00，整體 81）
- **地表物質與裸露**：73 km from Edd (ER)（0.96，整體 48）；87 km from Colbun (CL)（0.96，整體 39）；105 km from Gul'cha (KG)（0.95，整體 32）；58 km from La Consulta (AR)（0.95，整體 24）；52 km from Salamanca (CL)（0.95，整體 23）
- **環境極端**：1417 km from Gjoa Haven (CA)（0.90，整體 61）；120 km from Nur (CN)（0.90，整體 39）；106 km from Zangguy (CN)（0.89，整體 30）；127 km from Jisegumen (CN)（0.89，整體 29）；161 km from Rutog (CN)（0.88，整體 77）
- **水與冰**：30 km from Qimantage (CN)（1.00，整體 80）；56 km from Qiangma (CN)（1.00，整體 78）；51 km from Jargalant (MN)（1.00，整體 76）；near Altan (MN)（1.00，整體 76）；75 km from Gangsha (CN)（1.00，整體 76）
- **大氣與沙塵**：90 km from Luring (CN)（1.00，整體 75）；31 km from Vlaa Vula (MN)（1.00，整體 73）；77 km from Kyzyl-Khaya (RU)（1.00，整體 71）；113 km from Zhabu (CN)（1.00，整體 70）；72 km from Cuozheqiangma (CN)（1.00，整體 70）

### 每個變數最像的前 5 名（一張圖看：`board_ap105.png`）

> 括號內：該變數的分數、地球的值、整體相似度。只有一個變數的面向（水與冰、大氣與沙塵）和上面的面向排名相同，不重複列。

- **坡度**（火星 0.21°）：near Qimantage (CN)（1.00，0.25°，整體 83）；near Kosh-Agach (RU)（1.00，0.38°，整體 82）；55 km from Tsetserleg (MN)（1.00，0.42°，整體 82）；near Telmin Suma (MN)（1.00，0.31°，整體 81）；114 km from Zhabu (CN)（1.00，0.46°，整體 81）
- **粗糙度**（火星 1.0 m）：near Qimantage (CN)（1.00，1.1 m，整體 83）；near Kosh-Agach (RU)（1.00，1.3 m，整體 82）；near Telmin Suma (MN)（1.00，1.1 m，整體 81）；114 km from Zhabu (CN)（1.00，2.1 m，整體 81）；175 km from Qimantage (CN)（0.99，2.2 m，整體 80）
- **岩性**（火星 basalt）：202 km from Zhabu (CN)（1.00，vb，整體 82）；167 km from Koramlik (CN)（1.00，vb，整體 81）；194 km from Qimantage (CN)（1.00，vb，整體 81）；81 km from Gangsha (CN)（1.00，vb，整體 78）；near Ovoot (MN)（1.00，vb，整體 77）
- **熱慣量**（火星 第 39 百分位）：62 km from Hoshoot (MN)（1.00，第 39 百分位，整體 83）；near Kosh-Agach (RU)（1.00，第 39 百分位，整體 82）；49 km from Urdgol (MN)（1.00，第 39 百分位，整體 77）；47 km from Ke'erlun (CN)（0.99，第 38 百分位，整體 74）；170 km from Khorixas (NA)（1.00，第 39 百分位，整體 74）
- **無植被**（火星 NDVI 0.00）：160 km from Yeyik (CN)（1.00，NDVI -0.01，整體 77）；120 km from Jisegumen (CN)（1.00，NDVI -0.01，整體 75）；83 km from Grantsville (US)（1.00，NDVI -0.01，整體 74）；75 km from Colchani (BO)（1.00，NDVI -0.00，整體 73）；103 km from Luring (CN)（1.00，NDVI -0.03，整體 71）
- **溫度**（火星 -72.7 °C）：526 km from Kugluktuk (CA)（0.99，-16.0 °C，整體 72）；1452 km from Gjoa Haven (CA)（1.00，-19.0 °C，整體 70）；995 km from Khatanga (RU)（1.00，-17.3 °C，整體 70）；1128 km from Rankin Inlet (CA)（1.00，-16.9 °C，整體 68）；707 km from Deputatsky (RU)（1.00，-17.6 °C，整體 66）
- **乾燥度**（火星 最乾）：near Paracas (PE)（0.99，乾燥指數 0.001，整體 63）；365 km from Maradah (LY)（1.00，乾燥指數 0.001，整體 62）；87 km from Al Kharijah (EG)（1.00，乾燥指數 0.001，整體 62）；342 km from Aozou (TD)（0.99，乾燥指數 0.001，整體 61）；126 km from Qasr al Farafirah (EG)（1.00，乾燥指數 0.001，整體 61）

### 已知類比地的剖面（沒有標給這個目標的；列出全部已知類比地中全球排名最前的 8 個，供參考）

| 類比地 | 整體 | 全球前 % | 地形 | 地表物質與裸露 | 環境極端 | 水與冰 | 大氣與沙塵 | 最強 | 最弱 |
|---|---|---|---|---|---|---|---|---|---|
| Dalangtan saline playa Qaidam Basin (China) | 65.3 | 1.7 | 0.99 | 0.53 | 0.80 | 0.42 | 0.76 | 地形 | 水與冰 |
| White Sands gypsum dunes and Lake Lucero (New Mexico) | 62.7 | 3.9 | 1.00 | 0.49 | 0.62 | 0.42 | 0.77 | 地形 | 水與冰 |
| Mars Desert Research Station Hanksville (Utah) | 62.5 | 4.2 | 0.78 | 0.51 | 0.69 | 0.42 | 0.88 | 大氣與沙塵 | 水與冰 |
| Black Point Lava Flow (Arizona) | 62.2 | 4.6 | 0.94 | 0.44 | 0.65 | 0.42 | 0.88 | 地形 | 水與冰 |
| Pilot Valley paleolake playa (Utah) | 61.5 | 5.5 | 0.72 | 0.56 | 0.71 | 0.42 | 0.94 | 大氣與沙塵 | 水與冰 |
| Lanzarote volcanic fields (Spain) | 58.2 | 10.5 | 0.62 | 0.67 | 0.58 | 0.42 | 0.78 | 大氣與沙塵 | 水與冰 |
| Lavic Lake and Sunshine volcanic field Mojave Desert (California) | 58.2 | 10.6 | 0.60 | 0.55 | 0.52 | 0.42 | 0.96 | 大氣與沙塵 | 水與冰 |
| Atacama Desert Yungay core (Chile) | 48.7 | 27.7 | 0.58 | 0.50 | 0.48 | 0.42 | 0.50 | 地形 | 水與冰 |
