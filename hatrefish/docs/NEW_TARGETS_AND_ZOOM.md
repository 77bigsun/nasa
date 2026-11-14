# 新火星目標與放大程式（11/14，B）

## 1. 新增三個火星目標

用 IanChen 的擷取程式（`IanChen/src/mars_analog/mars_features.py`，原始資料：TES 夜間熱慣量 2007、SWIM4MIM Ci、SIM3292 全球地質圖、HRSC+MOLA 200 m DEM、MCD 網頁版）在雲端跑。
先重跑 Jezero（18.4, 77.5, 25 km）確認和 IanChen 的正式值**完全一致**：坡度 2.236°、粗糙度 10.608 m、TI 296（pct 0.877）、HNt、Ci −0.206、溫度 −49.47 °C、日溫差 84.69、沙塵 0.554（pct 0.869）。

| id | 名稱 | 緯度 | 經度 | 半徑 | 任務 | 座標出處 |
|---|---|---|---|---|---|---|
| oxia | Oxia Planum（ExoMars Rosalind Franklin 著陸區） | 18.20 | −24.55 | 25 km | geology, rover | ESA：18.20°N 335.45°E，https://exploration.esa.int/mars/54724-oxia-planum/ |
| meridiani | Meridiani Planum（Opportunity 著陸點 Eagle 坑） | −1.95 | −5.53 | 25 km | geology, rover | NASA/JPL：1.95°S 354.47°E，https://www.jpl.nasa.gov/images/rovers-landing-hardware-at-eagle-crater-mars |
| protonilus | Protonilus Mensae（人類探索區候選，埋藏冰河） | 41.905 | 48.548 | 50 km | isru_base, landing | Gallegos & Newsom 2015 EZ，IAC-17,A5,IP,1,x39861，https://iafastro.directory/iac/archive/browse/IAC-17/A5/IP/39861/ |

擷取結果：

| 變數 | oxia | meridiani | protonilus |
|---|---|---|---|
| 坡度 | 0.559° | 1.279° | 4.594° |
| 粗糙度 | 2.767 m | 6.363 m | 22.599 m |
| 熱慣量 | 416（pct 0.981） | 190（0.425） | 197（0.457） |
| 岩性（SIM3292 → 類別） | lNh → **sedimentary_carbonate_clay**（文獻覆寫） | HNhu → **evaporite_sulfate_clastic**（文獻覆寫） | HNt → clastic |
| 冰 Ci | −0.323 | 0.034 | 0.162 |
| 溫度 | −50.75 °C | −46.09 °C | −71.24 °C |
| 日溫差 | 77.07 | 95.43 | 79.45 |
| 沙塵 | 0.620（pct 0.961） | 0.521（0.826） | 0.339（0.361） |

**岩性文獻覆寫**：1:20M 全球地質圖分不出礦物，兩個漫遊車目標都被畫成「高地單元 → impact_breccia_carbonate」，但任務選這兩個地方正是因為礦物：
- Oxia：Fe/Mg 黏土層狀單元（Quantin-Nataf et al. 2021, Astrobiology 21(3):345, doi:10.1089/ast.2019.2191）
- Meridiani：富硫酸鹽砂岩與赤鐵礦小球（Squyres et al. 2004, Science 306:1709, doi:10.1126/science.1104559）

JSON 裡 `group` 是覆寫後的類別，`group_sim3292` 保留地圖原值，`group_source = literature_override`，`group_note` 寫出處。Jezero（三角洲碳酸鹽與黏土）也可以用同樣方式覆寫，目前沒有動。

檔案：
- 合併進 `data/processed/mars_targets.json`（現在 6 個目標）
- 合併前備份：`data/interim/mars_targets.before_1114_new.json`；新目標單獨檔：`data/interim/mars_targets_new_1114.json`
- 給 IanChen 的 targets.yaml 寫法（他要重抽時用）：

```yaml
  - {id: oxia, name: "Oxia Planum (ExoMars Rosalind Franklin landing site)", lat: 18.20, lon: -24.55, radius_km: 25, missions: [geology, rover]}
  - {id: meridiani, name: "Meridiani Planum (Opportunity landing site, Eagle crater)", lat: -1.95, lon: -5.53, radius_km: 25, missions: [geology, rover]}
  - {id: protonilus, name: "Protonilus Mensae (candidate human exploration zone)", lat: 41.905, lon: 48.548, radius_km: 50, missions: [isru_base, landing]}
```

## 2. 類比剖面結果（`outputs/profiles/`）

- **Oxia**：前幾名在中亞（最近城鎮：Shumanay 烏茲別克、Turkmenbasy 與 Gazojak 土庫曼、Priozersk 哈薩克），整體約 89–91。
- **Meridiani**：前幾名在中國西北與蒙古西部的戈壁（最近城鎮：馬鬃山 127 km、溫圖高勒 92 km、Bayan-Ovoo 45 km）。地表物質面向前 5 名是烏尤尼鹽沼（玻利維亞）、馬卡迪卡迪鹽沼（波札那）、傑里德鹽湖（突尼西亞）——硫酸鹽覆寫有作用。已知類比地中排最前的是柴達木大浪灘（全球前 0.4%）；文獻常說的 Meridiani 類比地 Rio Tinto 只在前 40.5%（地表 0.16、地形 0.41：0.1° 格內有植被和起伏）。
- **Protonilus**：前幾名在青藏高原西部（最近城鎮：Maindong、Zhabu、Jiajuedibu）、美國懷俄明（Rock Springs）、阿根廷（Las Heras）。SWIM Ci 在 50 km 圓內中位數只有 0.16，冰的目標值偏低，所以永凍土地區沒有被往前推；如果要「圓內某處有冰就算」，冰的目標要改用圓內高百分位，這是方法上的決定，還沒改。
- 新目標沒有標給它們的已知類比地 → 總表和雷達圖改列「全部已知類比地中全球排名最前的 8 個」，標題註明。

## 3. 發現的問題

1. **缺岩性的格子在排名上佔便宜**。GLiM 沒資料（`nd`）的陸地只佔 0.15%，但在整體前 20 名裡：Meridiani 11 個、Oxia 9 個、Jezero 5 個、Arcadia 1 個、Gale 和 Protonilus 0 個。原因：面向分數只平均「有資料的變數」，目標岩性越特別（蒸發岩、黏土），大部分 GLiM 類別分數越低，缺岩性的格子就越不會被扣分。這些格子多在乾掉的鹹海、羅布泊一帶（GLiM 還標成水體或沒資料）。可選的修法：(a) 排名池要求岩性有資料；(b) 缺的變數用該目標在全球陸地的中位分數補（不加分也不扣分）；(c) 維持現狀但在表上標出。**尚未決定，目前結果是未修正的版本。**
2. `outputs/profiles/*.json` 的 `cell_id` 之前寫的是表格列號，不是格子編號（地點座標和數值都正確，只有標籤錯）。已修正為真正的 `e_<iy*3600+ix>`。

## 4. 放大程式（`scripts/zoom_candidates.py`、`src/mars_analog/zoom.py`、`adapters/earth/gee_zoom.py`）

- 候選地：剖面結果的整體前 N 名（`--dimension` 改用某面向的前 N 名，`--point LAT LON` 手動座標）。
- 方框：以 0.1° 候選格為中心，南北半寬 0.25°，東西放寬為 0.25°/cos(緯度)，約 55 km 見方；子格 0.01°（約 1 km）。
- 在 GEE 重算到子格：坡度、粗糙度、海拔（Copernicus GLO-30 在當地 UTM 粗化到 200 m，`--dem gmted` 可改回全球版的 GMTED2010）；地表溫度、日夜溫差（MODIS 1 km）；反照率；NDVI（MOD13Q1 250 m）；乾燥指數；陸地／冰雪／水體比例。底圖用 NASA HLS（S30+L30，2022–2024 中位數，雲量 < 20%），沒有 HLS 的地方用 DEM 陰影。
- 岩性、永凍土、沙塵沿用每個子格所在的 0.1° 格。
- 百分位用全球 0.1° 參考分布換算；計分用和全球版相同的 `similarity_vector` 與 `profiles.score_table`（重構出來共用）。
- 每個候選列出框內最佳 3 個子格（彼此 ≥ 5 km），並記錄「同一 0.1° 格內子格的中位數」——它和 0.1° 原分數的差是換資料、換尺度造成的，最佳子格要和這個中位數比，不是和原分數比。
- 輸出 `outputs/zoom/`：`zoom_<目標>_<名次>.png`（底圖、子格分數、面向比較）、`zoom_<目標>.json`、`ZOOM_SUMMARY.md`（含 Worldview 與衛星圖連結）。方框快取在 `data/interim/zoom/`（和目標無關，換目標不重抓）。
- 已在雲端用合成資料測過計分、選點、畫圖、總表；GEE 的部分只能在本機跑（`--test` 先抓一個方框檢查）。
