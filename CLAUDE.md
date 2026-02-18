# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Same-Age is a Django web app that compares photos of people, pets, or objects organized by age. Users import photos with EXIF metadata, and the app groups them side-by-side at matching age milestones.

## Development Commands

```bash
# Run development server (serves at http://127.0.0.1:8000)
python manage.py runserver

# Apply database migrations
python manage.py migrate

# Create new migrations after model changes
python manage.py makemigrations

# Trigger photo import (also accessible via browser at /autoimport)
# Place source photos in input/<person_name>/ folders first
```

**Dependencies:** Django 4.1.7, Pillow. No requirements.txt exists — dependencies are managed manually in a local venv (`venv/`).

## Architecture

**Single Django app (`timeline`)** within the `agecompare` project. SQLite database with two models:

- **Person** — name + birthday. Created automatically during import with a placeholder birthday (must be corrected via `/admin`).
- **TimelineImage** — photo record linked to a Person. Stores capture date (from EXIF), file path, and computes age in weeks/months dynamically from the Person's birthday.

**Request flow:**
- `GET /` → `views.show_images()` — renders gallery grouped by week-age, two columns for side-by-side comparison
- `GET /autoimport` → `views.autoimport()` → `prepprocessor.import_images()` — scans `input/` folders, extracts EXIF dates, rotates/resizes images to 800px, saves with UUID filenames to `timeline/static/photos/images/`, returns JSON stats

**Frontend:** Bootstrap 5.3 (CDN), vanilla JS. Lazy loading via Intersection Observer. Hover-to-enlarge with person name and capture date overlay.

**Key files:**
- `timeline/prepprocessor.py` — image import pipeline (EXIF extraction, rotation fix, resize, duplicate detection)
- `timeline/utils.py` — age calculation helpers (`get_number_of_weeks`, `diff_str`)
- `timeline/models.py` — Person and TimelineImage models
- `timeline/views.py` — two views (gallery display + autoimport trigger)

## Import Pipeline Details

Photos require EXIF `DateTimeOriginal` metadata. The preprocessor:
1. Creates a Person record per subfolder name in `input/`
2. Skips duplicates by checking filename + capture_date combinations
3. Applies EXIF orientation rotation before saving
4. Resizes to 800px width, preserving aspect ratio
5. Saves with UUID-based filenames to avoid collisions
