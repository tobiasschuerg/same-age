# SameAge

Compare photos of people at the same age. Connects to your [Immich](https://immich.app/) instance and groups photos side-by-side at matching age milestones.

Select people from your Immich library, and SameAge displays their photos organized by age-in-weeks — so you can see what everyone looked like at 12 weeks, 6 months, 2 years, etc.

## Requirements

- A running [Immich](https://immich.app/) instance with people identified and birthdates set
- Docker and Docker Compose

## Quick Start

```bash
docker compose up --build
```

Open `http://localhost:5050`. The setup wizard will ask for:

1. **Immich URL** — automatically verified
2. **API key** — create one in Immich under *User Settings > API Keys* with **People**, **Search**, and **Assets** permissions

Config is saved in a Docker volume and persists across restarts.

## Configuration

The setup wizard is the recommended way to configure SameAge. Alternatively, set environment variables to skip it:

```bash
IMMICH_URL=http://your-immich-host:2283
IMMICH_API_KEY=your-api-key
```

Add these to a `.env` file or pass them via `docker-compose.yml`.

Only people with a birthdate set in Immich are shown. Set birthdates in Immich under *People > Edit*.

## How It Works

Photos are grouped by age-in-weeks. Select two or more people and the gallery shows their photos side-by-side at matching ages. Click a photo to select it, then use "Enlarge" to view a fullscreen comparison. Hover over a thumbnail to preview it with name and date. Rows with many photos collapse to keep things manageable.

## Development

```bash
# Build and run
docker compose up --build

# Lint
ruff check app/          # Python
biome check app/static/  # JS/CSS
```

See [CLAUDE.md](CLAUDE.md) for architecture details.
