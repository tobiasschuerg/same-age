import json
import os
from collections import OrderedDict
from datetime import datetime

import requests
from flask import Flask, Response, jsonify, redirect, render_template, request, stream_with_context, url_for

from utils import diff_str, get_number_of_weeks

app = Flask(__name__)

CONFIG_PATH = os.environ.get("CONFIG_PATH", "/data/config.json")

config = {"immich_url": "", "api_key": ""}


def load_config():
    """Load config from JSON file, with env var overrides."""
    global config
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH) as f:
                config = json.load(f)
        except (json.JSONDecodeError, OSError):
            config = {"immich_url": "", "api_key": ""}
    env_url = os.environ.get("IMMICH_URL")
    env_key = os.environ.get("IMMICH_API_KEY")
    if env_url:
        config["immich_url"] = env_url
    if env_key:
        config["api_key"] = env_key


def save_config():
    """Save current config to JSON file."""
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)


def normalize_url(url):
    """Strip whitespace/trailing slashes, prepend http:// if no scheme."""
    url = (url or "").strip().rstrip("/")
    if url and not url.startswith(("http://", "https://")):
        url = "http://" + url
    return url


def is_configured():
    return bool(config.get("immich_url") and config.get("api_key"))


load_config()


@app.before_request
def require_setup():
    """Redirect to setup if not yet configured."""
    if not is_configured() and request.endpoint not in ("setup", "check_url", "check_key", "static"):
        return redirect(url_for("setup"))


def immich_request(method, path, **kwargs):
    """Make an authenticated request to the Immich API."""
    headers = kwargs.pop("headers", {})
    headers["x-api-key"] = config["api_key"]
    return requests.request(
        method, f"{config['immich_url']}/api{path}", headers=headers, **kwargs
    )


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


@app.route("/setup", methods=["GET", "POST"])
def setup():
    """Setup wizard for Immich connection."""
    if request.method == "GET":
        step = int(request.args.get("step", 1))
        return render_template(
            "setup.html",
            step=step,
            immich_url=config.get("immich_url", ""),
        )

    # POST — validate input
    step = int(request.form.get("step", 1))

    if step == 1:
        url = normalize_url(request.form.get("immich_url", ""))
        if not url:
            return redirect(url_for("setup"))
        config["immich_url"] = url
        return render_template("setup.html", step=2, immich_url=url)

    if step == 2:
        api_key = request.form.get("api_key", "").strip()
        url = normalize_url(request.form.get("immich_url", "")) or config.get("immich_url", "")
        if not api_key:
            return render_template("setup.html", step=2, immich_url=url)
        config["immich_url"] = url
        config["api_key"] = api_key
        save_config()
        return redirect(url_for("select_persons"))

    return redirect(url_for("setup"))


@app.route("/setup/check-url", methods=["POST"])
def check_url():
    """AJAX endpoint to verify Immich URL reachability."""
    url = normalize_url((request.json or {}).get("url", ""))
    if not url:
        return jsonify(ok=False, error="Please enter a URL.")
    try:
        resp = requests.get(f"{url}/api/server/ping", timeout=5)
        resp.raise_for_status()
        if resp.json().get("res") != "pong":
            raise ValueError("Unexpected response")
    except Exception:
        return jsonify(ok=False, error="Could not reach Immich at that URL.")
    return jsonify(ok=True, url=url)


@app.route("/setup/check-key", methods=["POST"])
def check_key():
    """AJAX endpoint to verify API key and check permissions."""
    data = request.json or {}
    url = normalize_url(data.get("url", "")) or config.get("immich_url", "")
    api_key = data.get("api_key", "").strip()
    if not api_key:
        return jsonify(ok=False, error="Please enter an API key.")

    headers = {"x-api-key": api_key}

    # Validate key
    try:
        resp = requests.get(f"{url}/api/users/me", headers=headers, timeout=5)
        if resp.status_code == 401:
            return jsonify(ok=False, error="Invalid API key.")
        resp.raise_for_status()
    except requests.exceptions.ConnectionError:
        return jsonify(ok=False, error="Could not connect to Immich.")
    except Exception:
        return jsonify(ok=False, error="Invalid API key or could not authenticate.")

    # Check required permissions
    checks = []

    def check_perm(name, method, path, **kwargs):
        try:
            r = requests.request(
                method, f"{url}/api{path}", headers=headers, timeout=5, **kwargs
            )
            checks.append({"name": name, "ok": r.status_code == 200})
        except Exception:
            checks.append({"name": name, "ok": False})

    check_perm("People", "GET", "/people")
    check_perm("Search", "POST", "/search/metadata", json={"type": "IMAGE", "size": 1})
    # Search returns asset data, so if it works, asset read access is confirmed
    search_ok = checks[-1]["ok"]
    checks.append({"name": "Assets", "ok": search_ok})

    all_ok = all(c["ok"] for c in checks)
    return jsonify(ok=True, checks=checks, all_ok=all_ok)


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

    groups = {}

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
