# Data contract / 團隊資料交接

`seed/` 分為 catalog 管理的任務定義，以及 measurements 管理的量測檔。**目前 17 個目標與 20 個候選的特徵數值全部是 placeholder**，不是衛星觀測、場址驗證或科學發現。Demo 座標僅用來驗證地圖，不表示該地符合任務需求。

## 替換成真實資料

1. 編輯 `tasks_moon.yaml` / `tasks_mars.yaml` 的特徵定義與來源；確認來源產品、版本、解析度、時間、品質旗標與單位。現有來源多為入口頁，未用的 11 項官方 Resources 也保留在列表。
2. 候選資料存於 `earth_candidates.demo.json`（檔名為既有讀取契約，即使換真實資料也可沿用）。目標資料存於 `target_values.demo.yaml`，key 必須對應 `target_sites.yaml` 的 id。
3. 只在完成來源及品質檢查後，將該筆 `is_placeholder` 改為 `false`。混用任何 placeholder，結果仍顯示警示。若目標整筆缺失，API 會改用同任務可用的 placeholder 並回傳 warning；若無示範替代，回傳 422。
4. 重啟 catalog、measurements、similarity 與 planning；HTTP 定義與量測快取預設 60 秒，重啟可立即更新。執行 pytest 檢查資料契約。新增正式資料後，示範 fixture 數量驗收測試需分離。

每個候選必要欄位：`id`, `name`, `lat` (−90…90), `lon` (−180…180), `known_analog`, `is_placeholder`。可加 `name_en`；缺少英文回退中文。

```json
{
  "id": "reviewed-site-001", "name": "待驗證場址", "name_en": "Site pending review",
  "lat": 36.0, "lon": -116.0,
  "known_analog": false, "is_placeholder": true,
  "values": {"m1_slope": 7.2},
  "categories": {"m6_permafrost": "yes"},
  "spectra": {"m5_vswir_mineral": [0.2, 0.4, 0.3]},
  "series": {"m2_sun_elevation": {
    "phase": [0.0, 0.25, 0.5, 0.75], "values": [-2, 4, 8, 4],
    "step_hours": 1, "period": "local_solar_day"
  }},
  "planet_values": {}
}
```

此例也是 placeholder；光譜波段數只是格式示例，不可直接拿來作真實比較。實際目標與地球光譜須有相同波長網格及校正流程，目前 ingest 不會自動重採樣。

- `values`: absolute 使用物理值；relative_rank 的**目標**填團隊指定的百分位 0–1，**地球候選**填地球原始值，由固定完整候選母體計算百分位。
- relative_rank 的時間序列：目標同時在 `values[feature_id]` 填指定百分位，在 `series` 保留原始序列以供圖表；候選統計量由 series 依 `stat` 萃取。
- `planet_values`: 行星專屬條件的原始物理值，例如岩石率 .03、熱慣量 160；獨立於百分位，不套用到地球。
- `categories`: 使用 `categorical_tables.yaml` 中的字串。未知配對為缺值。YAML 的 yes/no 請加引號，避免被轉成布林。
- `spectra`: 一維數組、相同波長網格。零向量不可評分，會回傳 warning。
- `series`: phase 依序遞增、建議 [0,1)；values 長度一致且不可空；step_hours 是統計時數的採樣間隔，真實月球／火星資料須按各自週期換算，不可沿用示範的 1 小時。
- 缺值用 `null` 或省略對應 feature key；不使用 NaN / Infinity。API 顯示資料不足與可評分特徵數，不會編造值。
- 行星目標座標使用東經 0–360；介面轉為 −180–180。所有月球座標仍為 null / todo。AP-105 與工程限制是團隊提供的設計參考案例，尚未逐項核對原始文獻。

若從 CSV 匯入，先轉為以上 JSON/YAML 契約；此原型未實作通用 CSV 匯入器。

## 新增特徵或任務

在對應 tasks YAML 增加唯一 id，補 `type` / `compare_mode` / 權重 / 來源 / notes，並在目標及候選新增值。絕對 threshold 需要 `{ideal_max, zero_at}` 或 `{zero_at, ideal_min}`；類別型需補對照表。資料來源的 `used_by` 也要加入新 id。新增任務必須有唯一 order；請一併調整請求 task_ids 數量上限（原型 6）。

新評分演算法加在 `services/similarity/app/core/scoring.py` 的 `SCORERS`；選址與敏感度在 `services/planning/app/core/`。其餘方法見 `docs/METHOD.md`。服務分工見 `docs/SERVICES.md`。不要把科學內容放入 Vue 元件。

## 重建示範資料

```powershell
.\.venv\Scripts\python.exe scripts/generate_seed.py
```

**這會覆寫 seed 全部內容**，只在刻意重置時執行。使用 Python random seed=42，從保存的 `docs/SPEC.md` 解析任務表，再產生確定性的示範數值。
