# Project video — Earth Analog Finder (30s)

`EarthAnalogFinder_30s.mp4` — 30.0s, 1920×1080, 30 fps, H.264 + AAC.

| Time | Content | On screen |
|---|---|---|
| 0–7s | Mars: astronaut wide shot → boot in red dust → visor reflecting Mars → glove on red rock | Before Mars… |
| 7–8s | Black, silence | — |
| 8–15s | Earth: boot in sand → visor → glove on sandstone → wide shot | …we practise on Earth. → EARTH ANALOG FINDER — "Find the places on Earth that match the Moon and Mars." |
| 15–19s | Website: home → Moon/Mars cards → Moon missions | MOON · MARS — Pick a mission |
| 19–24s | Moon Earth analogs (Northern Yakutia 92.7/100) + map, then Mars ranking + map | EARTH ANALOGS — See where on Earth to test it |
| 24–26s | Mars missing-evidence section | LIMITS — …and what Earth can't reproduce |
| 26–30s | Website globe + logo | EARTH ANALOG FINDER / Our home planet. A testbed for other worlds. |

## AI disclosure (Space Apps rules)
**Intro shots (0–15s) generated with Google Veo 3.1 (Google Flow).** Everything from 15s on is a real screen capture of this project's website. Earth imagery: NASA. No music; audio is Veo's generated ambience.

## How it was made
- Intro: 8 Veo clips (wide shots + boot/visor/glove match cuts on Mars and Earth).
- Website footage: automated capture of the local site (Playwright driving Edge, frames encoded with ffmpeg), English UI.
- Assembly, captions and logo: ffmpeg, with captions rendered from the website's own font and logo.

Source clips and the recorder/assembly scripts are kept outside this repo (Ian's `nasa-video` folder); ask Ian if you need to re-cut the video.
