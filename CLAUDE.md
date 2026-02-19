# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SameAge is a containerized Flask app that compares photos of people organized by age. It connects to an Immich instance via its API — no local database needed. Users select people from Immich, and the app groups their photos side-by-side at matching age-in-weeks milestones.

## Development Commands

```bash
# Build and run with Docker Compose (serves at http://localhost:5050)
docker compose up --build

# Rebuild after code changes
docker compose up --build -d --force-recreate

# View logs
docker compose logs -f

# Stop
docker compose down

# Reset config and rebuild
docker compose down -v && docker compose up --build
```

**First run:** No env vars needed. Open `http://localhost:5050` and the setup wizard will guide you through connecting to Immich. Config is persisted in a Docker volume.

**Env var override:** Set `IMMICH_URL` and `IMMICH_API_KEY` in `.env` or as environment variables to skip the setup wizard.

## Linting

```bash
# Python (ruff)
ruff check app/
ruff format --check app/

# JS/CSS (biome)
biome check app/static/
```

Both run in CI via GitHub Actions on every push and PR.

## Architecture

**Single Flask app** in the `app/` package. No database — all data comes from the Immich API at runtime. Config is stored in `/data/config.json` (Docker volume).

**Routes:**

| Route | Purpose |
|---|---|
| `GET /` | Person selection page — shows Immich people with face thumbnails |
| `GET /setup` | Setup wizard (URL + API key validation) |
| `POST /setup/check-url` | AJAX: validate Immich URL reachability |
| `POST /setup/check-key` | AJAX: validate API key + check permissions |
| `GET /gallery?persons=id1&persons=id2` | Gallery view, grouped by age-in-weeks |
| `GET /person-thumbnail/<person_id>` | Proxy for Immich person face thumbnail |
| `GET /thumbnail/<asset_id>` | Proxy for Immich asset thumbnail (preview size) |
| `GET /original/<asset_id>` | Proxy for full-resolution Immich asset (fullscreen) |

**Gallery view logic:**
1. Fetch people list from `GET /api/people`, filter to those with name + birthDate
2. For selected people: `POST /api/search/metadata` with `personIds` filter to get assets
3. Compute `age_in_weeks` for each asset using `(capture_date - birthDate)`
4. Group into rows by week, render template with columns per person
5. Rows with >8 thumbnails per column are collapsed with a "+N" expand overlay

**Proxy routes** keep the Immich API key server-side — the browser never sees it.

**Frontend:** Bootstrap 5.3 (CDN), vanilla JS. Lazy loading via Intersection Observer. Hover-to-enlarge with person name and capture date overlay. Photo selection with fullscreen side-by-side comparison.

**Key files:**
- `app/__init__.py` — Flask app: routes, Immich API client, config management, gallery grouping logic
- `app/utils.py` — age calculation helpers (`get_number_of_weeks`, `diff_str`)
- `app/templates/setup.html` — two-step setup wizard with async validation
- `app/templates/select.html` — person selection page with face thumbnail cards
- `app/templates/gallery.html` — photo gallery grouped by age-in-weeks
- `app/static/style.css` — all styling
- `app/static/timeline.js` — hover preview, photo selection, fullscreen, lazy loading, collapsible rows
- `Dockerfile` — Python 3.13 slim + gunicorn
- `docker-compose.yml` — single service, port 5050, persistent volume
- `pyproject.toml` — ruff config
- `biome.json` — biome config
