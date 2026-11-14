# 測試項目分數（自動產生）

> 產生時間 2026-11-14 23:54，由 `scripts/make_mission_tests.py` 產生；數字以 `outputs/mission_tests/*_tests.json` 為準。
> 測試 R1–R6 的定義來自整合者的規劃（`nasa/docs/火星.pdf`），特徵、門檻、資料寫在 `config/mission_tests.yaml`。
> 測試分數 = 測試內特徵的等權重幾何平均（下限 0.01）。必要特徵缺資料的格子不評分；可選特徵有資料才納入。前 20 名彼此至少相距 150 km；已知類比地 = 50 km 內。

## 面向 × 測試交叉表

● = 主要組成，○ = 相關但目前沒資料。

| 測試 | 地形 | 地表物質與裸露 | 環境極端 | 水與冰 | 大氣與沙塵 | 生物與棲息性 | 洞穴與地下 |
|---|---|---|---|---|---|---|---|
| R1 著陸地表條件 | ● | ● |  |  |  |  |  |
| R2 視覺導航可行性 | ○ | ○ |  |  |  |  |  |
| R3 淺層地下冰 |  |  | ● | ● |  |  | ○ |
| R4 含水礦物辨識 |  | ● |  |  |  |  |  |
| R5 冰河與冰緣地形 | ● |  | ○ | ● |  |  |  |
| R6 沙塵與近地表氣象 |  |  | ● |  | ● |  |  |

生物面向沒有對應到任何測試；R2 沒有任何面向能算。

## Jezero Crater（18.4, 77.5）

測試狀態：R1 已評分；R2 無法評估；R3 不適用（目標沒有可靠的冰訊號）；R4 已評分；R5 不適用（目標沒有可靠的冰訊號）；R6 已評分。冰訊號 clip(Ci, 0, 1) = 0.0（R3、R5 需要 ≥ 0.1）。

### R1 著陸地表條件

可評分陸地格 790,599；分數 ≥ 0.8 的陸地面積 6.0%、≥ 0.9 的 1.8%。

| # | 地點 | 座標 | 分數 | slope | roughness | thermal_inertia | barrenness | summer_barren | ice_free | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 113 km from Mori (CN) | 43.55, 91.55 | 0.985 | 1.00 | 1.00 | 1.00 | 0.91 | 1.00 | 1.00 | barrenness | 否（qaidam_dalangtan 581 km） |
| 2 | near Toksun (CN) | 42.95, 88.35 | 0.985 | 1.00 | 0.99 | 1.00 | 0.93 | 1.00 | 1.00 | barrenness | 否（qaidam_dalangtan 585 km） |
| 3 | 57 km from Yiwu (CN) | 43.75, 94.55 | 0.983 | 1.00 | 0.98 | 1.00 | 0.92 | 1.00 | 1.00 | barrenness | 否（qaidam_dalangtan 649 km） |
| 4 | 140 km from Barkol (CN) | 44.85, 93.25 | 0.983 | 1.00 | 0.99 | 1.00 | 0.92 | 1.00 | 1.00 | barrenness | 否（qaidam_dalangtan 737 km） |
| 5 | 165 km from Bulgan (MN) | 43.45, 97.75 | 0.982 | 1.00 | 0.99 | 1.00 | 0.91 | 1.00 | 1.00 | barrenness | 否（qaidam_dalangtan 765 km） |
| 6 | 34 km from Yuli (CN) | 41.55, 86.55 | 0.979 | 1.00 | 1.00 | 1.00 | 0.88 | 1.00 | 1.00 | barrenness | 否（qaidam_dalangtan 564 km） |
| 7 | 138 km from Qimantage (CN) | 36.25, 91.15 | 0.979 | 1.00 | 0.99 | 1.00 | 0.89 | 1.00 | 1.00 | barrenness | 否（qaidam_dalangtan 236 km） |
| 8 | 317 km from Clyde River (CA) | 70.25, -77.05 | 0.979 | 1.00 | 1.00 | 1.00 | 0.96 | 0.92 | 1.00 | summer_barren | 否（haughton_crater 702 km） |
| 9 | 111 km from Khur (IR) | 32.95, 55.75 | 0.978 | 1.00 | 0.98 | 1.00 | 0.89 | 1.00 | 1.00 | barrenness | 否（dhofar_amadee18 1649 km） |
| 10 | near Zouerat (MR) | 22.65, -12.65 | 0.978 | 1.00 | 1.00 | 1.00 | 0.88 | 1.00 | 1.00 | barrenness | 否（lanzarote 716 km） |

交叉驗證（用面向 地形、地表物質與裸露 組成）：前 20 名在 100 km 內重疊 5%，全部格子的等級相關 0.826。

### R4 含水礦物辨識

可評分陸地格 1,399,027；分數 ≥ 0.8 的陸地面積 0.1%、≥ 0.9 的 0.0%。

| # | 地點 | 座標 | 分數 | lithology | barrenness | summer_barren | ice_free | mineral_signature | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 548 km from Gjoa Haven (CA) | 73.55, -95.35 | 0.956 | 0.80 | 1.00 | 1.00 | 1.00 | 1.00 | lithology | 否（haughton_crater 264 km） |
| 2 | 765 km from Gjoa Haven (CA) | 74.55, -84.65 | 0.955 | 0.80 | 0.99 | 1.00 | 1.00 | 1.00 | lithology | 否（haughton_crater 172 km） |
| 3 | 1027 km from Kugluktuk (CA) | 77.05, -116.65 | 0.95 | 0.80 | 0.96 | 1.00 | 1.00 | 1.00 | lithology | 否（axel_heiberg_lost_hammer 642 km） |
| 4 | 828 km from Clyde River (CA) | 76.85, -82.55 | 0.943 | 0.80 | 0.99 | 0.95 | 1.00 | 1.00 | lithology | 否（haughton_crater 251 km） |
| 5 | 159 km from Gjoa Haven (CA) | 69.85, -97.95 | 0.941 | 0.80 | 0.97 | 0.96 | 1.00 | 0.99 | lithology | 否（haughton_crater 672 km） |
| 6 | 498 km from Clyde River (CA) | 72.45, -81.25 | 0.941 | 0.90 | 1.00 | 0.92 | 1.00 | 0.90 | mineral_signature | 否（haughton_crater 416 km） |
| 7 | 534 km from Kugluktuk (CA) | 72.35, -110.35 | 0.937 | 0.80 | 0.98 | 0.92 | 1.00 | 1.00 | lithology | 否（haughton_crater 717 km） |
| 8 | 542 km from Iskateley (RU) | 72.55, 53.95 | 0.936 | 0.90 | 0.99 | 0.81 | 1.00 | 1.00 | summer_barren | 否（svalbard_bockfjorden 1291 km） |
| 9 | 268 km from Okhotsk (RU) | 61.75, 142.55 | 0.936 | 0.90 | 0.94 | 0.85 | 1.00 | 1.00 | summer_barren | 否（svalbard_bockfjorden 3981 km） |
| 10 | 909 km from Gjoa Haven (CA) | 76.55, -88.95 | 0.93 | 0.90 | 0.99 | 0.95 | 0.98 | 0.83 | mineral_signature | 否（haughton_crater 132 km） |

交叉驗證（用面向 地表物質與裸露 組成）：前 20 名在 100 km 內重疊 0%，全部格子的等級相關 0.762。

### R6 沙塵與近地表氣象

可評分陸地格 1,314,474；分數 ≥ 0.8 的陸地面積 0.0%、≥ 0.9 的 0.0%。

| # | 地點 | 座標 | 分數 | dust | temperature | diurnal_range | dust_season_shape | dust_season_amplitude | temperature_season_shape | temperature_season_amplitude | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | near Vilaflor (ES) | 28.25, -16.65 | 0.773 | 0.91 | 0.57 | 0.94 | 0.38 | 0.91 | 0.98 | 1.00 | dust_season_shape | 否（lanzarote 307 km） |
| 2 | near Zuogaiduoma (CN) | 35.15, 103.25 | 0.757 | 0.88 | 0.78 | 0.83 | 0.28 | 0.98 | 0.97 | 0.93 | dust_season_shape | 否（qaidam_dalangtan 1090 km） |
| 3 | near Lujing Zhen (CN) | 34.35, 104.65 | 0.746 | 0.86 | 0.72 | 0.74 | 0.33 | 0.95 | 0.97 | 0.92 | dust_season_shape | 否（qaidam_dalangtan 1243 km） |
| 4 | near Nyinma (CN) | 34.05, 102.15 | 0.745 | 0.79 | 0.75 | 0.93 | 0.25 | 0.98 | 0.97 | 0.99 | dust_season_shape | 否（qaidam_dalangtan 1053 km） |
| 5 | 36 km from Qiakeri (CN) | 35.35, 101.35 | 0.735 | 0.82 | 0.77 | 0.95 | 0.22 | 0.97 | 0.97 | 0.92 | dust_season_shape | 否（qaidam_dalangtan 922 km） |
| 6 | 56 km from Jin'an (CN) | 33.05, 103.25 | 0.732 | 0.77 | 0.76 | 0.78 | 0.26 | 0.98 | 0.97 | 0.98 | dust_season_shape | 否（qaidam_dalangtan 1198 km） |
| 7 | near Huazangsi (CN) | 37.15, 103.05 | 0.729 | 0.93 | 0.74 | 0.91 | 0.25 | 0.89 | 0.97 | 0.81 | dust_season_shape | 否（qaidam_dalangtan 1009 km） |
| 8 | near Shirong (CN) | 29.15, 102.65 | 0.728 | 0.79 | 0.68 | 0.60 | 0.36 | 1.00 | 0.94 | 0.98 | dust_season_shape | 否（qaidam_dalangtan 1438 km） |
| 9 | near Gyangqai (CN) | 34.25, 100.35 | 0.727 | 0.78 | 0.80 | 0.90 | 0.22 | 0.93 | 0.98 | 0.95 | dust_season_shape | 否（qaidam_dalangtan 900 km） |
| 10 | near As Suwayda' (SY) | 32.65, 36.55 | 0.726 | 0.89 | 0.45 | 0.92 | 0.36 | 1.00 | 0.98 | 0.81 | dust_season_shape | 否（lake_salda 829 km） |

交叉驗證（用面向 大氣與沙塵、環境極端 組成）：前 20 名在 100 km 內重疊 0%，全部格子的等級相關 0.659。

### 每項測試第 1 名的面向分數（面向 × 測試）

| 測試 | 第 1 名 | 測試分數 | 地形 | 地表物質與裸露 | 環境極端 | 水與冰 | 大氣與沙塵 | 剖面整體 |
|---|---|---|---|---|---|---|---|---|
| R1 | 113 km from Mori (CN)（43.55, 91.55） | 0.985 | **0.99** | **0.75** | 0.74 | 1.00 | 0.92 | 87.1 |
| R4 | 548 km from Gjoa Haven (CA)（73.55, -95.35） | 0.956 | 0.95 | **0.89** | 0.65 | 0.01 | 0.29 | 27.7 |
| R6 | near Vilaflor (ES)（28.25, -16.65） | 0.773 | 0.01 | 0.42 | **0.64** | 1.00 | **0.91** | 30.1 |

粗體 = 這項測試的主要面向。

### 參考用加權總分（ROC 權重，只用適用的測試、重新正規化）

權重：R1 0.651、R6 0.252、R4 0.097

| # | 地點 | 座標 | 總分 | R1 | R6 | R4 |
|---|---|---|---|---|---|---|
| 1 | near Sharbulag (MN) | 49.05, 92.95 | 0.829 | 0.96 | 0.56 | 0.88 |
| 2 | near Malah (SY) | 32.35, 37.05 | 0.828 | 0.94 | 0.67 | 0.61 |
| 3 | 34 km from Yuli (CN) | 41.55, 86.55 | 0.827 | 0.98 | 0.62 | 0.57 |
| 4 | near Eskil (TR) | 38.45, 33.55 | 0.827 | 0.91 | 0.66 | 0.78 |
| 5 | near Qarah (SY) | 34.25, 36.75 | 0.823 | 0.89 | 0.70 | 0.73 |
| 6 | near Yengiawat (CN) | 41.45, 79.25 | 0.822 | 0.97 | 0.63 | 0.56 |
| 7 | near Eilat (IL) | 29.75, 34.85 | 0.821 | 0.89 | 0.65 | 0.89 |
| 8 | near Akhfennir (MA) | 28.05, -11.75 | 0.818 | 0.93 | 0.67 | 0.57 |
| 9 | 84 km from Grantsville (US) | 41.15, -113.15 | 0.818 | 0.93 | 0.56 | 0.89 |
| 10 | near Halwan (EG) | 29.85, 31.45 | 0.818 | 0.92 | 0.60 | 0.82 |

### 已知類比地檢查

標了對應任務的已知類比地，在該測試的全球前百分比中位數（越小越前面）vs 沒標的：

| 測試 | 對應任務 | 有標（n） | 中位數 | 沒標（n） | 中位數 |
|---|---|---|---|---|---|
| R1 | landing、rover | 7 | 35.0% | 13 | 23.1% |
| R4 | geology | 17 | 16.6% | 2 | 7.3% |
| R6 | — | 0 | —% | 26 | 41.0% |

## Gale Crater（-5.4, 137.8）

測試狀態：R1 已評分；R2 無法評估；R3 不適用（目標沒有可靠的冰訊號）；R4 已評分；R5 不適用（目標沒有可靠的冰訊號）；R6 已評分。冰訊號 clip(Ci, 0, 1) = 0.059（R3、R5 需要 ≥ 0.1）。

### R1 著陸地表條件

可評分陸地格 790,599；分數 ≥ 0.8 的陸地面積 2.2%、≥ 0.9 的 0.6%。

| # | 地點 | 座標 | 分數 | slope | roughness | thermal_inertia | barrenness | summer_barren | ice_free | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 39 km from Ocucaje (PE) | -14.65, -75.85 | 0.976 | 1.00 | 1.00 | 1.00 | 0.87 | 1.00 | 1.00 | barrenness | 否（atacama_yungay 1219 km） |
| 2 | 132 km from Bohu (CN) | 41.15, 87.75 | 0.973 | 1.00 | 0.99 | 1.00 | 0.85 | 1.00 | 1.00 | barrenness | 否（qaidam_dalangtan 459 km） |
| 3 | 75 km from Khur (IR) | 33.35, 54.45 | 0.973 | 0.99 | 1.00 | 1.00 | 0.86 | 1.00 | 1.00 | barrenness | 否（dhofar_amadee18 1694 km） |
| 4 | 94 km from Panjgur (PK) | 27.65, 64.65 | 0.973 | 1.00 | 1.00 | 1.00 | 0.85 | 1.00 | 1.00 | barrenness | 否（kachchh_matanumadh 627 km） |
| 5 | 83 km from Umm Lajj (SA) | 25.55, 37.85 | 0.973 | 1.00 | 1.00 | 1.00 | 0.85 | 1.00 | 1.00 | barrenness | 否（dallol 1283 km） |
| 6 | 47 km from A'yi Take (CN) | 38.75, 74.95 | 0.972 | 0.99 | 0.94 | 1.00 | 0.90 | 1.00 | 1.00 | barrenness | 否（qaidam_dalangtan 1453 km） |
| 7 | 143 km from Qimantage (CN) | 36.25, 91.25 | 0.972 | 0.98 | 0.99 | 1.00 | 0.87 | 1.00 | 1.00 | barrenness | 否（qaidam_dalangtan 234 km） |
| 8 | 58 km from Khash (IR) | 28.45, 61.75 | 0.97 | 1.00 | 0.98 | 1.00 | 0.85 | 1.00 | 1.00 | barrenness | 否（kachchh_matanumadh 902 km） |
| 9 | 39 km from Toksun (CN) | 42.45, 88.75 | 0.969 | 1.00 | 0.98 | 1.00 | 0.85 | 1.00 | 1.00 | barrenness | 否（qaidam_dalangtan 521 km） |
| 10 | 46 km from Bur Safajah (EG) | 26.35, 33.75 | 0.969 | 1.00 | 0.98 | 1.00 | 0.85 | 1.00 | 1.00 | barrenness | 否（lake_salda 1303 km） |

交叉驗證（用面向 地形、地表物質與裸露 組成）：前 20 名在 100 km 內重疊 0%，全部格子的等級相關 0.77。

### R4 含水礦物辨識

可評分陸地格 1,434,366；分數 ≥ 0.8 的陸地面積 10.4%、≥ 0.9 的 0.5%。

| # | 地點 | 座標 | 分數 | lithology | barrenness | summer_barren | ice_free | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 92 km from Wutumeiren (CN) | 37.45, 93.95 | 0.974 | 0.90 | 1.00 | 1.00 | 1.00 | lithology | 否（qaidam_dalangtan 223 km） |
| 2 | 40 km from Xitieshan (CN) | 36.95, 95.65 | 0.974 | 0.90 | 1.00 | 1.00 | 1.00 | lithology | 否（qaidam_dalangtan 383 km） |
| 3 | 167 km from Torghay (KZ) | 48.15, 63.15 | 0.974 | 0.90 | 1.00 | 1.00 | 1.00 | lithology | 否（qaidam_dalangtan 2536 km） |
| 4 | 120 km from Jisegumen (CN) | 35.05, 80.25 | 0.974 | 0.90 | 1.00 | 1.00 | 1.00 | lithology | 否（qaidam_dalangtan 1081 km） |
| 5 | 928 km from Kugluktuk (CA) | 75.85, -107.55 | 0.973 | 0.90 | 0.99 | 1.00 | 1.00 | lithology | 否（haughton_crater 494 km） |
| 6 | 1036 km from Gjoa Haven (CA) | 77.55, -86.35 | 0.973 | 0.90 | 0.99 | 1.00 | 1.00 | lithology | 否（axel_heiberg_lost_hammer 191 km） |
| 7 | 804 km from Vorgashor (RU) | 74.65, 58.95 | 0.973 | 0.90 | 1.00 | 1.00 | 1.00 | lithology | 否（svalbard_bockfjorden 1213 km） |
| 8 | 890 km from Rankin Inlet (CA) | 70.45, -85.95 | 0.973 | 0.90 | 1.00 | 1.00 | 1.00 | lithology | 否（haughton_crater 561 km） |
| 9 | 857 km from Gjoa Haven (CA) | 76.25, -99.75 | 0.972 | 0.90 | 0.99 | 1.00 | 1.00 | lithology | 否（haughton_crater 291 km） |
| 10 | 1126 km from Rankin Inlet (CA) | 72.25, -82.25 | 0.972 | 0.90 | 0.99 | 1.00 | 1.00 | lithology | 否（haughton_crater 417 km） |

交叉驗證（用面向 地表物質與裸露 組成）：前 20 名在 100 km 內重疊 5%，全部格子的等級相關 0.887。

### R6 沙塵與近地表氣象

可評分陸地格 1,314,474；分數 ≥ 0.8 的陸地面積 11.8%、≥ 0.9 的 0.6%。

| # | 地點 | 座標 | 分數 | dust | temperature | diurnal_range | dust_season_shape | dust_season_amplitude | temperature_season_shape | temperature_season_amplitude | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 118 km from Khapalu (PK) | 36.05, 77.05 | 0.95 | 0.99 | 0.93 | 0.96 | 0.95 | 0.99 | 0.86 | 0.97 | temperature_season_shape | 否（qaidam_dalangtan 1318 km） |
| 2 | 183 km from Koramlik (CN) | 36.45, 87.55 | 0.949 | 0.99 | 0.88 | 0.95 | 0.97 | 0.98 | 0.88 | 0.99 | temperature | 否（qaidam_dalangtan 420 km） |
| 3 | 144 km from Wutumeiren (CN) | 35.75, 92.45 | 0.949 | 0.99 | 0.85 | 0.96 | 0.95 | 1.00 | 0.91 | 0.99 | temperature | 否（qaidam_dalangtan 295 km） |
| 4 | 78 km from Hoit Taria (CN) | 38.05, 96.75 | 0.949 | 1.00 | 0.88 | 0.95 | 0.95 | 1.00 | 0.90 | 0.97 | temperature | 否（qaidam_dalangtan 445 km） |
| 5 | 153 km from Qimantage (CN) | 36.05, 89.65 | 0.946 | 0.99 | 0.88 | 0.94 | 0.96 | 0.99 | 0.90 | 0.97 | temperature | 否（qaidam_dalangtan 310 km） |
| 6 | 81 km from Madoi (CN) | 35.55, 95.75 | 0.945 | 0.99 | 0.83 | 0.97 | 0.95 | 0.99 | 0.90 | 0.99 | temperature | 否（qaidam_dalangtan 476 km） |
| 7 | 116 km from Aqqan (CN) | 35.45, 82.25 | 0.944 | 0.99 | 0.88 | 0.96 | 0.97 | 0.93 | 0.89 | 0.99 | temperature | 否（qaidam_dalangtan 896 km） |
| 8 | 186 km from Aqqan (CN) | 35.65, 85.85 | 0.944 | 1.00 | 0.87 | 0.95 | 0.98 | 0.95 | 0.89 | 0.98 | temperature | 否（qaidam_dalangtan 596 km） |
| 9 | 142 km from Qimantage (CN) | 37.45, 88.75 | 0.941 | 0.95 | 0.84 | 0.95 | 0.96 | 1.00 | 0.89 | 1.00 | temperature | 否（qaidam_dalangtan 274 km） |
| 10 | 44 km from Yanglong (CN) | 38.45, 98.65 | 0.941 | 1.00 | 0.83 | 0.95 | 0.94 | 1.00 | 0.90 | 0.98 | temperature | 否（qaidam_dalangtan 608 km） |

交叉驗證（用面向 大氣與沙塵、環境極端 組成）：前 20 名在 100 km 內重疊 50%，全部格子的等級相關 0.782。

### 每項測試第 1 名的面向分數（面向 × 測試）

| 測試 | 第 1 名 | 測試分數 | 地形 | 地表物質與裸露 | 環境極端 | 水與冰 | 大氣與沙塵 | 剖面整體 |
|---|---|---|---|---|---|---|---|---|
| R1 | 39 km from Ocucaje (PE)（-14.65, -75.85） | 0.976 | **0.95** | **0.37** | 0.59 | 0.94 | 0.74 | 67.7 |
| R4 | 92 km from Wutumeiren (CN)（37.45, 93.95） | 0.974 | 0.13 | **0.96** | 0.83 | 0.94 | 0.93 | 61.7 |
| R6 | 118 km from Khapalu (PK)（36.05, 77.05） | 0.95 | 0.03 | 0.51 | **0.86** | 0.06 | **0.99** | 23.7 |

粗體 = 這項測試的主要面向。

### 參考用加權總分（ROC 權重，只用適用的測試、重新正規化）

權重：R1 0.651、R6 0.252、R4 0.097

| # | 地點 | 座標 | 總分 | R1 | R6 | R4 |
|---|---|---|---|---|---|---|
| 1 | 273 km from Cuozheqiangma (CN) | 35.75, 88.05 | 0.953 | 0.97 | 0.92 | 0.93 |
| 2 | 176 km from Qimantage (CN) | 36.05, 91.55 | 0.937 | 0.94 | 0.93 | 0.91 |
| 3 | 189 km from Qimantage (CN) | 35.65, 89.85 | 0.928 | 0.94 | 0.92 | 0.85 |
| 4 | near Burenhayrhan (MN) | 45.85, 91.45 | 0.923 | 0.96 | 0.84 | 0.87 |
| 5 | near Khadan Khak (PK) | 30.75, 67.95 | 0.923 | 0.96 | 0.86 | 0.86 |
| 6 | 132 km from Bohu (CN) | 41.15, 87.75 | 0.922 | 0.97 | 0.80 | 0.94 |
| 7 | 102 km from Barkol (CN) | 43.55, 91.75 | 0.921 | 0.96 | 0.84 | 0.91 |
| 8 | 96 km from Bayangol (MN) | 44.85, 93.65 | 0.919 | 0.95 | 0.85 | 0.88 |
| 9 | 106 km from A'yi Take (CN) | 39.75, 74.75 | 0.918 | 0.94 | 0.87 | 0.90 |
| 10 | 42 km from Yiwu (CN) | 43.45, 94.25 | 0.918 | 0.95 | 0.87 | 0.87 |

### 已知類比地檢查

標了對應任務的已知類比地，在該測試的全球前百分比中位數（越小越前面）vs 沒標的：

| 測試 | 對應任務 | 有標（n） | 中位數 | 沒標（n） | 中位數 |
|---|---|---|---|---|---|
| R1 | landing、rover | 7 | 29.9% | 13 | 22.7% |
| R4 | geology | 24 | 23.1% | 3 | 8.8% |
| R6 | — | 0 | —% | 26 | 42.6% |

## Arcadia Planitia (shallow ground ice)（47.2, -175.7）

測試狀態：R1 已評分；R2 無法評估；R3 已評分；R4 已評分；R5 已評分；R6 已評分。冰訊號 clip(Ci, 0, 1) = 0.526（R3、R5 需要 ≥ 0.1）。

### R1 著陸地表條件

可評分陸地格 790,599；分數 ≥ 0.8 的陸地面積 5.9%、≥ 0.9 的 1.4%。

| # | 地點 | 座標 | 分數 | slope | roughness | thermal_inertia | barrenness | summer_barren | ice_free | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 75 km from Colchani (BO) | -19.95, -67.55 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（atacama_yungay 520 km） |
| 2 | 52 km from Xitieshan (CN) | 36.85, 95.35 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（qaidam_dalangtan 364 km） |
| 3 | 235 km from Qilanbulak (CN) | 40.45, 90.75 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（qaidam_dalangtan 249 km） |
| 4 | near Sidi el Hani (TN) | 35.55, 10.45 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | slope | 否（ries_crater 1482 km） |
| 5 | 39 km from Hoveyzeh (IR) | 31.25, 47.75 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（dhofar_amadee18 1640 km） |
| 6 | 52 km from Dayapar (IN) | 23.85, 69.35 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（kachchh_matanumadh 53 km） |
| 7 | 83 km from Grantsville (US) | 41.25, -112.95 | 0.999 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（pilot_valley_utah 92 km） |
| 8 | 160 km from Yeyik (CN) | 35.25, 82.95 | 0.999 | 1.00 | 0.99 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（qaidam_dalangtan 848 km） |
| 9 | 161 km from Caralue (AU) | -31.85, 136.15 | 0.999 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（pilbara_dresser 2040 km） |
| 10 | 167 km from Torghay (KZ) | 48.15, 63.15 | 0.999 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（qaidam_dalangtan 2536 km） |

交叉驗證（用面向 地形、地表物質與裸露 組成）：前 20 名在 100 km 內重疊 5%，全部格子的等級相關 0.847。

### R3 淺層地下冰

可評分陸地格 1,434,261；分數 ≥ 0.8 的陸地面積 2.4%、≥ 0.9 的 0.2%。

| # | 地點 | 座標 | 分數 | permafrost | cold | dryness | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|
| 1 | 67 km from McMurdo Station (AQ) | -78.15, 164.15 | 1.0 | 1.00 | 1.00 | 1.00 | permafrost | 否（mcmurdo_dry_valleys 88 km） |
| 2 | 494 km from McMurdo Station (AQ) | -82.25, 163.25 | 1.0 | 1.00 | 1.00 | 1.00 | permafrost | 否（beacon_valley 495 km） |
| 3 | 2641 km from Port-aux-Francais (TF) | -73.05, 66.55 | 1.0 | 1.00 | 1.00 | 1.00 | permafrost | 否（beacon_valley 2387 km） |
| 4 | 398 km from McMurdo Station (AQ) | -74.35, 163.45 | 1.0 | 1.00 | 1.00 | 1.00 | permafrost | 否（mcmurdo_dry_valleys 352 km） |
| 5 | 4547 km from Waitangi (NZ) | -84.85, -176.85 | 1.0 | 1.00 | 1.00 | 1.00 | permafrost | 否（beacon_valley 853 km） |
| 6 | 522 km from McMurdo Station (AQ) | -73.15, 167.15 | 1.0 | 1.00 | 1.00 | 1.00 | permafrost | 否（mcmurdo_dry_valleys 505 km） |
| 7 | 1067 km from Stanley (FK) | -61.15, -54.85 | 1.0 | 1.00 | 1.00 | 1.00 | permafrost | 否（atacama_yungay 4280 km） |
| 8 | 321 km from McMurdo Station (AQ) | -79.95, 156.35 | 1.0 | 1.00 | 1.00 | 1.00 | permafrost | 否（beacon_valley 254 km） |
| 9 | 91 km from Jisegumen (CN) | 34.85, 81.05 | 0.966 | 1.00 | 1.00 | 0.90 | dryness | 否（qaidam_dalangtan 1023 km） |
| 10 | 93 km from Zangguy (CN) | 36.45, 78.85 | 0.966 | 1.00 | 1.00 | 0.90 | dryness | 否（qaidam_dalangtan 1151 km） |

交叉驗證（用面向 水與冰、環境極端 組成）：前 20 名在 100 km 內重疊 20%，全部格子的等級相關 0.646。

### R4 含水礦物辨識

可評分陸地格 1,399,028；分數 ≥ 0.8 的陸地面積 0.1%、≥ 0.9 的 0.0%。

| # | 地點 | 座標 | 分數 | lithology | barrenness | summer_barren | ice_free | mineral_signature | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 260 km from Talnakh (RU) | 69.15, 94.95 | 0.986 | 1.00 | 0.99 | 0.94 | 1.00 | 1.00 | summer_barren | 否（svalbard_bockfjorden 2429 km） |
| 2 | 147 km from Sultanah (SA) | 25.75, 40.05 | 0.972 | 1.00 | 0.87 | 1.00 | 1.00 | 1.00 | barrenness | 否（dallol 1280 km） |
| 3 | 153 km from Kotzebue (US) | 68.25, -161.95 | 0.964 | 1.00 | 0.93 | 0.89 | 1.00 | 1.00 | summer_barren | 否（axel_heiberg_lost_hammer 2328 km） |
| 4 | near Assab (ER) | 12.85, 42.65 | 0.948 | 1.00 | 0.77 | 1.00 | 1.00 | 1.00 | barrenness | 否（dallol 297 km） |
| 5 | 85 km from Al 'Ula (SA) | 27.25, 37.45 | 0.938 | 1.00 | 0.73 | 1.00 | 1.00 | 1.00 | barrenness | 否（lake_salda 1357 km） |
| 6 | 120 km from Maralal (KE) | 2.15, 36.45 | 0.936 | 1.00 | 0.72 | 1.00 | 1.00 | 1.00 | barrenness | 否（dallol 1409 km） |
| 7 | 81 km from Puerto Villamil (EC) | -0.25, -91.15 | 0.932 | 1.00 | 0.74 | 1.00 | 1.00 | 0.95 | barrenness | 否（atacama_yungay 3501 km） |
| 8 | near Djibouti (DJ) | 11.55, 43.05 | 0.931 | 1.00 | 0.70 | 1.00 | 1.00 | 1.00 | barrenness | 否（dallol 422 km） |
| 9 | 103 km from Colchani (BO) | -19.95, -67.85 | 0.93 | 0.70 | 0.99 | 1.00 | 1.00 | 1.00 | lithology | 否（atacama_yungay 506 km） |
| 10 | 40 km from Ad Dumayr (SY) | 33.35, 36.95 | 0.928 | 1.00 | 0.69 | 1.00 | 1.00 | 1.00 | barrenness | 否（lake_salda 807 km） |

交叉驗證（用面向 地表物質與裸露 組成）：前 20 名在 100 km 內重疊 10%，全部格子的等級相關 0.686。

### R5 冰河與冰緣地形

可評分陸地格 1,435,234；分數 ≥ 0.8 的陸地面積 0.5%、≥ 0.9 的 0.2%。

| # | 地點 | 座標 | 分數 | permafrost | cold | slope | roughness | barrenness | summer_barren | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1196 km from Kugluktuk (CA) | 78.55, -111.95 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | permafrost | 否（axel_heiberg_lost_hammer 470 km） |
| 2 | 995 km from Khatanga (RU) | 80.85, 97.25 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | permafrost | 否（svalbard_bockfjorden 1467 km） |
| 3 | 1522 km from Vorgashor (RU) | 81.25, 60.45 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（svalbard_bockfjorden 875 km） |
| 4 | 1273 km from Gjoa Haven (CA) | 80.05, -98.85 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | permafrost | 否（axel_heiberg_lost_hammer 204 km） |
| 5 | 697 km from Deputatsky (RU) | 75.55, 141.85 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（svalbard_bockfjorden 2509 km） |
| 6 | 1189 km from Gjoa Haven (CA) | 79.05, -104.85 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | permafrost | 否（axel_heiberg_lost_hammer 308 km） |
| 7 | 1083 km from Gjoa Haven (CA) | 78.35, -97.95 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | slope | 否（axel_heiberg_lost_hammer 187 km） |
| 8 | 243 km from Longyearbyen (SJ) | 80.35, 18.35 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | permafrost | 否（svalbard_bockfjorden 142 km） |
| 9 | 1010 km from Kugluktuk (CA) | 76.75, -109.35 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | permafrost | 否（axel_heiberg_lost_hammer 512 km） |
| 10 | 639 km from Gjoa Haven (CA) | 73.45, -105.55 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | slope | 否（haughton_crater 518 km） |

交叉驗證（用面向 水與冰、地形 組成）：前 20 名在 100 km 內重疊 0%，全部格子的等級相關 0.566。

### R6 沙塵與近地表氣象

可評分陸地格 1,314,474；分數 ≥ 0.8 的陸地面積 0.0%、≥ 0.9 的 0.0%。

| # | 地點 | 座標 | 分數 | dust | temperature | diurnal_range | dust_season_shape | dust_season_amplitude | temperature_season_shape | temperature_season_amplitude | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 37 km from Todok (CN) | 44.85, 83.75 | 0.788 | 0.58 | 0.65 | 0.95 | 0.56 | 0.99 | 0.99 | 0.95 | dust_season_shape | 否（qaidam_dalangtan 979 km） |
| 2 | 68 km from Bay-Khaak (RU) | 50.55, 94.35 | 0.784 | 0.77 | 0.82 | 0.91 | 0.38 | 0.86 | 0.99 | 0.99 | dust_season_shape | 否（qaidam_dalangtan 1375 km） |
| 3 | 203 km from Zeya (RU) | 54.65, 129.95 | 0.784 | 0.90 | 0.92 | 0.61 | 0.43 | 0.91 | 0.99 | 0.95 | dust_season_shape | 否（qaidam_dalangtan 3385 km） |
| 4 | 94 km from Amazar (RU) | 54.65, 120.35 | 0.783 | 0.89 | 0.91 | 0.66 | 0.39 | 0.95 | 0.99 | 0.93 | dust_season_shape | 否（qaidam_dalangtan 2814 km） |
| 5 | 104 km from Romny (RU) | 51.65, 129.45 | 0.781 | 0.84 | 0.85 | 0.68 | 0.44 | 0.93 | 0.99 | 0.90 | dust_season_shape | 否（qaidam_dalangtan 3271 km） |
| 6 | 72 km from Burenhayrhan (MN) | 45.45, 91.65 | 0.779 | 0.66 | 0.70 | 0.98 | 0.46 | 0.90 | 0.99 | 0.96 | dust_season_shape | 否（qaidam_dalangtan 792 km） |
| 7 | 88 km from Erenhot (CN) | 42.95, 111.45 | 0.779 | 0.66 | 0.69 | 0.97 | 0.48 | 0.99 | 0.99 | 0.84 | dust_season_shape | 否（qaidam_dalangtan 1741 km） |
| 8 | 162 km from Chul'man (RU) | 56.45, 127.45 | 0.779 | 0.93 | 0.94 | 0.60 | 0.39 | 0.89 | 0.99 | 0.96 | dust_season_shape | 否（qaidam_dalangtan 3303 km） |
| 9 | 61 km from Zeya (RU) | 53.45, 128.05 | 0.778 | 0.86 | 0.88 | 0.64 | 0.41 | 0.95 | 0.99 | 0.91 | dust_season_shape | 否（qaidam_dalangtan 3228 km） |
| 10 | near Chara (RU) | 56.85, 118.15 | 0.777 | 0.95 | 0.91 | 0.62 | 0.38 | 0.91 | 0.99 | 0.94 | dust_season_shape | 否（qaidam_dalangtan 2826 km） |

交叉驗證（用面向 大氣與沙塵、環境極端 組成）：前 20 名在 100 km 內重疊 0%，全部格子的等級相關 0.766。

### 每項測試第 1 名的面向分數（面向 × 測試）

| 測試 | 第 1 名 | 測試分數 | 地形 | 地表物質與裸露 | 環境極端 | 水與冰 | 大氣與沙塵 | 剖面整體 |
|---|---|---|---|---|---|---|---|---|
| R1 | 75 km from Colchani (BO)（-19.95, -67.55） | 1.0 | **1.00** | **0.81** | 0.74 | — | 0.60 | 77.5 |
| R3 | 67 km from McMurdo Station (AQ)（-78.15, 164.15） | 1.0 | 0.88 | 1.00 | **1.00** | **0.53** | 0.60 | 77.3 |
| R4 | 260 km from Talnakh (RU)（69.15, 94.95） | 0.986 | 0.64 | **1.00** | 0.17 | 0.53 | 0.85 | 54.4 |
| R5 | 1196 km from Kugluktuk (CA)（78.55, -111.95） | 1.0 | **1.00** | 1.00 | 0.78 | **0.53** | 0.77 | 79.2 |
| R6 | 37 km from Todok (CN)（44.85, 83.75） | 0.788 | 1.00 | 0.43 | **0.74** | 0.47 | **0.58** | 61.6 |

粗體 = 這項測試的主要面向。

### 參考用加權總分（ROC 權重，只用適用的測試、重新正規化）

權重：R1 0.455、R3 0.27、R6 0.176、R4 0.068、R5 0.031

| # | 地點 | 座標 | 總分 | R1 | R3 | R6 | R4 | R5 |
|---|---|---|---|---|---|---|---|---|
| 1 | 226 km from Qimantage (CN) | 35.95, 88.45 | 0.811 | 0.98 | 0.91 | 0.60 | 0.28 | 0.98 |
| 2 | 231 km from Qimantage (CN) | 35.25, 89.95 | 0.809 | 0.98 | 0.88 | 0.58 | 0.35 | 0.97 |
| 3 | 34 km from Vilyuysk (RU) | 63.95, 122.15 | 0.803 | 0.86 | 0.83 | 0.73 | 0.52 | 0.86 |
| 4 | 204 km from Cuozheqiangma (CN) | 35.05, 87.05 | 0.785 | 0.96 | 0.83 | 0.60 | 0.30 | 0.91 |
| 5 | 143 km from Wutumeiren (CN) | 35.65, 92.85 | 0.777 | 0.96 | 0.80 | 0.61 | 0.28 | 0.91 |
| 6 | 119 km from Qimantage (CN) | 36.35, 90.95 | 0.775 | 0.88 | 0.89 | 0.63 | 0.30 | 0.90 |
| 7 | 172 km from Pagnag (CN) | 33.65, 90.85 | 0.773 | 0.94 | 0.85 | 0.60 | 0.24 | 0.94 |
| 8 | 158 km from Yeyik (CN) | 35.25, 83.05 | 0.765 | 0.98 | 0.76 | 0.56 | 0.31 | 0.87 |
| 9 | 83 km from Baetov (KG) | 40.55, 75.25 | 0.762 | 0.87 | 0.87 | 0.69 | 0.22 | 0.87 |
| 10 | 438 km from Rankin Inlet (CA) | 63.95, -83.65 | 0.753 | 0.92 | 0.76 | 0.51 | 0.51 | 0.92 |

### 已知類比地檢查

標了對應任務的已知類比地，在該測試的全球前百分比中位數（越小越前面）vs 沒標的：

| 測試 | 對應任務 | 有標（n） | 中位數 | 沒標（n） | 中位數 |
|---|---|---|---|---|---|
| R1 | landing、rover | 7 | 37.3% | 13 | 35.2% |
| R3 | isru_base | 6 | 32.6% | 22 | 38.4% |
| R4 | geology | 17 | 15.6% | 2 | 3.5% |
| R5 | geology | 25 | 23.3% | 3 | 23.6% |
| R6 | — | 0 | —% | 26 | 60.4% |

## Oxia Planum (ExoMars Rosalind Franklin landing site)（18.2, -24.55）

測試狀態：R1 已評分；R2 無法評估；R3 不適用（目標沒有可靠的冰訊號）；R4 已評分；R5 不適用（目標沒有可靠的冰訊號）；R6 已評分。冰訊號 clip(Ci, 0, 1) = 0.0（R3、R5 需要 ≥ 0.1）。

### R1 著陸地表條件

可評分陸地格 790,599；分數 ≥ 0.8 的陸地面積 6.2%、≥ 0.9 的 1.7%。

| # | 地點 | 座標 | 分數 | slope | roughness | thermal_inertia | barrenness | summer_barren | ice_free | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 160 km from Yeyik (CN) | 35.25, 82.95 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（qaidam_dalangtan 848 km） |
| 2 | 40 km from Xitieshan (CN) | 36.95, 95.65 | 0.998 | 1.00 | 0.99 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（qaidam_dalangtan 383 km） |
| 3 | near Sidi el Hani (TN) | 35.55, 10.45 | 0.998 | 1.00 | 0.99 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（ries_crater 1482 km） |
| 4 | 61 km from Dayapar (IN) | 23.85, 69.45 | 0.998 | 1.00 | 0.99 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（kachchh_matanumadh 61 km） |
| 5 | 235 km from Qilanbulak (CN) | 40.45, 90.75 | 0.997 | 1.00 | 0.98 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（qaidam_dalangtan 249 km） |
| 6 | 47 km from Tieganlike (CN) | 39.45, 88.25 | 0.997 | 1.00 | 0.99 | 1.00 | 0.99 | 1.00 | 1.00 | roughness | 否（qaidam_dalangtan 321 km） |
| 7 | 87 km from Qo'ng'irot Shahri (UZ) | 43.35, 57.85 | 0.997 | 1.00 | 0.99 | 1.00 | 0.99 | 1.00 | 1.00 | roughness | 否（kachchh_matanumadh 2425 km） |
| 8 | 39 km from Hoveyzeh (IR) | 31.25, 47.75 | 0.997 | 1.00 | 0.98 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（dhofar_amadee18 1640 km） |
| 9 | 52 km from Colchani (BO) | -20.55, -67.35 | 0.997 | 1.00 | 0.98 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（atacama_yungay 473 km） |
| 10 | 92 km from Wutumeiren (CN) | 37.45, 93.95 | 0.996 | 1.00 | 0.97 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（qaidam_dalangtan 223 km） |

交叉驗證（用面向 地形、地表物質與裸露 組成）：前 20 名在 100 km 內重疊 0%，全部格子的等級相關 0.803。

### R4 含水礦物辨識

可評分陸地格 1,434,366；分數 ≥ 0.8 的陸地面積 5.1%、≥ 0.9 的 0.1%。

| # | 地點 | 座標 | 分數 | lithology | barrenness | summer_barren | ice_free | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 156 km from Beyneu (KZ) | 45.65, 57.15 | 0.946 | 0.80 | 1.00 | 1.00 | 1.00 | lithology | 否（lake_salda 2440 km） |
| 2 | 82 km from Colchani (BO) | -19.75, -67.45 | 0.946 | 0.80 | 1.00 | 1.00 | 1.00 | lithology | 否（atacama_yungay 545 km） |
| 3 | 1086 km from Kugluktuk (CA) | 77.55, -111.75 | 0.946 | 0.80 | 1.00 | 1.00 | 1.00 | lithology | 否（axel_heiberg_lost_hammer 511 km） |
| 4 | 516 km from Gjoa Haven (CA) | 72.75, -102.35 | 0.946 | 0.80 | 1.00 | 1.00 | 1.00 | lithology | 否（haughton_crater 483 km） |
| 5 | 157 km from Gjoa Haven (CA) | 69.85, -97.85 | 0.946 | 0.80 | 1.00 | 1.00 | 1.00 | lithology | 否（haughton_crater 671 km） |
| 6 | 606 km from Gjoa Haven (CA) | 73.95, -92.25 | 0.946 | 0.80 | 1.00 | 1.00 | 1.00 | lithology | 否（haughton_crater 176 km） |
| 7 | 759 km from Gjoa Haven (CA) | 75.35, -91.95 | 0.946 | 0.80 | 1.00 | 1.00 | 1.00 | lithology | 否（haughton_crater 64 km） |
| 8 | 1232 km from Clyde River (CA) | 81.55, -67.75 | 0.946 | 0.80 | 1.00 | 1.00 | 1.00 | lithology | 否（axel_heiberg_lost_hammer 497 km） |
| 9 | 314 km from Clyde River (CA) | 67.65, -68.75 | 0.946 | 0.80 | 1.00 | 1.00 | 1.00 | lithology | 否（haughton_crater 1120 km） |
| 10 | 936 km from Gjoa Haven (CA) | 76.65, -87.15 | 0.946 | 0.80 | 1.00 | 1.00 | 1.00 | lithology | 否（haughton_crater 157 km） |

交叉驗證（用面向 地表物質與裸露 組成）：前 20 名在 100 km 內重疊 0%，全部格子的等級相關 0.866。

### R6 沙塵與近地表氣象

可評分陸地格 1,314,474；分數 ≥ 0.8 的陸地面積 0.0%、≥ 0.9 的 0.0%。

| # | 地點 | 座標 | 分數 | dust | temperature | diurnal_range | dust_season_shape | dust_season_amplitude | temperature_season_shape | temperature_season_amplitude | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | near Zuogaiduoma (CN) | 35.15, 103.25 | 0.757 | 0.79 | 0.78 | 0.83 | 0.30 | 1.00 | 0.97 | 0.96 | dust_season_shape | 否（qaidam_dalangtan 1090 km） |
| 2 | near Vilaflor (ES) | 28.25, -16.65 | 0.755 | 0.82 | 0.57 | 0.94 | 0.34 | 0.96 | 0.97 | 1.00 | dust_season_shape | 否（lanzarote 307 km） |
| 3 | near Lujing Zhen (CN) | 34.35, 104.65 | 0.748 | 0.77 | 0.72 | 0.74 | 0.34 | 0.98 | 0.97 | 0.95 | dust_season_shape | 否（qaidam_dalangtan 1243 km） |
| 4 | near Qiakeri (CN) | 35.15, 101.45 | 0.736 | 0.73 | 0.78 | 0.93 | 0.25 | 0.95 | 0.98 | 0.95 | dust_season_shape | 否（qaidam_dalangtan 940 km） |
| 5 | near Huazangsi (CN) | 37.15, 103.05 | 0.736 | 0.84 | 0.74 | 0.91 | 0.26 | 0.94 | 0.97 | 0.86 | dust_season_shape | 否（qaidam_dalangtan 1009 km） |
| 6 | near Nyinma (CN) | 33.85, 102.15 | 0.732 | 0.68 | 0.74 | 0.96 | 0.26 | 0.91 | 0.97 | 0.99 | dust_season_shape | 否（qaidam_dalangtan 1064 km） |
| 7 | near As Suwayda' (SY) | 32.65, 36.65 | 0.729 | 0.80 | 0.50 | 0.85 | 0.39 | 0.99 | 0.98 | 0.83 | dust_season_shape | 否（lake_salda 836 km） |
| 8 | near Xitan (CN) | 36.05, 105.65 | 0.728 | 0.82 | 0.69 | 0.85 | 0.31 | 0.96 | 0.96 | 0.78 | dust_season_shape | 否（qaidam_dalangtan 1263 km） |
| 9 | near Baalbek (LB) | 34.05, 36.15 | 0.72 | 0.80 | 0.52 | 0.88 | 0.34 | 0.99 | 0.98 | 0.82 | dust_season_shape | 否（lake_salda 701 km） |
| 10 | near Daotanghe (CN) | 36.45, 100.95 | 0.72 | 0.76 | 0.74 | 0.97 | 0.22 | 0.98 | 0.97 | 0.88 | dust_season_shape | 否（qaidam_dalangtan 846 km） |

交叉驗證（用面向 大氣與沙塵、環境極端 組成）：前 20 名在 100 km 內重疊 0%，全部格子的等級相關 0.734。

### 每項測試第 1 名的面向分數（面向 × 測試）

| 測試 | 第 1 名 | 測試分數 | 地形 | 地表物質與裸露 | 環境極端 | 水與冰 | 大氣與沙塵 | 剖面整體 |
|---|---|---|---|---|---|---|---|---|
| R1 | 160 km from Yeyik (CN)（35.25, 82.95） | 1.0 | **1.00** | **0.62** | 0.86 | 0.01 | 0.79 | 33.6 |
| R4 | 156 km from Beyneu (KZ)（45.65, 57.15） | 0.946 | 0.98 | **0.86** | 0.72 | 1.00 | 0.83 | 87.2 |
| R6 | near Zuogaiduoma (CN)（35.15, 103.25） | 0.757 | 0.44 | 0.08 | **0.55** | 0.93 | **0.79** | 43.1 |

粗體 = 這項測試的主要面向。

### 參考用加權總分（ROC 權重，只用適用的測試、重新正規化）

權重：R1 0.651、R6 0.252、R4 0.097

| # | 地點 | 座標 | 總分 | R1 | R6 | R4 |
|---|---|---|---|---|---|---|
| 1 | 30 km from Eskil (TR) | 38.65, 33.55 | 0.873 | 0.98 | 0.65 | 0.86 |
| 2 | 157 km from Qiangma (CN) | 33.35, 90.45 | 0.869 | 0.97 | 0.66 | 0.87 |
| 3 | 107 km from Sayotesh (KZ) | 45.25, 53.15 | 0.866 | 0.97 | 0.62 | 0.91 |
| 4 | 156 km from Beyneu (KZ) | 45.65, 57.15 | 0.863 | 1.00 | 0.57 | 0.95 |
| 5 | near Shabestar (IR) | 38.05, 45.55 | 0.863 | 0.96 | 0.65 | 0.88 |
| 6 | 32 km from Toksun (CN) | 42.75, 88.25 | 0.862 | 0.98 | 0.64 | 0.81 |
| 7 | 178 km from Torghay (KZ) | 48.05, 63.15 | 0.861 | 0.99 | 0.59 | 0.88 |
| 8 | 98 km from Cuozheqiangma (CN) | 33.05, 86.75 | 0.861 | 0.96 | 0.64 | 0.89 |
| 9 | 229 km from Qimantage (CN) | 35.25, 90.25 | 0.861 | 0.99 | 0.61 | 0.83 |
| 10 | 137 km from Zhanaozen (KZ) | 42.65, 54.25 | 0.859 | 0.98 | 0.60 | 0.92 |

### 已知類比地檢查

標了對應任務的已知類比地，在該測試的全球前百分比中位數（越小越前面）vs 沒標的：

| 測試 | 對應任務 | 有標（n） | 中位數 | 沒標（n） | 中位數 |
|---|---|---|---|---|---|
| R1 | landing、rover | 7 | 37.3% | 13 | 36.0% |
| R4 | geology | 24 | 22.9% | 3 | 11.3% |
| R6 | — | 0 | —% | 26 | 42.5% |

## Meridiani Planum (Opportunity landing site, Eagle crater)（-1.95, -5.53）

測試狀態：R1 已評分；R2 無法評估；R3 不適用（目標沒有可靠的冰訊號）；R4 已評分；R5 不適用（目標沒有可靠的冰訊號）；R6 已評分。冰訊號 clip(Ci, 0, 1) = 0.034（R3、R5 需要 ≥ 0.1）。

### R1 著陸地表條件

可評分陸地格 790,599；分數 ≥ 0.8 的陸地面積 6.4%、≥ 0.9 的 1.9%。

| # | 地點 | 座標 | 分數 | slope | roughness | thermal_inertia | barrenness | summer_barren | ice_free | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 160 km from Yeyik (CN) | 35.25, 82.95 | 0.99 | 1.00 | 0.94 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（qaidam_dalangtan 848 km） |
| 2 | 174 km from Sangiyn Dalay (MN) | 43.65, 97.05 | 0.987 | 1.00 | 1.00 | 1.00 | 0.93 | 1.00 | 1.00 | barrenness | 否（qaidam_dalangtan 744 km） |
| 3 | 105 km from Kugluktuk (CA) | 68.65, -116.35 | 0.986 | 1.00 | 0.97 | 1.00 | 0.94 | 1.00 | 1.00 | barrenness | 否（haughton_crater 1165 km） |
| 4 | near Sidi el Hani (TN) | 35.55, 10.45 | 0.985 | 1.00 | 0.91 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（ries_crater 1482 km） |
| 5 | 57 km from Yiwu (CN) | 43.75, 94.55 | 0.984 | 1.00 | 0.99 | 1.00 | 0.92 | 1.00 | 1.00 | barrenness | 否（qaidam_dalangtan 649 km） |
| 6 | near Toksun (CN) | 42.95, 88.35 | 0.984 | 1.00 | 0.98 | 1.00 | 0.93 | 1.00 | 1.00 | barrenness | 否（qaidam_dalangtan 585 km） |
| 7 | 61 km from Dayapar (IN) | 23.85, 69.45 | 0.984 | 1.00 | 0.91 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（kachchh_matanumadh 61 km） |
| 8 | 40 km from Xitieshan (CN) | 36.95, 95.65 | 0.983 | 1.00 | 0.90 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（qaidam_dalangtan 383 km） |
| 9 | 73 km from Edd (ER) | 13.45, 42.15 | 0.983 | 1.00 | 0.99 | 1.00 | 0.91 | 1.00 | 1.00 | barrenness | 否（dallol 218 km） |
| 10 | 142 km from Jisegumen (CN) | 35.15, 79.95 | 0.983 | 1.00 | 0.92 | 1.00 | 0.98 | 1.00 | 1.00 | roughness | 否（qaidam_dalangtan 1102 km） |

交叉驗證（用面向 地形、地表物質與裸露 組成）：前 20 名在 100 km 內重疊 10%，全部格子的等級相關 0.844。

### R4 含水礦物辨識

可評分陸地格 1,434,366；分數 ≥ 0.8 的陸地面積 1.5%、≥ 0.9 的 0.1%。

| # | 地點 | 座標 | 分數 | lithology | barrenness | summer_barren | ice_free | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 65 km from Colchani (BO) | -20.35, -67.55 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | lithology | 否（atacama_yungay 481 km） |
| 2 | 150 km from Antofagasta de la Sierra (AR) | -24.75, -67.75 | 0.985 | 1.00 | 0.94 | 1.00 | 1.00 | barrenness | 否（atacama_yungay 232 km） |
| 3 | 563 km from Kugluktuk (CA) | 72.55, -109.65 | 0.98 | 1.00 | 1.00 | 0.92 | 1.00 | summer_barren | 否（haughton_crater 685 km） |
| 4 | 54 km from Rapar (IN) | 24.05, 70.55 | 0.971 | 1.00 | 0.89 | 1.00 | 1.00 | barrenness | 否（kachchh_matanumadh 172 km） |
| 5 | 62 km from San Pedro de Atacama (CL) | -23.45, -68.35 | 0.97 | 1.00 | 0.88 | 1.00 | 1.00 | barrenness | 否（atacama_yungay 174 km） |
| 6 | 101 km from Diego de Almagro (CL) | -26.25, -69.05 | 0.967 | 1.00 | 0.87 | 1.00 | 1.00 | barrenness | 否（atacama_yungay 257 km） |
| 7 | 57 km from Zahedan (IR) | 29.55, 61.45 | 0.964 | 1.00 | 0.86 | 1.00 | 1.00 | barrenness | 否（kachchh_matanumadh 1000 km） |
| 8 | near Zaranj (AF) | 31.05, 62.15 | 0.957 | 1.00 | 0.84 | 1.00 | 1.00 | barrenness | 否（kachchh_matanumadh 1070 km） |
| 9 | 155 km from Ar Ruways (AE) | 23.05, 51.75 | 0.951 | 1.00 | 0.82 | 1.00 | 1.00 | barrenness | 否（dhofar_amadee18 654 km） |
| 10 | 39 km from Tubarjal (SA) | 30.85, 38.25 | 0.946 | 1.00 | 0.80 | 1.00 | 1.00 | barrenness | 否（lake_salda 1084 km） |

交叉驗證（用面向 地表物質與裸露 組成）：前 20 名在 100 km 內重疊 10%，全部格子的等級相關 0.907。

### R6 沙塵與近地表氣象

可評分陸地格 1,314,474；分數 ≥ 0.8 的陸地面積 4.1%、≥ 0.9 的 0.2%。

| # | 地點 | 座標 | 分數 | dust | temperature | diurnal_range | dust_season_shape | dust_season_amplitude | temperature_season_shape | temperature_season_amplitude | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 37 km from Yeyik (CN) | 36.35, 83.35 | 0.938 | 0.97 | 0.87 | 0.94 | 0.97 | 0.99 | 0.86 | 0.96 | temperature_season_shape | 否（qaidam_dalangtan 767 km） |
| 2 | 160 km from Waxxari (CN) | 37.35, 87.95 | 0.934 | 0.95 | 0.85 | 0.97 | 0.97 | 1.00 | 0.87 | 0.93 | temperature | 否（qaidam_dalangtan 344 km） |
| 3 | 99 km from Nur (CN) | 35.65, 80.35 | 0.934 | 0.96 | 0.90 | 0.95 | 0.96 | 0.99 | 0.85 | 0.92 | temperature_season_shape | 否（qaidam_dalangtan 1048 km） |
| 4 | 32 km from Koramlik (CN) | 37.15, 86.05 | 0.931 | 0.96 | 0.86 | 0.98 | 0.98 | 0.99 | 0.85 | 0.90 | temperature_season_shape | 否（qaidam_dalangtan 511 km） |
| 5 | 77 km from Qimantage (CN) | 36.65, 90.05 | 0.925 | 0.94 | 0.86 | 0.95 | 0.94 | 1.00 | 0.88 | 0.92 | temperature | 否（qaidam_dalangtan 235 km） |
| 6 | 138 km from Wutumeiren (CN) | 36.05, 92.05 | 0.925 | 0.94 | 0.84 | 0.93 | 0.93 | 1.00 | 0.89 | 0.95 | temperature | 否（qaidam_dalangtan 256 km） |
| 7 | 55 km from Qilanbulak (CN) | 38.25, 89.55 | 0.924 | 0.99 | 0.83 | 0.91 | 0.95 | 0.99 | 0.85 | 0.95 | temperature | 否（qaidam_dalangtan 185 km） |
| 8 | 118 km from Khapalu (PK) | 36.05, 77.05 | 0.924 | 0.92 | 0.93 | 0.96 | 0.97 | 0.99 | 0.84 | 0.87 | temperature_season_shape | 否（qaidam_dalangtan 1318 km） |
| 9 | 124 km from Aqqan (CN) | 35.35, 82.05 | 0.923 | 0.92 | 0.91 | 0.92 | 0.98 | 0.93 | 0.85 | 0.95 | temperature_season_shape | 否（qaidam_dalangtan 917 km） |
| 10 | 85 km from Golmud (CN) | 35.65, 95.05 | 0.919 | 0.92 | 0.85 | 0.92 | 0.93 | 1.00 | 0.86 | 0.97 | temperature | 否（qaidam_dalangtan 423 km） |

交叉驗證（用面向 大氣與沙塵、環境極端 組成）：前 20 名在 100 km 內重疊 50%，全部格子的等級相關 0.753。

### 每項測試第 1 名的面向分數（面向 × 測試）

| 測試 | 第 1 名 | 測試分數 | 地形 | 地表物質與裸露 | 環境極端 | 水與冰 | 大氣與沙塵 | 剖面整體 |
|---|---|---|---|---|---|---|---|---|
| R1 | 160 km from Yeyik (CN)（35.25, 82.95） | 0.99 | **0.96** | **0.78** | 0.86 | 0.03 | 0.93 | 45.9 |
| R4 | 65 km from Colchani (BO)（-20.35, -67.55） | 1.0 | 0.91 | **0.97** | 0.75 | — | 0.20 | 59.9 |
| R6 | 37 km from Yeyik (CN)（36.35, 83.35） | 0.938 | 0.01 | 0.70 | **0.87** | 0.03 | **0.97** | 18.7 |

粗體 = 這項測試的主要面向。

### 參考用加權總分（ROC 權重，只用適用的測試、重新正規化）

權重：R1 0.651、R6 0.252、R4 0.097

| # | 地點 | 座標 | 總分 | R1 | R6 | R4 |
|---|---|---|---|---|---|---|
| 1 | 158 km from Yeyik (CN) | 35.25, 83.05 | 0.942 | 0.99 | 0.88 | 0.83 |
| 2 | 201 km from Waxxari (CN) | 37.05, 88.25 | 0.932 | 0.97 | 0.89 | 0.81 |
| 3 | 126 km from Qimantage (CN) | 36.25, 90.85 | 0.93 | 0.97 | 0.89 | 0.80 |
| 4 | 58 km from Haquxiang (CN) | 36.95, 94.75 | 0.929 | 0.98 | 0.85 | 0.84 |
| 5 | 38 km from Qimantage (CN) | 37.45, 89.95 | 0.927 | 0.97 | 0.85 | 0.82 |
| 6 | 204 km from Cuozheqiangma (CN) | 35.05, 87.05 | 0.925 | 0.97 | 0.86 | 0.81 |
| 7 | 143 km from Wutumeiren (CN) | 35.65, 92.85 | 0.918 | 0.95 | 0.88 | 0.80 |
| 8 | 83 km from Ghoriyan (AF) | 33.65, 61.15 | 0.917 | 0.98 | 0.79 | 0.86 |
| 9 | 166 km from Sangiyn Dalay (MN) | 43.65, 97.55 | 0.912 | 0.98 | 0.78 | 0.85 |
| 10 | 102 km from Queren (CN) | 45.05, 90.15 | 0.912 | 0.97 | 0.81 | 0.84 |

### 已知類比地檢查

標了對應任務的已知類比地，在該測試的全球前百分比中位數（越小越前面）vs 沒標的：

| 測試 | 對應任務 | 有標（n） | 中位數 | 沒標（n） | 中位數 |
|---|---|---|---|---|---|
| R1 | landing、rover | 7 | 34.5% | 13 | 32.9% |
| R4 | geology | 24 | 23.8% | 3 | 8.5% |
| R6 | — | 0 | —% | 26 | 37.5% |

## Protonilus Mensae (candidate human exploration zone, buried glacial ice)（41.905, 48.548）

測試狀態：R1 已評分；R2 無法評估；R3 已評分；R4 已評分；R5 已評分；R6 已評分。冰訊號 clip(Ci, 0, 1) = 0.162（R3、R5 需要 ≥ 0.1）。

### R1 著陸地表條件

可評分陸地格 790,599；分數 ≥ 0.8 的陸地面積 2.9%、≥ 0.9 的 0.9%。

| # | 地點 | 座標 | 分數 | slope | roughness | thermal_inertia | barrenness | summer_barren | ice_free | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 67 km from Khash (IR) | 28.75, 61.55 | 0.98 | 1.00 | 1.00 | 1.00 | 0.89 | 1.00 | 1.00 | barrenness | 否（kachchh_matanumadh 938 km） |
| 2 | near Minas de Marcona (PE) | -15.25, -75.15 | 0.979 | 1.00 | 1.00 | 1.00 | 0.88 | 1.00 | 1.00 | barrenness | 否（atacama_yungay 1124 km） |
| 3 | 96 km from Bayangol (MN) | 44.85, 93.65 | 0.976 | 1.00 | 0.99 | 1.00 | 0.87 | 1.00 | 1.00 | barrenness | 否（qaidam_dalangtan 743 km） |
| 4 | 46 km from Edd (ER) | 13.55, 41.85 | 0.976 | 1.00 | 0.98 | 1.00 | 0.88 | 1.00 | 1.00 | barrenness | 否（dallol 184 km） |
| 5 | 74 km from La Consulta (AR) | -34.15, -69.75 | 0.975 | 1.00 | 0.97 | 1.00 | 0.89 | 1.00 | 1.00 | barrenness | 否（atacama_yungay 1120 km） |
| 6 | 50 km from Jask (IR) | 26.05, 57.55 | 0.975 | 1.00 | 1.00 | 1.00 | 0.86 | 1.00 | 1.00 | barrenness | 否（dhofar_amadee18 913 km） |
| 7 | 90 km from Saravan (IR) | 27.35, 63.25 | 0.972 | 1.00 | 1.00 | 1.00 | 0.84 | 1.00 | 1.00 | barrenness | 否（kachchh_matanumadh 711 km） |
| 8 | 51 km from Bur Safajah (EG) | 26.35, 33.65 | 0.971 | 1.00 | 1.00 | 1.00 | 0.84 | 1.00 | 1.00 | barrenness | 否（lake_salda 1300 km） |
| 9 | 58 km from Antofagasta (CL) | -23.15, -70.55 | 0.97 | 1.00 | 0.99 | 1.00 | 0.84 | 1.00 | 1.00 | barrenness | 否（atacama_yungay 122 km） |
| 10 | 32 km from Luntai (CN) | 42.05, 84.35 | 0.97 | 1.00 | 1.00 | 1.00 | 0.84 | 1.00 | 1.00 | barrenness | 否（qaidam_dalangtan 746 km） |

交叉驗證（用面向 地形、地表物質與裸露 組成）：前 20 名在 100 km 內重疊 5%，全部格子的等級相關 0.863。

### R3 淺層地下冰

可評分陸地格 1,434,261；分數 ≥ 0.8 的陸地面積 2.4%、≥ 0.9 的 0.2%。

| # | 地點 | 座標 | 分數 | permafrost | cold | dryness | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|
| 1 | 522 km from McMurdo Station (AQ) | -73.15, 167.15 | 1.0 | 1.00 | 1.00 | 1.00 | permafrost | 否（mcmurdo_dry_valleys 505 km） |
| 2 | 37 km from McMurdo Station (AQ) | -77.65, 167.95 | 1.0 | 1.00 | 1.00 | 1.00 | permafrost | 否（mcmurdo_dry_valleys 143 km） |
| 3 | 1067 km from Stanley (FK) | -61.15, -54.85 | 1.0 | 1.00 | 1.00 | 1.00 | permafrost | 否（atacama_yungay 4280 km） |
| 4 | 2641 km from Port-aux-Francais (TF) | -73.05, 66.55 | 1.0 | 1.00 | 1.00 | 1.00 | permafrost | 否（beacon_valley 2387 km） |
| 5 | 494 km from McMurdo Station (AQ) | -82.25, 163.25 | 1.0 | 1.00 | 1.00 | 1.00 | permafrost | 否（beacon_valley 495 km） |
| 6 | 141 km from McMurdo Station (AQ) | -78.65, 161.85 | 1.0 | 1.00 | 1.00 | 1.00 | permafrost | 否（beacon_valley 96 km） |
| 7 | 398 km from McMurdo Station (AQ) | -74.35, 163.45 | 1.0 | 1.00 | 1.00 | 1.00 | permafrost | 否（mcmurdo_dry_valleys 352 km） |
| 8 | 4547 km from Waitangi (NZ) | -84.85, -176.85 | 1.0 | 1.00 | 1.00 | 1.00 | permafrost | 否（beacon_valley 853 km） |
| 9 | 321 km from McMurdo Station (AQ) | -79.95, 156.35 | 1.0 | 1.00 | 1.00 | 1.00 | permafrost | 否（beacon_valley 254 km） |
| 10 | 99 km from Jisegumen (CN) | 34.95, 80.85 | 0.966 | 1.00 | 1.00 | 0.90 | dryness | 否（qaidam_dalangtan 1035 km） |

交叉驗證（用面向 水與冰、環境極端 組成）：前 20 名在 100 km 內重疊 25%，全部格子的等級相關 -0.003。

### R4 含水礦物辨識

可評分陸地格 1,434,366；分數 ≥ 0.8 的陸地面積 10.4%、≥ 0.9 的 0.5%。

| # | 地點 | 座標 | 分數 | lithology | barrenness | summer_barren | ice_free | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 40 km from Xitieshan (CN) | 36.95, 95.65 | 0.974 | 0.90 | 1.00 | 1.00 | 1.00 | lithology | 否（qaidam_dalangtan 383 km） |
| 2 | 167 km from Torghay (KZ) | 48.15, 63.15 | 0.974 | 0.90 | 1.00 | 1.00 | 1.00 | lithology | 否（qaidam_dalangtan 2536 km） |
| 3 | 92 km from Wutumeiren (CN) | 37.45, 93.95 | 0.974 | 0.90 | 1.00 | 1.00 | 1.00 | lithology | 否（qaidam_dalangtan 223 km） |
| 4 | 120 km from Jisegumen (CN) | 35.05, 80.25 | 0.974 | 0.90 | 1.00 | 1.00 | 1.00 | lithology | 否（qaidam_dalangtan 1081 km） |
| 5 | 928 km from Kugluktuk (CA) | 75.85, -107.55 | 0.973 | 0.90 | 0.99 | 1.00 | 1.00 | lithology | 否（haughton_crater 494 km） |
| 6 | 1036 km from Gjoa Haven (CA) | 77.55, -86.35 | 0.973 | 0.90 | 0.99 | 1.00 | 1.00 | lithology | 否（axel_heiberg_lost_hammer 191 km） |
| 7 | 890 km from Rankin Inlet (CA) | 70.45, -85.95 | 0.973 | 0.90 | 1.00 | 1.00 | 1.00 | lithology | 否（haughton_crater 561 km） |
| 8 | 804 km from Vorgashor (RU) | 74.65, 58.95 | 0.973 | 0.90 | 1.00 | 1.00 | 1.00 | lithology | 否（svalbard_bockfjorden 1213 km） |
| 9 | 857 km from Gjoa Haven (CA) | 76.25, -99.75 | 0.972 | 0.90 | 0.99 | 1.00 | 1.00 | lithology | 否（haughton_crater 291 km） |
| 10 | 733 km from Gjoa Haven (CA) | 73.65, -82.55 | 0.972 | 0.90 | 0.99 | 1.00 | 1.00 | lithology | 否（haughton_crater 286 km） |

交叉驗證（用面向 地表物質與裸露 組成）：前 20 名在 100 km 內重疊 10%，全部格子的等級相關 0.915。

### R5 冰河與冰緣地形

可評分陸地格 1,435,234；分數 ≥ 0.8 的陸地面積 0.4%、≥ 0.9 的 0.2%。

| # | 地點 | 座標 | 分數 | permafrost | cold | slope | roughness | barrenness | summer_barren | glacier_distance | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 881 km from Kugluktuk (CA) | 75.75, -114.75 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（haughton_crater 691 km） |
| 2 | 1389 km from Clyde River (CA) | 82.95, -71.15 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（axel_heiberg_lost_hammer 537 km） |
| 3 | 1237 km from Clyde River (CA) | 81.55, -73.15 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（axel_heiberg_lost_hammer 418 km） |
| 4 | 612 km from Clyde River (CA) | 74.65, -80.65 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | permafrost | 否（haughton_crater 272 km） |
| 5 | 599 km from Gjoa Haven (CA) | 73.05, -86.45 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（haughton_crater 277 km） |
| 6 | 115 km from Clyde River (CA) | 69.45, -68.05 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | slope | 否（haughton_crater 971 km） |
| 7 | 292 km from Clyde River (CA) | 67.85, -67.95 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（haughton_crater 1119 km） |
| 8 | 99 km from Longyearbyen (SJ) | 78.85, 12.45 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | slope | 否（svalbard_bockfjorden 67 km） |
| 9 | 927 km from Gjoa Haven (CA) | 76.45, -86.05 | 0.999 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（haughton_crater 154 km） |
| 10 | 819 km from Vorgashor (RU) | 74.85, 59.95 | 0.999 | 1.00 | 1.00 | 1.00 | 0.99 | 1.00 | 1.00 | 1.00 | roughness | 否（svalbard_bockfjorden 1218 km） |

交叉驗證（用面向 水與冰、地形 組成）：前 20 名在 100 km 內重疊 0%，全部格子的等級相關 -0.055。

### R6 沙塵與近地表氣象

可評分陸地格 1,314,474；分數 ≥ 0.8 的陸地面積 0.0%、≥ 0.9 的 0.0%。

| # | 地點 | 座標 | 分數 | dust | temperature | diurnal_range | dust_season_shape | dust_season_amplitude | temperature_season_shape | temperature_season_amplitude | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 128 km from Jumla (NP) | 30.35, 82.65 | 0.742 | 0.97 | 0.78 | 0.99 | 0.23 | 0.88 | 0.97 | 0.85 | dust_season_shape | 否（qaidam_dalangtan 1212 km） |
| 2 | near Craig (US) | 40.55, -107.75 | 0.74 | 1.00 | 0.70 | 0.90 | 0.20 | 0.97 | 0.98 | 0.98 | dust_season_shape | 否（mdrs_hanksville 353 km） |
| 3 | 92 km from Kyelang (IN) | 32.85, 77.95 | 0.739 | 0.86 | 0.86 | 0.96 | 0.20 | 0.99 | 0.95 | 0.90 | dust_season_shape | 否（kachchh_matanumadh 1358 km） |
| 4 | near Kosh-Agach (RU) | 49.85, 88.65 | 0.738 | 0.74 | 0.83 | 0.88 | 0.22 | 1.00 | 1.00 | 1.00 | dust_season_shape | 否（qaidam_dalangtan 1303 km） |
| 5 | 57 km from Marbleton (US) | 42.25, -109.55 | 0.737 | 0.99 | 0.74 | 0.96 | 0.18 | 0.97 | 0.98 | 0.98 | dust_season_shape | 否（pilot_valley_utah 396 km） |
| 6 | near Monticello (US) | 37.95, -109.15 | 0.735 | 0.99 | 0.67 | 0.95 | 0.21 | 0.95 | 0.99 | 0.90 | dust_season_shape | 否（mdrs_hanksville 152 km） |
| 7 | 112 km from Leh (IN) | 34.45, 78.75 | 0.735 | 0.84 | 0.85 | 0.98 | 0.20 | 0.98 | 0.97 | 0.88 | dust_season_shape | 否（qaidam_dalangtan 1233 km） |
| 8 | 33 km from Center (US) | 37.85, -105.75 | 0.731 | 0.86 | 0.66 | 0.99 | 0.22 | 0.94 | 0.99 | 0.94 | dust_season_shape | 否（mdrs_hanksville 445 km） |
| 9 | near Kavak (TR) | 39.25, 37.45 | 0.73 | 0.68 | 0.64 | 0.89 | 0.32 | 1.00 | 0.97 | 0.93 | dust_season_shape | 否（lake_salda 703 km） |
| 10 | 90 km from Maindong (CN) | 30.95, 86.25 | 0.729 | 0.98 | 0.75 | 0.99 | 0.24 | 0.88 | 0.98 | 0.74 | dust_season_shape | 否（qaidam_dalangtan 958 km） |

交叉驗證（用面向 大氣與沙塵、環境極端 組成）：前 20 名在 100 km 內重疊 20%，全部格子的等級相關 0.751。

### 每項測試第 1 名的面向分數（面向 × 測試）

| 測試 | 第 1 名 | 測試分數 | 地形 | 地表物質與裸露 | 環境極端 | 水與冰 | 大氣與沙塵 | 剖面整體 |
|---|---|---|---|---|---|---|---|---|
| R1 | 67 km from Khash (IR)（28.75, 61.55） | 0.98 | **0.99** | **0.85** | 0.32 | 0.84 | 0.48 | 64.1 |
| R3 | 522 km from McMurdo Station (AQ)（-73.15, 167.15） | 1.0 | 0.89 | 0.80 | **1.00** | **0.16** | 0.65 | 59.6 |
| R4 | 40 km from Xitieshan (CN)（36.95, 95.65） | 0.974 | 0.26 | **0.95** | 0.78 | 0.84 | 0.57 | 62.2 |
| R5 | 881 km from Kugluktuk (CA)（75.75, -114.75） | 1.0 | **1.00** | 0.89 | 0.73 | **0.16** | 0.82 | 61.4 |
| R6 | 128 km from Jumla (NP)（30.35, 82.65） | 0.742 | 0.63 | 0.32 | **0.72** | 0.43 | **0.97** | 57.2 |

粗體 = 這項測試的主要面向。

### 參考用加權總分（ROC 權重，只用適用的測試、重新正規化）

權重：R1 0.455、R3 0.27、R6 0.176、R4 0.068、R5 0.031

| # | 地點 | 座標 | 總分 | R1 | R3 | R6 | R4 | R5 |
|---|---|---|---|---|---|---|---|---|
| 1 | 273 km from Cuozheqiangma (CN) | 35.75, 88.05 | 0.865 | 0.96 | 0.90 | 0.60 | 0.93 | 0.94 |
| 2 | 290 km from Pagnag (CN) | 34.85, 91.25 | 0.864 | 0.95 | 0.86 | 0.65 | 0.91 | 0.96 |
| 3 | 134 km from Qimantage (CN) | 36.15, 90.75 | 0.859 | 0.97 | 0.88 | 0.58 | 0.87 | 0.97 |
| 4 | 181 km from Cuozheqiangma (CN) | 34.45, 86.35 | 0.853 | 0.93 | 0.93 | 0.65 | 0.69 | 0.94 |
| 5 | 66 km from Cuozheqiangma (CN) | 33.85, 88.05 | 0.841 | 0.91 | 0.90 | 0.67 | 0.68 | 0.91 |
| 6 | 47 km from Karabulak (CN) | 41.15, 77.45 | 0.836 | 0.91 | 0.86 | 0.63 | 0.85 | 0.92 |
| 7 | 131 km from Wutumeiren (CN) | 35.75, 93.45 | 0.827 | 0.90 | 0.86 | 0.58 | 0.94 | 0.98 |
| 8 | 79 km from At-Bashi (KG) | 40.55, 75.35 | 0.827 | 0.88 | 0.87 | 0.65 | 0.82 | 0.90 |
| 9 | 141 km from Ruoqiang (CN) | 37.75, 88.25 | 0.824 | 0.90 | 0.91 | 0.55 | 0.80 | 0.92 |
| 10 | 51 km from Biluu (MN) | 49.45, 89.75 | 0.821 | 0.89 | 0.79 | 0.71 | 0.81 | 0.85 |

### 已知類比地檢查

標了對應任務的已知類比地，在該測試的全球前百分比中位數（越小越前面）vs 沒標的：

| 測試 | 對應任務 | 有標（n） | 中位數 | 沒標（n） | 中位數 |
|---|---|---|---|---|---|
| R1 | landing、rover | 7 | 29.1% | 13 | 23.1% |
| R3 | isru_base | 6 | 32.6% | 22 | 38.4% |
| R4 | geology | 24 | 23.1% | 3 | 8.8% |
| R5 | geology | 25 | 19.1% | 3 | 13.5% |
| R6 | — | 0 | —% | 26 | 55.9% |

## Arcadia Planitia AP-105 (SkyFall design reference landing site)（43.3295, -161.4772）

測試狀態：R1 已評分；R2 無法評估；R3 已評分；R4 已評分；R5 已評分；R6 已評分。冰訊號 clip(Ci, 0, 1) = 0.583（R3、R5 需要 ≥ 0.1）。

### R1 著陸地表條件

可評分陸地格 790,599；分數 ≥ 0.8 的陸地面積 5.9%、≥ 0.9 的 1.4%。

| # | 地點 | 座標 | 分數 | slope | roughness | thermal_inertia | barrenness | summer_barren | ice_free | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 75 km from Colchani (BO) | -19.95, -67.55 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（atacama_yungay 520 km） |
| 2 | 52 km from Xitieshan (CN) | 36.85, 95.35 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（qaidam_dalangtan 364 km） |
| 3 | 235 km from Qilanbulak (CN) | 40.45, 90.75 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（qaidam_dalangtan 249 km） |
| 4 | near Sidi el Hani (TN) | 35.55, 10.45 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | slope | 否（ries_crater 1482 km） |
| 5 | 39 km from Hoveyzeh (IR) | 31.25, 47.75 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（dhofar_amadee18 1640 km） |
| 6 | 52 km from Dayapar (IN) | 23.85, 69.35 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（kachchh_matanumadh 53 km） |
| 7 | 160 km from Yeyik (CN) | 35.25, 82.95 | 0.999 | 1.00 | 0.99 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（qaidam_dalangtan 848 km） |
| 8 | 83 km from Grantsville (US) | 41.25, -112.95 | 0.999 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（pilot_valley_utah 92 km） |
| 9 | 178 km from Torghay (KZ) | 48.05, 63.15 | 0.999 | 1.00 | 1.00 | 1.00 | 0.99 | 1.00 | 1.00 | barrenness | 否（qaidam_dalangtan 2533 km） |
| 10 | 161 km from Caralue (AU) | -31.85, 136.15 | 0.999 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（pilbara_dresser 2040 km） |

交叉驗證（用面向 地形、地表物質與裸露 組成）：前 20 名在 100 km 內重疊 10%，全部格子的等級相關 0.853。

### R3 淺層地下冰

可評分陸地格 1,434,261；分數 ≥ 0.8 的陸地面積 2.4%、≥ 0.9 的 0.2%。

| # | 地點 | 座標 | 分數 | permafrost | cold | dryness | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|
| 1 | 67 km from McMurdo Station (AQ) | -78.15, 164.15 | 1.0 | 1.00 | 1.00 | 1.00 | permafrost | 否（mcmurdo_dry_valleys 88 km） |
| 2 | 494 km from McMurdo Station (AQ) | -82.25, 163.25 | 1.0 | 1.00 | 1.00 | 1.00 | permafrost | 否（beacon_valley 495 km） |
| 3 | 2641 km from Port-aux-Francais (TF) | -73.05, 66.55 | 1.0 | 1.00 | 1.00 | 1.00 | permafrost | 否（beacon_valley 2387 km） |
| 4 | 398 km from McMurdo Station (AQ) | -74.35, 163.45 | 1.0 | 1.00 | 1.00 | 1.00 | permafrost | 否（mcmurdo_dry_valleys 352 km） |
| 5 | 4547 km from Waitangi (NZ) | -84.85, -176.85 | 1.0 | 1.00 | 1.00 | 1.00 | permafrost | 否（beacon_valley 853 km） |
| 6 | 522 km from McMurdo Station (AQ) | -73.15, 167.15 | 1.0 | 1.00 | 1.00 | 1.00 | permafrost | 否（mcmurdo_dry_valleys 505 km） |
| 7 | 1067 km from Stanley (FK) | -61.15, -54.85 | 1.0 | 1.00 | 1.00 | 1.00 | permafrost | 否（atacama_yungay 4280 km） |
| 8 | 321 km from McMurdo Station (AQ) | -79.95, 156.35 | 1.0 | 1.00 | 1.00 | 1.00 | permafrost | 否（beacon_valley 254 km） |
| 9 | 91 km from Jisegumen (CN) | 34.85, 81.05 | 0.966 | 1.00 | 1.00 | 0.90 | dryness | 否（qaidam_dalangtan 1023 km） |
| 10 | 93 km from Zangguy (CN) | 36.45, 78.85 | 0.966 | 1.00 | 1.00 | 0.90 | dryness | 否（qaidam_dalangtan 1151 km） |

交叉驗證（用面向 水與冰、環境極端 組成）：前 20 名在 100 km 內重疊 30%，全部格子的等級相關 0.678。

### R4 含水礦物辨識

可評分陸地格 1,399,028；分數 ≥ 0.8 的陸地面積 0.1%、≥ 0.9 的 0.0%。

| # | 地點 | 座標 | 分數 | lithology | barrenness | summer_barren | ice_free | mineral_signature | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 260 km from Talnakh (RU) | 69.15, 94.95 | 0.986 | 1.00 | 0.99 | 0.94 | 1.00 | 1.00 | summer_barren | 否（svalbard_bockfjorden 2429 km） |
| 2 | 147 km from Sultanah (SA) | 25.75, 40.05 | 0.972 | 1.00 | 0.87 | 1.00 | 1.00 | 1.00 | barrenness | 否（dallol 1280 km） |
| 3 | 153 km from Kotzebue (US) | 68.25, -161.95 | 0.964 | 1.00 | 0.93 | 0.89 | 1.00 | 1.00 | summer_barren | 否（axel_heiberg_lost_hammer 2328 km） |
| 4 | near Assab (ER) | 12.85, 42.65 | 0.948 | 1.00 | 0.77 | 1.00 | 1.00 | 1.00 | barrenness | 否（dallol 297 km） |
| 5 | 85 km from Al 'Ula (SA) | 27.25, 37.45 | 0.938 | 1.00 | 0.73 | 1.00 | 1.00 | 1.00 | barrenness | 否（lake_salda 1357 km） |
| 6 | 120 km from Maralal (KE) | 2.15, 36.45 | 0.936 | 1.00 | 0.72 | 1.00 | 1.00 | 1.00 | barrenness | 否（dallol 1409 km） |
| 7 | 81 km from Puerto Villamil (EC) | -0.25, -91.15 | 0.932 | 1.00 | 0.74 | 1.00 | 1.00 | 0.95 | barrenness | 否（atacama_yungay 3501 km） |
| 8 | near Djibouti (DJ) | 11.55, 43.05 | 0.931 | 1.00 | 0.70 | 1.00 | 1.00 | 1.00 | barrenness | 否（dallol 422 km） |
| 9 | 103 km from Colchani (BO) | -19.95, -67.85 | 0.93 | 0.70 | 0.99 | 1.00 | 1.00 | 1.00 | lithology | 否（atacama_yungay 506 km） |
| 10 | 40 km from Ad Dumayr (SY) | 33.35, 36.95 | 0.928 | 1.00 | 0.69 | 1.00 | 1.00 | 1.00 | barrenness | 否（lake_salda 807 km） |

交叉驗證（用面向 地表物質與裸露 組成）：前 20 名在 100 km 內重疊 10%，全部格子的等級相關 0.694。

### R5 冰河與冰緣地形

可評分陸地格 1,435,234；分數 ≥ 0.8 的陸地面積 0.5%、≥ 0.9 的 0.2%。

| # | 地點 | 座標 | 分數 | permafrost | cold | slope | roughness | barrenness | summer_barren | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1196 km from Kugluktuk (CA) | 78.55, -111.95 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | permafrost | 否（axel_heiberg_lost_hammer 470 km） |
| 2 | 995 km from Khatanga (RU) | 80.85, 97.25 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | permafrost | 否（svalbard_bockfjorden 1467 km） |
| 3 | 1522 km from Vorgashor (RU) | 81.25, 60.45 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（svalbard_bockfjorden 875 km） |
| 4 | 697 km from Deputatsky (RU) | 75.55, 141.85 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（svalbard_bockfjorden 2509 km） |
| 5 | 1273 km from Gjoa Haven (CA) | 80.05, -98.85 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | permafrost | 否（axel_heiberg_lost_hammer 204 km） |
| 6 | 1189 km from Gjoa Haven (CA) | 79.05, -104.85 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | permafrost | 否（axel_heiberg_lost_hammer 308 km） |
| 7 | 1083 km from Gjoa Haven (CA) | 78.35, -97.95 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | slope | 否（axel_heiberg_lost_hammer 187 km） |
| 8 | 243 km from Longyearbyen (SJ) | 80.35, 18.35 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | permafrost | 否（svalbard_bockfjorden 142 km） |
| 9 | 944 km from Kugluktuk (CA) | 76.05, -122.05 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | permafrost | 否（axel_heiberg_lost_hammer 820 km） |
| 10 | 1070 km from Kugluktuk (CA) | 77.45, -115.95 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（axel_heiberg_lost_hammer 604 km） |

交叉驗證（用面向 水與冰、地形 組成）：前 20 名在 100 km 內重疊 0%，全部格子的等級相關 0.615。

### R6 沙塵與近地表氣象

可評分陸地格 1,314,474；分數 ≥ 0.8 的陸地面積 0.0%、≥ 0.9 的 0.0%。

| # | 地點 | 座標 | 分數 | dust | temperature | diurnal_range | dust_season_shape | dust_season_amplitude | temperature_season_shape | temperature_season_amplitude | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | near Kyzyl-Mazhalyk (RU) | 51.05, 90.45 | 0.788 | 0.97 | 0.80 | 0.81 | 0.30 | 0.98 | 0.99 | 1.00 | dust_season_shape | 否（qaidam_dalangtan 1418 km） |
| 2 | near Kosh-Agach (RU) | 49.85, 88.65 | 0.783 | 0.97 | 0.83 | 0.88 | 0.29 | 0.89 | 1.00 | 1.00 | dust_season_shape | 否（qaidam_dalangtan 1303 km） |
| 3 | 40 km from Chernogorsk (RU) | 53.65, 90.75 | 0.78 | 0.97 | 0.77 | 0.74 | 0.33 | 1.00 | 1.00 | 0.98 | dust_season_shape | 否（qaidam_dalangtan 1705 km） |
| 4 | near Turan (RU) | 52.05, 93.65 | 0.779 | 0.99 | 0.86 | 0.69 | 0.30 | 1.00 | 0.99 | 1.00 | dust_season_shape | 否（qaidam_dalangtan 1533 km） |
| 5 | 39 km from Tooromt (MN) | 50.65, 94.05 | 0.777 | 0.95 | 0.83 | 0.88 | 0.25 | 1.00 | 0.98 | 0.99 | dust_season_shape | 否（qaidam_dalangtan 1383 km） |
| 6 | 40 km from Chongshan (CN) | 41.95, 128.55 | 0.777 | 0.94 | 0.77 | 0.72 | 0.38 | 1.00 | 0.99 | 0.87 | dust_season_shape | 否（qaidam_dalangtan 3136 km） |
| 7 | 104 km from Romny (RU) | 51.65, 129.45 | 0.774 | 0.98 | 0.85 | 0.68 | 0.30 | 0.99 | 0.99 | 0.99 | dust_season_shape | 否（qaidam_dalangtan 3271 km） |
| 8 | 88 km from Erenhot (CN) | 42.95, 111.45 | 0.772 | 0.84 | 0.69 | 0.97 | 0.33 | 0.92 | 0.99 | 0.97 | dust_season_shape | 否（qaidam_dalangtan 1741 km） |
| 9 | 78 km from Urzhar (KZ) | 46.45, 82.05 | 0.772 | 0.82 | 0.68 | 0.90 | 0.33 | 1.00 | 0.99 | 1.00 | dust_season_shape | 否（qaidam_dalangtan 1198 km） |
| 10 | 32 km from Erfenzi (CN) | 41.65, 110.75 | 0.772 | 0.83 | 0.72 | 0.89 | 0.35 | 0.93 | 0.99 | 0.95 | dust_season_shape | 否（qaidam_dalangtan 1663 km） |

交叉驗證（用面向 大氣與沙塵、環境極端 組成）：前 20 名在 100 km 內重疊 5%，全部格子的等級相關 0.847。

### 每項測試第 1 名的面向分數（面向 × 測試）

| 測試 | 第 1 名 | 測試分數 | 地形 | 地表物質與裸露 | 環境極端 | 水與冰 | 大氣與沙塵 | 剖面整體 |
|---|---|---|---|---|---|---|---|---|
| R1 | 75 km from Colchani (BO)（-19.95, -67.55） | 1.0 | **1.00** | **0.89** | 0.74 | — | 0.42 | 72.7 |
| R3 | 67 km from McMurdo Station (AQ)（-78.15, 164.15） | 1.0 | 0.88 | 1.00 | **1.00** | **0.58** | 0.42 | 73.5 |
| R4 | 260 km from Talnakh (RU)（69.15, 94.95） | 0.986 | 0.64 | **1.00** | 0.17 | 0.58 | 0.68 | 52.9 |
| R5 | 1196 km from Kugluktuk (CA)（78.55, -111.95） | 1.0 | **1.00** | 1.00 | 0.78 | **0.58** | 0.58 | 76.6 |
| R6 | near Kyzyl-Mazhalyk (RU)（51.05, 90.45） | 0.788 | 0.99 | 0.32 | **0.75** | 0.42 | **0.97** | 62.6 |

粗體 = 這項測試的主要面向。

### 參考用加權總分（ROC 權重，只用適用的測試、重新正規化）

權重：R1 0.455、R3 0.27、R6 0.176、R4 0.068、R5 0.031

| # | 地點 | 座標 | 總分 | R1 | R3 | R6 | R4 | R5 |
|---|---|---|---|---|---|---|---|---|
| 1 | 231 km from Qimantage (CN) | 35.25, 89.95 | 0.819 | 0.98 | 0.88 | 0.62 | 0.35 | 0.97 |
| 2 | 226 km from Qimantage (CN) | 35.95, 88.45 | 0.817 | 0.98 | 0.91 | 0.63 | 0.28 | 0.98 |
| 3 | 34 km from Vilyuysk (RU) | 63.95, 122.15 | 0.796 | 0.86 | 0.83 | 0.70 | 0.52 | 0.86 |
| 4 | 204 km from Cuozheqiangma (CN) | 35.05, 87.05 | 0.794 | 0.96 | 0.83 | 0.64 | 0.30 | 0.91 |
| 5 | 172 km from Pagnag (CN) | 33.65, 90.85 | 0.787 | 0.94 | 0.85 | 0.67 | 0.24 | 0.94 |
| 6 | 220 km from Wutumeiren (CN) | 35.15, 92.05 | 0.783 | 0.92 | 0.85 | 0.66 | 0.28 | 0.90 |
| 7 | 119 km from Qimantage (CN) | 36.35, 90.95 | 0.778 | 0.88 | 0.89 | 0.65 | 0.30 | 0.90 |
| 8 | 158 km from Yeyik (CN) | 35.25, 83.05 | 0.774 | 0.98 | 0.76 | 0.60 | 0.31 | 0.87 |
| 9 | 83 km from Baetov (KG) | 40.55, 75.25 | 0.766 | 0.87 | 0.87 | 0.71 | 0.22 | 0.87 |
| 10 | near Kosh-Agach (RU) | 49.95, 88.65 | 0.758 | 0.85 | 0.78 | 0.77 | 0.31 | 0.78 |

### 已知類比地檢查

標了對應任務的已知類比地，在該測試的全球前百分比中位數（越小越前面）vs 沒標的：

| 測試 | 對應任務 | 有標（n） | 中位數 | 沒標（n） | 中位數 |
|---|---|---|---|---|---|
| R1 | landing、rover | 7 | 37.3% | 13 | 35.2% |
| R3 | isru_base | 6 | 32.6% | 22 | 38.4% |
| R4 | geology | 17 | 15.6% | 2 | 3.5% |
| R5 | geology | 25 | 23.3% | 3 | 23.6% |
| R6 | — | 0 | —% | 26 | 57.5% |
