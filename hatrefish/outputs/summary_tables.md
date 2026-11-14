# 數字總表（自動產生）

## 每個任務的權重（先驗 → 最後）

| 變數 | geology 先驗 | geology 最後 | rover 先驗 | rover 最後 | isru_base 先驗 | isru_base 最後 | landing 先驗 | landing 最後 |
|---|---|---|---|---|---|---|---|---|
| slope | 0.05 | **0.05** | 0.25 | **0.17** | 0.10 | **0.08** | 0.30 | **0.29** |
| roughness | 0.10 | **0.10** | 0.25 | **0.17** | 0.05 | **0.04** | 0.30 | **0.29** |
| thermal_inertia | 0.10 | **0.10** | 0.20 | **0.14** | 0.10 | **0.08** | 0.15 | **0.14** |
| lithology | 0.35 | **0.35** | 0.05 | **0.03** | 0.05 | **0.08** | 0.00 | **0.01** |
| ice | 0.05 | **0.05** | 0.00 | **0.00** | 0.35 | **0.31** | 0.00 | **0.01** |
| temperature | 0.05 | **0.05** | 0.05 | **0.09** | 0.20 | **0.18** | 0.00 | **0.00** |
| diurnal_range | 0.00 | **0.00** | 0.00 | **0.00** | 0.00 | **0.00** | 0.00 | **0.00** |
| aridity | 0.10 | **0.10** | 0.05 | **0.03** | 0.05 | **0.05** | 0.05 | **0.05** |
| barrenness | 0.15 | **0.15** | 0.05 | **0.29** | 0.05 | **0.12** | 0.05 | **0.07** |
| dust | 0.05 | **0.05** | 0.10 | **0.07** | 0.05 | **0.04** | 0.15 | **0.14** |

## 學到的權重（資料證據）與 90% 信賴區間（以類比地為單位 bootstrap 200 次）

| 變數 | 全域（29 個類比地） | 90% CI | 地質專屬（24 個） | 90% CI |
|---|---|---|---|---|
| slope | 0.00 | 0.00–0.06 | 0.07 | 0.00–0.16 |
| roughness | 0.00 | 0.00–0.05 | 0.10 | 0.00–0.19 |
| thermal_inertia | 0.00 | 0.00–0.11 | 0.05 | 0.00–0.15 |
| lithology | 0.24 | 0.05–0.35 | 0.02 | 0.00–0.15 |
| ice | 0.13 | 0.00–0.27 | 0.00 | 0.00–0.15 |
| temperature | 0.08 | 0.00–0.31 | 0.00 | 0.00–0.22 |
| diurnal_range | 0.00 | 0.00–0.17 | 0.15 | 0.00–0.27 |
| aridity | 0.07 | 0.00–0.29 | 0.05 | 0.00–0.26 |
| barrenness | 0.48 | 0.17–0.62 | 0.56 | 0.19–0.72 |
| dust | 0.00 | 0.00–0.09 | 0.00 | 0.00–0.07 |

## 留一法（每次拿掉一個已知類比地，用其他的學權重）

| 任務 | 類比地數 | α | 學習來源 | 採用 | AUC 先驗 | AUC 混合(任務專屬) | AUC 混合(全域) | AUC 逐項相乘(原規格) | AUC 只用學到的 | 前10% 命中 先驗→混合 |
|---|---|---|---|---|---|---|---|---|---|---|
| geology | 21 | 0.51 | global | prior | 0.681 | 0.593 | 0.674 | 0.541 | 0.531 | 0.28 → 0.36 |
| rover | 9 | 0.31 | mission | blend | 0.596 | 0.724 | 0.687 | 0.722 | 0.703 | 0.18 → 0.55 |
| isru_base | 4 | 0.17 | global | blend | 0.441 | — | 0.673 | 0.839 | 0.792 | 0.00 → 0.00 |
| landing | 1 | 0.05 | global | blend | 0.009 | — | 0.013 | 0.123 | 0.688 | 0.00 → 0.00 |

## 驗證（已知類比地 vs 隨機陸地＋高植被；排名 = 在全球陸地的百分位）

| 目標 | 任務 | 類比地數 | AUC 先驗 | AUC 最後 | 前1% | 前5% | 前10% |
|---|---|---|---|---|---|---|---|
| jezero | geology | 11 | 0.625 | **0.625** | 0.00 | 0.18 | 0.18 |
| jezero | rover | 7 | 0.609 | **0.672** | 0.14 | 0.29 | 0.57 |
| jezero | isru_base | 12 | 0.542 | **0.560** | 0.00 | 0.17 | 0.33 |
| jezero | landing | 12 | 0.653 | **0.657** | 0.00 | 0.00 | 0.17 |
| gale | geology | 14 | 0.740 | **0.740** | 0.07 | 0.21 | 0.36 |
| gale | rover | 4 | 0.679 | **0.900** | 0.00 | 0.50 | 0.75 |
| gale | isru_base | 16 | 0.688 | **0.750** | 0.06 | 0.31 | 0.50 |
| gale | landing | 16 | 0.699 | **0.724** | 0.00 | 0.12 | 0.25 |
| arcadia | geology | 5 | 0.519 | **0.519** | 0.00 | 0.00 | 0.00 |
| arcadia | rover | 5 | 0.169 | **0.389** | 0.00 | 0.00 | 0.20 |
| arcadia | isru_base | 4 | 0.441 | **0.659** | 0.00 | 0.00 | 0.25 |
| arcadia | landing | 1 | 0.009 | **0.013** | 0.00 | 0.00 | 0.00 |
| oxia | geology | 0 | nan | **nan** | nan | nan | nan |
| oxia | rover | 0 | nan | **nan** | nan | nan | nan |
| oxia | isru_base | 0 | nan | **nan** | nan | nan | nan |
| oxia | landing | 0 | nan | **nan** | nan | nan | nan |
| meridiani | geology | 0 | nan | **nan** | nan | nan | nan |
| meridiani | rover | 0 | nan | **nan** | nan | nan | nan |
| meridiani | isru_base | 0 | nan | **nan** | nan | nan | nan |
| meridiani | landing | 0 | nan | **nan** | nan | nan | nan |
| protonilus | geology | 0 | nan | **nan** | nan | nan | nan |
| protonilus | rover | 0 | nan | **nan** | nan | nan | nan |
| protonilus | isru_base | 0 | nan | **nan** | nan | nan | nan |
| protonilus | landing | 0 | nan | **nan** | nan | nan | nan |
| ap105 | geology | 0 | nan | **nan** | nan | nan | nan |
| ap105 | rover | 0 | nan | **nan** | nan | nan | nan |
| ap105 | isru_base | 0 | nan | **nan** | nan | nan | nan |
| ap105 | landing | 0 | nan | **nan** | nan | nan | nan |

## 算法比較（AUC）

| 目標 | 任務 | A 全部直接比 | B 預設 | C 夾到地球範圍 | B 沙塵改直接比 | B + 日溫差 0.05 |
|---|---|---|---|---|---|---|
| jezero | geology | 0.615 | 0.625 | 0.616 | 0.626 | 0.612 |
| jezero | rover | 0.654 | 0.672 | 0.657 | 0.670 | 0.665 |
| gale | geology | 0.735 | 0.740 | 0.735 | 0.738 | 0.746 |
| gale | rover | 0.926 | 0.900 | 0.926 | 0.900 | 0.903 |
| arcadia | isru_base | 0.461 | 0.659 | 0.651 | 0.628 | 0.587 |
| arcadia | landing | 0.052 | 0.013 | 0.059 | 0.005 | 0.002 |
| oxia | geology | nan | nan | nan | nan | nan |
| oxia | rover | nan | nan | nan | nan | nan |
| meridiani | geology | nan | nan | nan | nan | nan |
| meridiani | rover | nan | nan | nan | nan | nan |
| protonilus | isru_base | nan | nan | nan | nan | nan |
| protonilus | landing | nan | nan | nan | nan | nan |
| ap105 | landing | nan | nan | nan | nan | nan |
| ap105 | isru_base | nan | nan | nan | nan | nan |

## 權重敏感度（每個權重 ±20%，前 10 名重疊率 Jaccard）

| 目標 | 任務 | 平均 | 最低 |
|---|---|---|---|
| jezero | geology | 0.87 | 0.67 |
| jezero | rover | 0.97 | 0.82 |
| gale | geology | 0.95 | 0.82 |
| gale | rover | 0.84 | 0.54 |
| arcadia | isru_base | 0.93 | 0.67 |
| arcadia | landing | 0.91 | 0.67 |
| oxia | geology | 1.00 | 1.00 |
| oxia | rover | 0.90 | 0.67 |
| meridiani | geology | 0.72 | 0.18 |
| meridiani | rover | 0.87 | 0.67 |
| protonilus | isru_base | 0.90 | 0.82 |
| protonilus | landing | 0.80 | 0.43 |
| ap105 | landing | 0.88 | 0.82 |
| ap105 | isru_base | 0.83 | 0.54 |

## 交叉檢查：Random Forest / XGBoost（XGBoost 跑在 cuda）

**global**（26 個類比地）　留一法 AUC：我們 0.701、RF 0.801、XGBoost 0.822　｜　重要性排序一致性（Spearman）：我們 vs RF 0.27、我們 vs XGB 0.24、RF vs XGB 0.95

| 變數 | 我們的權重 | RF permutation | XGB SHAP |
|---|---|---|---|
| slope | 0.00 | 0.01 | 0.04 |
| roughness | 0.00 | 0.01 | 0.01 |
| thermal_inertia | 0.00 | 0.02 | 0.04 |
| lithology | 0.24 | 0.03 | 0.06 |
| ice | 0.13 | 0.18 | 0.14 |
| temperature | 0.08 | 0.11 | 0.13 |
| diurnal_range | 0.00 | 0.20 | 0.20 |
| aridity | 0.07 | 0.12 | 0.07 |
| barrenness | 0.48 | 0.17 | 0.15 |
| dust | 0.00 | 0.13 | 0.15 |

**geology**（21 個類比地）　留一法 AUC：我們 0.621、RF 0.713、XGBoost 0.741　｜　重要性排序一致性（Spearman）：我們 vs RF 0.15、我們 vs XGB 0.02、RF vs XGB 0.85

| 變數 | 我們的權重 | RF permutation | XGB SHAP |
|---|---|---|---|
| slope | 0.07 | 0.03 | 0.05 |
| roughness | 0.10 | 0.02 | 0.03 |
| thermal_inertia | 0.05 | 0.05 | 0.08 |
| lithology | 0.02 | 0.02 | 0.04 |
| ice | 0.00 | 0.01 | 0.05 |
| temperature | 0.00 | 0.15 | 0.16 |
| diurnal_range | 0.15 | 0.15 | 0.19 |
| aridity | 0.05 | 0.12 | 0.10 |
| barrenness | 0.56 | 0.25 | 0.14 |
| dust | 0.00 | 0.20 | 0.17 |

## Drop-column：拿掉一個變數（其他權重重新正規化），AUC 掉多少

| 目標/任務 | 原 AUC | 掉最多的前 3 個變數 |
|---|---|---|
| jezero/geology | 0.625 | barrenness +0.045、lithology +0.033、temperature +0.005 |
| jezero/rover | 0.672 | barrenness +0.183、thermal_inertia +0.013、temperature +0.011 |
| gale/geology | 0.740 | barrenness +0.118、ice +0.008、roughness +0.006 |
| gale/rover | 0.900 | barrenness +0.337、roughness +0.011、slope +0.004 |
| arcadia/isru_base | 0.659 | barrenness +0.268、temperature +0.164、ice +0.041 |
| arcadia/landing | 0.013 | dust +0.008、barrenness +0.006、lithology +0.000 |
| oxia/geology | nan | slope +nan、roughness +nan、thermal_inertia +nan |
| oxia/rover | nan | slope +nan、roughness +nan、thermal_inertia +nan |
| meridiani/geology | nan | slope +nan、roughness +nan、thermal_inertia +nan |
| meridiani/rover | nan | slope +nan、roughness +nan、thermal_inertia +nan |
| protonilus/isru_base | nan | slope +nan、roughness +nan、thermal_inertia +nan |
| protonilus/landing | nan | slope +nan、roughness +nan、thermal_inertia +nan |
| ap105/landing | nan | slope +nan、roughness +nan、thermal_inertia +nan |
| ap105/isru_base | nan | slope +nan、roughness +nan、thermal_inertia +nan |

## IanChen 的 12 個點快速檢查

- jezero/geology：6 個已知類比地全部排在台灣點與負樣本前面 = **False**（AUC 0.86）；排名：black_point_lava 70.9、mdrs_utah 67.1、atacama_yungay 56.5、haughton_crater 54.9、iowa_farmland 36.7、askja_iceland 36.6、tw_penghu_basalt 29.4、amazon_rainforest 28.6、tw_tianliao 26.0、mcmurdo_dry_valleys 18.5、tw_liji 17.9、tw_xiaoyoukeng 17.2
- gale/rover：6 個已知類比地全部排在台灣點與負樣本前面 = **False**（AUC 0.83）；排名：haughton_crater 70.8、askja_iceland 53.8、mdrs_utah 51.6、atacama_yungay 50.6、black_point_lava 41.9、tw_xiaoyoukeng 14.8、amazon_rainforest 12.3、tw_tianliao 9.9、iowa_farmland 9.6、tw_penghu_basalt 7.6、tw_liji 7.6、mcmurdo_dry_valleys 4.3
- arcadia/isru_base：6 個已知類比地全部排在台灣點與負樣本前面 = **False**（AUC 0.94）；排名：askja_iceland 59.3、mdrs_utah 55.5、haughton_crater 54.1、black_point_lava 53.0、atacama_yungay 42.1、iowa_farmland 31.6、tw_penghu_basalt 27.6、mcmurdo_dry_valleys 26.4、tw_tianliao 24.3、amazon_rainforest 22.9、tw_xiaoyoukeng 17.2、tw_liji 16.0