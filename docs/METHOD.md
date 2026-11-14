# 相似度方法 / Similarity method

這是團隊可替換的初版方法。網站使用固定種子產生的 **placeholder**；計算結果只能驗證流程，不能支持真實世界場址發現。This prototype uses synthetic measurements, not scientific findings.

## 01 · 從任務到特徵 / From mission to evidence

每個分支任務由設定檔中的特徵定義組成。行星資料與地球資料的來源、代理指標、單位、比較模式及限制會一起回傳。資料入口列於 `/data`，目前不代表已完成衛星資料下載或產品級品質審查。

任務定義唯一來源是 catalog，量測數值由 measurements 提供。評分演算法集中在 `services/similarity/app/core/`，選址與敏感度在 `services/planning/app/core/`；planning 經 HTTP 使用 similarity 的評分結果。跨星球值不在同一物理尺度時，只能採用團隊定義的百分位比較。相對模式的目標值必須為 0–1。

## 02 · 五類評分 / Five feature scorers

門檻型使用線性滿意度。低值較佳時，理想值以下得 1、零點以上得 0，中間線性遞減；高值較佳則反向。Mars R1 provisional slope limits remain subject to source review. 行星端專屬門檻只檢查行星，不套用在地球代理值。

$$s=\mathrm{clip}\left(\frac{b-x}{b-a},0,1\right)$$

絕對剖面以完整地球候選母體的平均與標準差標準化，目標使用相同轉換。排除已知場址不改變母體。零變異時，完全相同得 1，否則得 0。目標超過地球母體平均三個標準差會發出警告。

$$s=\exp\left(-\frac{(z_c-z_t)^2}{2\sigma^2}\right)$$

相對百分位模式以地球 midrank ECDF 與行星的指定百分位比較。相同值的百分位採中位秩，避免 tie 造成不穩定。

$$s=\exp\left(-\frac{(p_c-p_t)^2}{2\sigma_{rank}^2}\right)$$

類別型查詢明示的相似度表；未知類別組合保留缺值。光譜型使用 Spectral Angle Mapper，須先對齊波長與解析度；真實產品的重採樣尚待 ingest 實作，不能將未對齊波段直接比較。

$$\theta=\arccos\frac{a\cdot b}{\|a\|\|b\|},\qquad s=\mathrm{clip}\left(1-\frac{\theta}{\pi/2},0,1\right)$$

時間序列先換成當地週期相位，再萃取設定指定的平均、極差、低溫時數、最長黑暗等統計量，依絕對或百分位模式評分。連續黑暗跨相位零點時視為同一段。圖表提供相位疊圖、ECDF 與 Wasserstein 距離；距離本身有原始資料單位，不直接等同相似度。

## 03 · 任務分數與權重 / Aggregation and weights

同任務特徵使用加權幾何平均。超出地球可重現範圍的特徵完全排除，並在詳情中說明。缺值不給分，顯示可用特徵數；全部缺值的任務為 null，整體分數保留其權重並計為零，以免缺證據反而提高名次。

$$S_{task}=\exp\left(\sum_i w_i\ln(\max(s_i,\epsilon))\right),\qquad \sum_i w_i=1$$

ROC 由團隊設定的 order 排序計算。等差與自訂非負權重也可用；只選部分任務時，會重新計算並正規化。技術缺口的 rank 與 order 是不同欄位，手動調整理由會顯示。原始 NASA 排名沿用提供規格，尚未逐項核對 Rev C 附錄。

$$w_k^{ROC}=\frac{1}{n}\sum_{i=k}^{n}\frac{1}{i},\qquad S_{overall}=\sum_k w_kS_k$$

## 04 · 最少地點與邊際效益 / Coverage optimization

當任務分數大於或等於 τ，該場址涵蓋該需求。PuLP + CBC 先最小化場址數，再固定最少數量，最大化各需求的最佳合格分數加權總和，加上設定中的同地整合加分。整合加分不會增加最小地點數，也不改變個別相似度。沒有候選達標的任務不進入覆蓋限制，列入 uncoverable。

$$\min\sum_jx_j,\qquad \sum_{j:S_{ij}\ge\tau}x_j\ge1$$

邊際效益採固定 k 的最大加權涵蓋率，k=1 至 min(任務數, 候選數)。20 個候選的原型以枚舉組合精確求解；相同涵蓋率時以品質取捨。未來大量候選需改用 MILP 或經證明的近似法，避免組合爆炸。

## 05 · 敏感度與穩健性 / Sensitivity and robustness

敏感度從對稱 Dirichlet(α) 抽樣權重（預設 500 次，seed 42），每次固定 k 為最小集合覆蓋地點數，解最大覆蓋。比例表示此方法下的入選頻率，不是統計信賴度，也不是對真實相似度的機率。固定種子讓結果可重現。

當至少有兩個可用的絕對 profile 特徵時，計算標準化後的正則化 Mahalanobis 距離，並與主要排名計算 Spearman 相關；候選數少於三個時不回報。交叉檢查不取代主要分數。

`tost_equivalence` 目前是獨立配對差值的探索性實作，不在主要評分或介面結論中使用。自相關時間序列應改採 block bootstrap；目前尚未實作，不能據此宣稱等效。

## 06 · 類比的界線 / What an analog cannot reproduce

低重力、真空或稀薄大氣、輻射及月塵靜電等限制不能靠地球場址重現。高分只代表所選特徵下的測試相似性，不代表整個星球或任務可被重現。

## 參考方法 / References

以下作者／年份沿用團隊規格，書目與原文連結待團隊確認；不表示已逐篇重現其論文方法。

- Derringer & Suich (1980), desirability functions.
- Gower (1971), general similarity coefficient.
- Kruse et al. (1993), spectral analysis / SAM.
- Barron & Barrett (1996), ROC weights.
- Mahalanobis (1936), generalized distance.
- Toregas et al. (1971), set covering.
- Church & ReVelle (1974), maximal covering.
- Lahdelma et al. (1998), SMAA.
- Ramdas et al. (2017), Wasserstein two-sample tests.
- Schuirmann (1987), TOST; Künsch (1989), block bootstrap.

## 官方資料 / Official data references

- [NASA Planetary Fact Sheet](https://nssdc.gsfc.nasa.gov/planetary/factsheet/)：太陽日與恆星日分開；主表 Mars 約 −65°C，介面以約 −60°C 表示量級。
- [NASA Moon Base User’s Guide entry](https://www.nasa.gov/moonbase-phases/)
- [NASA SkyFall](https://science.nasa.gov/mission/skyfall/)
- [NASA GIBS API](https://nasa-gibs.github.io/gibs-api-docs/)

查閱日：2026-11-14。精確工程數值、產品覆蓋、波段對齊、原始 NASA 排名與任務時程仍需團隊逐項審核。
