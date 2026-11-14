# Future ingestion worker

Not implemented in this prototype. The Compose file reserves the role in a comment.

Planned boundary: use earthaccess / openEO to retrieve products, apply quality masks,
record acquisition time, footprint, units, native resolution and product version,
align spatial scales and spectral wavelength grids, convert temporal axes to local
solar phase / Mars Ls, then export the validated measurement contract in data/README.md.

Do not flip `is_placeholder` to false merely because a download succeeded. Product
provenance, calibration, coverage and uncertainty need team review first. Never add
Earthdata credentials to Git; the future worker must read runtime secrets.
