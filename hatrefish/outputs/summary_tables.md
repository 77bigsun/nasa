# 數字總表（自動產生）

## 每個任務的權重（先驗 → 最後）

| 變數 | geology 先驗 | geology 最後 | rover 先驗 | rover 最後 | isru_base 先驗 | isru_base 最後 | landing 先驗 | landing 最後 |
|---|---|---|---|---|---|---|---|---|
| slope | 0.05 | **0.05** | 0.25 | **0.17** | 0.10 | **0.08** | 0.30 | **0.29** |
| roughness | 0.10 | **0.10** | 0.25 | **0.17** | 0.05 | **0.04** | 0.30 | **0.29** |
| thermal_inertia | 0.10 | **0.10** | 0.20 | **0.14** | 0.10 | **0.08** | 0.15 | **0.14** |
| lithology | 0.35 | **0.35** | 0.05 | **0.03** | 0.05 | **0.08** | 0.00 | **0.01** |
| ice | 0.05 | **0.05** | 0.00 | **0.00** | 0.35 | **0.33** | 0.00 | **0.01** |
| temperature | 0.05 | **0.05** | 0.05 | **0.09** | 0.20 | **0.18** | 0.00 | **0.00** |
| diurnal_range | 0.00 | **0.00** | 0.00 | **0.00** | 0.00 | **0.00** | 0.00 | **0.00** |
| aridity | 0.10 | **0.10** | 0.05 | **0.03** | 0.05 | **0.06** | 0.05 | **0.05** |
| barrenness | 0.15 | **0.15** | 0.05 | **0.29** | 0.05 | **0.11** | 0.05 | **0.07** |
| dust | 0.05 | **0.05** | 0.10 | **0.07** | 0.05 | **0.04** | 0.15 | **0.14** |

## 學到的權重（資料證據）與 90% 信賴區間（以類比地為單位 bootstrap 200 次）

| 變數 | 全域（29 個類比地） | 90% CI | 地質專屬（24 個） | 90% CI |
|---|---|---|---|---|
| slope | 0.00 | 0.00–0.06 | 0.07 | 0.00–0.17 |
| roughness | 0.00 | 0.00–0.04 | 0.10 | 0.00–0.19 |
| thermal_inertia | 0.00 | 0.00–0.09 | 0.05 | 0.00–0.15 |
| lithology | 0.22 | 0.04–0.31 | 0.02 | 0.00–0.15 |
| ice | 0.22 | 0.09–0.29 | 0.00 | 0.00–0.00 |
| temperature | 0.05 | 0.00–0.26 | 0.00 | 0.00–0.22 |
| diurnal_range | 0.00 | 0.00–0.19 | 0.15 | 0.00–0.32 |
| aridity | 0.08 | 0.00–0.26 | 0.05 | 0.00–0.27 |
| barrenness | 0.43 | 0.16–0.53 | 0.56 | 0.19–0.72 |
| dust | 0.00 | 0.00–0.09 | 0.00 | 0.00–0.07 |

## 留一法（每次拿掉一個已知類比地，用其他的學權重）

| 任務 | 類比地數 | α | 學習來源 | 採用 | AUC 先驗 | AUC 混合(任務專屬) | AUC 混合(全域) | AUC 逐項相乘(原規格) | AUC 只用學到的 | 前10% 命中 先驗→混合 |
|---|---|---|---|---|---|---|---|---|---|---|
| geology | 21 | 0.51 | global | prior | 0.680 | 0.626 | 0.662 | 0.573 | 0.573 | 0.32 → 0.32 |
| rover | 9 | 0.31 | mission | blend | 0.596 | 0.724 | 0.679 | 0.702 | 0.677 | 0.18 → 0.55 |
| isru_base | 4 | 0.17 | global | blend | 0.552 | — | 0.729 | 0.861 | 0.794 | 0.25 → 0.25 |
| landing | 1 | 0.05 | global | blend | 0.009 | — | 0.013 | 0.112 | 0.708 | 0.00 → 0.00 |

## 驗證（已知類比地 vs 隨機陸地＋高植被；排名 = 在全球陸地的百分位）

| 目標 | 任務 | 類比地數 | AUC 先驗 | AUC 最後 | 前1% | 前5% | 前10% |
|---|---|---|---|---|---|---|---|
| jezero | geology | 11 | 0.637 | **0.637** | 0.00 | 0.18 | 0.27 |
| jezero | rover | 7 | 0.609 | **0.672** | 0.14 | 0.29 | 0.57 |
| jezero | isru_base | 12 | 0.572 | **0.610** | 0.00 | 0.08 | 0.25 |
| jezero | landing | 12 | 0.653 | **0.657** | 0.00 | 0.00 | 0.17 |
| gale | geology | 14 | 0.732 | **0.732** | 0.00 | 0.21 | 0.36 |
| gale | rover | 4 | 0.679 | **0.900** | 0.00 | 0.50 | 0.75 |
| gale | isru_base | 16 | 0.618 | **0.685** | 0.00 | 0.06 | 0.19 |
| gale | landing | 16 | 0.699 | **0.721** | 0.00 | 0.12 | 0.19 |
| arcadia | geology | 5 | 0.529 | **0.529** | 0.00 | 0.00 | 0.00 |
| arcadia | rover | 5 | 0.169 | **0.389** | 0.00 | 0.00 | 0.20 |
| arcadia | isru_base | 4 | 0.552 | **0.723** | 0.00 | 0.25 | 0.25 |
| arcadia | landing | 1 | 0.009 | **0.015** | 0.00 | 0.00 | 0.00 |

## 算法比較（AUC）

| 目標 | 任務 | A 全部直接比 | B 預設 | C 夾到地球範圍 | B 沙塵改直接比 | B + 日溫差 0.05 |
|---|---|---|---|---|---|---|
| jezero | geology | 0.629 | 0.637 | 0.631 | 0.638 | 0.619 |
| jezero | rover | 0.654 | 0.672 | 0.657 | 0.670 | 0.665 |
| gale | geology | 0.731 | 0.732 | 0.731 | 0.729 | 0.741 |
| gale | rover | 0.926 | 0.900 | 0.926 | 0.900 | 0.903 |
| arcadia | isru_base | 0.559 | 0.723 | 0.697 | 0.698 | 0.692 |
| arcadia | landing | 0.059 | 0.015 | 0.060 | 0.007 | 0.002 |

## 權重敏感度（每個權重 ±20%，前 10 名重疊率 Jaccard）

| 目標 | 任務 | 平均 | 最低 |
|---|---|---|---|
| jezero | geology | 0.87 | 0.67 |
| jezero | rover | 0.97 | 0.82 |
| gale | geology | 0.93 | 0.67 |
| gale | rover | 0.84 | 0.54 |
| arcadia | isru_base | 0.97 | 0.82 |
| arcadia | landing | 0.85 | 0.67 |

## 交叉檢查：Random Forest / XGBoost（XGBoost 跑在 cuda）

**global**（26 個類比地）　留一法 AUC：我們 0.706、RF 0.793、XGBoost 0.818　｜　重要性排序一致性（Spearman）：我們 vs RF 0.42、我們 vs XGB 0.29、RF vs XGB 0.93

| 變數 | 我們的權重 | RF permutation | XGB SHAP |
|---|---|---|---|
| slope | 0.00 | 0.01 | 0.04 |
| roughness | 0.00 | 0.01 | 0.01 |
| thermal_inertia | 0.00 | 0.03 | 0.04 |
| lithology | 0.22 | 0.04 | 0.05 |
| ice | 0.22 | 0.14 | 0.13 |
| temperature | 0.05 | 0.12 | 0.14 |
| diurnal_range | 0.00 | 0.19 | 0.21 |
| aridity | 0.08 | 0.13 | 0.07 |
| barrenness | 0.43 | 0.18 | 0.15 |
| dust | 0.00 | 0.14 | 0.15 |

**geology**（21 個類比地）　留一法 AUC：我們 0.630、RF 0.711、XGBoost 0.734　｜　重要性排序一致性（Spearman）：我們 vs RF 0.14、我們 vs XGB 0.02、RF vs XGB 0.92

| 變數 | 我們的權重 | RF permutation | XGB SHAP |
|---|---|---|---|
| slope | 0.07 | 0.03 | 0.06 |
| roughness | 0.10 | 0.02 | 0.03 |
| thermal_inertia | 0.05 | 0.05 | 0.08 |
| lithology | 0.02 | 0.02 | 0.04 |
| ice | 0.00 | 0.02 | 0.05 |
| temperature | 0.00 | 0.15 | 0.17 |
| diurnal_range | 0.15 | 0.16 | 0.18 |
| aridity | 0.05 | 0.12 | 0.09 |
| barrenness | 0.56 | 0.24 | 0.14 |
| dust | 0.00 | 0.19 | 0.17 |

## Drop-column：拿掉一個變數（其他權重重新正規化），AUC 掉多少

| 目標/任務 | 原 AUC | 掉最多的前 3 個變數 |
|---|---|---|
| jezero/geology | 0.637 | barrenness +0.047、lithology +0.033、temperature +0.006 |
| jezero/rover | 0.672 | barrenness +0.183、thermal_inertia +0.013、temperature +0.011 |
| gale/geology | 0.732 | barrenness +0.118、roughness +0.009、slope +0.002 |
| gale/rover | 0.900 | barrenness +0.337、roughness +0.011、slope +0.004 |
| arcadia/isru_base | 0.723 | barrenness +0.186、ice +0.130、temperature +0.101 |
| arcadia/landing | 0.015 | dust +0.008、barrenness +0.006、ice +0.002 |

## IanChen 的 12 個點快速檢查

- jezero/geology：6 個已知類比地全部排在台灣點與負樣本前面 = **False**（AUC 0.86）；排名：black_point_lava 69.1、haughton_crater 67.3、mdrs_utah 65.4、atacama_yungay 55.1、iowa_farmland 35.7、askja_iceland 35.6、tw_penghu_basalt 28.6、amazon_rainforest 27.9、tw_tianliao 25.3、mcmurdo_dry_valleys 24.5、tw_liji 17.4、tw_xiaoyoukeng 16.7
- gale/rover：6 個已知類比地全部排在台灣點與負樣本前面 = **False**（AUC 0.83）；排名：haughton_crater 70.8、askja_iceland 53.8、mdrs_utah 51.6、atacama_yungay 50.6、black_point_lava 41.9、tw_xiaoyoukeng 14.8、amazon_rainforest 12.3、tw_tianliao 9.9、iowa_farmland 9.6、tw_penghu_basalt 7.6、tw_liji 7.6、mcmurdo_dry_valleys 4.3
- arcadia/isru_base：6 個已知類比地全部排在台灣點與負樣本前面 = **True**（AUC 1.00）；排名：haughton_crater 61.7、askja_iceland 45.9、mdrs_utah 44.1、black_point_lava 42.3、atacama_yungay 33.0、mcmurdo_dry_valleys 31.5、iowa_farmland 25.6、tw_penghu_basalt 22.4、tw_tianliao 19.8、amazon_rainforest 18.6、tw_xiaoyoukeng 13.9、tw_liji 13.0