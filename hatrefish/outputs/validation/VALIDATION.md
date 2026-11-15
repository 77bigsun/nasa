# 類比剖面驗證

> 產生時間 2026-11-15T17:07:04+08:00，`scripts/validate_profiles.py`。百分位：0% = 全球最像，50% = 隨機，100% = 最不像（面積加權，排名池同剖面）。

## 1. 分面向找回已知類比地

每個已知類比地只看它被選上的原因對應的面向（對照表在第 5 節），只對標給它的火星目標算。

| 指標 | 用對應面向 | 用總體分數 |
|---|---|---|
| 地點 × 目標組數 | 34 | 34 |
| 百分位中位數 | 11.7% | 31.5% |
| 前 10% 的比例（隨機 = 10%） | 47% | 32% |
| 前 25% 的比例（隨機 = 25%） | 71% | 44% |

「用對應面向」取該地點對應面向中最好的那個百分位（一個地點被選上，通常只要一個面向像就夠）。

沒算的（被選上的原因我們量不到，例如生物、隕石坑形態）：pavilion_lake, pilbara_dresser, ries_crater。

| 目標 | 已知類比地 | 對應面向：百分位 | 總體百分位 |
|---|---|---|---|
| jezero | Bockfjorden Volcanic Complex Svalbard (Norway) | surface 0%、water_ice 98% | 100% |
| jezero | Askja lava fields Vikrahraun (Iceland) | surface 8%、terrain 24% | 51% |
| jezero | Lavic Lake and Sunshine volcanic field Mojave Desert (California) | terrain 20%、surface 8% | 9% |
| jezero | Mars Desert Research Station Hanksville (Utah) | surface 13%、terrain 14% | 6% |
| jezero | Black Point Lava Flow (Arizona) | surface 13%、terrain 25% | 8% |
| jezero | Haughton impact crater Devon Island (Canada) | environment 42%、water_ice 98% | 86% |
| jezero | Matanumadh jarosite locality Kachchh (India) | surface 45% | 26% |
| jezero | Lake Salda (Turkey) | surface 51% | 21% |
| jezero | Lonar crater (India) | surface 57% | 37% |
| jezero | Pavilion Lake (British Columbia) | — | 93% |
| jezero | Ries impact crater (Germany) | — | 43% |
| jezero | Dresser Formation stromatolites Pilbara (Australia) | — | 44% |
| gale | Dalangtan saline playa Qaidam Basin (China) | surface 20%、environment 1% | 7% |
| gale | Dallol geothermal area Afar (Ethiopia) | surface 1% | 51% |
| gale | Badwater Basin Death Valley (California) | surface 1%、environment 39% | 6% |
| gale | Lavic Lake and Sunshine volcanic field Mojave Desert (California) | terrain 15%、surface 8% | 2% |
| gale | Pilot Valley paleolake playa (Utah) | surface 8% | 2% |
| gale | Askja lava fields Vikrahraun (Iceland) | surface 9%、terrain 25% | 42% |
| gale | Navajo Sandstone hematite concretions southern Utah | surface 10% | 1% |
| gale | Mars Desert Research Station Hanksville (Utah) | surface 12%、terrain 23% | 2% |
| gale | AMADEE-18 field site Marmul area Dhofar (Oman) | terrain 74%、surface 16%、environment 89% | 42% |
| gale | White Sands gypsum dunes and Lake Lucero (New Mexico) | surface 23% | 22% |
| gale | Atacama Desert Yungay core (Chile) | environment 41%、surface 25% | 16% |
| gale | Matanumadh jarosite locality Kachchh (India) | surface 44% | 38% |
| gale | Rio Tinto acid river headwaters (Spain) | surface 45% | 6% |
| gale | Lonar crater (India) | surface 57% | 47% |
| gale | Ka'u Desert Kilauea (Hawaii) | surface 87% | 63% |
| gale | Mauna Kea upper slopes palagonitic tephra (Hawaii) | surface 95% | 81% |
| arcadia | McMurdo Dry Valleys (Antarctica) | environment 0%、water_ice 12% | 88% |
| arcadia | Beacon Valley ancient buried ice (Antarctica) | water_ice 12%、environment 0% | 88% |
| arcadia | HI-SEAS habitat Mauna Loa (Hawaii) | terrain 78%、surface 0% | 47% |
| arcadia | Lanzarote volcanic fields (Spain) | surface 1%、terrain 71% | 12% |
| arcadia | Pilot Valley paleolake playa (Utah) | surface 3% | 6% |
| arcadia | Bockfjorden Volcanic Complex Svalbard (Norway) | surface 26%、water_ice 10% | 92% |
| arcadia | Lost Hammer cold saline spring Axel Heiberg Island (Canada) | environment 12%、water_ice 12% | 86% |
| arcadia | Haughton impact crater Devon Island (Canada) | environment 42%、water_ice 12% | 25% |
| arcadia | Mauna Kea upper slopes palagonitic tephra (Hawaii) | surface 64% | 91% |

## 2. 負對照（明顯不像火星的地方）

判準：不能進全球前 25%，總體分數也要遠低於前 20 名。格子裡是百分位（總體分數）。

| 地點 | jezero | gale | arcadia | oxia | meridiani | protonilus | ap105 |
|---|---|---|---|---|---|---|---|
| Amazon rainforest, Brazil | 76%（32） | 91%（25） | 74%（30） | 69%（32） | 75%（33） | 88%（29） | 76%（28） |
| Congo Basin rainforest, DR Congo | 59%（41） | 67%（34） | 74%（31） | 55%（39） | 58%（40） | 81%（33） | 70%（31） |
| Borneo rainforest, Indonesia | 100%（10） | 99%（14） | 100%（9） | 100%（8） | 100%（10） | 99%（15） | 100%（8） |
| Ganges–Brahmaputra delta, Bangladesh | 52%（44） | 74%（32） | 65%（34） | 45%（44） | 50%（44） | 82%（32） | 60%（35） |
| Mekong Delta, Vietnam | 77%（32） | 90%（25） | 67%（34） | 74%（29） | 74%（33） | 82%（32） | 71%（31） |
| Paris Basin farmland, France | 45%（47） | 51%（38） | 57%（38） | 36%（48） | 43%（47） | 55%（41） | 54%（38） |
| Corn Belt, Iowa, USA | 44%（47） | 60%（36） | 52%（40） | 41%（46） | 45%（46） | 57%（41） | 52%（38） |
| Pasture, central Ireland | 63%（40） | 75%（32） | 68%（33） | 55%（39） | 61%（39） | 67%（38） | 71%（31） |
| **對照：前 20 名的最低分** | 86.0 | 84.7 | 77.3 | 84.1 | 87.7 | 83.3 | 78.3 |

全部 56 組：進入前 25% 的 0 組，百分位最低 36%，中位數 68%。
負對照多半落在中段而不是最後：例如對沒有冰訊號的目標，溫帶農地在「水與冰」拿滿分、在「地形」接近滿分，五個面向的幾何平均會被撐到中段。所以排名只有最前面一段有意義，中段的先後不代表像不像。

## 3. 穩健性（和等權重前 20 名比）

數字 = 前 20 名裡有幾個地點仍在（150 km 內算同一處）；★ = 等權重第 1 名仍在前 5。

| 情境 | jezero | gale | arcadia | oxia | meridiani | protonilus | ap105 |
|---|---|---|---|---|---|---|---|
| 權重：terrain ×0.5 | 15 ★ | 17 ★ | 17 ★ | 20 ★ | 17 ★ | 19 ★ | 16 ★ |
| 權重：terrain ×1.5 | 19 | 19 ★ | 20 ★ | 20 ★ | 17 ★ | 18 ★ | 19 ★ |
| 權重：surface ×0.5 | 17 | 19 ★ | 15 ★ | 16 ★ | 16 ★ | 17 ★ | 16 ★ |
| 權重：surface ×1.5 | 16 ★ | 19 ★ | 16 ★ | 19 ★ | 16 ★ | 18 ★ | 16 ★ |
| 權重：environment ×0.5 | 19 ★ | 17 ★ | 16 ★ | 17 ★ | 17 ★ | 16 ★ | 19 ★ |
| 權重：environment ×1.5 | 18 ★ | 20 ★ | 14 ★ | 16 ★ | 17 ★ | 20 ★ | 18 ★ |
| 權重：water_ice ×0.5 | 20 ★ | 20 ★ | 12 | 20 ★ | 20 ★ | 18 ★ | 14 ★ |
| 權重：water_ice ×1.5 | 20 ★ | 20 ★ | 17 ★ | 20 ★ | 19 ★ | 18 ★ | 17 ★ |
| 權重：atmosphere_dust ×0.5 | 18 ★ | 19 ★ | 16 ★ | 17 ★ | 17 ★ | 15 ★ | 19 ★ |
| 權重：atmosphere_dust ×1.5 | 18 ★ | 19 ★ | 17 ★ | 16 ★ | 18 ★ | 16 ★ | 18 ★ |
| 拿掉面向（不算進穩定度）：terrain 拿掉 | 8 ★ | 9 | 10 | 9 ★ | 13 ★ | 14 ★ | 10 |
| 拿掉面向（不算進穩定度）：surface 拿掉 | 9 | 12 ★ | 5 | 2 | 10 | 8 ★ | 11 ★ |
| 拿掉面向（不算進穩定度）：environment 拿掉 | 2 | 13 | 10 ★ | 8 | 5 ★ | 10 | 15 ★ |
| 拿掉面向（不算進穩定度）：water_ice 拿掉 | 18 ★ | 14 | 3 | 19 ★ | 16 ★ | 8 | 6 |
| 拿掉面向（不算進穩定度）：atmosphere_dust 拿掉 | 11 ★ | 17 ★ | 13 | 12 ★ | 11 | 4 | 13 ★ |
| 合成方式：算術平均 | 18 ★ | 20 ★ | 16 ★ | 17 ★ | 18 ★ | 18 ★ | 18 ★ |
| 合成方式：取最小值 | 10 ★ | 15 | 10 | 15 ★ | 14 ★ | 13 | 8 ★ |
| 合成方式：幾何平均，最低分 0.05 | 20 ★ | 20 ★ | 20 ★ | 20 ★ | 20 ★ | 20 ★ | 20 ★ |
| 排名池門檻：資料覆蓋 ≥ 60% | 20 ★ | 20 ★ | 17 ★ | 20 ★ | 20 ★ | 20 ★ | 20 ★ |
| 排名池門檻：資料覆蓋 ≥ 100% | 20 ★ | 20 ★ | 17 ★ | 18 ★ | 13 ★ | 20 ★ | 20 ★ |
| 最小間距：最小間距 100 km | 19 ★ | 16 ★ | 13 ★ | 19 ★ | 16 ★ | 15 ★ | 16 ★ |
| 最小間距：最小間距 300 km | 13 ★ | 13 ★ | 17 ★ | 13 ★ | 11 ★ | 12 ★ | 11 ★ |
| 方法變體（不算進穩定度）：植被獨立成一個面向 | 14 ★ | 16 ★ | 8 | 16 ★ | 13 ★ | 14 ★ | 15 ★ |
| 方法變體（不算進穩定度）：沒冰的目標不算冰 | 18 ★ | 14 | — | 19 ★ | 16 ★ | — | — |
| 方法變體（不算進穩定度）：溫度冷到最冷 10% 就滿分 | 20 ★ | 20 ★ | 19 ★ | 20 ★ | 20 ★ | 20 ★ | 20 ★ |
| 方法變體（不算進穩定度）：三者一起 | 11 ★ | 11 | 8 | 16 ★ | 12 ★ | 14 ★ | 15 ★ |
| 隨機權重 100 組：重疊中位數（第 10 百分位） | 12（7） | 14（8） | 8（3） | 13（4） | 11（5） | 10（4） | 10（7） |
| 隨機權重：第 1 名仍在前 5 的比例 | 54% | 51% | 52% | 74% | 54% | 55% | 65% |

### 3.1 每個地點的穩定度

等權重前 10 名，在各類情境裡留在前 20 名的比例。總穩定度 = 五類的平均；≥ 80% 可以說「換假設也穩」，< 50% 表示這個地點的名次靠特定假設。

**jezero**

| # | 地點 | 總體 | 權重 ±50% | 隨機權重 | 合成方式 | 排名池門檻 | 最小間距 | 總穩定度 |
|---|---|---|---|---|---|---|---|---|
| 1 | （37.45, 93.95） | 88.4 | 80% | 64% | 100% | 100% | 100% | **89%** |
| 2 | （43.35, 88.15） | 88.2 | 100% | 91% | 100% | 100% | 100% | **98%** |
| 3 | （39.95, 103.55） | 87.4 | 100% | 69% | 67% | 100% | 100% | **87%** |
| 4 | （43.55, 91.55） | 87.1 | 100% | 89% | 100% | 100% | 50% | **88%** |
| 5 | （39.45, 106.95） | 87.0 | 100% | 69% | 100% | 100% | 50% | **84%** |
| 6 | （40.15, 97.45） | 86.9 | 100% | 55% | 67% | 100% | 100% | **84%** |
| 7 | （42.95, 98.35） | 86.9 | 100% | 60% | 67% | 100% | 100% | **85%** |
| 8 | （44.35, 83.75） | 86.8 | 100% | 59% | 67% | 100% | 100% | **85%** |
| 9 | （42.95, 95.55） | 86.8 | 100% | 58% | 100% | 100% | 50% | **82%** |
| 10 | （43.85, 94.15） | 86.6 | 100% | 38% | 100% | 100% | 100% | **88%** |

**gale**

| # | 地點 | 總體 | 權重 ±50% | 隨機權重 | 合成方式 | 排名池門檻 | 最小間距 | 總穩定度 |
|---|---|---|---|---|---|---|---|---|
| 1 | （47.05, 92.85） | 87.4 | 100% | 88% | 67% | 100% | 100% | **91%** |
| 2 | （44.95, 92.25） | 87.2 | 100% | 97% | 100% | 100% | 100% | **99%** |
| 3 | （45.45, 99.25） | 87.1 | 100% | 90% | 100% | 100% | 100% | **98%** |
| 4 | （46.45, 90.15） | 87.0 | 100% | 91% | 100% | 100% | 50% | **88%** |
| 5 | （43.45, 92.05） | 86.8 | 100% | 92% | 100% | 100% | 100% | **98%** |
| 6 | （45.85, 94.65） | 86.3 | 100% | 90% | 100% | 100% | 50% | **88%** |
| 7 | （42.85, 98.75） | 86.2 | 100% | 68% | 100% | 100% | 50% | **84%** |
| 8 | （44.55, 102.15） | 86.2 | 100% | 77% | 67% | 100% | 100% | **89%** |
| 9 | （43.25, 88.25） | 86.0 | 100% | 65% | 100% | 100% | 100% | **93%** |
| 10 | （48.35, 91.15） | 85.9 | 100% | 68% | 100% | 100% | 50% | **84%** |

**arcadia**

| # | 地點 | 總體 | 權重 ±50% | 隨機權重 | 合成方式 | 排名池門檻 | 最小間距 | 總穩定度 |
|---|---|---|---|---|---|---|---|---|
| 1 | （63.95, 110.65） | 81.7 | 100% | 74% | 100% | 100% | 100% | **95%** |
| 2 | （30.25, 82.95） | 80.9 | 100% | 70% | 67% | 100% | 100% | **87%** |
| 3 | （64.25, 149.25） | 80.9 | 100% | 59% | 67% | 100% | 100% | **85%** |
| 4 | （62.05, 159.65） | 80.4 | 100% | 57% | 100% | 100% | 100% | **91%** |
| 5 | （64.45, 104.25） | 80.3 | 100% | 66% | 67% | 100% | 100% | **87%** |
| 6 | （48.25, 92.65） | 79.9 | 100% | 51% | 100% | 100% | 100% | **90%** |
| 7 | （67.85, 170.95） | 79.9 | 100% | 41% | 100% | 100% | 100% | **88%** |
| 8 | （49.85, 94.95） | 79.8 | 100% | 40% | 100% | 100% | 100% | **88%** |
| 9 | （49.95, 88.65） | 79.8 | 100% | 37% | 100% | 100% | 100% | **87%** |
| 10 | （64.95, 107.25） | 79.1 | 100% | 55% | 100% | 100% | 50% | **81%** |

**oxia**

| # | 地點 | 總體 | 權重 ±50% | 隨機權重 | 合成方式 | 排名池門檻 | 最小間距 | 總穩定度 |
|---|---|---|---|---|---|---|---|---|
| 1 | （37.45, 93.95） | 88.9 | 100% | 87% | 100% | 100% | 100% | **97%** |
| 2 | （40.45, 90.75） | 88.7 | 100% | 97% | 100% | 100% | 100% | **99%** |
| 3 | （39.45, 88.25） | 88.1 | 100% | 94% | 100% | 100% | 50% | **89%** |
| 4 | （39.65, 106.75） | 87.6 | 100% | 77% | 100% | 50% | 100% | **85%** |
| 5 | （45.65, 57.25） | 87.3 | 100% | 72% | 100% | 100% | 100% | **94%** |
| 6 | （45.45, 53.95） | 86.9 | 100% | 76% | 100% | 100% | 50% | **85%** |
| 7 | （41.15, 61.45） | 86.1 | 100% | 68% | 100% | 100% | 100% | **94%** |
| 8 | （45.45, 73.75） | 85.9 | 100% | 70% | 100% | 100% | 100% | **94%** |
| 9 | （41.65, 57.75） | 85.4 | 100% | 66% | 100% | 100% | 100% | **93%** |
| 10 | （38.85, 56.85） | 85.1 | 100% | 53% | 67% | 100% | 100% | **84%** |

**meridiani**

| # | 地點 | 總體 | 權重 ±50% | 隨機權重 | 合成方式 | 排名池門檻 | 最小間距 | 總穩定度 |
|---|---|---|---|---|---|---|---|---|
| 1 | （42.55, 97.65） | 89.9 | 100% | 90% | 100% | 100% | 100% | **98%** |
| 2 | （47.15, 87.05） | 89.8 | 100% | 71% | 100% | 50% | 100% | **84%** |
| 3 | （42.15, 102.05） | 89.8 | 100% | 87% | 100% | 100% | 100% | **97%** |
| 4 | （49.15, 93.05） | 89.4 | 100% | 69% | 100% | 50% | 100% | **84%** |
| 5 | （45.65, 90.95） | 89.1 | 100% | 68% | 100% | 100% | 100% | **94%** |
| 6 | （44.85, 94.35） | 89.0 | 100% | 69% | 67% | 100% | 100% | **87%** |
| 7 | （37.55, 93.95） | 89.0 | 100% | 72% | 100% | 100% | 100% | **94%** |
| 8 | （46.95, 74.95） | 88.9 | 100% | 55% | 100% | 50% | 100% | **81%** |
| 9 | （43.95, 96.35） | 88.5 | 100% | 63% | 100% | 100% | 50% | **83%** |
| 10 | （42.65, 95.75） | 88.5 | 100% | 63% | 67% | 100% | 50% | **76%** |

**protonilus**

| # | 地點 | 總體 | 權重 ±50% | 隨機權重 | 合成方式 | 排名池門檻 | 最小間距 | 總穩定度 |
|---|---|---|---|---|---|---|---|---|
| 1 | （30.95, 84.55） | 86.6 | 100% | 80% | 100% | 100% | 100% | **96%** |
| 2 | （32.45, 82.95） | 86.3 | 100% | 78% | 100% | 100% | 50% | **86%** |
| 3 | （31.35, 87.95） | 85.8 | 100% | 74% | 100% | 100% | 100% | **95%** |
| 4 | （33.75, 80.65） | 85.6 | 100% | 64% | 100% | 100% | 100% | **93%** |
| 5 | （41.65, -107.35） | 85.3 | 100% | 62% | 100% | 100% | 100% | **92%** |
| 6 | （-32.35, -69.15） | 84.8 | 100% | 43% | 67% | 100% | 100% | **82%** |
| 7 | （41.65, -109.45） | 84.5 | 100% | 58% | 100% | 100% | 100% | **92%** |
| 8 | （32.25, 86.55） | 84.4 | 100% | 58% | 100% | 100% | 50% | **82%** |
| 9 | （38.25, -111.15） | 84.3 | 100% | 46% | 100% | 100% | 100% | **89%** |
| 10 | （38.75, -108.25） | 84.2 | 90% | 45% | 67% | 100% | 50% | **70%** |

**ap105**

| # | 地點 | 總體 | 權重 ±50% | 隨機權重 | 合成方式 | 排名池門檻 | 最小間距 | 總穩定度 |
|---|---|---|---|---|---|---|---|---|
| 1 | （49.95, 88.65） | 86.1 | 100% | 97% | 100% | 100% | 100% | **99%** |
| 2 | （49.85, 95.15） | 85.4 | 100% | 91% | 100% | 100% | 100% | **98%** |
| 3 | （33.45, 82.95） | 84.1 | 100% | 79% | 67% | 100% | 100% | **89%** |
| 4 | （48.35, 92.65） | 83.7 | 100% | 97% | 100% | 100% | 50% | **89%** |
| 5 | （48.55, 88.55） | 82.7 | 100% | 60% | 67% | 100% | 50% | **75%** |
| 6 | （37.35, 90.05） | 82.6 | 100% | 64% | 100% | 100% | 100% | **93%** |
| 7 | （34.55, 84.65） | 81.8 | 100% | 61% | 67% | 100% | 50% | **76%** |
| 8 | （33.95, 80.85） | 81.6 | 100% | 52% | 67% | 100% | 50% | **74%** |
| 9 | （35.05, 90.65） | 81.5 | 80% | 52% | 67% | 100% | 100% | **80%** |
| 10 | （39.15, 73.35） | 81.2 | 100% | 40% | 100% | 100% | 100% | **88%** |

全部目標的前 10 名（70 個）：總穩定度 ≥ 80% 的 64 個，50–80% 的 6 個，< 50% 的 0 個。

### 3.2 方法變體的細節

**植被獨立後，第 1 節的分面向找回**（地表物質只看岩性＋熱慣量）

| 指標 | 現在 | 植被獨立 |
|---|---|---|
| 百分位中位數 | 11.7% | 23.6% |
| 前 10% 的比例 | 47% | 21% |
| 前 25% 的比例 | 71% | 59% |

| 目標 | 已知類比地 | 地表物質：現在 → 只看岩石 |
|---|---|---|
| jezero | Bockfjorden Volcanic Complex Svalbard (Norway) | 0% → 22% |
| jezero | Mars Desert Research Station Hanksville (Utah) | 13% → 61% |
| jezero | Black Point Lava Flow (Arizona) | 13% → 59% |
| jezero | Lavic Lake and Sunshine volcanic field Mojave Desert (California) | 8% → 55% |
| jezero | Lake Salda (Turkey) | 51% → 31% |
| jezero | Askja lava fields Vikrahraun (Iceland) | 8% → 78% |
| jezero | Matanumadh jarosite locality Kachchh (India) | 45% → 17% |
| gale | Atacama Desert Yungay core (Chile) | 25% → 74% |
| gale | Mars Desert Research Station Hanksville (Utah) | 12% → 60% |
| gale | Navajo Sandstone hematite concretions southern Utah | 10% → 30% |
| gale | Pilot Valley paleolake playa (Utah) | 8% → 57% |
| gale | Badwater Basin Death Valley (California) | 1% → 29% |
| gale | Lavic Lake and Sunshine volcanic field Mojave Desert (California) | 8% → 54% |
| gale | White Sands gypsum dunes and Lake Lucero (New Mexico) | 23% → 70% |
| gale | Rio Tinto acid river headwaters (Spain) | 45% → 16% |
| gale | Askja lava fields Vikrahraun (Iceland) | 9% → 79% |
| gale | Matanumadh jarosite locality Kachchh (India) | 44% → 15% |
| gale | Dalangtan saline playa Qaidam Basin (China) | 20% → 74% |
| gale | Dallol geothermal area Afar (Ethiopia) | 1% → 31% |
| gale | AMADEE-18 field site Marmul area Dhofar (Oman) | 16% → 63% |
| arcadia | Bockfjorden Volcanic Complex Svalbard (Norway) | 26% → 93% |
| arcadia | Pilot Valley paleolake playa (Utah) | 3% → 28% |
| arcadia | Mauna Kea upper slopes palagonitic tephra (Hawaii) | 64% → 5% |

（只列變動 ≥ 15 個百分點的。）

**溫度飽和後，環境面向的前 3 名**

| 目標 | 現在 | 冷到最冷 10% 就滿分 |
|---|---|---|
| jezero | ；； | ；； |
| gale | ；； | ；； |
| arcadia | ；； | ；； |
| oxia | ；； | ；； |
| meridiani | ；； | ；； |
| protonilus | ；； | ；； |
| ap105 | ；； | ；； |

注意：環境面向的兩個變數（溫度、乾燥度）都是「越極端越像」，和火星目標無關，所以每個目標的環境前幾名都一樣；溫度飽和只會換掉被極端值獨佔的地點，不會讓它隨目標改變。

「沒冰的目標不算冰」適用 SWIM Ci < 0.1 的目標（同 R3、R5 的標準）：jezero、gale、oxia、meridiani；其他目標標「—」。

## 4. 區域層級的找回

前 20 名落在任一已知類比地 300 km 內的比例，和排名池裡隨機一格的比例（面積加權）相比。

| 目標 | 前 20 名 | 隨機 | 倍數 |
|---|---|---|---|
| jezero | 5% | 3.1% | 1.6 |
| gale | 0% | 3.1% | 0.0 |
| arcadia | 5% | 3.1% | 1.6 |
| oxia | 10% | 3.1% | 3.2 |
| meridiani | 10% | 3.1% | 3.2 |
| protonilus | 20% | 3.1% | 6.4 |
| ap105 | 5% | 3.1% | 1.6 |

已知類比地本身偏向容易到達、研究多的地方，所以這是區域層級的佐證，不是準確率。

## 5. 已知類比地 → 面向對照（本隊判斷）

| 地點 | 面向 |
|---|---|
| atacama_yungay | environment、surface |
| mcmurdo_dry_valleys | environment、water_ice |
| beacon_valley | water_ice、environment |
| haughton_crater | environment、water_ice |
| axel_heiberg_lost_hammer | environment、water_ice |
| svalbard_bockfjorden | surface、water_ice |
| mdrs_hanksville | surface、terrain |
| utah_navajo_concretions | surface |
| pilot_valley_utah | surface |
| black_point_lava_flow | surface、terrain |
| death_valley_badwater | surface、environment |
| mojave_lavic_lake | terrain、surface |
| white_sands_lake_lucero | surface |
| pavilion_lake | （量不到，不算） |
| lake_salda | surface |
| rio_tinto | surface |
| ries_crater | （量不到，不算） |
| askja_vikrahraun | surface、terrain |
| lanzarote | surface、terrain |
| mauna_kea_palagonite | surface |
| hiseas_mauna_loa | terrain、surface |
| kau_desert_kilauea | surface |
| lonar_crater | surface |
| kachchh_matanumadh | surface |
| qaidam_dalangtan | surface、environment |
| dallol | surface |
| dhofar_amadee18 | terrain、surface、environment |
| pilbara_dresser | （量不到，不算） |

## 6. 限制

- 沒有「正確答案」：已知類比地多半因為單一特徵被選上，也偏向容易到達的地方。
- 已知類比地只有 28 個，而且 4 個目標（ap105、oxia、meridiani、protonilus）沒有標給它們的已知類比地，第 1 節只涵蓋 jezero、gale、arcadia。
- 面向對照是人工判斷；改 `SITE_DIMS` 就能重算。
- 負對照只有 8 個點，用來排除「算法亂來」，不能證明排在前面的就是好的類比地。
- 穩健性只改了「怎麼合成、怎麼篩選」，沒有改輸入資料本身（例如溫度 ±1–2 K 的誤差）、單一變數的比較參數，也沒有改火星端的目標值；這些列為之後的工作。
