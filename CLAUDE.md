# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SameAge (Immich Edition) is a containerized Flask app that compares photos of people organized by age. It pulls all data (people, birthdays, assets, thumbnails) from an Immich instance via its API — no local database needed. Users select people from Immich, and the app groups their photos side-by-side at matching age-in-weeks milestones.

## Development Commands

```bash
# Build and run with Docker Compose (serves at http://localhost:5050)
cd immich && docker compose up --build

# Rebuild after code changes
cd immich && docker compose up --build -d --force-recreate

# View logs
cd immich && docker compose logs -f

# Stop
cd immich && docker compose down
```

**Configuration:** Set `IMMICH_API_KEY` in `immich/.env` or export it. `IMMICH_URL` defaults to `http://192.168.178.19:2283`.

**Dependencies:** Flask, Gunicorn, Requests. Managed via `immich/requirements.txt`.

## Architecture

**Single Flask app** in `immich/`. No database — all data comes from the Immich API at runtime.

**Routes:**

| Route | Purpose |
|---|---|
| `GET /` | Person selection page — shows Immich people with face thumbnails |
| `GET /gallery?persons=id1&persons=id2` | Gallery view for selected people, grouped by age-in-weeks |
| `GET /person-thumbnail/<person_id>` | Proxy for Immich person face thumbnail |
| `GET /thumbnail/<asset_id>` | Proxy for Immich asset thumbnail (preview size) |
| `GET /original/<asset_id>` | Proxy for full-resolution Immich asset (used in fullscreen) |

**Gallery view logic:**
1. Fetch people list from `GET /api/people`, filter to those with name + birthDate
2. For selected people: `POST /api/search/metadata` with `personIds` filter to get assets
3. Compute `age_in_weeks` for each asset using `(capture_date - birthDate)`
4. Group into rows by week, render template with columns per person

**Proxy routes** keep the Immich API key server-side — the browser never sees it.

**Frontend:** Bootstrap 5.3 (CDN), vanilla JS. Lazy loading via Intersection Observer. Hover-to-enlarge with person name and capture date overlay. Photo selection with fullscreen side-by-side comparison.

**Key files:**
- `immich/app.py` — Flask app: routes, Immich API client, gallery grouping logic
- `immich/utils.py` — age calculation helpers (`get_number_of_weeks`, `diff_str`)
- `immich/templates/select.html` — person selection page with face thumbnail cards
- `immich/templates/gallery.html` — photo gallery grouped by age-in-weeks
- `immich/static/style.css` — all styling
- `immich/static/timeline.js` — hover preview, photo selection, fullscreen, lazy loading
- `immich/Dockerfile` — Python 3.11 slim + gunicorn
- `immich/docker-compose.yml` — single service, port 5050, env vars
