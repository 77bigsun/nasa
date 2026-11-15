# Project video — Earth Analog Finder (30s)

`EarthAnalogFinder_30s.mp4` — 30.0s, 1920×1080, 30 fps, H.264 + AAC.

| Time | Content | On screen / voice-over |
|---|---|---|
| 0–7s | Moon & Mars: Moon wide shot → Mars wide shot → boot in lunar dust → visor reflecting Mars | BEFORE MISSIONS… |
| 7–8s | Black, silence | — |
| 8–15s | Earth: boot in sand → visor → glove on sandstone → wide shot with title | …WE PRACTISE ON EARTH. → EARTH ANALOG FINDER |
| 15–19s | Website: home → Moon/Mars cards → Moon missions | Pick a mission — a base on the Moon, a landing on Mars. |
| 19–23s | Mars ranking + map, Moon Earth analogs on the map | Find the places on Earth that match it best… |
| 23–26s | Top Earth analog (Northern Yakutia 92.7/100) with its feature scores | …and see why it's the best fit. |
| 26–30s | Website globe + logo | Our home planet. A testbed for other worlds. |

Text: Orbitron (titles) and Exo 2 Light (subtitles), white; logo in the site's mint. The subtitles are also the voice-over script (voice not recorded yet).

## AI disclosure (Space Apps rules)
**Intro shots (0–15s) generated with Google Veo 3.1 (Google Flow).** Everything from 15s on is a real screen capture of this project's website. Earth imagery: NASA. No music; audio is Veo's generated ambience.

## How it was made
- Intro: Veo clips: Moon and Mars wide shots and close-ups, then boot/visor/glove match cuts on Earth.
- Website footage: automated capture of the local site (Playwright driving Edge, frames encoded with ffmpeg), English UI.
- Assembly, captions and logo: ffmpeg, with captions rendered from the website's own font and logo.

Source clips and the recorder/assembly scripts are kept outside this repo (Ian's `nasa-video` folder); ask Ian if you need to re-cut the video.
