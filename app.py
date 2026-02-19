import os
from collections import OrderedDict, defaultdict
from datetime import datetime

import requests
from flask import Flask, Response, render_template, request, stream_with_context

from utils import diff_str, get_number_of_weeks

app = Flask(__name__)

IMMICH_URL = os.environ.get("IMMICH_URL", "http://192.168.178.19:2283")
IMMICH_API_KEY = os.environ.get("IMMICH_API_KEY", "")


def immich_request(method, path, **kwargs):
    """Make an authenticated request to the Immich API."""
    headers = kwargs.pop("headers", {})
    headers["x-api-key"] = IMMICH_API_KEY
    return requests.request(method, f"{IMMICH_URL}/api{path}", headers=headers, **kwargs)


def immich_get(path, **kwargs):
    """Make an authenticated GET request to the Immich API."""
    return immich_request("GET", path, **kwargs)


def immich_post(path, **kwargs):
    """Make an authenticated POST request to the Immich API."""
    return immich_request("POST", path, **kwargs)


class Group:
    def __init__(self, total_weeks, age_string, num_persons):
        self.total_weeks = total_weeks
        self.age_string = age_string
        self.columns = [[] for _ in range(num_persons)]


def fetch_people():
    """Fetch all people with a name and birthDate from Immich."""
    resp = immich_get("/people")
    resp.raise_for_status()
    all_people = resp.json().get("people", [])
    persons = [
        p for p in all_people
        if p.get("name") and p.get("birthDate")
    ]
    persons.sort(key=lambda p: p["name"])
    return persons


@app.route("/")
def select_persons():
    """Show person selection page."""
    persons = fetch_people()
    return render_template("select.html", persons=persons)


@app.route("/gallery")
def gallery():
    selected_ids = request.args.getlist("persons")
    if not selected_ids:
        return render_template("gallery.html", persons=[], data={})

    all_persons = fetch_people()
    persons = [p for p in all_persons if p["id"] in selected_ids]

    if not persons:
        return render_template("gallery.html", persons=[], data={})

    person_index = {p["id"]: i for i, p in enumerate(persons)}
    num_persons = len(persons)

    # Parse birthdays
    birthdays = {}
    for p in persons:
        birthdays[p["id"]] = datetime.fromisoformat(
            p["birthDate"].replace("Z", "+00:00")
        ).date()

    groups = defaultdict(lambda: None)

    for person in persons:
        pid = person["id"]
        birthday = birthdays[pid]

        # Fetch assets for this person via search endpoint
        page = 1
        assets = []
        while True:
            resp = immich_post("/search/metadata", json={
                "personIds": [pid],
                "type": "IMAGE",
                "withExif": True,
                "size": 1000,
                "page": page,
            })
            resp.raise_for_status()
            result = resp.json()
            items = result.get("assets", result).get("items", [])
            assets.extend(items)
            if len(items) < 1000:
                break
            page += 1

        for asset in assets:
            # Only include images, skip trashed/archived
            if asset.get("type") != "IMAGE":
                continue
            if asset.get("isTrashed") or asset.get("isArchived"):
                continue

            exif = asset.get("exifInfo") or {}
            date_str = exif.get("dateTimeOriginal") or asset.get("fileCreatedAt")
            if not date_str:
                continue

            capture_date = datetime.fromisoformat(
                date_str.replace("Z", "+00:00")
            ).date()

            weeks = get_number_of_weeks(birthday, capture_date)
            if weeks < 1:
                continue

            age_string = diff_str(birthday, capture_date)

            group = groups.get(weeks)
            if group is None:
                group = Group(
                    total_weeks=weeks,
                    age_string=age_string,
                    num_persons=num_persons,
                )
                groups[weeks] = group

            group.columns[person_index[pid]].append({
                "id": asset["id"],
                "person_name": person["name"],
                "capture_date": capture_date.strftime("%Y-%m-%d"),
            })

    # Sort by week ascending
    sorted_groups = OrderedDict(sorted(groups.items()))

    return render_template("gallery.html", persons=persons, data=sorted_groups)


@app.route("/person-thumbnail/<person_id>")
def person_thumbnail(person_id):
    """Proxy Immich person face thumbnail."""
    resp = immich_get(f"/people/{person_id}/thumbnail", stream=True)
    resp.raise_for_status()

    return Response(
        stream_with_context(resp.iter_content(chunk_size=8192)),
        content_type=resp.headers.get("Content-Type", "image/jpeg"),
        headers={"Cache-Control": "public, max-age=3600"},
    )


@app.route("/thumbnail/<asset_id>")
def thumbnail(asset_id):
    """Proxy Immich thumbnail with API key kept server-side."""
    resp = immich_get(
        f"/assets/{asset_id}/thumbnail",
        params={"size": "preview"},
        stream=True,
    )
    resp.raise_for_status()

    return Response(
        stream_with_context(resp.iter_content(chunk_size=8192)),
        content_type=resp.headers.get("Content-Type", "image/jpeg"),
        headers={"Cache-Control": "public, max-age=3600"},
    )


@app.route("/original/<asset_id>")
def original(asset_id):
    """Proxy full-resolution Immich asset."""
    resp = immich_get(f"/assets/{asset_id}/original", stream=True)
    resp.raise_for_status()

    return Response(
        stream_with_context(resp.iter_content(chunk_size=8192)),
        content_type=resp.headers.get("Content-Type", "image/jpeg"),
        headers={"Cache-Control": "public, max-age=3600"},
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
