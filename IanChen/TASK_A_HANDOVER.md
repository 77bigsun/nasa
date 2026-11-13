# 任務 A（火星端）交接說明

> 給 B 和其他隊友。寫的人：IanChen。日期：2026-11-13。
> 對照文件：`hatrefish/docs/TASK_A_mars.md`（我的任務）、`hatrefish/docs/TASK_B_earth.md`（B 的任務）。

## 一句話版本

任務 A 的 A1–A7 都做完了，A8（細地形）只完成一半（只有 Gale 有資料）。三個火星目標的數值、百分位表、岩性相似度表、已知類比地清單、資料出處，全部放在 `IanChen/` 底下，**B 可以直接開始用，不用等我**。

有兩件事要在 11/13 晚上 21:00 的會議一起決定：**目標座標**要不要照現在這組、**Gale 的熱慣量**為什麼和 B 量到的差很多（見下面「要一起決定的事」）。

---

## 1. 我做了什麼

| 編號 | 任務 | 狀態 | 檔案（都在 `IanChen/` 底下） |
|---|---|---|---|
| A1 | 三個目標的座標 | 完成，**待會議確認** | `config/targets.yaml` |
| A2 | 火星擷取器 | 完成 | `src/mars_analog/mars_features.py`、`src/mars_analog/adapters/mars/` |
| A3 | 火星百分位表 | 完成 | `data/processed/mars_reference_pct.json` |
| A4 | 三個目標的數值 | 完成 | `data/processed/mars_targets.json` |
| A5 | 岩性相似度表 | 完成 | `data/mappings/sim3292_unit_groups.csv`、`lithology_mars_to_glim.csv` |
| A6 | 已知類比地清單 | 完成，28 個（要求至少 20） | `data/labels/known_analogs.csv`、`known_analogs_notes.md` |
| A7 | 資料出處 | 完成 | `docs/DATA_SOURCES.md` |
| A8（選做） | 更細的地形 | **只有 Gale** | 見下面第 4 節 |

另外附上的檔案：`config/targets_alt.yaml`、`targets_check.yaml`（備選座標、和 B 的參考值比對用）、`data/processed/mars_targets_alt.json`、`mars_targets_check.json`、`scripts/run_task_a.py`（一鍵執行）。

## 2. 三個目標的數值（`mars_targets.json`）

座標用 `targets.yaml` 原本那組：Jezero (18.4, 77.5)、Gale (−5.4, 137.8)，半徑 25 km；Arcadia (47.2, −175.7)，半徑 50 km。

| 變數 | Jezero | Gale | Arcadia |
|---|---|---|---|
| slope 坡度（°，200 m） | 2.236 | 5.455 | 0.209 |
| roughness 粗糙度（m，5×5 視窗 ≈ 1 km） | 10.608 | 27.254 | 1.008 |
| thermal_inertia 熱慣量（tiu）／百分位 | 296 ／ 0.877 | 283 ／ 0.843 | 233 ／ 0.640 |
| lithology 岩性（SIM3292 代碼 → 大類） | HNt → clastic | Htu → clastic | Av → basalt |
| ice 冰（SWIM）／ p | −0.206 ／ 0.397 | 0.059 ／ 0.529 | 0.526 ／ 0.763 |
| temperature 年均地表溫度（°C） | −49.47 | −50.85 | −75.93 |
| diurnal_range 日溫差（°C） | 84.69 | 93.30 | 62.61 |
| dust 沙塵 τ ／ 百分位 | 0.554 ／ 0.869 | 0.464 ／ 0.735 | 0.355 ／ 0.415 |
| aridity 乾燥度 | max（固定） | max（固定） | max（固定） |
| barrenness 荒蕪度（NDVI） | 0（固定） | 0（固定） | 0（固定） |
| slope_fine／roughness_fine（30 m） | 沒資料 | 5.396° ／ 4.078 m | 沒資料 |

每個變數都有 `value`、`coverage`、`source`、`n_pixels`。熱慣量和沙塵另有 `pct`，冰另有 `p`，岩性另有 `group`。沒資料的是 `coverage: false`、`value: null`，沒有填 0。

**請注意定義**：粗糙度是「5×5 像素視窗的高程標準差，再取範圍內中位數」（照 TASK_A 的規定）。這和我之前舊腳本用的 3×3 去趨勢版本不同，所以數字不一樣（舊的 Jezero 是 1.75 m，現在是 10.6 m）。**地球端要用完全一樣的定義**（B2 已經這樣寫了）。

## 3. 和 B 之前量的參考值比對

| | Jezero（B 的／我的） | Gale | Arcadia |
|---|---|---|---|
| 熱慣量 | 281 ／ 296 | **433 ／ 283** | 241 ／ 233 |
| 冰（SWIM） | −0.19 ／ −0.206 | 0.06 ／ 0.059 | 0.51 ／ 0.526 |
| 溫度（°C） | −49.5 ／ −49.47 | −50.9 ／ −50.85 | −75.9 ／ −75.93 |
| 沙塵（百分位） | 0.55（0.87）／ 0.554（0.869） | 0.46（0.73）／ 0.464（0.735） | 0.35（0.42）／ 0.355（0.415） |

冰、溫度、沙塵幾乎一致。**只有熱慣量不一致，尤其 Gale（433 對 283）**，原因還不知道，可能是用了白天或夜間不同的圖、不同的統計量，或不同的範圍。

## 4. 細地形（A8）的結果

| 目標 | 細資料 | 結果 |
|---|---|---|
| Gale | 30 m HRSC DTM（Zenodo，CC BY 4.0） | 有值：坡度 5.40°、粗糙度 4.08 m，涵蓋 100% |
| Jezero | 20 m CTX DTM（USGS），平均到 30 m | **沒資料**：這份檔案只涵蓋 25 km 圓的約 46%，低於門檻 50%。只算涵蓋到的部分，坡度約 3.33°，但沒有採用 |
| Arcadia | 沒有現成的細資料 | 沒資料，維持 200 m，結果裡要註明（照 TASK_A） |

細地形是 30 m 搭配 5×5（150 m）視窗，**只能和地球端同尺度的資料比**（Copernicus GLO-30、5×5 視窗），不能和 200 m 的坡度、粗糙度混用。

要補 Jezero，需要範圍更大的 USGS「Mars 2020 Science Investigation CTX DEM Mosaic」，現在還沒下載。

## 5. B 接下來可以做什麼（對照 TASK_B）

| B 的任務 | 現在可以怎麼接 |
|---|---|
| **B1 骨架** | 先把我的程式接進 `hatrefish/src/mars_analog/`：複製 `adapters/mars/`、`mars_features.py`、`mars_reference.py`、`paths.py`。**不要覆蓋 B 的 `__init__.py`**（我的 `__init__.py` 只有說明文字）。我的 adapter 是用 `adapter(name).load(lat, lon, radius_km, cfg)` 呼叫，沒有用 B 的 `registry.py` 註冊；要註冊的話，在 `adapters/mars/__init__.py` 包一層就可以，需要我配合隨時說。 |
| **B2、B3 地球資料與網格** | 地球端要和火星端同定義：坡度、粗糙度都在 200 m 算，粗糙度用 5×5 視窗，範圍內取中位數。熱慣量和沙塵比的是「在自己星球的百分位」，火星這邊的百分位表是 TES 夜間圖、用 cos(緯度) 加權算的。 |
| **B4 單項相似度** | `mars_targets.json` 可以直接讀，不用再手寫臨時版本。岩性：先用 `sim3292_unit_groups.csv` 把 Unit 轉成大類（結果檔的 `group` 欄位已經轉好），再查 `lithology_mars_to_glim.csv`，查不到給 0.1。冰：`p`，已經算好。 |
| **B5 總分** | 沒有需要我這邊配合的地方。 |
| **B6、B7 驗證與學權重** | `known_analogs.csv` 有 28 筆，超過「少於 20 個就不學權重」的門檻。正樣本：`mars_target_ids` 包含該目標的列。 |
| **B8 標記新候選地** | 同一份 `known_analogs.csv`，50 km 內視為已知。 |
| **B9 先粗後細** | 現在只有 **Gale** 有細地形值（`slope_fine`、`roughness_fine`）。Jezero 要等補上更大的 CTX 檔，Arcadia 維持 200 m。 |
| **B10 輸出** | 「哪裡不像」可以直接用 `mars_targets.json` 裡的原始數值（例如溫度 −49.47 °C）。 |

要把設定接起來的話：`features.yaml` 裡的 `data/mappings/...` 是相對於專案根目錄寫的，所以把 `IanChen/data/mappings/`、`data/labels/` 也複製到 `hatrefish/data/` 底下（或者改路徑）。

## 6. 怎麼重新跑

好消息：我的程式用到的套件（`geopandas`、`rasterio`、`pyproj`、`shapely`、`scipy`、`requests`、`pyyaml`、`numpy`）都已經在 B 的 `environment.yml`（環境名稱 `analog`）裡，不用另外裝。

```bash
conda activate analog
cd IanChen
python scripts/run_task_a.py targets            # 重新算 mars_targets.json
python scripts/run_task_a.py point 0 0 25       # 任意火星座標（緯度 經度 半徑km）
python scripts/run_task_a.py reference          # 重新算百分位表
python scripts/run_task_a.py check              # 和 B 的參考值比對
```

**重新跑需要原始資料**，這些檔案太大，沒有放進 git（`data/raw/` 被忽略）：

| 資料 | 大小 | 放哪裡 |
|---|---|---|
| SIM3292 地質圖 | 約 833 MB | `data/raw/mars/sim3292/` |
| TES 熱慣量圖 | 約 49 MB | `data/raw/mars/tes/` |
| SWIM 冰（沒有的話會改讀網路上的檔案） | 約 68 MB | `data/raw/mars/swim/` |
| 細地形 DEM（Jezero、Gale） | 約 307 MB | `data/raw/mars/fine/` |
| MCD 氣候查詢（會自動快取，每次查詢會暫停一下，不要狂跑） | 很小 | `data/raw/mars/mcd/` |

下載連結在 `docs/DATA_SOURCES.md`，或直接跟我拿。**只是要用現成的數值，不需要重新跑。**

## 7. 已知問題與注意事項

- **已知類比地清單**：28 筆都有查到文獻來源（`verified = true` 的意思是我確認過有文獻支持，來源寫在 `known_analogs_notes.md`）。**但很多座標只是我估的研究區中心**，筆記裡標了 approx；`hiseas_mauna_loa` 的來源網頁只在搜尋結果裡看到，直接開被伺服器拒絕。拿來驗證時請知道這一點。
- **岩性**：SIM3292 的單位是依年代和地形分的，不是依礦物，所以全球尺度分不出碳酸鹽、黏土和硫酸鹽。`sedimentary_carbonate_clay` 這類大類還留在對照表裡，但沒有任何 SIM3292 單位被歸到那邊。Jezero 和 Gale 目前都被歸在 `clastic`。
- **Gale 的座標**：Curiosity 的 Bradbury 著陸點（−4.59, 137.44）離這個圓心約 48 km，在 25 km 圓的外面。這個圓涵蓋的是坑底和 Mount Sharp 山腳，不是著陸點。
- **MCD 氣候值**：是目標中心點的單點值，來自約 5 度的粗網格，半徑沒有用。
- **原始 `data/raw` 沒有 commit**，所以另一台電腦 clone 之後，要先放好資料才能重新跑（見第 6 節）。

## 8. 11/13 會議要決定的事

1. **座標**：Jezero (18.4, 77.5)、Gale (−5.4, 137.8)、Arcadia (47.2, −175.7) 照現在這組嗎？Arcadia 另有一個 SWIM 試驗區中心的備選（`targets_alt.yaml`，冰指標較高，0.65）。座標一換，所有數值和 B 的排名都會跟著變，所以兩邊必須用同一組。
2. **Gale 熱慣量**（283 對 433）：B 當初怎麼量的（哪一張圖、哪一個統計量、什麼範圍）？
3. **Jezero 細地形**：要不要下載更大的 CTX 檔補上？
4. **程式怎麼合併**：由 B 複製進 `hatrefish/`，還是我來移？

---

## AI 輔助聲明

擷取器程式、對照表草稿和 `DATA_SOURCES.md` 是在 AI 程式助理（Claude，Anthropic）的協助下寫的。岩性分類和相似度分數是草稿，團隊要自己審過並負責。（NASA Space Apps 規定要揭露資料與程式中使用 AI。）
