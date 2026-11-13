"""Folders and the Mars sphere radius shared by every adapter."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "config"
RAW_MARS = ROOT / "data" / "raw" / "mars"
PROCESSED = ROOT / "data" / "processed"
MAPPINGS = ROOT / "data" / "mappings"

R_MARS = 3396190.0          # IAU Mars sphere radius (m), used for distances and the local metric projection
MARS_LONLAT = f"+proj=longlat +R={R_MARS} +no_defs"
