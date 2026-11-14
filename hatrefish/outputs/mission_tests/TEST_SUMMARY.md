# 測試項目分數（自動產生）

> 產生時間 2026-11-14 15:39，由 `scripts/make_mission_tests.py` 產生；數字以 `outputs/mission_tests/*_tests.json` 為準。
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

可評分陸地格 791,247；分數 ≥ 0.8 的陸地面積 8.6%、≥ 0.9 的 1.4%。

| # | 地點 | 座標 | 分數 | slope | roughness | thermal_inertia | barrenness | ice_free | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 64 km from Jisegumen (CN) | 33.95, 81.45 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | barrenness | 否（qaidam_dalangtan 1038 km） |
| 2 | 110 km from Edd (ER) | 13.25, 40.95 | 0.999 | 1.00 | 0.99 | 1.00 | 1.00 | 1.00 | roughness | 否（dallol 131 km） |
| 3 | 110 km from Cuozheqiangma (CN) | 32.35, 88.05 | 0.998 | 1.00 | 0.99 | 1.00 | 1.00 | 1.00 | roughness | 否（qaidam_dalangtan 741 km） |
| 4 | 282 km from Clyde River (CA) | 69.85, -75.85 | 0.997 | 1.00 | 1.00 | 1.00 | 0.98 | 1.00 | barrenness | 否（haughton_crater 764 km） |
| 5 | 199 km from Qimantage (CN) | 36.05, 88.75 | 0.996 | 1.00 | 1.00 | 1.00 | 0.98 | 1.00 | barrenness | 否（qaidam_dalangtan 362 km） |
| 6 | near Urdgol (MN) | 47.95, 92.35 | 0.994 | 1.00 | 1.00 | 1.00 | 0.97 | 1.00 | barrenness | 否（qaidam_dalangtan 1071 km） |
| 7 | 188 km from Yeyik (CN) | 35.35, 84.55 | 0.992 | 1.00 | 1.00 | 1.00 | 0.96 | 1.00 | barrenness | 否（qaidam_dalangtan 715 km） |
| 8 | 285 km from Qimantage (CN) | 34.75, 90.55 | 0.989 | 1.00 | 1.00 | 1.00 | 0.95 | 1.00 | barrenness | 否（qaidam_dalangtan 410 km） |
| 9 | 130 km from Wutumeiren (CN) | 35.75, 92.95 | 0.988 | 1.00 | 1.00 | 1.00 | 0.95 | 1.00 | barrenness | 否（qaidam_dalangtan 309 km） |
| 10 | 46 km from Zhabu (CN) | 32.95, 83.75 | 0.986 | 1.00 | 1.00 | 1.00 | 0.93 | 1.00 | barrenness | 否（qaidam_dalangtan 932 km） |

交叉驗證（用面向 地形、地表物質與裸露 組成）：前 20 名在 100 km 內重疊 5%，全部格子的等級相關 0.557。

### R4 含水礦物辨識

可評分陸地格 1,391,042；分數 ≥ 0.8 的陸地面積 0.2%、≥ 0.9 的 0.0%。

| # | 地點 | 座標 | 分數 | lithology | barrenness | ice_free | mineral_signature | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 145 km from Haines Junction (CA) | 59.45, -137.45 | 0.973 | 0.90 | 1.00 | 1.00 | 1.00 | lithology | 否（pavilion_lake 1374 km） |
| 2 | 521 km from Iskateley (RU) | 72.35, 54.35 | 0.97 | 0.90 | 0.98 | 1.00 | 1.00 | lithology | 否（svalbard_bockfjorden 1317 km） |
| 3 | 504 km from Clyde River (CA) | 72.05, -81.85 | 0.967 | 0.90 | 0.97 | 1.00 | 1.00 | lithology | 否（haughton_crater 443 km） |
| 4 | 1049 km from Gjoa Haven (CA) | 78.05, -97.05 | 0.965 | 0.90 | 0.98 | 1.00 | 0.98 | lithology | 否（axel_heiberg_lost_hammer 189 km） |
| 5 | 846 km from Gjoa Haven (CA) | 76.15, -99.65 | 0.957 | 0.90 | 0.93 | 1.00 | 1.00 | lithology | 否（haughton_crater 285 km） |
| 6 | 211 km from Tok (US) | 61.45, -142.55 | 0.957 | 0.90 | 0.93 | 1.00 | 1.00 | lithology | 否（pavilion_lake 1731 km） |
| 7 | 847 km from Kugluktuk (CA) | 75.05, -107.35 | 0.95 | 0.90 | 0.91 | 1.00 | 1.00 | lithology | 否（haughton_crater 501 km） |
| 8 | 332 km from Clyde River (CA) | 71.55, -77.15 | 0.95 | 0.90 | 1.00 | 1.00 | 0.91 | lithology | 否（haughton_crater 580 km） |
| 9 | 268 km from Okhotsk (RU) | 61.75, 142.55 | 0.949 | 0.90 | 0.90 | 1.00 | 1.00 | lithology | 否（svalbard_bockfjorden 3981 km） |
| 10 | 824 km from Gjoa Haven (CA) | 75.55, -87.15 | 0.946 | 0.80 | 1.00 | 1.00 | 1.00 | lithology | 否（haughton_crater 73 km） |

交叉驗證（用面向 地表物質與裸露 組成）：前 20 名在 100 km 內重疊 5%，全部格子的等級相關 0.719。

### R6 沙塵與近地表氣象

可評分陸地格 1,441,481；分數 ≥ 0.8 的陸地面積 0.0%、≥ 0.9 的 0.0%。

| # | 地點 | 座標 | 分數 | dust | temperature | diurnal_range | dust_season_shape | dust_season_amplitude | temperature_season_shape | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | near Zuogaiduoma (CN) | 35.05, 103.25 | 0.738 | 0.88 | 0.73 | 0.94 | 0.28 | 0.98 | 0.97 | dust_season_shape | 否（qaidam_dalangtan 1094 km） |
| 2 | 104 km from Laochenglu (CN) | 42.05, 89.55 | 0.734 | 0.94 | 0.57 | 0.98 | 0.43 | 0.71 | 0.97 | dust_season_shape | 否（qaidam_dalangtan 451 km） |
| 3 | near Vilaflor (ES) | 28.25, -16.65 | 0.731 | 0.91 | 0.54 | 0.92 | 0.38 | 0.91 | 0.98 | dust_season_shape | 否（lanzarote 307 km） |
| 4 | near Malah (SY) | 32.55, 36.85 | 0.73 | 0.89 | 0.50 | 0.95 | 0.36 | 1.00 | 0.98 | dust_season_shape | 否（lake_salda 857 km） |
| 5 | 68 km from A'yi Take (CN) | 39.05, 74.65 | 0.728 | 1.00 | 0.78 | 0.96 | 0.21 | 0.97 | 0.98 | dust_season_shape | 否（qaidam_dalangtan 1477 km） |
| 6 | near Huazangsi (CN) | 36.95, 103.35 | 0.727 | 0.92 | 0.71 | 0.98 | 0.26 | 0.92 | 0.96 | dust_season_shape | 否（qaidam_dalangtan 1039 km） |
| 7 | 32 km from Nanyuki (KE) | -0.05, 37.35 | 0.726 | 0.55 | 0.65 | 0.78 | 0.74 | 0.95 | 0.74 | dust | 否（dallol 1622 km） |
| 8 | 39 km from Zhonghualu (CN) | 35.95, 104.55 | 0.724 | 0.90 | 0.66 | 0.87 | 0.30 | 0.95 | 0.96 | dust_season_shape | 否（qaidam_dalangtan 1171 km） |
| 9 | near Kangal (TR) | 39.15, 37.35 | 0.719 | 0.81 | 0.65 | 0.88 | 0.30 | 0.98 | 0.98 | dust_season_shape | 否（lake_salda 692 km） |
| 10 | near Magaozhuang (CN) | 36.85, 106.45 | 0.718 | 0.92 | 0.64 | 0.91 | 0.30 | 0.88 | 0.96 | dust_season_shape | 否（qaidam_dalangtan 1311 km） |

交叉驗證（用面向 大氣與沙塵、環境極端 組成）：前 20 名在 100 km 內重疊 5%，全部格子的等級相關 0.741。

### 每項測試第 1 名的面向分數（面向 × 測試）

| 測試 | 第 1 名 | 測試分數 | 地形 | 地表物質與裸露 | 環境極端 | 水與冰 | 大氣與沙塵 | 剖面整體 |
|---|---|---|---|---|---|---|---|---|
| R1 | 64 km from Jisegumen (CN)（33.95, 81.45） | 1.0 | **1.00** | **0.82** | 0.86 | 0.01 | 0.71 | 34.7 |
| R4 | 145 km from Haines Junction (CA)（59.45, -137.45） | 0.973 | 0.01 | **0.95** | 0.11 | 1.00 | 0.34 | 20.4 |
| R6 | near Zuogaiduoma (CN)（35.05, 103.25） | 0.738 | 0.97 | 0.06 | **0.54** | 1.00 | **0.88** | 48.0 |

粗體 = 這項測試的主要面向。

### 參考用加權總分（ROC 權重，只用適用的測試、重新正規化）

權重：R1 0.651、R6 0.252、R4 0.097

| # | 地點 | 座標 | 總分 | R1 | R6 | R4 |
|---|---|---|---|---|---|---|
| 1 | near Naranbulag (MN) | 49.35, 92.75 | 0.835 | 0.93 | 0.64 | 0.82 |
| 2 | 76 km from Milford (US) | 39.05, -113.25 | 0.831 | 0.96 | 0.56 | 0.84 |
| 3 | near Kurchum (KZ) | 48.65, 83.55 | 0.829 | 0.94 | 0.57 | 0.89 |
| 4 | 34 km from Yuli (CN) | 41.55, 86.55 | 0.827 | 0.97 | 0.66 | 0.50 |
| 5 | near Qarah (SY) | 34.25, 36.75 | 0.824 | 0.89 | 0.70 | 0.77 |
| 6 | 64 km from Jisegumen (CN) | 33.95, 81.45 | 0.822 | 1.00 | 0.59 | 0.53 |
| 7 | 67 km from Urdgol (MN) | 47.85, 93.55 | 0.821 | 0.90 | 0.64 | 0.85 |
| 8 | near Yamansu (CN) | 41.35, 79.15 | 0.818 | 0.96 | 0.65 | 0.49 |
| 9 | 113 km from Cuozheqiangma (CN) | 33.15, 88.95 | 0.818 | 0.99 | 0.58 | 0.55 |
| 10 | 130 km from Wutumeiren (CN) | 35.75, 92.95 | 0.816 | 0.99 | 0.60 | 0.50 |

### 已知類比地檢查

標了對應任務的已知類比地，在該測試的全球前百分比中位數（越小越前面）vs 沒標的：

| 測試 | 對應任務 | 有標（n） | 中位數 | 沒標（n） | 中位數 |
|---|---|---|---|---|---|
| R1 | landing、rover | 7 | 71.1% | 13 | 30.1% |
| R4 | geology | 17 | 31.2% | 2 | 17.0% |
| R6 | — | 0 | —% | 28 | 44.0% |

## Gale Crater（-5.4, 137.8）

測試狀態：R1 已評分；R2 無法評估；R3 不適用（目標沒有可靠的冰訊號）；R4 已評分；R5 不適用（目標沒有可靠的冰訊號）；R6 已評分。冰訊號 clip(Ci, 0, 1) = 0.059（R3、R5 需要 ≥ 0.1）。

### R1 著陸地表條件

可評分陸地格 791,247；分數 ≥ 0.8 的陸地面積 2.2%、≥ 0.9 的 0.4%。

| # | 地點 | 座標 | 分數 | slope | roughness | thermal_inertia | barrenness | ice_free | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 79 km from A'yi Take (CN) | 39.15, 74.55 | 0.989 | 0.99 | 0.99 | 1.00 | 0.96 | 1.00 | barrenness | 否（qaidam_dalangtan 1485 km） |
| 2 | near Jiajuedibu (CN) | 31.05, 88.55 | 0.986 | 1.00 | 0.94 | 1.00 | 0.99 | 1.00 | roughness | 否（qaidam_dalangtan 858 km） |
| 3 | 79 km from Xagmakajor (CN) | 31.65, 83.15 | 0.984 | 1.00 | 1.00 | 1.00 | 0.92 | 1.00 | barrenness | 否（qaidam_dalangtan 1073 km） |
| 4 | 162 km from Qimantage (CN) | 35.85, 90.35 | 0.984 | 1.00 | 0.99 | 1.00 | 0.93 | 1.00 | barrenness | 否（qaidam_dalangtan 300 km） |
| 5 | 173 km from Mazongshan (CN) | 43.35, 97.35 | 0.973 | 0.98 | 1.00 | 1.00 | 0.89 | 1.00 | barrenness | 否（qaidam_dalangtan 734 km） |
| 6 | 154 km from Cochrane (CL) | -48.55, -71.85 | 0.973 | 0.91 | 0.99 | 1.00 | 0.97 | 1.00 | slope | 否（atacama_yungay 2726 km） |
| 7 | near Antofagasta (CL) | -23.75, -70.45 | 0.971 | 1.00 | 1.00 | 1.00 | 0.87 | 1.00 | barrenness | 否（atacama_yungay 65 km） |
| 8 | near Minas de Marcona (PE) | -15.15, -75.25 | 0.97 | 1.00 | 1.00 | 1.00 | 0.86 | 1.00 | barrenness | 否（atacama_yungay 1139 km） |
| 9 | 109 km from Yeyik (CN) | 36.55, 84.45 | 0.97 | 1.00 | 0.88 | 1.00 | 0.97 | 1.00 | roughness | 否（qaidam_dalangtan 667 km） |
| 10 | 75 km from Khur (IR) | 33.35, 54.45 | 0.969 | 0.99 | 1.00 | 1.00 | 0.86 | 1.00 | barrenness | 否（dhofar_amadee18 1694 km） |

交叉驗證（用面向 地形、地表物質與裸露 組成）：前 20 名在 100 km 內重疊 0%，全部格子的等級相關 0.677。

### R4 含水礦物辨識

可評分陸地格 1,434,366；分數 ≥ 0.8 的陸地面積 5.5%、≥ 0.9 的 0.3%。

| # | 地點 | 座標 | 分數 | lithology | barrenness | ice_free | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|
| 1 | 167 km from Torghay (KZ) | 48.15, 63.15 | 0.965 | 0.90 | 1.00 | 1.00 | lithology | 否（qaidam_dalangtan 2536 km） |
| 2 | 38 km from Aswan (EG) | 23.75, 32.85 | 0.965 | 0.90 | 1.00 | 1.00 | lithology | 否（dallol 1315 km） |
| 3 | 847 km from Gjoa Haven (CA) | 76.15, -99.85 | 0.965 | 0.90 | 1.00 | 1.00 | lithology | 否（haughton_crater 291 km） |
| 4 | 900 km from Clyde River (CA) | 77.65, -82.55 | 0.965 | 0.90 | 1.00 | 1.00 | lithology | 否（axel_heiberg_lost_hammer 234 km） |
| 5 | 859 km from Rankin Inlet (CA) | 70.15, -85.95 | 0.965 | 0.90 | 1.00 | 1.00 | lithology | 否（haughton_crater 594 km） |
| 6 | 158 km from Maqian (CN) | 33.05, 89.85 | 0.965 | 0.90 | 1.00 | 1.00 | lithology | 否（qaidam_dalangtan 610 km） |
| 7 | 120 km from Jisegumen (CN) | 35.05, 80.25 | 0.965 | 0.90 | 1.00 | 1.00 | lithology | 否（qaidam_dalangtan 1081 km） |
| 8 | 145 km from Haines Junction (CA) | 59.45, -137.45 | 0.965 | 0.90 | 1.00 | 1.00 | lithology | 否（pavilion_lake 1374 km） |
| 9 | 37 km from Khandud (AF) | 36.75, 72.65 | 0.965 | 0.90 | 1.00 | 1.00 | lithology | 否（kachchh_matanumadh 1510 km） |
| 10 | 332 km from Clyde River (CA) | 71.55, -77.15 | 0.965 | 0.90 | 1.00 | 1.00 | lithology | 否（haughton_crater 580 km） |

交叉驗證（用面向 地表物質與裸露 組成）：前 20 名在 100 km 內重疊 5%，全部格子的等級相關 0.892。

### R6 沙塵與近地表氣象

可評分陸地格 1,441,481；分數 ≥ 0.8 的陸地面積 10.5%、≥ 0.9 的 0.6%。

| # | 地點 | 座標 | 分數 | dust | temperature | diurnal_range | dust_season_shape | dust_season_amplitude | temperature_season_shape | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 80 km from Hoit Taria (CN) | 38.05, 96.95 | 0.947 | 1.00 | 0.87 | 0.96 | 0.95 | 1.00 | 0.91 | temperature | 否（qaidam_dalangtan 462 km） |
| 2 | 185 km from Qimantage (CN) | 36.15, 88.85 | 0.946 | 0.99 | 0.87 | 0.96 | 0.97 | 0.98 | 0.90 | temperature | 否（qaidam_dalangtan 348 km） |
| 3 | 129 km from Thang (IN) | 36.05, 77.15 | 0.945 | 0.99 | 0.88 | 0.99 | 0.95 | 0.99 | 0.88 | temperature | 否（qaidam_dalangtan 1309 km） |
| 4 | 166 km from Koramlik (CN) | 36.25, 87.05 | 0.944 | 0.99 | 0.86 | 0.98 | 0.97 | 0.98 | 0.89 | temperature | 否（qaidam_dalangtan 470 km） |
| 5 | 153 km from Aqqan (CN) | 35.95, 85.15 | 0.939 | 0.99 | 0.85 | 0.98 | 0.98 | 0.96 | 0.88 | temperature | 否（qaidam_dalangtan 635 km） |
| 6 | 148 km from Wutumeiren (CN) | 35.75, 92.35 | 0.937 | 0.99 | 0.81 | 0.97 | 0.95 | 1.00 | 0.91 | temperature | 否（qaidam_dalangtan 293 km） |
| 7 | 80 km from Yeyik (CN) | 35.95, 83.35 | 0.937 | 0.94 | 0.87 | 0.98 | 0.97 | 0.97 | 0.89 | temperature | 否（qaidam_dalangtan 783 km） |
| 8 | 97 km from Dagur (CN) | 35.55, 95.65 | 0.937 | 0.99 | 0.83 | 0.97 | 0.95 | 0.99 | 0.90 | temperature | 否（qaidam_dalangtan 470 km） |
| 9 | 163 km from Waxxari (CN) | 37.35, 88.05 | 0.937 | 0.96 | 0.83 | 0.99 | 0.97 | 1.00 | 0.90 | temperature | 否（qaidam_dalangtan 336 km） |
| 10 | 141 km from Nur (CN) | 35.15, 81.65 | 0.936 | 0.98 | 0.88 | 0.98 | 0.97 | 0.92 | 0.90 | temperature | 否（qaidam_dalangtan 960 km） |

交叉驗證（用面向 大氣與沙塵、環境極端 組成）：前 20 名在 100 km 內重疊 65%，全部格子的等級相關 0.81。

### 每項測試第 1 名的面向分數（面向 × 測試）

| 測試 | 第 1 名 | 測試分數 | 地形 | 地表物質與裸露 | 環境極端 | 水與冰 | 大氣與沙塵 | 剖面整體 |
|---|---|---|---|---|---|---|---|---|
| R1 | 79 km from A'yi Take (CN)（39.15, 74.55） | 0.989 | **0.99** | **0.52** | 0.79 | 0.06 | 0.87 | 46.1 |
| R4 | 167 km from Torghay (KZ)（48.15, 63.15） | 0.965 | 0.13 | **0.91** | 0.76 | 0.94 | 1.00 | 60.7 |
| R6 | 80 km from Hoit Taria (CN)（38.05, 96.95） | 0.947 | 0.22 | 0.26 | **0.79** | 0.06 | **1.00** | 30.4 |

粗體 = 這項測試的主要面向。

### 參考用加權總分（ROC 權重，只用適用的測試、重新正規化）

權重：R1 0.651、R6 0.252、R4 0.097

| # | 地點 | 座標 | 總分 | R1 | R6 | R4 |
|---|---|---|---|---|---|---|
| 1 | 273 km from Cuozheqiangma (CN) | 35.75, 88.05 | 0.939 | 0.96 | 0.91 | 0.90 |
| 2 | 144 km from Wutumeiren (CN) | 36.15, 91.85 | 0.937 | 0.95 | 0.91 | 0.90 |
| 3 | 99 km from Jisegumen (CN) | 34.95, 80.85 | 0.928 | 0.95 | 0.88 | 0.91 |
| 4 | near Gahe (CN) | 38.55, 97.55 | 0.925 | 0.94 | 0.89 | 0.90 |
| 5 | 142 km from Qimantage (CN) | 36.05, 90.05 | 0.923 | 0.93 | 0.91 | 0.90 |
| 6 | 102 km from Barkol (CN) | 43.55, 91.75 | 0.922 | 0.95 | 0.86 | 0.89 |
| 7 | 79 km from Xagmakajor (CN) | 31.65, 83.15 | 0.92 | 0.98 | 0.79 | 0.86 |
| 8 | 96 km from Leh (IN) | 33.85, 78.55 | 0.92 | 0.97 | 0.83 | 0.85 |
| 9 | 102 km from Cuozheqiangma (CN) | 32.45, 88.15 | 0.919 | 0.96 | 0.81 | 0.92 |
| 10 | near Dabancheng (CN) | 43.35, 88.05 | 0.918 | 0.95 | 0.83 | 0.91 |

### 已知類比地檢查

標了對應任務的已知類比地，在該測試的全球前百分比中位數（越小越前面）vs 沒標的：

| 測試 | 對應任務 | 有標（n） | 中位數 | 沒標（n） | 中位數 |
|---|---|---|---|---|---|
| R1 | landing、rover | 7 | 44.5% | 13 | 20.5% |
| R4 | geology | 24 | 40.2% | 3 | 10.2% |
| R6 | — | 0 | —% | 28 | 34.9% |

## Arcadia Planitia (shallow ground ice)（47.2, -175.7）

測試狀態：R1 已評分；R2 無法評估；R3 已評分；R4 已評分；R5 已評分；R6 已評分。冰訊號 clip(Ci, 0, 1) = 0.526（R3、R5 需要 ≥ 0.1）。

### R1 著陸地表條件

可評分陸地格 791,247；分數 ≥ 0.8 的陸地面積 9.2%、≥ 0.9 的 1.5%。

| # | 地點 | 座標 | 分數 | slope | roughness | thermal_inertia | barrenness | ice_free | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 70 km from Colchani (BO) | -20.55, -67.55 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | slope | 否（atacama_yungay 462 km） |
| 2 | 77 km from Antofagasta de la Sierra (AR) | -25.45, -67.05 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | slope | 否（atacama_yungay 327 km） |
| 3 | 142 km from Jisegumen (CN) | 35.15, 79.95 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | slope | 否（qaidam_dalangtan 1102 km） |
| 4 | Pilot Valley paleolake playa (Utah) | 41.05, -113.65 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | slope | 是 |
| 5 | near Xungmai (CN) | 31.55, 89.15 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（qaidam_dalangtan 788 km） |
| 6 | 57 km from Xitieshan (CN) | 37.05, 94.95 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（qaidam_dalangtan 322 km） |
| 7 | 44 km from Cruz de Machacamarca (BO) | -19.25, -68.25 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | slope | 否（atacama_yungay 564 km） |
| 8 | 36 km from Urho (CN) | 45.85, 85.95 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | slope | 否（qaidam_dalangtan 960 km） |
| 9 | 40 km from Dostyq (KZ) | 44.95, 82.75 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | slope | 否（qaidam_dalangtan 1043 km） |
| 10 | 88 km from Turkmenbasy (TM) | 40.75, 53.35 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | slope | 否（lake_salda 2065 km） |

交叉驗證（用面向 地形、地表物質與裸露 組成）：前 20 名在 100 km 內重疊 5%，全部格子的等級相關 0.541。

### R3 淺層地下冰

可評分陸地格 1,434,064；分數 ≥ 0.8 的陸地面積 2.5%、≥ 0.9 的 0.2%。

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
| 9 | 93 km from Guma (CN) | 36.85, 77.85 | 0.969 | 1.00 | 1.00 | 0.91 | dryness | 否（qaidam_dalangtan 1228 km） |
| 10 | 77 km from Jisegumen (CN) | 34.75, 80.85 | 0.968 | 1.00 | 1.00 | 0.91 | dryness | 否（qaidam_dalangtan 1045 km） |

交叉驗證（用面向 水與冰、環境極端 組成）：前 20 名在 100 km 內重疊 20%，全部格子的等級相關 0.653。

### R4 含水礦物辨識

可評分陸地格 1,391,042；分數 ≥ 0.8 的陸地面積 0.1%、≥ 0.9 的 0.0%。

| # | 地點 | 座標 | 分數 | lithology | barrenness | ice_free | mineral_signature | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 272 km from Talnakh (RU) | 69.15, 95.25 | 0.995 | 1.00 | 0.98 | 1.00 | 1.00 | barrenness | 否（svalbard_bockfjorden 2435 km） |
| 2 | 135 km from Antofagasta de la Sierra (AR) | -25.05, -68.15 | 0.964 | 1.00 | 0.86 | 1.00 | 1.00 | barrenness | 否（atacama_yungay 209 km） |
| 3 | 473 km from Rankin Inlet (CA) | 67.05, -91.15 | 0.962 | 1.00 | 0.85 | 1.00 | 1.00 | barrenness | 否（haughton_crater 928 km） |
| 4 | 88 km from Tigil' (RU) | 57.35, 159.95 | 0.962 | 1.00 | 0.90 | 1.00 | 0.95 | barrenness | 否（axel_heiberg_lost_hammer 4183 km） |
| 5 | 90 km from Haines Junction (CA) | 59.95, -137.75 | 0.953 | 1.00 | 0.83 | 1.00 | 1.00 | barrenness | 否（pavilion_lake 1421 km） |
| 6 | 328 km from Iqaluit (CA) | 61.65, -73.05 | 0.942 | 1.00 | 0.86 | 1.00 | 0.91 | barrenness | 否（haughton_crater 1656 km） |
| 7 | 132 km from Talnakh (RU) | 69.95, 91.55 | 0.937 | 1.00 | 0.77 | 1.00 | 1.00 | barrenness | 否（svalbard_bockfjorden 2286 km） |
| 8 | 120 km from Maralal (KE) | 2.15, 36.45 | 0.931 | 1.00 | 0.75 | 1.00 | 1.00 | barrenness | 否（dallol 1409 km） |
| 9 | 58 km from Valdez (US) | 61.65, -146.35 | 0.931 | 1.00 | 0.75 | 1.00 | 1.00 | barrenness | 否（pavilion_lake 1916 km） |
| 10 | 36 km from El Calafate (AR) | -50.65, -72.15 | 0.919 | 1.00 | 0.75 | 1.00 | 0.95 | barrenness | 否（atacama_yungay 2961 km） |

交叉驗證（用面向 地表物質與裸露 組成）：前 20 名在 100 km 內重疊 10%，全部格子的等級相關 0.453。

### R5 冰河與冰緣地形

可評分陸地格 1,435,231；分數 ≥ 0.8 的陸地面積 1.9%、≥ 0.9 的 0.8%。

| # | 地點 | 座標 | 分數 | permafrost | cold | slope | roughness | barrenness | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1205 km from Kugluktuk (CA) | 78.55, -109.45 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | slope | 否（axel_heiberg_lost_hammer 417 km） |
| 2 | 982 km from Khatanga (RU) | 80.75, 97.75 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（svalbard_bockfjorden 1481 km） |
| 3 | 1522 km from Vorgashor (RU) | 81.25, 60.45 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（svalbard_bockfjorden 875 km） |
| 4 | 731 km from Deputatsky (RU) | 75.85, 142.25 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（svalbard_bockfjorden 2483 km） |
| 5 | 1273 km from Gjoa Haven (CA) | 80.05, -98.85 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | permafrost | 否（axel_heiberg_lost_hammer 204 km） |
| 6 | 1049 km from Gjoa Haven (CA) | 78.05, -97.25 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | slope | 否（axel_heiberg_lost_hammer 193 km） |
| 7 | 797 km from Khatanga (RU) | 79.15, 102.55 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | permafrost | 否（svalbard_bockfjorden 1668 km） |
| 8 | 982 km from Kugluktuk (CA) | 76.65, -116.05 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | permafrost | 否（axel_heiberg_lost_hammer 655 km） |
| 9 | 292 km from Gjoa Haven (CA) | 70.25, -101.75 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | permafrost | 否（haughton_crater 692 km） |
| 10 | 674 km from Kugluktuk (CA) | 73.15, -106.35 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | barrenness | 否（haughton_crater 558 km） |

交叉驗證（用面向 水與冰、地形 組成）：前 20 名在 100 km 內重疊 0%，全部格子的等級相關 0.584。

### R6 沙塵與近地表氣象

可評分陸地格 1,441,481；分數 ≥ 0.8 的陸地面積 0.0%、≥ 0.9 的 0.0%。

| # | 地點 | 座標 | 分數 | dust | temperature | diurnal_range | dust_season_shape | dust_season_amplitude | temperature_season_shape | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | near Patambuco (PE) | -14.45, -69.75 | 0.775 | 0.64 | 0.67 | 0.99 | 0.78 | 0.96 | 0.69 | dust | 否（atacama_yungay 1071 km） |
| 2 | 88 km from Erenhot (CN) | 42.95, 111.45 | 0.767 | 0.66 | 0.69 | 0.95 | 0.48 | 0.99 | 0.99 | dust_season_shape | 否（qaidam_dalangtan 1741 km） |
| 3 | near Huarina (BO) | -16.15, -68.55 | 0.766 | 0.62 | 0.66 | 0.95 | 0.73 | 0.91 | 0.78 | dust | 否（atacama_yungay 893 km） |
| 4 | 55 km from Galutu (CN) | 38.45, 108.25 | 0.765 | 0.62 | 0.66 | 0.94 | 0.52 | 0.99 | 1.00 | dust_season_shape | 否（qaidam_dalangtan 1443 km） |
| 5 | 60 km from Dostyq (KZ) | 44.75, 82.75 | 0.764 | 0.59 | 0.66 | 0.89 | 0.58 | 0.99 | 0.99 | dust_season_shape | 否（qaidam_dalangtan 1029 km） |
| 6 | 81 km from Xin Bulag (CN) | 42.95, 113.65 | 0.764 | 0.68 | 0.71 | 0.88 | 0.48 | 0.98 | 0.99 | dust_season_shape | 否（qaidam_dalangtan 1918 km） |
| 7 | 32 km from Erfenzi (CN) | 41.65, 110.75 | 0.764 | 0.65 | 0.72 | 0.89 | 0.49 | 0.99 | 0.99 | dust_season_shape | 否（qaidam_dalangtan 1663 km） |
| 8 | near Huazangsi (CN) | 37.05, 103.45 | 0.763 | 0.60 | 0.71 | 0.98 | 0.51 | 0.93 | 1.00 | dust_season_shape | 否（qaidam_dalangtan 1046 km） |
| 9 | near Hami (CN) | 42.85, 93.15 | 0.761 | 0.59 | 0.61 | 0.98 | 0.56 | 1.00 | 1.00 | dust_season_shape | 否（qaidam_dalangtan 518 km） |
| 10 | 66 km from Toksun (CN) | 42.25, 88.95 | 0.761 | 0.49 | 0.61 | 0.95 | 0.69 | 1.00 | 1.00 | dust | 否（qaidam_dalangtan 493 km） |

交叉驗證（用面向 大氣與沙塵、環境極端 組成）：前 20 名在 100 km 內重疊 0%，全部格子的等級相關 0.577。

### 每項測試第 1 名的面向分數（面向 × 測試）

| 測試 | 第 1 名 | 測試分數 | 地形 | 地表物質與裸露 | 環境極端 | 水與冰 | 大氣與沙塵 | 剖面整體 |
|---|---|---|---|---|---|---|---|---|
| R1 | 70 km from Colchani (BO)（-20.55, -67.55） | 1.0 | **1.00** | **0.81** | 0.75 | — | 0.61 | 78.1 |
| R3 | 67 km from McMurdo Station (AQ)（-78.15, 164.15） | 1.0 | 0.88 | 1.00 | **1.00** | **0.53** | 0.60 | 77.3 |
| R4 | 272 km from Talnakh (RU)（69.15, 95.25） | 0.995 | 0.31 | **0.99** | 0.18 | 0.53 | 0.85 | 47.6 |
| R5 | 1205 km from Kugluktuk (CA)（78.55, -109.45） | 1.0 | **1.00** | 1.00 | 0.79 | **0.53** | 0.76 | 79.5 |
| R6 | near Patambuco (PE)（-14.45, -69.75） | 0.775 | 0.06 | 0.10 | **0.54** | — | **0.64** | 21.5 |

粗體 = 這項測試的主要面向。

### 參考用加權總分（ROC 權重，只用適用的測試、重新正規化）

權重：R1 0.455、R3 0.27、R6 0.176、R4 0.068、R5 0.031

| # | 地點 | 座標 | 總分 | R1 | R3 | R6 | R4 | R5 |
|---|---|---|---|---|---|---|---|---|
| 1 | 236 km from Myaundzha (RU) | 65.15, 146.55 | 0.814 | 0.92 | 0.84 | 0.61 | 0.67 | 0.91 |
| 2 | 194 km from Qimantage (CN) | 35.75, 89.35 | 0.805 | 0.97 | 0.90 | 0.59 | 0.31 | 0.97 |
| 3 | 271 km from Ust-Nera (RU) | 62.15, 142.55 | 0.803 | 0.95 | 0.76 | 0.63 | 0.57 | 0.94 |
| 4 | 254 km from Deputatsky (RU) | 67.05, 140.85 | 0.799 | 0.89 | 0.84 | 0.61 | 0.64 | 0.88 |
| 5 | 151 km from Jisegumen (CN) | 34.45, 82.35 | 0.797 | 0.98 | 0.95 | 0.61 | 0.18 | 0.97 |
| 6 | 237 km from Qiangma (CN) | 34.05, 90.25 | 0.797 | 0.91 | 0.85 | 0.65 | 0.40 | 0.89 |
| 7 | 79 km from Myaundzha (RU) | 63.75, 146.95 | 0.793 | 0.91 | 0.77 | 0.63 | 0.60 | 0.89 |
| 8 | 198 km from Qimantage (CN) | 35.65, 91.15 | 0.79 | 0.97 | 0.89 | 0.63 | 0.20 | 0.97 |
| 9 | 436 km from Rankin Inlet (CA) | 64.05, -83.75 | 0.787 | 0.96 | 0.77 | 0.51 | 0.62 | 0.96 |
| 10 | 74 km from Gahe (CN) | 38.15, 97.45 | 0.786 | 0.94 | 0.89 | 0.66 | 0.22 | 0.93 |

### 已知類比地檢查

標了對應任務的已知類比地，在該測試的全球前百分比中位數（越小越前面）vs 沒標的：

| 測試 | 對應任務 | 有標（n） | 中位數 | 沒標（n） | 中位數 |
|---|---|---|---|---|---|
| R1 | landing、rover | 7 | 79.1% | 13 | 52.8% |
| R3 | isru_base | 6 | 33.6% | 22 | 39.2% |
| R4 | geology | 17 | 28.1% | 2 | 37.7% |
| R5 | geology | 25 | 36.5% | 3 | 36.6% |
| R6 | — | 0 | —% | 28 | 46.2% |

## Oxia Planum (ExoMars Rosalind Franklin landing site)（18.2, -24.55）

測試狀態：R1 已評分；R2 無法評估；R3 不適用（目標沒有可靠的冰訊號）；R4 已評分；R5 不適用（目標沒有可靠的冰訊號）；R6 已評分。冰訊號 clip(Ci, 0, 1) = 0.0（R3、R5 需要 ≥ 0.1）。

### R1 著陸地表條件

可評分陸地格 791,247；分數 ≥ 0.8 的陸地面積 9.7%、≥ 0.9 的 1.7%。

| # | 地點 | 座標 | 分數 | slope | roughness | thermal_inertia | barrenness | ice_free | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | near Mynaral (KZ) | 45.45, 73.75 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（qaidam_dalangtan 1676 km） |
| 2 | 76 km from Xungmai (CN) | 31.95, 88.65 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | slope | 否（qaidam_dalangtan 761 km） |
| 3 | 83 km from Zhabu (CN) | 33.35, 84.15 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（qaidam_dalangtan 875 km） |
| 4 | 117 km from Xagmakajor (CN) | 32.55, 82.35 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（qaidam_dalangtan 1060 km） |
| 5 | near `En Boqeq (IL) | 31.25, 35.45 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（lake_salda 878 km） |
| 6 | 160 km from Yeyik (CN) | 35.25, 82.95 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（qaidam_dalangtan 848 km） |
| 7 | 158 km from Maqian (CN) | 33.05, 89.85 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | slope | 否（qaidam_dalangtan 610 km） |
| 8 | 77 km from Antofagasta de la Sierra (AR) | -25.45, -67.05 | 0.999 | 1.00 | 0.99 | 1.00 | 1.00 | 1.00 | roughness | 否（atacama_yungay 327 km） |
| 9 | 117 km from Qimantage (CN) | 37.55, 89.05 | 0.999 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（qaidam_dalangtan 246 km） |
| 10 | 170 km from Turkmenbasy (TM) | 41.55, 52.85 | 0.998 | 1.00 | 0.99 | 1.00 | 1.00 | 1.00 | roughness | 否（lake_salda 2029 km） |

交叉驗證（用面向 地形、地表物質與裸露 組成）：前 20 名在 100 km 內重疊 10%，全部格子的等級相關 0.642。

### R4 含水礦物辨識

可評分陸地格 1,434,366；分數 ≥ 0.8 的陸地面積 2.4%、≥ 0.9 的 0.1%。

| # | 地點 | 座標 | 分數 | lithology | barrenness | ice_free | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|
| 1 | 170 km from Turkmenbasy (TM) | 41.55, 52.85 | 0.928 | 0.80 | 1.00 | 1.00 | lithology | 否（lake_salda 2029 km） |
| 2 | near Mynaral (KZ) | 45.45, 73.75 | 0.928 | 0.80 | 1.00 | 1.00 | lithology | 否（qaidam_dalangtan 1676 km） |
| 3 | 156 km from Beyneu (KZ) | 45.65, 57.15 | 0.928 | 0.80 | 1.00 | 1.00 | lithology | 否（lake_salda 2440 km） |
| 4 | 83 km from Zhabu (CN) | 33.35, 84.15 | 0.928 | 0.80 | 1.00 | 1.00 | lithology | 否（qaidam_dalangtan 875 km） |
| 5 | 117 km from Xagmakajor (CN) | 32.55, 82.35 | 0.928 | 0.80 | 1.00 | 1.00 | lithology | 否（qaidam_dalangtan 1060 km） |
| 6 | 42 km from Maintang (CN) | 31.75, 89.55 | 0.928 | 0.80 | 1.00 | 1.00 | lithology | 否（qaidam_dalangtan 757 km） |
| 7 | 110 km from Cuozheqiangma (CN) | 32.35, 88.05 | 0.928 | 0.80 | 1.00 | 1.00 | lithology | 否（qaidam_dalangtan 741 km） |
| 8 | 58 km from Colchani (BO) | -20.65, -67.35 | 0.928 | 0.80 | 1.00 | 1.00 | lithology | 否（atacama_yungay 464 km） |
| 9 | 966 km from Vorgashor (RU) | 76.25, 61.75 | 0.928 | 0.80 | 1.00 | 1.00 | lithology | 否（svalbard_bockfjorden 1148 km） |
| 10 | 64 km from Jisegumen (CN) | 33.95, 81.45 | 0.928 | 0.80 | 1.00 | 1.00 | lithology | 否（qaidam_dalangtan 1038 km） |

交叉驗證（用面向 地表物質與裸露 組成）：前 20 名在 100 km 內重疊 15%，全部格子的等級相關 0.88。

### R6 沙塵與近地表氣象

可評分陸地格 1,441,481；分數 ≥ 0.8 的陸地面積 0.0%、≥ 0.9 的 0.0%。

| # | 地點 | 座標 | 分數 | dust | temperature | diurnal_range | dust_season_shape | dust_season_amplitude | temperature_season_shape | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 66 km from Toksun (CN) | 42.25, 88.95 | 0.742 | 0.97 | 0.61 | 0.95 | 0.41 | 0.75 | 0.97 | dust_season_shape | 否（qaidam_dalangtan 493 km） |
| 2 | near Zuogaiduoma (CN) | 35.05, 103.25 | 0.734 | 0.79 | 0.73 | 0.94 | 0.30 | 1.00 | 0.97 | dust_season_shape | 否（qaidam_dalangtan 1094 km） |
| 3 | near Huazangsi (CN) | 36.95, 103.35 | 0.727 | 0.82 | 0.71 | 0.98 | 0.28 | 0.96 | 0.96 | dust_season_shape | 否（qaidam_dalangtan 1039 km） |
| 4 | near Malah (SY) | 32.55, 36.85 | 0.725 | 0.80 | 0.50 | 0.95 | 0.39 | 0.99 | 0.98 | dust_season_shape | 否（lake_salda 857 km） |
| 5 | 39 km from Zhonghualu (CN) | 35.95, 104.55 | 0.724 | 0.81 | 0.66 | 0.87 | 0.33 | 0.98 | 0.96 | dust_season_shape | 否（qaidam_dalangtan 1171 km） |
| 6 | near Yuwang (CN) | 36.85, 106.35 | 0.72 | 0.83 | 0.64 | 0.91 | 0.32 | 0.93 | 0.96 | dust_season_shape | 否（qaidam_dalangtan 1302 km） |
| 7 | 154 km from Sekseuil (KZ) | 45.75, 60.65 | 0.719 | 0.82 | 0.59 | 0.95 | 0.31 | 1.00 | 0.96 | dust_season_shape | 否（kachchh_matanumadh 2579 km） |
| 8 | 51 km from Dingbian (CN) | 37.95, 107.95 | 0.716 | 0.83 | 0.65 | 0.94 | 0.33 | 0.84 | 0.97 | dust_season_shape | 否（qaidam_dalangtan 1423 km） |
| 9 | near Kangal (TR) | 39.15, 37.35 | 0.713 | 0.72 | 0.65 | 0.88 | 0.34 | 0.95 | 0.98 | dust_season_shape | 否（lake_salda 692 km） |
| 10 | near `Assal al Ward (SY) | 34.05, 36.45 | 0.713 | 0.79 | 0.63 | 0.74 | 0.37 | 0.98 | 0.98 | dust_season_shape | 否（lake_salda 724 km） |

交叉驗證（用面向 大氣與沙塵、環境極端 組成）：前 20 名在 100 km 內重疊 0%，全部格子的等級相關 0.783。

### 每項測試第 1 名的面向分數（面向 × 測試）

| 測試 | 第 1 名 | 測試分數 | 地形 | 地表物質與裸露 | 環境極端 | 水與冰 | 大氣與沙塵 | 剖面整體 |
|---|---|---|---|---|---|---|---|---|
| R1 | near Mynaral (KZ)（45.45, 73.75） | 1.0 | **1.00** | **0.92** | 0.76 | 1.00 | 0.84 | 89.8 |
| R4 | 170 km from Turkmenbasy (TM)（41.55, 52.85） | 0.928 | 0.99 | **0.92** | 0.72 | 1.00 | 0.90 | 89.9 |
| R6 | 66 km from Toksun (CN)（42.25, 88.95） | 0.742 | 0.91 | 0.52 | **0.74** | 1.00 | **0.97** | 80.5 |

粗體 = 這項測試的主要面向。

### 參考用加權總分（ROC 權重，只用適用的測試、重新正規化）

權重：R1 0.651、R6 0.252、R4 0.097

| # | 地點 | 座標 | 總分 | R1 | R6 | R4 |
|---|---|---|---|---|---|---|
| 1 | 178 km from Torghay (KZ) | 48.05, 63.15 | 0.881 | 0.99 | 0.66 | 0.84 |
| 2 | 42 km from Maintang (CN) | 31.75, 89.55 | 0.877 | 1.00 | 0.61 | 0.93 |
| 3 | near Aral (KZ) | 46.85, 61.95 | 0.875 | 0.97 | 0.67 | 0.88 |
| 4 | near Beyneu (KZ) | 45.55, 55.25 | 0.873 | 0.99 | 0.63 | 0.91 |
| 5 | 40 km from Dostyq (KZ) | 44.95, 82.75 | 0.873 | 1.00 | 0.64 | 0.79 |
| 6 | 117 km from Xagmakajor (CN) | 32.55, 82.35 | 0.873 | 1.00 | 0.60 | 0.93 |
| 7 | 105 km from Taushyq (KZ) | 45.25, 51.75 | 0.871 | 0.98 | 0.64 | 0.90 |
| 8 | 109 km from Altay sumu (MN) | 44.85, 91.95 | 0.87 | 0.96 | 0.67 | 0.88 |
| 9 | 150 km from Barkol (CN) | 42.55, 91.85 | 0.869 | 0.95 | 0.69 | 0.90 |
| 10 | 40 km from Toksun (CN) | 42.75, 88.15 | 0.869 | 0.97 | 0.69 | 0.76 |

### 已知類比地檢查

標了對應任務的已知類比地，在該測試的全球前百分比中位數（越小越前面）vs 沒標的：

| 測試 | 對應任務 | 有標（n） | 中位數 | 沒標（n） | 中位數 |
|---|---|---|---|---|---|
| R1 | landing、rover | 7 | 80.0% | 13 | 32.7% |
| R4 | geology | 24 | 40.1% | 3 | 13.6% |
| R6 | — | 0 | —% | 28 | 49.2% |

## Meridiani Planum (Opportunity landing site, Eagle crater)（-1.95, -5.53）

測試狀態：R1 已評分；R2 無法評估；R3 不適用（目標沒有可靠的冰訊號）；R4 已評分；R5 不適用（目標沒有可靠的冰訊號）；R6 已評分。冰訊號 clip(Ci, 0, 1) = 0.034（R3、R5 需要 ≥ 0.1）。

### R1 著陸地表條件

可評分陸地格 791,247；分數 ≥ 0.8 的陸地面積 9.8%、≥ 0.9 的 1.8%。

| # | 地點 | 座標 | 分數 | slope | roughness | thermal_inertia | barrenness | ice_free | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | near Xagmakajor (CN) | 31.65, 82.35 | 0.999 | 1.00 | 1.00 | 1.00 | 0.99 | 1.00 | barrenness | 否（qaidam_dalangtan 1127 km） |
| 2 | 107 km from Maindong (CN) | 30.95, 86.45 | 0.998 | 1.00 | 0.99 | 1.00 | 1.00 | 1.00 | roughness | 否（qaidam_dalangtan 949 km） |
| 3 | 62 km from Cuozheqiangma (CN) | 32.75, 87.75 | 0.998 | 1.00 | 0.99 | 1.00 | 1.00 | 1.00 | roughness | 否（qaidam_dalangtan 715 km） |
| 4 | near Jisegumen (CN) | 33.95, 80.85 | 0.997 | 1.00 | 0.99 | 1.00 | 1.00 | 1.00 | roughness | 否（qaidam_dalangtan 1086 km） |
| 5 | 298 km from Clyde River (CA) | 69.95, -76.35 | 0.996 | 1.00 | 1.00 | 1.00 | 0.98 | 1.00 | barrenness | 否（haughton_crater 744 km） |
| 6 | near `En Boqeq (IL) | 31.25, 35.45 | 0.995 | 1.00 | 0.97 | 1.00 | 1.00 | 1.00 | roughness | 否（lake_salda 878 km） |
| 7 | 110 km from Edd (ER) | 13.25, 40.95 | 0.995 | 1.00 | 0.97 | 1.00 | 1.00 | 1.00 | roughness | 否（dallol 131 km） |
| 8 | 117 km from Qimantage (CN) | 37.55, 89.05 | 0.995 | 1.00 | 0.98 | 1.00 | 1.00 | 1.00 | roughness | 否（qaidam_dalangtan 246 km） |
| 9 | 83 km from Zhabu (CN) | 33.35, 84.15 | 0.994 | 1.00 | 0.97 | 1.00 | 1.00 | 1.00 | roughness | 否（qaidam_dalangtan 875 km） |
| 10 | 55 km from Cruz de Machacamarca (BO) | -19.35, -68.25 | 0.994 | 1.00 | 1.00 | 1.00 | 0.97 | 1.00 | barrenness | 否（atacama_yungay 554 km） |

交叉驗證（用面向 地形、地表物質與裸露 組成）：前 20 名在 100 km 內重疊 15%，全部格子的等級相關 0.443。

### R4 含水礦物辨識

可評分陸地格 1,434,366；分數 ≥ 0.8 的陸地面積 0.4%、≥ 0.9 的 0.0%。

| # | 地點 | 座標 | 分數 | lithology | barrenness | ice_free | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|
| 1 | 66 km from Colchani (BO) | -20.15, -67.55 | 1.0 | 1.00 | 1.00 | 1.00 | lithology | 否（atacama_yungay 501 km） |
| 2 | 585 km from Kugluktuk (CA) | 72.75, -109.55 | 0.999 | 1.00 | 1.00 | 1.00 | barrenness | 否（haughton_crater 669 km） |
| 3 | 150 km from Antofagasta de la Sierra (AR) | -24.75, -67.75 | 0.979 | 1.00 | 0.94 | 1.00 | barrenness | 否（atacama_yungay 232 km） |
| 4 | 415 km from Khatanga (RU) | 75.65, 104.95 | 0.979 | 1.00 | 0.94 | 1.00 | barrenness | 否（svalbard_bockfjorden 2001 km） |
| 5 | 58 km from Letlhakane (BW) | -20.95, 25.85 | 0.975 | 1.00 | 0.93 | 1.00 | barrenness | 否（dallol 4219 km） |
| 6 | 54 km from Rapar (IN) | 24.05, 70.55 | 0.968 | 1.00 | 0.91 | 1.00 | barrenness | 否（kachchh_matanumadh 172 km） |
| 7 | near Al Jabayish (IQ) | 30.75, 47.05 | 0.967 | 1.00 | 0.91 | 1.00 | barrenness | 否（dhofar_amadee18 1626 km） |
| 8 | 103 km from Diego de Almagro (CL) | -26.15, -69.05 | 0.96 | 1.00 | 0.88 | 1.00 | barrenness | 否（atacama_yungay 246 km） |
| 9 | 57 km from Zahedan (IR) | 29.55, 61.45 | 0.95 | 1.00 | 0.86 | 1.00 | barrenness | 否（kachchh_matanumadh 1000 km） |
| 10 | near Zaranj (AF) | 31.05, 62.15 | 0.946 | 1.00 | 0.84 | 1.00 | barrenness | 否（kachchh_matanumadh 1070 km） |

交叉驗證（用面向 地表物質與裸露 組成）：前 20 名在 100 km 內重疊 10%，全部格子的等級相關 0.9。

### R6 沙塵與近地表氣象

可評分陸地格 1,441,481；分數 ≥ 0.8 的陸地面積 8.0%、≥ 0.9 的 0.3%。

| # | 地點 | 座標 | 分數 | dust | temperature | diurnal_range | dust_season_shape | dust_season_amplitude | temperature_season_shape | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 86 km from Yeyik (CN) | 36.25, 84.05 | 0.943 | 0.99 | 0.86 | 0.99 | 0.98 | 0.99 | 0.87 | temperature | 否（qaidam_dalangtan 712 km） |
| 2 | 108 km from Aqqan (CN) | 35.55, 82.35 | 0.943 | 0.98 | 0.88 | 0.98 | 0.98 | 0.97 | 0.87 | temperature_season_shape | 否（qaidam_dalangtan 884 km） |
| 3 | 63 km from Aqqan (CN) | 36.75, 85.65 | 0.941 | 0.99 | 0.87 | 0.97 | 0.98 | 0.98 | 0.86 | temperature_season_shape | 否（qaidam_dalangtan 559 km） |
| 4 | 132 km from Nur (CN) | 35.55, 79.95 | 0.941 | 1.00 | 0.93 | 0.93 | 0.96 | 0.98 | 0.85 | temperature_season_shape | 否（qaidam_dalangtan 1086 km） |
| 5 | 163 km from Waxxari (CN) | 37.25, 87.55 | 0.938 | 0.98 | 0.84 | 0.98 | 0.97 | 1.00 | 0.87 | temperature | 否（qaidam_dalangtan 381 km） |
| 6 | 129 km from Thang (IN) | 36.05, 77.15 | 0.932 | 0.92 | 0.88 | 0.99 | 0.97 | 0.99 | 0.86 | temperature_season_shape | 否（qaidam_dalangtan 1309 km） |
| 7 | 106 km from Qilanbulak (CN) | 37.85, 89.15 | 0.931 | 0.98 | 0.81 | 0.98 | 0.95 | 1.00 | 0.88 | temperature | 否（qaidam_dalangtan 227 km） |
| 8 | 171 km from Qimantage (CN) | 36.25, 88.95 | 0.925 | 0.90 | 0.87 | 0.97 | 0.95 | 0.99 | 0.87 | temperature_season_shape | 否（qaidam_dalangtan 334 km） |
| 9 | 97 km from Wutumeiren (CN) | 36.05, 92.95 | 0.924 | 0.95 | 0.81 | 0.97 | 0.93 | 0.99 | 0.90 | temperature | 否（qaidam_dalangtan 278 km） |
| 10 | 78 km from Hoit Taria (CN) | 38.05, 96.85 | 0.924 | 0.91 | 0.87 | 0.96 | 0.93 | 1.00 | 0.88 | temperature | 否（qaidam_dalangtan 454 km） |

交叉驗證（用面向 大氣與沙塵、環境極端 組成）：前 20 名在 100 km 內重疊 55%，全部格子的等級相關 0.82。

### 每項測試第 1 名的面向分數（面向 × 測試）

| 測試 | 第 1 名 | 測試分數 | 地形 | 地表物質與裸露 | 環境極端 | 水與冰 | 大氣與沙塵 | 剖面整體 |
|---|---|---|---|---|---|---|---|---|
| R1 | near Xagmakajor (CN)（31.65, 82.35） | 0.999 | **1.00** | **0.46** | 0.78 | 0.15 | 0.66 | 51.2 |
| R4 | 66 km from Colchani (BO)（-20.15, -67.55） | 1.0 | 0.91 | **0.99** | 0.75 | — | 0.20 | 60.3 |
| R6 | 86 km from Yeyik (CN)（36.25, 84.05） | 0.943 | 0.86 | 0.64 | **0.86** | 0.03 | **0.99** | 43.7 |

粗體 = 這項測試的主要面向。

### 參考用加權總分（ROC 權重，只用適用的測試、重新正規化）

權重：R1 0.651、R6 0.252、R4 0.097

| # | 地點 | 座標 | 總分 | R1 | R6 | R4 |
|---|---|---|---|---|---|---|
| 1 | 151 km from Jisegumen (CN) | 34.45, 82.35 | 0.94 | 1.00 | 0.84 | 0.84 |
| 2 | 228 km from Qimantage (CN) | 36.25, 88.15 | 0.939 | 0.99 | 0.88 | 0.78 |
| 3 | 130 km from Wutumeiren (CN) | 35.75, 92.95 | 0.934 | 0.98 | 0.88 | 0.78 |
| 4 | 89 km from Qimantage (CN) | 37.45, 89.35 | 0.932 | 0.97 | 0.89 | 0.78 |
| 5 | 183 km from Yeyik (CN) | 35.35, 84.45 | 0.93 | 0.98 | 0.86 | 0.77 |
| 6 | 100 km from Wutumeiren (CN) | 37.55, 93.95 | 0.927 | 0.98 | 0.86 | 0.78 |
| 7 | 117 km from Xagmakajor (CN) | 32.55, 82.35 | 0.926 | 0.99 | 0.80 | 0.84 |
| 8 | 151 km from Koramlik (CN) | 36.05, 86.05 | 0.926 | 0.98 | 0.87 | 0.72 |
| 9 | 177 km from Qimantage (CN) | 35.75, 89.95 | 0.923 | 0.98 | 0.84 | 0.77 |
| 10 | 166 km from Sangiyn Dalay (MN) | 43.65, 97.55 | 0.922 | 0.97 | 0.85 | 0.81 |

### 已知類比地檢查

標了對應任務的已知類比地，在該測試的全球前百分比中位數（越小越前面）vs 沒標的：

| 測試 | 對應任務 | 有標（n） | 中位數 | 沒標（n） | 中位數 |
|---|---|---|---|---|---|
| R1 | landing、rover | 7 | 80.3% | 13 | 31.9% |
| R4 | geology | 24 | 40.4% | 3 | 9.6% |
| R6 | — | 0 | —% | 28 | 39.2% |

## Protonilus Mensae (candidate human exploration zone, buried glacial ice)（41.905, 48.548）

測試狀態：R1 已評分；R2 無法評估；R3 已評分；R4 已評分；R5 已評分；R6 已評分。冰訊號 clip(Ci, 0, 1) = 0.162（R3、R5 需要 ≥ 0.1）。

### R1 著陸地表條件

可評分陸地格 791,247；分數 ≥ 0.8 的陸地面積 3.0%、≥ 0.9 的 0.6%。

| # | 地點 | 座標 | 分數 | slope | roughness | thermal_inertia | barrenness | ice_free | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 102 km from Cuozheqiangma (CN) | 32.45, 88.15 | 0.993 | 1.00 | 0.98 | 1.00 | 0.98 | 1.00 | roughness | 否（qaidam_dalangtan 727 km） |
| 2 | 155 km from Qimantage (CN) | 35.95, 90.75 | 0.985 | 1.00 | 0.96 | 1.00 | 0.96 | 1.00 | barrenness | 否（qaidam_dalangtan 277 km） |
| 3 | 105 km from Luring (CN) | 31.35, 83.95 | 0.984 | 1.00 | 0.99 | 1.00 | 0.93 | 1.00 | barrenness | 否（qaidam_dalangtan 1047 km） |
| 4 | 67 km from Khash (IR) | 28.75, 61.55 | 0.981 | 1.00 | 1.00 | 1.00 | 0.91 | 1.00 | barrenness | 否（kachchh_matanumadh 938 km） |
| 5 | 153 km from Jisegumen (CN) | 35.15, 79.75 | 0.98 | 1.00 | 1.00 | 1.00 | 0.90 | 1.00 | barrenness | 否（qaidam_dalangtan 1118 km） |
| 6 | 74 km from Assab (ER) | 13.35, 42.15 | 0.979 | 1.00 | 0.99 | 1.00 | 0.91 | 1.00 | barrenness | 否（dallol 223 km） |
| 7 | 125 km from Jisegumen (CN) | 34.45, 82.05 | 0.978 | 1.00 | 0.94 | 1.00 | 0.95 | 1.00 | roughness | 否（qaidam_dalangtan 962 km） |
| 8 | 74 km from La Consulta (AR) | -34.15, -69.75 | 0.974 | 1.00 | 0.97 | 1.00 | 0.91 | 1.00 | barrenness | 否（atacama_yungay 1120 km） |
| 9 | near Gahe (CN) | 38.55, 97.55 | 0.973 | 1.00 | 0.97 | 1.00 | 0.90 | 1.00 | barrenness | 否（qaidam_dalangtan 513 km） |
| 10 | 51 km from Bur Safajah (EG) | 26.35, 33.65 | 0.97 | 1.00 | 1.00 | 1.00 | 0.86 | 1.00 | barrenness | 否（lake_salda 1300 km） |

交叉驗證（用面向 地形、地表物質與裸露 組成）：前 20 名在 100 km 內重疊 15%，全部格子的等級相關 0.545。

### R3 淺層地下冰

可評分陸地格 1,434,064；分數 ≥ 0.8 的陸地面積 2.5%、≥ 0.9 的 0.2%。

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
| 10 | 93 km from Guma (CN) | 36.85, 77.85 | 0.969 | 1.00 | 1.00 | 0.91 | dryness | 否（qaidam_dalangtan 1228 km） |

交叉驗證（用面向 水與冰、環境極端 組成）：前 20 名在 100 km 內重疊 20%，全部格子的等級相關 0.004。

### R4 含水礦物辨識

可評分陸地格 1,434,366；分數 ≥ 0.8 的陸地面積 5.5%、≥ 0.9 的 0.3%。

| # | 地點 | 座標 | 分數 | lithology | barrenness | ice_free | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|
| 1 | 847 km from Gjoa Haven (CA) | 76.15, -99.85 | 0.965 | 0.90 | 1.00 | 1.00 | lithology | 否（haughton_crater 291 km） |
| 2 | 178 km from Torghay (KZ) | 48.05, 63.15 | 0.965 | 0.90 | 1.00 | 1.00 | lithology | 否（qaidam_dalangtan 2533 km） |
| 3 | 859 km from Rankin Inlet (CA) | 70.15, -85.95 | 0.965 | 0.90 | 1.00 | 1.00 | lithology | 否（haughton_crater 594 km） |
| 4 | 900 km from Clyde River (CA) | 77.65, -82.55 | 0.965 | 0.90 | 1.00 | 1.00 | lithology | 否（axel_heiberg_lost_hammer 234 km） |
| 5 | 38 km from Aswan (EG) | 23.75, 32.85 | 0.965 | 0.90 | 1.00 | 1.00 | lithology | 否（dallol 1315 km） |
| 6 | 158 km from Maqian (CN) | 33.05, 89.85 | 0.965 | 0.90 | 1.00 | 1.00 | lithology | 否（qaidam_dalangtan 610 km） |
| 7 | 120 km from Jisegumen (CN) | 35.05, 80.25 | 0.965 | 0.90 | 1.00 | 1.00 | lithology | 否（qaidam_dalangtan 1081 km） |
| 8 | 332 km from Clyde River (CA) | 71.55, -77.15 | 0.965 | 0.90 | 1.00 | 1.00 | lithology | 否（haughton_crater 580 km） |
| 9 | 145 km from Haines Junction (CA) | 59.45, -137.45 | 0.965 | 0.90 | 1.00 | 1.00 | lithology | 否（pavilion_lake 1374 km） |
| 10 | 37 km from Khandud (AF) | 36.75, 72.65 | 0.965 | 0.90 | 1.00 | 1.00 | lithology | 否（kachchh_matanumadh 1510 km） |

交叉驗證（用面向 地表物質與裸露 組成）：前 20 名在 100 km 內重疊 5%，全部格子的等級相關 0.908。

### R5 冰河與冰緣地形

可評分陸地格 1,435,231；分數 ≥ 0.8 的陸地面積 0.5%、≥ 0.9 的 0.2%。

| # | 地點 | 座標 | 分數 | permafrost | cold | slope | roughness | barrenness | glacier_distance | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 881 km from Kugluktuk (CA) | 75.75, -114.75 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（haughton_crater 691 km） |
| 2 | 1389 km from Clyde River (CA) | 82.95, -71.15 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（axel_heiberg_lost_hammer 537 km） |
| 3 | 612 km from Clyde River (CA) | 74.65, -80.65 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | permafrost | 否（haughton_crater 272 km） |
| 4 | 599 km from Gjoa Haven (CA) | 73.05, -86.45 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（haughton_crater 277 km） |
| 5 | 113 km from Clyde River (CA) | 69.45, -68.55 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | permafrost | 否（haughton_crater 959 km） |
| 6 | 292 km from Clyde River (CA) | 67.85, -67.95 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（haughton_crater 1119 km） |
| 7 | 99 km from Longyearbyen (SJ) | 78.85, 12.45 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | slope | 否（svalbard_bockfjorden 67 km） |
| 8 | 1348 km from Gjoa Haven (CA) | 80.75, -94.75 | 0.999 | 1.00 | 1.00 | 1.00 | 0.99 | 1.00 | 1.00 | roughness | 否（axel_heiberg_lost_hammer 206 km） |
| 9 | 927 km from Gjoa Haven (CA) | 76.45, -86.05 | 0.999 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（haughton_crater 154 km） |
| 10 | 1554 km from Gjoa Haven (CA) | 82.35, -83.95 | 0.999 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | slope | 否（axel_heiberg_lost_hammer 380 km） |

交叉驗證（用面向 水與冰、地形 組成）：前 20 名在 100 km 內重疊 0%，全部格子的等級相關 -0.017。

### R6 沙塵與近地表氣象

可評分陸地格 1,441,481；分數 ≥ 0.8 的陸地面積 0.0%、≥ 0.9 的 0.0%。

| # | 地點 | 座標 | 分數 | dust | temperature | diurnal_range | dust_season_shape | dust_season_amplitude | temperature_season_shape | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | near Quero (EC) | -1.35, -78.65 | 0.802 | 0.67 | 0.64 | 0.90 | 0.84 | 0.95 | 0.87 | temperature | 否（atacama_yungay 2696 km） |
| 2 | near Molo (KE) | -0.35, 35.65 | 0.792 | 0.95 | 0.58 | 0.73 | 0.79 | 0.97 | 0.80 | temperature | 否（dallol 1701 km） |
| 3 | 32 km from Nanyuki (KE) | -0.05, 37.35 | 0.776 | 0.94 | 0.65 | 0.78 | 0.79 | 0.97 | 0.59 | temperature_season_shape | 否（dallol 1622 km） |
| 4 | near Cuenca (EC) | -3.05, -79.05 | 0.771 | 0.67 | 0.64 | 0.66 | 0.84 | 0.97 | 0.92 | temperature | 否（atacama_yungay 2536 km） |
| 5 | near Pumwani (KE) | -1.35, 36.85 | 0.767 | 0.97 | 0.46 | 0.69 | 0.76 | 0.98 | 0.88 | temperature | 否（dallol 1775 km） |
| 6 | near Jiru (CN) | 27.95, 88.95 | 0.752 | 1.00 | 0.78 | 0.96 | 0.28 | 0.89 | 0.96 | dust_season_shape | 否（qaidam_dalangtan 1181 km） |
| 7 | 73 km from Magadi (KE) | -2.05, 35.65 | 0.751 | 0.95 | 0.55 | 0.59 | 0.70 | 0.99 | 0.84 | temperature | 否（dallol 1882 km） |
| 8 | 66 km from Douyu (CN) | 27.95, 92.55 | 0.75 | 0.97 | 0.79 | 0.94 | 0.28 | 0.90 | 0.96 | dust_season_shape | 否（qaidam_dalangtan 1157 km） |
| 9 | near Arusha (TZ) | -3.25, 36.65 | 0.744 | 0.91 | 0.46 | 0.73 | 0.70 | 0.97 | 0.82 | temperature | 否（dallol 1986 km） |
| 10 | near Cayambe (EC) | -0.05, -78.05 | 0.743 | 0.66 | 0.72 | 0.49 | 0.85 | 1.00 | 0.85 | diurnal_range | 否（atacama_yungay 2812 km） |

交叉驗證（用面向 大氣與沙塵、環境極端 組成）：前 20 名在 100 km 內重疊 25%，全部格子的等級相關 0.555。

### 每項測試第 1 名的面向分數（面向 × 測試）

| 測試 | 第 1 名 | 測試分數 | 地形 | 地表物質與裸露 | 環境極端 | 水與冰 | 大氣與沙塵 | 剖面整體 |
|---|---|---|---|---|---|---|---|---|
| R1 | 102 km from Cuozheqiangma (CN)（32.45, 88.15） | 0.993 | **0.96** | **0.91** | 0.74 | 0.44 | 0.86 | 75.3 |
| R3 | 522 km from McMurdo Station (AQ)（-73.15, 167.15） | 1.0 | 0.89 | 0.80 | **1.00** | **0.16** | 0.65 | 59.6 |
| R4 | 847 km from Gjoa Haven (CA)（76.15, -99.85） | 0.965 | 0.99 | **0.95** | 0.72 | 0.16 | 0.80 | 61.5 |
| R5 | 881 km from Kugluktuk (CA)（75.75, -114.75） | 1.0 | **1.00** | 0.89 | 0.73 | **0.16** | 0.82 | 61.3 |
| R6 | near Quero (EC)（-1.35, -78.65） | 0.802 | 0.97 | 0.10 | **0.52** | 0.84 | **0.67** | 48.7 |

粗體 = 這項測試的主要面向。

### 參考用加權總分（ROC 權重，只用適用的測試、重新正規化）

權重：R1 0.455、R3 0.27、R6 0.176、R4 0.068、R5 0.031

| # | 地點 | 座標 | 總分 | R1 | R3 | R6 | R4 | R5 |
|---|---|---|---|---|---|---|---|---|
| 1 | 99 km from Jisegumen (CN) | 34.95, 80.85 | 0.888 | 0.96 | 0.97 | 0.62 | 0.91 | 0.96 |
| 2 | 155 km from Qimantage (CN) | 35.95, 90.75 | 0.864 | 0.98 | 0.89 | 0.58 | 0.88 | 0.97 |
| 3 | 218 km from Qimantage (CN) | 35.75, 88.85 | 0.861 | 0.96 | 0.89 | 0.59 | 0.91 | 0.95 |
| 4 | 45 km from Hoshoot (MN) | 49.05, 88.55 | 0.853 | 0.91 | 0.90 | 0.68 | 0.80 | 0.92 |
| 5 | 31 km from Tolbo (MN) | 48.55, 90.65 | 0.852 | 0.92 | 0.90 | 0.64 | 0.86 | 0.93 |
| 6 | near Gahe (CN) | 38.55, 97.55 | 0.851 | 0.97 | 0.86 | 0.56 | 0.90 | 0.97 |
| 7 | 192 km from Yeyik (CN) | 34.95, 83.05 | 0.848 | 0.89 | 0.96 | 0.61 | 0.87 | 0.83 |
| 8 | 189 km from Cuozheqiangma (CN) | 34.55, 86.35 | 0.844 | 0.89 | 0.92 | 0.62 | 0.91 | 0.95 |
| 9 | 91 km from Jumla (NP) | 29.85, 82.85 | 0.841 | 0.95 | 0.85 | 0.69 | 0.55 | 0.96 |
| 10 | 79 km from A'yi Take (CN) | 39.15, 74.55 | 0.841 | 0.97 | 0.88 | 0.59 | 0.66 | 0.96 |

### 已知類比地檢查

標了對應任務的已知類比地，在該測試的全球前百分比中位數（越小越前面）vs 沒標的：

| 測試 | 對應任務 | 有標（n） | 中位數 | 沒標（n） | 中位數 |
|---|---|---|---|---|---|
| R1 | landing、rover | 7 | 50.2% | 13 | 22.0% |
| R3 | isru_base | 6 | 33.6% | 22 | 39.2% |
| R4 | geology | 24 | 40.2% | 3 | 10.2% |
| R5 | geology | 25 | 26.0% | 3 | 19.7% |
| R6 | — | 0 | —% | 28 | 33.9% |

## Arcadia Planitia AP-105 (SkyFall design reference landing site)（43.3295, -161.4772）

測試狀態：R1 已評分；R2 無法評估；R3 已評分；R4 已評分；R5 已評分；R6 已評分。冰訊號 clip(Ci, 0, 1) = 0.583（R3、R5 需要 ≥ 0.1）。

### R1 著陸地表條件

可評分陸地格 791,247；分數 ≥ 0.8 的陸地面積 9.2%、≥ 0.9 的 1.5%。

| # | 地點 | 座標 | 分數 | slope | roughness | thermal_inertia | barrenness | ice_free | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 142 km from Jisegumen (CN) | 35.15, 79.95 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | slope | 否（qaidam_dalangtan 1102 km） |
| 2 | 70 km from Colchani (BO) | -20.55, -67.55 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | slope | 否（atacama_yungay 462 km） |
| 3 | 59 km from Wendover (US) | 40.85, -113.35 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | slope | 否（pilot_valley_utah 51 km） |
| 4 | 57 km from Xitieshan (CN) | 37.05, 94.95 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（qaidam_dalangtan 322 km） |
| 5 | 77 km from Antofagasta de la Sierra (AR) | -25.45, -67.05 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | slope | 否（atacama_yungay 327 km） |
| 6 | 40 km from Dostyq (KZ) | 44.95, 82.75 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | slope | 否（qaidam_dalangtan 1043 km） |
| 7 | 36 km from Urho (CN) | 45.85, 85.95 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | slope | 否（qaidam_dalangtan 960 km） |
| 8 | 42 km from Maintang (CN) | 31.75, 89.55 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（qaidam_dalangtan 757 km） |
| 9 | 88 km from Turkmenbasy (TM) | 40.75, 53.35 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | slope | 否（lake_salda 2065 km） |
| 10 | 36 km from Ziway (ET) | 7.65, 38.55 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（dallol 757 km） |

交叉驗證（用面向 地形、地表物質與裸露 組成）：前 20 名在 100 km 內重疊 0%，全部格子的等級相關 0.502。

### R3 淺層地下冰

可評分陸地格 1,434,064；分數 ≥ 0.8 的陸地面積 2.5%、≥ 0.9 的 0.2%。

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
| 9 | 93 km from Guma (CN) | 36.85, 77.85 | 0.969 | 1.00 | 1.00 | 0.91 | dryness | 否（qaidam_dalangtan 1228 km） |
| 10 | 77 km from Jisegumen (CN) | 34.75, 80.85 | 0.968 | 1.00 | 1.00 | 0.91 | dryness | 否（qaidam_dalangtan 1045 km） |

交叉驗證（用面向 水與冰、環境極端 組成）：前 20 名在 100 km 內重疊 30%，全部格子的等級相關 0.684。

### R4 含水礦物辨識

可評分陸地格 1,391,042；分數 ≥ 0.8 的陸地面積 0.1%、≥ 0.9 的 0.0%。

| # | 地點 | 座標 | 分數 | lithology | barrenness | ice_free | mineral_signature | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 272 km from Talnakh (RU) | 69.15, 95.25 | 0.995 | 1.00 | 0.98 | 1.00 | 1.00 | barrenness | 否（svalbard_bockfjorden 2435 km） |
| 2 | 135 km from Antofagasta de la Sierra (AR) | -25.05, -68.15 | 0.964 | 1.00 | 0.86 | 1.00 | 1.00 | barrenness | 否（atacama_yungay 209 km） |
| 3 | 473 km from Rankin Inlet (CA) | 67.05, -91.15 | 0.962 | 1.00 | 0.85 | 1.00 | 1.00 | barrenness | 否（haughton_crater 928 km） |
| 4 | 88 km from Tigil' (RU) | 57.35, 159.95 | 0.962 | 1.00 | 0.90 | 1.00 | 0.95 | barrenness | 否（axel_heiberg_lost_hammer 4183 km） |
| 5 | 90 km from Haines Junction (CA) | 59.95, -137.75 | 0.953 | 1.00 | 0.83 | 1.00 | 1.00 | barrenness | 否（pavilion_lake 1421 km） |
| 6 | 328 km from Iqaluit (CA) | 61.65, -73.05 | 0.942 | 1.00 | 0.86 | 1.00 | 0.91 | barrenness | 否（haughton_crater 1656 km） |
| 7 | 132 km from Talnakh (RU) | 69.95, 91.55 | 0.937 | 1.00 | 0.77 | 1.00 | 1.00 | barrenness | 否（svalbard_bockfjorden 2286 km） |
| 8 | 120 km from Maralal (KE) | 2.15, 36.45 | 0.931 | 1.00 | 0.75 | 1.00 | 1.00 | barrenness | 否（dallol 1409 km） |
| 9 | 58 km from Valdez (US) | 61.65, -146.35 | 0.931 | 1.00 | 0.75 | 1.00 | 1.00 | barrenness | 否（pavilion_lake 1916 km） |
| 10 | 36 km from El Calafate (AR) | -50.65, -72.15 | 0.919 | 1.00 | 0.75 | 1.00 | 0.95 | barrenness | 否（atacama_yungay 2961 km） |

交叉驗證（用面向 地表物質與裸露 組成）：前 20 名在 100 km 內重疊 10%，全部格子的等級相關 0.44。

### R5 冰河與冰緣地形

可評分陸地格 1,435,231；分數 ≥ 0.8 的陸地面積 1.9%、≥ 0.9 的 0.8%。

| # | 地點 | 座標 | 分數 | permafrost | cold | slope | roughness | barrenness | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1205 km from Kugluktuk (CA) | 78.55, -109.45 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | slope | 否（axel_heiberg_lost_hammer 417 km） |
| 2 | 982 km from Khatanga (RU) | 80.75, 97.75 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（svalbard_bockfjorden 1481 km） |
| 3 | 1522 km from Vorgashor (RU) | 81.25, 60.45 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（svalbard_bockfjorden 875 km） |
| 4 | 731 km from Deputatsky (RU) | 75.85, 142.25 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | roughness | 否（svalbard_bockfjorden 2483 km） |
| 5 | 1273 km from Gjoa Haven (CA) | 80.05, -98.85 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | permafrost | 否（axel_heiberg_lost_hammer 204 km） |
| 6 | 1049 km from Gjoa Haven (CA) | 78.05, -97.25 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | slope | 否（axel_heiberg_lost_hammer 193 km） |
| 7 | 797 km from Khatanga (RU) | 79.15, 102.55 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | permafrost | 否（svalbard_bockfjorden 1668 km） |
| 8 | 982 km from Kugluktuk (CA) | 76.65, -116.05 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | permafrost | 否（axel_heiberg_lost_hammer 655 km） |
| 9 | 292 km from Gjoa Haven (CA) | 70.25, -101.75 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | permafrost | 否（haughton_crater 692 km） |
| 10 | 674 km from Kugluktuk (CA) | 73.15, -106.35 | 1.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | barrenness | 否（haughton_crater 558 km） |

交叉驗證（用面向 水與冰、地形 組成）：前 20 名在 100 km 內重疊 0%，全部格子的等級相關 0.634。

### R6 沙塵與近地表氣象

可評分陸地格 1,441,481；分數 ≥ 0.8 的陸地面積 0.0%、≥ 0.9 的 0.0%。

| # | 地點 | 座標 | 分數 | dust | temperature | diurnal_range | dust_season_shape | dust_season_amplitude | temperature_season_shape | 最弱 | 已知類比地 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | near Zuogaiduoma (CN) | 35.05, 103.25 | 0.769 | 0.85 | 0.73 | 0.94 | 0.36 | 0.98 | 0.99 | dust_season_shape | 否（qaidam_dalangtan 1094 km） |
| 2 | near Huazangsi (CN) | 36.95, 103.35 | 0.76 | 0.81 | 0.71 | 0.98 | 0.34 | 1.00 | 0.99 | dust_season_shape | 否（qaidam_dalangtan 1039 km） |
| 3 | 39 km from Zhonghualu (CN) | 35.95, 104.55 | 0.755 | 0.83 | 0.66 | 0.87 | 0.39 | 1.00 | 1.00 | dust_season_shape | 否（qaidam_dalangtan 1171 km） |
| 4 | 35 km from Oljoq (CN) | 37.95, 107.75 | 0.752 | 0.80 | 0.65 | 0.94 | 0.39 | 0.95 | 0.99 | dust_season_shape | 否（qaidam_dalangtan 1405 km） |
| 5 | near Magaozhuang (CN) | 36.85, 106.45 | 0.752 | 0.81 | 0.64 | 0.91 | 0.39 | 0.99 | 1.00 | dust_season_shape | 否（qaidam_dalangtan 1311 km） |
| 6 | near Kosh-Agach (RU) | 49.85, 88.65 | 0.75 | 0.97 | 0.82 | 0.88 | 0.29 | 0.89 | 1.00 | dust_season_shape | 否（qaidam_dalangtan 1303 km） |
| 7 | near Lujing Zhen (CN) | 34.25, 104.65 | 0.749 | 0.86 | 0.72 | 0.70 | 0.41 | 1.00 | 0.99 | dust_season_shape | 否（qaidam_dalangtan 1247 km） |
| 8 | near Youganning (CN) | 34.85, 101.55 | 0.748 | 0.93 | 0.76 | 0.97 | 0.32 | 0.82 | 0.99 | dust_season_shape | 否（qaidam_dalangtan 963 km） |
| 9 | 68 km from Leh (IN) | 33.55, 77.55 | 0.747 | 0.99 | 0.81 | 0.96 | 0.27 | 0.87 | 0.97 | dust_season_shape | 否（qaidam_dalangtan 1376 km） |
| 10 | 33 km from Ordos (CN) | 39.85, 109.55 | 0.746 | 0.81 | 0.68 | 0.92 | 0.37 | 0.93 | 1.00 | dust_season_shape | 否（qaidam_dalangtan 1550 km） |

交叉驗證（用面向 大氣與沙塵、環境極端 組成）：前 20 名在 100 km 內重疊 10%，全部格子的等級相關 0.722。

### 每項測試第 1 名的面向分數（面向 × 測試）

| 測試 | 第 1 名 | 測試分數 | 地形 | 地表物質與裸露 | 環境極端 | 水與冰 | 大氣與沙塵 | 剖面整體 |
|---|---|---|---|---|---|---|---|---|
| R1 | 142 km from Jisegumen (CN)（35.15, 79.95） | 1.0 | **1.00** | **0.57** | 0.85 | 0.58 | 0.88 | 75.7 |
| R3 | 67 km from McMurdo Station (AQ)（-78.15, 164.15） | 1.0 | 0.88 | 1.00 | **1.00** | **0.58** | 0.42 | 73.5 |
| R4 | 272 km from Talnakh (RU)（69.15, 95.25） | 0.995 | 0.31 | **0.99** | 0.18 | 0.58 | 0.67 | 46.4 |
| R5 | 1205 km from Kugluktuk (CA)（78.55, -109.45） | 1.0 | **1.00** | 1.00 | 0.79 | **0.58** | 0.58 | 76.9 |
| R6 | near Zuogaiduoma (CN)（35.05, 103.25） | 0.769 | 0.63 | 0.03 | **0.54** | 0.42 | **0.85** | 32.8 |

粗體 = 這項測試的主要面向。

### 參考用加權總分（ROC 權重，只用適用的測試、重新正規化）

權重：R1 0.455、R3 0.27、R6 0.176、R4 0.068、R5 0.031

| # | 地點 | 座標 | 總分 | R1 | R3 | R6 | R4 | R5 |
|---|---|---|---|---|---|---|---|---|
| 1 | 236 km from Myaundzha (RU) | 65.15, 146.55 | 0.807 | 0.92 | 0.84 | 0.58 | 0.67 | 0.91 |
| 2 | 151 km from Jisegumen (CN) | 34.45, 82.35 | 0.805 | 0.98 | 0.95 | 0.65 | 0.18 | 0.97 |
| 3 | 191 km from Qimantage (CN) | 35.75, 89.45 | 0.804 | 0.94 | 0.90 | 0.63 | 0.30 | 0.94 |
| 4 | 237 km from Qiangma (CN) | 34.05, 90.25 | 0.803 | 0.91 | 0.85 | 0.68 | 0.40 | 0.89 |
| 5 | 271 km from Ust-Nera (RU) | 62.15, 142.55 | 0.796 | 0.95 | 0.76 | 0.59 | 0.57 | 0.94 |
| 6 | 254 km from Deputatsky (RU) | 67.05, 140.85 | 0.792 | 0.89 | 0.84 | 0.58 | 0.64 | 0.88 |
| 7 | 198 km from Qimantage (CN) | 35.65, 91.15 | 0.79 | 0.97 | 0.89 | 0.63 | 0.20 | 0.97 |
| 8 | 79 km from Myaundzha (RU) | 63.75, 146.95 | 0.787 | 0.91 | 0.77 | 0.61 | 0.60 | 0.89 |
| 9 | 45 km from Hohtolgoy (MN) | 49.65, 91.15 | 0.785 | 0.83 | 0.86 | 0.70 | 0.48 | 0.78 |
| 10 | 436 km from Rankin Inlet (CA) | 64.05, -83.75 | 0.783 | 0.96 | 0.77 | 0.50 | 0.62 | 0.96 |

### 已知類比地檢查

標了對應任務的已知類比地，在該測試的全球前百分比中位數（越小越前面）vs 沒標的：

| 測試 | 對應任務 | 有標（n） | 中位數 | 沒標（n） | 中位數 |
|---|---|---|---|---|---|
| R1 | landing、rover | 7 | 79.1% | 13 | 52.8% |
| R3 | isru_base | 6 | 33.6% | 22 | 39.2% |
| R4 | geology | 17 | 28.1% | 2 | 37.7% |
| R5 | geology | 25 | 36.5% | 3 | 36.6% |
| R6 | — | 0 | —% | 28 | 38.0% |
