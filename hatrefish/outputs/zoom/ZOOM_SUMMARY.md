# 放大結果（自動產生）

> 產生時間 2026-11-14 15:50，由 `scripts/zoom_candidates.py` 產生；數字以 `outputs/zoom/zoom_*.json` 為準。
> 每個候選地以 0.1° 格為中心取方框，在約 1 km 子格重算坡度、粗糙度、溫度、乾燥度、NDVI、熱慣量；岩性、永凍土、沙塵沿用所在 0.1° 格。計分方法和全球版完全相同（面向等權重）。
> 「0.1° 格內 1 km 中位數」和「0.1° 原分數」的差，是換資料（地形 GMTED → Copernicus）和換尺度本身造成的，不是找到更好的地點；看「最佳 1 km」要和這個中位數比。
> 高解析坡度與雷達是最佳小區 1 km 方塊內的統計（R1 在全球尺度評估不了的部分），只列出、不計分；SkyFall 要求 1–5 m 尺度坡度 < 15°。坡度解析度：北緯 60° 以北 2 m、南緯 60° 以南 8 m、其他 30 m。

## Arcadia Planitia AP-105 (SkyFall design reference landing site)（整體前幾名；子格 0.01°，方框半寬 0.25°，地形 copernicus）

| 候選 | 0.1° 格 | 0.1° 原分數 | 0.1° 格內 1 km 中位數 | 最佳 1 km 子格 | 1 km 分數 | 最弱面向 | 框內 ≥ 原分數 | 高解析坡度 p50／p90 | 雷達 VV（dB） | 連結 |
|---|---|---|---|---|---|---|---|---|---|---|
| #1 46 km from Urdgol (MN) | 48.25, 92.65 | 88.7 | 71.6 | 48.245, 92.625（46 km from Urdgol (MN)） | 89.6 | 環境極端 | 0% | 0.86°／1.92°（Copernicus GLO-30） | -17.48 | [Worldview](https://worldview.earthdata.nasa.gov/?v=92.53,48.14,92.72,48.34&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01) · [衛星圖](https://www.google.com/maps/@48.2450,92.6250,12000m/data=!3m1!1e3) · 圖 `zoom_ap105_1.png` |
| #2 near Kosh-Agach (RU) | 49.95, 88.65 | 85.0 | 85.6 | 49.935, 88.675（near Kosh-Agach (RU)） | 86.5 | 地表物質與裸露 | 3% | 0.7°／1.49°（Copernicus GLO-30） | -16.06 | [Worldview](https://worldview.earthdata.nasa.gov/?v=88.58,49.84,88.77,50.04&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01) · [衛星圖](https://www.google.com/maps/@49.9350,88.6750,12000m/data=!3m1!1e3) · 圖 `zoom_ap105_2.png` |
| #3 49 km from Zhabu (CN) | 33.45, 82.95 | 85.0 | 83.7 | 33.415, 82.995（44 km from Zhabu (CN)） | 87.6 | 地表物質與裸露 | 0% | 0.8°／1.76°（Copernicus GLO-30） | -18.12 | [Worldview](https://worldview.earthdata.nasa.gov/?v=82.90,33.31,83.09,33.52&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01) · [衛星圖](https://www.google.com/maps/@33.4150,82.9950,12000m/data=!3m1!1e3) · 圖 `zoom_ap105_3.png` |

## Arcadia Planitia (shallow ground ice)（整體前幾名；子格 0.01°，方框半寬 0.25°，地形 copernicus）

| 候選 | 0.1° 格 | 0.1° 原分數 | 0.1° 格內 1 km 中位數 | 最佳 1 km 子格 | 1 km 分數 | 最弱面向 | 框內 ≥ 原分數 | 高解析坡度 p50／p90 | 雷達 VV（dB） | 連結 |
|---|---|---|---|---|---|---|---|---|---|---|
| #1 46 km from Urdgol (MN) | 48.25, 92.65 | 83.2 | 70.0 | 48.215, 92.655（42 km from Urdgol (MN)） | 84.3 | 大氣與沙塵 | 0% | 0.7°／2.05°（Copernicus GLO-30） | -14.2 | [Worldview](https://worldview.earthdata.nasa.gov/?v=92.56,48.12,92.75,48.32&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01) · [衛星圖](https://www.google.com/maps/@48.2150,92.6550,12000m/data=!3m1!1e3) · 圖 `zoom_arcadia_1.png` |
| #2 208 km from Pevek (RU) | 67.85, 170.95 | 81.6 | 79.3 | 67.715, 171.055（223 km from Pevek (RU)） | 81.8 | 環境極端 | 0% | 0.81°／1.81°（ArcticDEM v3 2 m） | -12.46 | [Worldview](https://worldview.earthdata.nasa.gov/?v=170.96,67.62,171.16,67.81&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01) · [衛星圖](https://www.google.com/maps/@67.7150,171.0550,12000m/data=!3m1!1e3) · 圖 `zoom_arcadia_2.png` |
| #3 131 km from Jumla (NP) | 30.25, 82.95 | 81.2 | 81.1 | 30.325, 82.965（139 km from Jumla (NP)） | 82.7 | 地表物質與裸露 | 2% | 0.54°／0.95°（Copernicus GLO-30） | -18.07 | [Worldview](https://worldview.earthdata.nasa.gov/?v=82.87,30.22,83.06,30.43&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01) · [衛星圖](https://www.google.com/maps/@30.3250,82.9650,12000m/data=!3m1!1e3) · 圖 `zoom_arcadia_3.png` |

## Gale Crater（整體前幾名；子格 0.01°，方框半寬 0.25°，地形 copernicus）

| 候選 | 0.1° 格 | 0.1° 原分數 | 0.1° 格內 1 km 中位數 | 最佳 1 km 子格 | 1 km 分數 | 最弱面向 | 框內 ≥ 原分數 | 高解析坡度 p50／p90 | 雷達 VV（dB） | 連結 |
|---|---|---|---|---|---|---|---|---|---|---|
| #1 near Altanteel (MN) | 47.05, 92.85 | 88.2 | 77.4 | 47.065, 92.815（near Altanteel (MN)） | 88.4 | 地表物質與裸露 | 0% | 5.42°／6.18°（Copernicus GLO-30） | -9.11 | [Worldview](https://worldview.earthdata.nasa.gov/?v=92.72,46.96,92.91,47.16&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01) · [衛星圖](https://www.google.com/maps/@47.0650,92.8150,12000m/data=!3m1!1e3) · 圖 `zoom_gale_1.png` |
| #2 111 km from Barkol (CN) | 43.75, 91.65 | 87.7 | 84.3 | 43.615, 91.555（112 km from Mori (CN)） | 88.3 | 環境極端 | 0% | 17.86°／29.64°（Copernicus GLO-30） | -11.74 | [Worldview](https://worldview.earthdata.nasa.gov/?v=91.46,43.52,91.66,43.72&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01) · [衛星圖](https://www.google.com/maps/@43.6150,91.5550,12000m/data=!3m1!1e3) · 圖 `zoom_gale_2.png` |
| #3 near Bayinbaolige (CN) | 41.05, 106.95 | 86.6 | 48.0 | 41.175, 106.725（30 km from Bayinbaolige (CN)） | 86.7 | 地表物質與裸露 | 0% | 16.39°／25.08°（Copernicus GLO-30） | -11.21 | [Worldview](https://worldview.earthdata.nasa.gov/?v=106.62,41.07,106.82,41.27&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01) · [衛星圖](https://www.google.com/maps/@41.1750,106.7250,12000m/data=!3m1!1e3) · 圖 `zoom_gale_3.png` |

## Jezero Crater（整體前幾名；子格 0.01°，方框半寬 0.25°，地形 copernicus）

| 候選 | 0.1° 格 | 0.1° 原分數 | 0.1° 格內 1 km 中位數 | 最佳 1 km 子格 | 1 km 分數 | 最弱面向 | 框內 ≥ 原分數 | 高解析坡度 p50／p90 | 雷達 VV（dB） | 連結 |
|---|---|---|---|---|---|---|---|---|---|---|
| #1 33 km from Urdgol (MN) | 48.05, 92.95 | 90.4 | 81.1 | 48.035, 92.995（34 km from Urdgol (MN)） | 88.3 | 地表物質與裸露 | 0% | 2.44°／5.08°（Copernicus GLO-30） | -16.32 | [Worldview](https://worldview.earthdata.nasa.gov/?v=92.90,47.93,93.09,48.13&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01) · [衛星圖](https://www.google.com/maps/@48.0350,92.9950,12000m/data=!3m1!1e3) · 圖 `zoom_jezero_1.png` |
| #2 203 km from Turkmenbasy (TM) | 41.65, 54.05 | 90.4 | 83.3 | 41.655, 54.025（203 km from Turkmenbasy (TM)） | 90.9 | 環境極端 | 0% | 1.81°／8.31°（Copernicus GLO-30） | -13.43 | [Worldview](https://worldview.earthdata.nasa.gov/?v=53.92,41.55,54.12,41.76&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01) · [衛星圖](https://www.google.com/maps/@41.6550,54.0250,12000m/data=!3m1!1e3) · 圖 `zoom_jezero_2.png` |
| #3 30 km from Jetaral (CN) | 47.15, 87.05 | 89.7 | 83.5 | 47.135, 87.135（near Jetaral (CN)） | 90.3 | 環境極端 | 0% | 1.46°／3.09°（Copernicus GLO-30） | -14.97 | [Worldview](https://worldview.earthdata.nasa.gov/?v=87.04,47.03,87.23,47.23&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01) · [衛星圖](https://www.google.com/maps/@47.1350,87.1350,12000m/data=!3m1!1e3) · 圖 `zoom_jezero_3.png` |

## Meridiani Planum (Opportunity landing site, Eagle crater)（整體前幾名；子格 0.01°，方框半寬 0.25°，地形 copernicus）

| 候選 | 0.1° 格 | 0.1° 原分數 | 0.1° 格內 1 km 中位數 | 最佳 1 km 子格 | 1 km 分數 | 最弱面向 | 框內 ≥ 原分數 | 高解析坡度 p50／p90 | 雷達 VV（dB） | 連結 |
|---|---|---|---|---|---|---|---|---|---|---|
| #1 127 km from Mazongshan (CN) | 42.85, 97.65 | 89.6 | 89.1 | 42.905, 97.595（131 km from Mazongshan (CN)） | 90.8 | 環境極端 | 3% | 4.55°／8.57°（Copernicus GLO-30） | -11.05 | [Worldview](https://worldview.earthdata.nasa.gov/?v=97.50,42.80,97.69,43.01&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01) · [衛星圖](https://www.google.com/maps/@42.9050,97.5950,12000m/data=!3m1!1e3) · 圖 `zoom_meridiani_1.png` |
| #2 92 km from Wentugaole (CN) | 42.25, 102.05 | 89.6 | 88.5 | 42.235, 102.025（90 km from Wentugaole (CN)） | 90.4 | 環境極端 | 3% | 4.96°／9.2°（Copernicus GLO-30） | -11.34 | [Worldview](https://worldview.earthdata.nasa.gov/?v=101.93,42.13,102.12,42.34&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01) · [衛星圖](https://www.google.com/maps/@42.2350,102.0250,12000m/data=!3m1!1e3) · 圖 `zoom_meridiani_2.png` |
| #3 near Takeshiken (CN) | 45.95, 90.65 | 89.4 | 88.2 | 45.955, 90.515（38 km from Agax Obo (CN)） | 90.1 | 環境極端 | 0% | 2.45°／11.1°（Copernicus GLO-30） | -14.16 | [Worldview](https://worldview.earthdata.nasa.gov/?v=90.42,45.85,90.61,46.05&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01) · [衛星圖](https://www.google.com/maps/@45.9550,90.5150,12000m/data=!3m1!1e3) · 圖 `zoom_meridiani_3.png` |

## Oxia Planum (ExoMars Rosalind Franklin landing site)（整體前幾名；子格 0.01°，方框半寬 0.25°，地形 copernicus）

| 候選 | 0.1° 格 | 0.1° 原分數 | 0.1° 格內 1 km 中位數 | 最佳 1 km 子格 | 1 km 分數 | 最弱面向 | 框內 ≥ 原分數 | 高解析坡度 p50／p90 | 雷達 VV（dB） | 連結 |
|---|---|---|---|---|---|---|---|---|---|---|
| #1 125 km from Shumanay Shahri (UZ) | 41.85, 57.85 | 90.9 | 82.5 | 41.685, 57.805（141 km from Shumanay Shahri (UZ)） | 91.2 | 環境極端 | 0% | 0.41°／1.07°（Copernicus GLO-30） | -19.83 | [Worldview](https://worldview.earthdata.nasa.gov/?v=57.70,41.59,57.91,41.79&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01) · [衛星圖](https://www.google.com/maps/@41.6850,57.8050,12000m/data=!3m1!1e3) · 圖 `zoom_oxia_1.png` |
| #2 58 km from Turkmenbasy (TM) | 39.55, 53.25 | 90.5 | 79.1 | 39.365, 53.145（75 km from Turkmenbasy (TM)） | 90.7 | 環境極端 | 0% | 0.33°／1.2°（Copernicus GLO-30） | -19.39 | [Worldview](https://worldview.earthdata.nasa.gov/?v=53.05,39.27,53.25,39.47&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01) · [衛星圖](https://www.google.com/maps/@39.3650,53.1450,12000m/data=!3m1!1e3) · 圖 `zoom_oxia_2.png` |
| #3 near Gazojak (TM) | 41.15, 61.45 | 89.9 | 84.9 | 41.165, 61.555（near Gazojak (TM)） | 89.6 | 環境極端 | 0% | 0.28°／2.6°（Copernicus GLO-30） | -18.96 | [Worldview](https://worldview.earthdata.nasa.gov/?v=61.45,41.06,61.66,41.27&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01) · [衛星圖](https://www.google.com/maps/@41.1650,61.5550,12000m/data=!3m1!1e3) · 圖 `zoom_oxia_3.png` |

## Protonilus Mensae (candidate human exploration zone, buried glacial ice)（整體前幾名；子格 0.01°，方框半寬 0.25°，地形 copernicus）

| 候選 | 0.1° 格 | 0.1° 原分數 | 0.1° 格內 1 km 中位數 | 最佳 1 km 子格 | 1 km 分數 | 最弱面向 | 框內 ≥ 原分數 | 高解析坡度 p50／p90 | 雷達 VV（dB） | 連結 |
|---|---|---|---|---|---|---|---|---|---|---|
| #1 93 km from Maindong (CN) | 30.95, 84.55 | 89.9 | 73.0 | 30.805, 84.505（105 km from Maindong (CN)） | 87.7 | 地表物質與裸露 | 0% | 4.07°／7.2°（Copernicus GLO-30） | -16.27 | [Worldview](https://worldview.earthdata.nasa.gov/?v=84.41,30.70,84.60,30.91&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01) · [衛星圖](https://www.google.com/maps/@30.8050,84.5050,12000m/data=!3m1!1e3) · 圖 `zoom_protonilus_1.png` |
| #2 81 km from Zhabu (CN) | 32.45, 82.95 | 88.7 | 70.1 | 32.465, 82.935（80 km from Zhabu (CN)） | 88.7 | 環境極端 | 0% | 4.33°／5.42°（Copernicus GLO-30） | -14.45 | [Worldview](https://worldview.earthdata.nasa.gov/?v=82.84,32.37,83.03,32.57&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01) · [衛星圖](https://www.google.com/maps/@32.4650,82.9350,12000m/data=!3m1!1e3) · 圖 `zoom_protonilus_2.png` |
| #3 80 km from Jiajuedibu (CN) | 31.35, 87.95 | 87.9 | 73.9 | 31.395, 87.905（86 km from Jiajuedibu (CN)） | 89.2 | 環境極端 | 0% | 3.95°／9.57°（Copernicus GLO-30） | -16.68 | [Worldview](https://worldview.earthdata.nasa.gov/?v=87.81,31.29,88.00,31.50&l=MODIS_Terra_CorrectedReflectance_TrueColor,Coastlines_15m&t=2024-07-01) · [衛星圖](https://www.google.com/maps/@31.3950,87.9050,12000m/data=!3m1!1e3) · 圖 `zoom_protonilus_3.png` |
