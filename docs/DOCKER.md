# Run the project on Windows with Docker

## First-time setup

1. Download Docker Desktop from the [official Windows installation page](https://docs.docker.com/desktop/setup/install/windows-install/).
2. Use the WSL 2 backend and Linux containers; this project uses Linux images.
3. Follow the installer instructions for WSL installation/updates or restarting Windows. Open Docker Desktop after installation and wait for its engine to become ready.
4. Open a new PowerShell window and check:

```powershell
docker version
docker compose version
```

`docker version` should show both Client and Server. If only Client appears or the connection fails, check Docker Desktop. If the command is not found, reopen the terminal so it reads the updated PATH.

For the per-user installation in this workspace, a Git Bash session can temporarily add Docker with:

```bash
export PATH="/c/Users/User/AppData/Local/Programs/DockerDesktop/resources/bin:$PATH"
docker version
```

This affects that shell only. Fully restart the terminal or VS Code to pick up installation changes for new sessions.

## Start the application

```powershell
cd D:\NASA
docker compose config --quiet
docker compose up --build -d
docker compose ps
```

`config --quiet` validates configuration. `up --build -d` downloads images, builds the application, and starts it in the background. The first run downloads Python, Node, CBC, and other dependencies; duration depends on the network and computer. `ps` shows six services, initially starting and then healthy.

Open **http://localhost:8080**. Placeholder warnings are expected with the demo dataset.

- http://localhost:8080/api/catalog/docs
- http://localhost:8080/api/measurements/docs
- http://localhost:8080/api/similarity/docs
- http://localhost:8080/api/planning/docs

Docker provides Python and Node inside the images; host installations are not required for this mode.

## Everyday commands

| Purpose | Command |
|---|---|
| View service status | `docker compose ps` |
| Follow logs; Ctrl+C stops viewing | `docker compose logs -f` |
| Follow scoring and planning logs | `docker compose logs -f similarity planning` |
| Rebuild after source changes | `docker compose up --build -d` |
| Pause containers | `docker compose stop` |
| Start existing containers | `docker compose start` |
| Remove this stack's containers and network | `docker compose down` |

Seed files live in `D:\NASA\data` and are mounted read-only. Normal `down` does not delete that host directory.

## Development with hot reload

Stop normal mode before starting the development override:

```powershell
docker compose down
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

This displays foreground logs and uses Vite and uvicorn reload. Rebuild after changing dependencies. If the frontend node_modules volume contains stale packages, use the npm ci command in README.md.

## Troubleshooting

- Port 8080 in use: stop a previous `scripts/dev.py`, or copy `.env.example` to `.env`, set `PORT=8081`, run up again, and open localhost:8081.
- Gateway not starting: use `docker compose ps` to find an unhealthy dependency, then `docker compose logs SERVICE` to inspect it.
- Old content after editing data: run `docker compose restart catalog measurements similarity planning` to reload files and clear caches.
- Download/build failures: inspect Docker Desktop's network and registry connectivity, and share the relevant error with the team.

With host Python development dependencies installed, check real HTTP integration with:

```powershell
.\.venv\Scripts\python.exe scripts/smoke.py
```

The script checks four API docs/health prefixes and lunar/Martian scoring and planning. Its time-series case uses demo-01; update it when adopting a real dataset.

Production Docker mode has been validated: six healthy containers, all smoke checks passing through localhost:8080, and HTTP 200 for the homepage and production JavaScript/CSS. The development override and manual browser visual acceptance remain outstanding.

References: [Windows installation](https://docs.docker.com/desktop/setup/install/windows-install/), [Compose quickstart](https://docs.docker.com/compose/gettingstarted/).


After rebuilding or recreating backend containers, run `docker compose restart gateway` to refresh Nginx service addresses. If a health URL reports a different service name, stale address resolution is likely; run `scripts/smoke.py` again after the gateway restart.
