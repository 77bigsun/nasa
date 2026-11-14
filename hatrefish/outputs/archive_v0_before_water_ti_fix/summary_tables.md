# 數字總表（自動產生）

## 每個任務的權重（先驗 → 最後）

| 變數 | geology 先驗 | geology 最後 | rover 先驗 | rover 最後 | isru_base 先驗 | isru_base 最後 | landing 先驗 | landing 最後 |
|---|---|---|---|---|---|---|---|---|
| slope | 0.05 | **0.07** | 0.25 | **0.15** | 0.10 | **0.07** | 0.30 | **0.30** |
| roughness | 0.10 | **0.05** | 0.25 | **0.15** | 0.05 | **0.04** | 0.30 | **0.30** |
| thermal_inertia | 0.10 | **0.05** | 0.20 | **0.12** | 0.10 | **0.07** | 0.15 | **0.15** |
| lithology | 0.35 | **0.16** | 0.05 | **0.03** | 0.05 | **0.04** | 0.00 | **0.00** |
| ice | 0.05 | **0.02** | 0.00 | **0.18** | 0.35 | **0.38** | 0.00 | **0.00** |
| temperature | 0.05 | **0.19** | 0.05 | **0.10** | 0.20 | **0.19** | 0.00 | **0.00** |
| diurnal_range | 0.00 | **0.11** | 0.00 | **0.02** | 0.00 | **0.01** | 0.00 | **0.00** |
| aridity | 0.10 | **0.05** | 0.05 | **0.05** | 0.05 | **0.05** | 0.05 | **0.05** |
| barrenness | 0.15 | **0.29** | 0.05 | **0.15** | 0.05 | **0.12** | 0.05 | **0.05** |
| dust | 0.05 | **0.02** | 0.10 | **0.06** | 0.05 | **0.04** | 0.15 | **0.15** |

## 學到的權重（資料證據）與 90% 信賴區間（以類比地為單位 bootstrap 200 次）

| 變數 | 全域（29 個類比地） | 90% CI | 地質專屬（24 個） | 90% CI |
|---|---|---|---|---|
| slope | 0.00 | 0.00–0.09 | 0.08 | 0.00–0.20 |
| roughness | 0.00 | 0.00–0.03 | 0.00 | 0.00–0.14 |
| thermal_inertia | 0.00 | 0.00–0.00 | 0.00 | 0.00–0.00 |
| lithology | 0.00 | 0.00–0.08 | 0.00 | 0.00–0.06 |
| ice | 0.45 | 0.20–0.56 | 0.00 | 0.00–0.00 |
| temperature | 0.17 | 0.00–0.40 | 0.31 | 0.01–0.48 |
| diurnal_range | 0.04 | 0.00–0.20 | 0.20 | 0.00–0.46 |
| aridity | 0.04 | 0.00–0.23 | 0.00 | 0.00–0.39 |
| barrenness | 0.30 | 0.12–0.44 | 0.41 | 0.15–0.58 |
| dust | 0.00 | 0.00–0.10 | 0.00 | 0.00–0.12 |

## 留一法（每次拿掉一個已知類比地，用其他的學權重）

| 任務 | 類比地數 | α | 學習來源 | 採用 | AUC 先驗 | AUC 最後(混合) | AUC 逐項相乘 | AUC 只用學到的 | 前10% 命中 先驗→最後 |
|---|---|---|---|---|---|---|---|---|---|
| geology | 24 | 0.55 | mission | blend | 0.667 | 0.704 | 0.726 | 0.702 | 0.32 → 0.34 |
| rover | 13 | 0.39 | global | blend | 0.620 | 0.770 | 0.829 | 0.801 | 0.28 → 0.48 |
| isru_base | 8 | 0.29 | global | blend | 0.579 | 0.753 | 0.748 | 0.806 | 0.25 → 0.25 |
| landing | 3 | 0.13 | global | prior | 0.686 | 0.684 | 0.806 | 0.842 | 0.67 → 0.33 |

## 驗證（已知類比地 vs 隨機陸地＋高植被；排名 = 在全球陸地的百分位）

| 目標 | 任務 | 類比地數 | AUC 先驗 | AUC 最後 | 前1% | 前5% | 前10% |
|---|---|---|---|---|---|---|---|
| jezero | geology | 24 | 0.639 | **0.719** | 0.04 | 0.17 | 0.33 |
| jezero | rover | 13 | 0.611 | **0.780** | 0.00 | 0.23 | 0.54 |
| jezero | isru_base | 25 | 0.543 | **0.629** | 0.00 | 0.08 | 0.24 |
| jezero | landing | 25 | 0.562 | **0.562** | 0.04 | 0.08 | 0.12 |
| gale | geology | 20 | 0.707 | **0.770** | 0.00 | 0.30 | 0.40 |
| gale | rover | 12 | 0.684 | **0.832** | 0.00 | 0.33 | 0.67 |
| gale | isru_base | 21 | 0.657 | **0.721** | 0.00 | 0.05 | 0.10 |
| gale | landing | 21 | 0.663 | **0.663** | 0.00 | 0.10 | 0.19 |
| arcadia | geology | 11 | 0.636 | **0.734** | 0.00 | 0.09 | 0.18 |
| arcadia | rover | 11 | 0.411 | **0.571** | 0.00 | 0.09 | 0.27 |
| arcadia | isru_base | 8 | 0.579 | **0.784** | 0.00 | 0.25 | 0.25 |
| arcadia | landing | 3 | 0.686 | **0.686** | 0.00 | 0.00 | 0.67 |

## 算法比較（AUC）

| 目標 | 任務 | A 全部直接比 | B 預設 | C 夾到地球範圍 | B 沙塵改直接比 | B + 日溫差 0.05 |
|---|---|---|---|---|---|---|
| jezero | geology | 0.684 | 0.719 | 0.712 | 0.721 | 0.720 |
| jezero | rover | 0.790 | 0.780 | 0.794 | 0.781 | 0.779 |
| gale | geology | 0.746 | 0.770 | 0.748 | 0.769 | 0.759 |
| gale | rover | 0.855 | 0.832 | 0.857 | 0.828 | 0.837 |
| arcadia | isru_base | 0.748 | 0.784 | 0.809 | 0.790 | 0.757 |
| arcadia | landing | 0.626 | 0.686 | 0.626 | 0.590 | 0.713 |

## 權重敏感度（每個權重 ±20%，前 10 名重疊率 Jaccard）

| 目標 | 任務 | 平均 | 最低 |
|---|---|---|---|
| jezero | geology | 0.93 | 0.67 |
| jezero | rover | 0.88 | 0.67 |
| gale | geology | 0.95 | 0.82 |
| gale | rover | 0.81 | 0.43 |
| arcadia | isru_base | 0.84 | 0.54 |
| arcadia | landing | 0.67 | 0.43 |

## 交叉檢查：Random Forest / XGBoost（XGBoost 跑在 cuda）

**global**（29 個類比地）　留一法 AUC：我們 0.724、RF 0.784、XGBoost 0.788　｜　重要性排序一致性（Spearman）：我們 vs RF 0.51、我們 vs XGB 0.47、RF vs XGB 0.96

| 變數 | 我們的權重 | RF permutation | XGB SHAP |
|---|---|---|---|
| slope | 0.00 | 0.01 | 0.04 |
| roughness | 0.00 | 0.01 | 0.03 |
| thermal_inertia | 0.00 | 0.09 | 0.14 |
| lithology | 0.00 | 0.04 | 0.06 |
| ice | 0.45 | 0.06 | 0.06 |
| temperature | 0.17 | 0.20 | 0.18 |
| diurnal_range | 0.04 | 0.07 | 0.07 |
| aridity | 0.04 | 0.15 | 0.10 |
| barrenness | 0.30 | 0.25 | 0.20 |
| dust | 0.00 | 0.11 | 0.10 |

**geology**（24 個類比地）　留一法 AUC：我們 0.659、RF 0.707、XGBoost 0.778　｜　重要性排序一致性（Spearman）：我們 vs RF 0.57、我們 vs XGB 0.57、RF vs XGB 0.99

| 變數 | 我們的權重 | RF permutation | XGB SHAP |
|---|---|---|---|
| slope | 0.08 | 0.02 | 0.05 |
| roughness | 0.00 | 0.01 | 0.02 |
| thermal_inertia | 0.00 | 0.04 | 0.06 |
| lithology | 0.00 | 0.03 | 0.08 |
| ice | 0.00 | 0.01 | 0.01 |
| temperature | 0.31 | 0.23 | 0.20 |
| diurnal_range | 0.20 | 0.07 | 0.11 |
| aridity | 0.00 | 0.20 | 0.15 |
| barrenness | 0.41 | 0.25 | 0.22 |
| dust | 0.00 | 0.15 | 0.11 |

## Drop-column：拿掉一個變數（其他權重重新正規化），AUC 掉多少

| 目標/任務 | 原 AUC | 掉最多的前 3 個變數 |
|---|---|---|
| jezero/geology | 0.719 | barrenness +0.195、temperature +0.030、diurnal_range +0.005 |
| jezero/rover | 0.780 | barrenness +0.342、temperature +0.010、roughness +0.006 |
| gale/geology | 0.770 | barrenness +0.129、diurnal_range +0.026、temperature +0.015 |
| gale/rover | 0.832 | barrenness +0.225、aridity +0.005、diurnal_range +0.004 |
| arcadia/isru_base | 0.784 | barrenness +0.220、ice +0.151、temperature +0.030 |
| arcadia/landing | 0.686 | barrenness +0.153、dust +0.080、aridity +0.011 |

## IanChen 的 12 個點快速檢查

- jezero/geology：6 個已知類比地全部排在台灣點與負樣本前面 = **False**（AUC 0.97）；排名：mdrs_utah 68.2、black_point_lava 65.3、atacama_yungay 54.3、askja_iceland 52.8、haughton_crater 48.9、iowa_farmland 19.8、mcmurdo_dry_valleys 16.2、tw_penghu_basalt 15.4、tw_tianliao 14.7、tw_liji 12.9、amazon_rainforest 12.6、tw_xiaoyoukeng 10.4
- gale/rover：6 個已知類比地全部排在台灣點與負樣本前面 = **False**（AUC 0.83）；排名：haughton_crater 58.4、mdrs_utah 50.3、atacama_yungay 48.9、askja_iceland 48.7、black_point_lava 41.8、tw_xiaoyoukeng 29.0、amazon_rainforest 25.6、tw_tianliao 22.9、iowa_farmland 22.4、tw_penghu_basalt 19.3、tw_liji 18.6、mcmurdo_dry_valleys 8.7
- arcadia/isru_base：6 個已知類比地全部排在台灣點與負樣本前面 = **True**（AUC 1.00）；排名：haughton_crater 65.3、askja_iceland 46.5、mdrs_utah 42.8、black_point_lava 41.3、mcmurdo_dry_valleys 36.9、atacama_yungay 32.5、iowa_farmland 26.7、tw_penghu_basalt 23.4、tw_tianliao 21.1、amazon_rainforest 19.3、tw_liji 15.6、tw_xiaoyoukeng 15.5