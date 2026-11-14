# Finding places on Earth that are like Mars: what we did

*NASA Space Apps Challenge 2026, Mars group. Written 14 Nov 2026, evening. Plain-language summary; the technical details are in `PROJECT_CONTEXT.md` and `WORKLOG_B_1114.md`.*

---

## 1. The question

The challenge asks: **which places on Earth are good stand-ins ("analogs") for places on Mars?**

Scientists and engineers test rovers, drills, landing systems and instruments in places like the Atacama Desert or Antarctica because those places resemble Mars in some way. The organisers asked teams to:

- compare places scientifically (rocks, temperature, ice, dust, terrain), not just by how they look;
- think about missions (landing, driving, drilling, finding water);
- say honestly **where the comparison works and where it breaks**, because no place on Earth is a perfect copy of Mars;
- search the **whole planet** systematically, not just list the famous analog sites.

## 2. Who did what

| Person | Role |
|---|---|
| IanChen (A) | Mars side: measures each Mars target from Mars datasets |
| B (this worklog) | Earth side: measures the whole Earth, builds the scoring, checks the results |
| Harris | Integrator: builds the website and the overall plan (the tests R1–R6) |
| Moon group | Same challenge for the Moon, separate code |

## 3. The big idea in one paragraph

We do **not** train a model to "predict" analogs. Instead we **compare**. For a Mars site, we write down its properties (how steep, how cold, how dusty, what rock, whether there is ice). Then for **every patch of land on Earth** we ask, one property at a time, "how close is this to Mars?" and give a mark between 0 (nothing alike) and 1 (as close as Earth can get). Finally we combine the marks into one score and rank the places. Think of it as matching a fingerprint, ridge by ridge, against every fingerprint in a database.

## 4. Step by step

### Step 1: describe the Mars sites

IanChen wrote a program that reads Mars datasets and measures a circle (usually 50 km across) around each target. We have **7 Mars targets**:

- **Jezero Crater** (Perseverance rover), **Gale Crater** (Curiosity rover)
- **Arcadia Planitia** and **AP-105**, the SkyFall mission's reference landing site in Arcadia
- **Oxia Planum** (clay minerals), **Meridiani Planum** (sulfate minerals, Opportunity rover)
- **Protonilus Mensae** (ice-rich, glacier-like landforms)

For each target we record: slope, roughness, thermal inertia (how fast the ground heats and cools, which tells sand from rock), rock type, buried ice, average temperature, day–night temperature swing, dust, plus how dust and temperature change through the Martian year.

Example, AP-105: very flat (slope 0.2°), medium thermal inertia (181), basalt, likely ice below the surface, average −73 °C, swings of about 75 °C between day and night.

### Step 2: describe the whole Earth

We cut all land into a grid of **0.1° squares (about 11 km on a side): 1.44 million squares**. For each square we measured the same properties using **Google Earth Engine**, a free cloud service that holds many NASA and ESA satellite datasets. The calculations run on Google's computers and we only download one number per square.

| Property | Earth data (source) |
|---|---|
| Slope, roughness | Elevation maps (USGS GMTED2010, Copernicus) |
| Temperature, day–night swing | MODIS satellites (NASA), 10 years |
| Plants or bare ground | MODIS vegetation index (NDVI) |
| Thermal inertia | Estimated from MODIS temperature and brightness |
| Rock type | Global lithology map (GLiM) |
| Frozen ground | ESA permafrost map |
| Dryness | Global Aridity Index |
| Dust | NASA MERRA-2 dust model |
| Minerals | ASTER satellite (NASA/Japan) |
| Glaciers | GLIMS glacier outlines |

### Step 3: compare one property at a time

Each property gets a mark from 0 to 1. Different properties need different kinds of comparison:

- **Same units on both planets** (slope, roughness): the closer the numbers, the higher the mark.
- **Different instruments or units** (thermal inertia, dust): we compare **rank on its own planet**. If a Mars site is dustier than 60% of Mars, we look for Earth places that are dustier than about 60% of Earth.
- **Mars is beyond anything on Earth** (cold, dryness): no place on Earth is −73 °C on average, so we give the highest mark to the **most extreme** places on Earth (the coldest, the driest).
- **Categories** (rock type): we use a lookup table, e.g. basalt on Mars matches volcanic rock on Earth.
- **Missing data**: we never fill a gap with 0. The property is skipped and the others share its weight. If too much is missing, the place is not ranked.

We tried three ways of comparing; this mixed approach was the best or close to the best at putting known analog sites near the top.

### Step 4: combine the marks

We built three ways of combining, then kept two:

1. **Analog profile ("how alike overall?")** *(kept)*. The properties are grouped into 7 aspects: terrain, surface material, extreme environment, water and ice, dust, biology, underground. Biology and underground have no global data yet, so they are not scored. Each aspect gets a score, and the overall score is out of 100. Besides the overall top 20, we list the **top 5 for each aspect and for each single property**, for example "the 5 places with the most Mars-like temperature" or "the 5 places with the most Mars-like rock". One picture per target (`board_<target>.png`) shows them all on world maps.

2. **Mission tests R1–R6 ("can I test this here?")** *(kept)*. These come from Harris's plan for the SkyFall mission:

   | Test | Meaning | What we check on Earth |
   |---|---|---|
   | R1 | Landing surface | Gentle slope, roughness like the target, firm ground, no plants, no ice sheet |
   | R2 | Visual navigation (helicopter) | Not possible yet: no global image-texture data |
   | R3 | Shallow buried ice | Permafrost, below-freezing average, very dry |
   | R4 | Water-bearing minerals | Right rock type, bare rock, mineral signal from ASTER |
   | R5 | Ice-related landforms | Permafrost, cold, similar terrain, near glaciers |
   | R6 | Dust and weather | Dust level, cold, big day–night swing, similar seasonal pattern |

   Some checks are **pass/fail-style with a soft edge**: for example, slope at or below 5° scores 1, at or above 15° scores 0, and in between it goes down evenly. Others compare with the Mars target as in Step 3. R3 and R5 only apply to Mars targets that actually have ice.

3. **Mission version with learned weights** *(dropped on 14 Nov)*. This one weighted the properties differently for four mission types and "learned" the weights from known analog sites. We dropped it because its mission types did not match the challenge's tests, and the website and Harris's plan both use R1–R6.

**Why we multiply instead of average** (a "geometric mean"): if one property is terrible, the whole score drops. A place that is perfect in every way except being a rainforest should not score well.

### Step 5: check our work

- **Known analog sites as a test**: we have a list of 28 famous analog sites (Atacama, Devon Island's Haughton Crater, Antarctica's Dry Valleys, Utah's Mars Desert Research Station and others). A good method should rank them higher than random land. We measured this with a standard score called AUC (0.5 = guessing, 1 = perfect), using "leave-one-out" testing so a site is never used to grade itself. The weighted version scored about 0.7–0.8. The same known sites are also checked in every profile and test result.
- **A second opinion from machine learning**: we also trained Random Forest and XGBoost models to cross-check which properties matter most.
- **Hand checks**: we recomputed several scores by hand and they matched the program.

### Step 6: zoom in

An 11 km square can hide a lake or a cliff. For the best places, we look at a ~55 km box around them in **1 km pieces**, recompute the scores, skip pieces right next to water, and add detail such as 2 m elevation models in the Arctic (ArcticDEM), 8 m in Antarctica (REMA), and radar images. This tells us **which exact spot** inside the square is the best analog.

### Step 7: hand the data to the website

The website (built by Harris) has its own scoring. We export our measured values in its format (`scripts/export_web_seed.py`, output in `outputs/web/`). Its current ranking method is temporary, so we do not tune our method to it.

## 5. Problems we found and fixed

| Problem | What was wrong | Fix |
|---|---|---|
| Ice target | The Mars ice signal ranges from −1 to +1. The old formula told Jezero (no ice) to look for places with 40% frozen ground | "No ice signal" now means "look for no ice" |
| Lakes mixed into land | Some 11 km squares averaged lake water with land, so temperature swings looked tiny. A top Jezero match in Mongolia was a lakeshore | Remove water before averaging (re-download pending) |
| Missing data as an advantage | Places missing one property sometimes ranked higher because they had fewer chances to fail | All properties required; Antarctica gets "no plants" and "very dry" filled in because that is true there |
| Glaciers ranked as landing sites | Ice sheets look flat and bare | Added an "ice-free" check |
| Snowy tundra looked barren | Yearly average plant cover is low where snow lies most of the year | Use summer plant cover (download pending) |
| Mineral signal biased to cold places | Temperature affects the ASTER mineral signal | Rank minerals only among places with similar temperature |

## 6. Early results (will change after the re-download)

- **AP-105 (SkyFall)**: the most alike places overall are in the high, cold, dry basins of **western Mongolia and the Altai** (for example near Kosh-Agach, Russia). For buried ice (R3) the best places are in **Antarctica near McMurdo**. For dust and weather (R6) the best is also near Kosh-Agach.
- **Temperature**: the most Mars-like temperatures are always in the **high Arctic**, because Mars is colder than anywhere on Earth.
- **No single place is good at everything.** A place that matches the terrain often does not match the cold, and vice versa. This is why we show the best place for each aspect separately, and why the next step picks a **small set of places** that together cover all tests.

## 7. What Earth cannot copy

These are listed for every site and never scored: **gravity** (Mars has 38% of Earth's), **air pressure** (about 0.6% of Earth's), **radiation** (no magnetic field, thin air), and **air composition** (about 95% CO₂).

## 8. Still to do

1. Finish the re-download of the corrected Earth data on B's computer and re-run everything (instructions: `docs/PROMPT_local_rerun_1114.md`).
2. **Set covering**: choose the fewest Earth sites that together cover all tests for a Mars target, and show how much each extra site adds.
3. R2 visual navigation needs image-texture data (Sentinel-2 on Earth, CTX on Mars).
4. Coordinates for the other SkyFall regions (Deuteronilus, Utopia, Phlegra, Erebus).
5. Look at the top new candidates on satellite images (NASA Worldview links are in the results).

## 9. Words used above

| Term | Meaning |
|---|---|
| Analog | A place on Earth that is like a place on Mars in some useful way |
| 0.1° grid square | A patch of land about 11 km × 11 km |
| Percentile / rank | "Dustier than 60% of the planet" = 60th percentile |
| Thermal inertia | How quickly the ground heats and cools; loose sand changes fast, solid rock slowly |
| NDVI | A satellite measure of green plants; 0 or below means bare ground |
| Geometric mean | Multiplying scores together (then taking the root), so one bad score pulls the total down |
| AUC | How well a score puts the right answers on top: 0.5 = random, 1 = perfect |
| Set covering | Picking the smallest group of places that together meet every requirement |
| Google Earth Engine | A free cloud service with satellite datasets that can do calculations for you |

## 10. Where to find things

| What | File |
|---|---|
| Full project rules | `docs/PROJECT_CONTEXT.md` |
| Daily log, every decision | `docs/WORKLOG_B_1114.md` |
| Analog profile results | `outputs/profiles/PROFILE_SUMMARY.md`, `board_<target>.png` |
| Mission test results | `outputs/mission_tests/TEST_SUMMARY.md` |
| Data for the website | `outputs/web/WEB_EXPORT.md` |
| Zoom results | `outputs/zoom/` |

---

*Use of AI (required by Space Apps rules): parts of the code and documents were written with AI assistants (Claude and Claude Code) and reviewed by the team. All data come from the public sources listed above.*
