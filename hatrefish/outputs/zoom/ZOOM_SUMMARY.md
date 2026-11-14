# 放大結果（自動產生）

> 產生時間 2026-11-15 00:01，由 `scripts/zoom_candidates.py` 產生；數字以 `outputs/zoom/zoom_*.json` 為準。
> 每個候選地以 0.1° 格為中心取方框，在約 1 km 子格重算坡度、粗糙度、溫度、乾燥度、NDVI、熱慣量；岩性、永凍土、沙塵沿用所在 0.1° 格。計分方法和全球版完全相同（面向等權重）。
> 「0.1° 格內 1 km 中位數」和「0.1° 原分數」的差，是換資料（地形 GMTED → Copernicus）和換尺度本身造成的，不是找到更好的地點；看「最佳 1 km」要和這個中位數比。
> 有水或緊鄰水體的子格（自己或鄰格水體 > 5%）不參加排名：湖岸的 1 km 地表溫仍會偏涼。
> 高解析坡度與雷達是最佳小區 1 km 方塊內的統計（R1 在全球尺度評估不了的部分），只列出、不計分；SkyFall 要求 1–5 m 尺度坡度 < 15°。坡度解析度：北緯 60° 以北 2 m、南緯 60° 以南 8 m、其他 30 m。

## Arcadia Planitia AP-105 (SkyFall design reference landing site)（整體前幾名；子格 0.01°，方框半寬 0.25°，地形 copernicus）

| 候選 | 0.1° 格 | 0.1° 原分數 | 0.1° 格內 1 km 中位數 | 最佳 1 km 子格 | 1 km 分數 | 最弱面向 | 框內 ≥ 原分數 | 高解析坡度 p50／p90 | 雷達 VV（dB） | 連結 |
|---|---|---|---|---|---|---|---|---|---|---|
| #1 near Kosh-Agach (RU) | 49.95, 88.65 | 86.1 | 85.6 | 49.935, 88.675（near Kosh-Agach (RU)） | 86.6 | 地表物質與裸露 | 1% | 0.7°／1.49°（Copernicus GLO-30） | -16.06 | [Worldview](https://worldview.earthdata.nasa.gov/?v=88.58,49.84,88.77,50.04&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01) · [衛星圖](https://www.google.com/maps/@49.9350,88.6750,12000m/data=!3m1!1e3) · 圖 `zoom_ap105_1.png` |
| #2 46 km from Erzin (RU) | 49.85, 95.15 | 85.4 | 85.1 | 49.785, 95.215（53 km from Erzin (RU)） | 86.8 | 地表物質與裸露 | 2% | 5.32°／9.95°（Copernicus GLO-30） | -16.61 | [Worldview](https://worldview.earthdata.nasa.gov/?v=95.12,49.68,95.31,49.88&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01) · [衛星圖](https://www.google.com/maps/@49.7850,95.2150,12000m/data=!3m1!1e3) · 圖 `zoom_ap105_2.png` |
| #3 49 km from Zhabu (CN) | 33.45, 82.95 | 84.1 | 83.8 | 33.415, 82.935（48 km from Zhabu (CN)） | 87.2 | 地表物質與裸露 | 1% | 0.78°／2.78°（Copernicus GLO-30） | -17.77 | [Worldview](https://worldview.earthdata.nasa.gov/?v=82.84,33.31,83.03,33.52&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01) · [衛星圖](https://www.google.com/maps/@33.4150,82.9350,12000m/data=!3m1!1e3) · 圖 `zoom_ap105_3.png` |

## Arcadia Planitia (shallow ground ice)（整體前幾名；子格 0.01°，方框半寬 0.25°，地形 copernicus）

| 候選 | 0.1° 格 | 0.1° 原分數 | 0.1° 格內 1 km 中位數 | 最佳 1 km 子格 | 1 km 分數 | 最弱面向 | 框內 ≥ 原分數 | 高解析坡度 p50／p90 | 雷達 VV（dB） | 連結 |
|---|---|---|---|---|---|---|---|---|---|---|
| #1 138 km from Chernyshevskiy (RU) | 63.95, 110.65 | 81.7 | 81.4 | 64.085, 110.525（210 km from Aykhal (RU)） | 83.7 | 地表物質與裸露 | 1% | 1.22°／2.59°（ArcticDEM v3 2 m） | -15.0 | [Worldview](https://worldview.earthdata.nasa.gov/?v=110.43,63.98,110.62,64.18&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01) · [衛星圖](https://www.google.com/maps/@64.0850,110.5250,12000m/data=!3m1!1e3) · 圖 `zoom_arcadia_1.png` |
| #2 131 km from Jumla (NP) | 30.25, 82.95 | 80.9 | 81.2 | 30.325, 82.965（139 km from Jumla (NP)） | 82.8 | 地表物質與裸露 | 3% | 0.54°／0.95°（Copernicus GLO-30） | -18.07 | [Worldview](https://worldview.earthdata.nasa.gov/?v=82.87,30.22,83.06,30.43&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01) · [衛星圖](https://www.google.com/maps/@30.3250,82.9650,12000m/data=!3m1!1e3) · 圖 `zoom_arcadia_2.png` |
| #3 193 km from Yagodnoye (RU) | 64.25, 149.25 | 80.9 | 81.0 | 64.155, 149.325（182 km from Yagodnoye (RU)） | 84.1 | 地表物質與裸露 | 4% | 1.44°／3.19°（ArcticDEM v3 2 m） | -12.7 | [Worldview](https://worldview.earthdata.nasa.gov/?v=149.22,64.06,149.42,64.25&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01) · [衛星圖](https://www.google.com/maps/@64.1550,149.3250,12000m/data=!3m1!1e3) · 圖 `zoom_arcadia_3.png` |

## Gale Crater（整體前幾名；子格 0.01°，方框半寬 0.25°，地形 copernicus）

| 候選 | 0.1° 格 | 0.1° 原分數 | 0.1° 格內 1 km 中位數 | 最佳 1 km 子格 | 1 km 分數 | 最弱面向 | 框內 ≥ 原分數 | 高解析坡度 p50／p90 | 雷達 VV（dB） | 連結 |
|---|---|---|---|---|---|---|---|---|---|---|
| #1 near Altanteel (MN) | 47.05, 92.85 | 87.4 | 77.4 | 47.065, 92.815（near Altanteel (MN)） | 88.5 | 地表物質與裸露 | 0% | 5.42°／6.18°（Copernicus GLO-30） | -9.11 | [Worldview](https://worldview.earthdata.nasa.gov/?v=92.72,46.96,92.91,47.16&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01) · [衛星圖](https://www.google.com/maps/@47.0650,92.8150,12000m/data=!3m1!1e3) · 圖 `zoom_gale_1.png` |
| #2 95 km from Altay sumu (MN) | 44.95, 92.25 | 87.2 | 77.4 | 45.065, 92.125（83 km from Altay sumu (MN)） | 87.8 | 地表物質與裸露 | 0% | 12.62°／25.15°（Copernicus GLO-30） | -11.28 | [Worldview](https://worldview.earthdata.nasa.gov/?v=92.03,44.96,92.22,45.16&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01) · [衛星圖](https://www.google.com/maps/@45.0650,92.1250,12000m/data=!3m1!1e3) · 圖 `zoom_gale_2.png` |
| #3 near Bayansayr (MN) | 45.45, 99.25 | 87.1 | 82.2 | 45.435, 99.475（near Bayansayr (MN)） | 88.2 | 地表物質與裸露 | 2% | 8.83°／22.15°（Copernicus GLO-30） | -15.72 | [Worldview](https://worldview.earthdata.nasa.gov/?v=99.38,45.34,99.57,45.54&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01) · [衛星圖](https://www.google.com/maps/@45.4350,99.4750,12000m/data=!3m1!1e3) · 圖 `zoom_gale_3.png` |

## Jezero Crater（整體前幾名；子格 0.01°，方框半寬 0.25°，地形 copernicus）

| 候選 | 0.1° 格 | 0.1° 原分數 | 0.1° 格內 1 km 中位數 | 最佳 1 km 子格 | 1 km 分數 | 最弱面向 | 框內 ≥ 原分數 | 高解析坡度 p50／p90 | 雷達 VV（dB） | 連結 |
|---|---|---|---|---|---|---|---|---|---|---|
| #1 92 km from Wutumeiren (CN) | 37.45, 93.95 | 88.4 | 87.3 | 37.495, 93.745（83 km from Wutumeiren (CN)） | 88.5 | 地形 | 1% | 0.31°／0.68°（Copernicus GLO-30） | -17.95 | [Worldview](https://worldview.earthdata.nasa.gov/?v=93.65,37.39,93.84,37.59&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01) · [衛星圖](https://www.google.com/maps/@37.4950,93.7450,12000m/data=!3m1!1e3) · 圖 `zoom_jezero_1.png` |
| #2 near Dabancheng (CN) | 43.35, 88.15 | 88.2 | 83.3 | 43.425, 88.135（near Dabancheng (CN)） | 88.1 | 環境極端 | 0% | 3.18°／11.55°（Copernicus GLO-30） | -10.62 | [Worldview](https://worldview.earthdata.nasa.gov/?v=88.04,43.32,88.23,43.52&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01) · [衛星圖](https://www.google.com/maps/@43.4250,88.1350,12000m/data=!3m1!1e3) · 圖 `zoom_jezero_2.png` |
| #3 152 km from Sanlei (CN) | 39.95, 103.55 | 87.4 | 86.9 | 39.895, 103.505（146 km from Sanlei (CN)） | 88.1 | 環境極端 | 1% | 11.64°／23.85°（Copernicus GLO-30） | -8.84 | [Worldview](https://worldview.earthdata.nasa.gov/?v=103.41,39.80,103.60,40.00&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01) · [衛星圖](https://www.google.com/maps/@39.8950,103.5050,12000m/data=!3m1!1e3) · 圖 `zoom_jezero_3.png` |

## Meridiani Planum (Opportunity landing site, Eagle crater)（整體前幾名；子格 0.01°，方框半寬 0.25°，地形 copernicus）

| 候選 | 0.1° 格 | 0.1° 原分數 | 0.1° 格內 1 km 中位數 | 最佳 1 km 子格 | 1 km 分數 | 最弱面向 | 框內 ≥ 原分數 | 高解析坡度 p50／p90 | 雷達 VV（dB） | 連結 |
|---|---|---|---|---|---|---|---|---|---|---|
| #1 97 km from Mazongshan (CN) | 42.55, 97.65 | 89.9 | 89.1 | 42.515, 97.665（95 km from Mazongshan (CN)） | 90.9 | 環境極端 | 2% | 2.78°／6.61°（Copernicus GLO-30） | -12.59 | [Worldview](https://worldview.earthdata.nasa.gov/?v=97.57,42.41,97.77,42.62&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01) · [衛星圖](https://www.google.com/maps/@42.5150,97.6650,12000m/data=!3m1!1e3) · 圖 `zoom_meridiani_1.png` |
| #2 30 km from Jetaral (CN) | 47.15, 87.05 | 89.8 | 89.5 | 47.325, 87.015（41 km from Jetaral (CN)） | 90.1 | 環境極端 | 1% | 1.53°／4.53°（Copernicus GLO-30） | -14.15 | [Worldview](https://worldview.earthdata.nasa.gov/?v=86.92,47.23,87.11,47.43&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01) · [衛星圖](https://www.google.com/maps/@47.3250,87.0150,12000m/data=!3m1!1e3) · 圖 `zoom_meridiani_2.png` |
| #3 81 km from Wentugaole (CN) | 42.15, 102.05 | 89.8 | 89.5 | 42.235, 102.025（90 km from Wentugaole (CN)） | 90.4 | 環境極端 | 2% | 4.96°／9.2°（Copernicus GLO-30） | -11.34 | [Worldview](https://worldview.earthdata.nasa.gov/?v=101.93,42.13,102.12,42.34&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01) · [衛星圖](https://www.google.com/maps/@42.2350,102.0250,12000m/data=!3m1!1e3) · 圖 `zoom_meridiani_3.png` |

## Oxia Planum (ExoMars Rosalind Franklin landing site)（整體前幾名；子格 0.01°，方框半寬 0.25°，地形 copernicus）

| 候選 | 0.1° 格 | 0.1° 原分數 | 0.1° 格內 1 km 中位數 | 最佳 1 km 子格 | 1 km 分數 | 最弱面向 | 框內 ≥ 原分數 | 高解析坡度 p50／p90 | 雷達 VV（dB） | 連結 |
|---|---|---|---|---|---|---|---|---|---|---|
| #1 92 km from Wutumeiren (CN) | 37.45, 93.95 | 88.9 | 87.5 | 37.495, 93.745（83 km from Wutumeiren (CN)） | 88.9 | 地表物質與裸露 | 0% | 0.31°／0.68°（Copernicus GLO-30） | -17.95 | [Worldview](https://worldview.earthdata.nasa.gov/?v=93.65,37.39,93.84,37.59&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01) · [衛星圖](https://www.google.com/maps/@37.4950,93.7450,12000m/data=!3m1!1e3) · 圖 `zoom_oxia_1.png` |
| #2 235 km from Qilanbulak (CN) | 40.45, 90.75 | 88.7 | 88.7 | 40.455, 90.715（235 km from Qilanbulak (CN)） | 89.4 | 環境極端 | 2% | 0.19°／0.4°（Copernicus GLO-30） | -22.74 | [Worldview](https://worldview.earthdata.nasa.gov/?v=90.62,40.35,90.81,40.55&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01) · [衛星圖](https://www.google.com/maps/@40.4550,90.7150,12000m/data=!3m1!1e3) · 圖 `zoom_oxia_2.png` |
| #3 47 km from Tieganlike (CN) | 39.45, 88.25 | 88.1 | 87.3 | 39.505, 88.305（54 km from Tieganlike (CN)） | 89.4 | 環境極端 | 2% | 0.45°／1.2°（Copernicus GLO-30） | -18.39 | [Worldview](https://worldview.earthdata.nasa.gov/?v=88.21,39.41,88.41,39.61&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01) · [衛星圖](https://www.google.com/maps/@39.5050,88.3050,12000m/data=!3m1!1e3) · 圖 `zoom_oxia_3.png` |

## Protonilus Mensae (candidate human exploration zone, buried glacial ice)（整體前幾名；子格 0.01°，方框半寬 0.25°，地形 copernicus）

| 候選 | 0.1° 格 | 0.1° 原分數 | 0.1° 格內 1 km 中位數 | 最佳 1 km 子格 | 1 km 分數 | 最弱面向 | 框內 ≥ 原分數 | 高解析坡度 p50／p90 | 雷達 VV（dB） | 連結 |
|---|---|---|---|---|---|---|---|---|---|---|
| #1 93 km from Maindong (CN) | 30.95, 84.55 | 86.6 | 73.1 | 30.805, 84.505（105 km from Maindong (CN)） | 87.7 | 地表物質與裸露 | 0% | 4.07°／7.2°（Copernicus GLO-30） | -16.27 | [Worldview](https://worldview.earthdata.nasa.gov/?v=84.41,30.70,84.60,30.91&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01) · [衛星圖](https://www.google.com/maps/@30.8050,84.5050,12000m/data=!3m1!1e3) · 圖 `zoom_protonilus_1.png` |
| #2 81 km from Zhabu (CN) | 32.45, 82.95 | 86.3 | 70.2 | 32.365, 82.785（97 km from Zhabu (CN)） | 85.3 | 地表物質與裸露 | 0% | 5.19°／6.68°（Copernicus GLO-30） | -13.12 | [Worldview](https://worldview.earthdata.nasa.gov/?v=82.69,32.27,82.88,32.47&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01) · [衛星圖](https://www.google.com/maps/@32.3650,82.7850,12000m/data=!3m1!1e3) · 圖 `zoom_protonilus_2.png` |
| #3 80 km from Jiajuedibu (CN) | 31.35, 87.95 | 85.8 | 73.9 | 31.225, 87.725（92 km from Jiajuedibu (CN)） | 86.0 | 地表物質與裸露 | 0% | 5.31°／9.52°（Copernicus GLO-30） | -16.14 | [Worldview](https://worldview.earthdata.nasa.gov/?v=87.62,31.12,87.82,31.33&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01) · [衛星圖](https://www.google.com/maps/@31.2250,87.7250,12000m/data=!3m1!1e3) · 圖 `zoom_protonilus_3.png` |
