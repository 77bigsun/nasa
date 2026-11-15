# Project video — Earth Analog Finder (30s)

`EarthAnalogFinder_30s.mp4` — 30.0s, 1920×1080, 30 fps, H.264 + AAC, with voice-over and background music.

| Time | Content | Voice-over / subtitles |
|---|---|---|
| 0–4.5s | Moon wide shot → Mars wide shot → boot in lunar dust → visor reflecting Mars | Before missions… |
| 4.5–5.2s | Black, silence | — |
| 5.2–10s | Earth: boot in sand → visor → glove on sandstone → wide shot with the title | …we practise on Earth. / Earth Analog Finder. |
| 10–13.3s | Split screen MOON / MARS: the two systems side by side | Two systems — one for the Moon, one for Mars. |
| 13.3–16.5s | Moon mission M3 selected, then the Mars test cards | Pick a mission, and the tests it needs. |
| 16.5–20.5s | Northern Yakutia (76.6/100) with its satellite image on hover, then the Mars AP-105 ranking map | Find the places on Earth that match it best… |
| 20.5–24s | Feature similarity radar chart | …see why, feature by feature… |
| 24–27s | "Where the feature weights come from" | …and exactly how it's scored. |
| 27–30s | Globe + logo + credits | Our home planet. A testbed for other worlds. |

Website footage is from the "final version" of this repo (c089480), captured locally in English.

## AI disclosure (Space Apps rules)
- **Intro shots (0–10s) generated with Google Veo 3.1 (Google Flow).**
- **Voice-over generated with ElevenLabs** (voice "Brian – Deep, Resonant and Comforting").
- **Background music generated with Google Flow Music** (Lyria; track "Deep Space Odyssey"), edited to the cuts and ducked under the voice.
- Everything from 10s to 27s is a real screen capture of this project's website. Earth imagery: NASA. Ambience is Veo's generated audio. No copyrighted music.

## How it was made
- Intro: Veo clips (Moon and Mars wide shots and close-ups, Earth match cuts).
- Website footage: automated capture of the local site (Playwright driving Edge, frames encoded with ffmpeg).
- Assembly, subtitles (Orbitron / Exo 2) and logo: ffmpeg, with text rendered from the website's own logo.

Source clips and the recorder/assembly scripts are kept outside this repo (Ian's `nasa-video` folder); ask Ian if you need to re-cut the video.
