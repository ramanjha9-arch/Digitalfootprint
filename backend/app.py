"""
Self-Footprint Checker — backend
Scope: single-input, self-lookup tool. You enter YOUR OWN phone/email/username
and get back what's publicly exposed, plus cleanup suggestions.

This is NOT a bulk lookup / identity-resolution service. Each request handles
one identifier at a time and returns exposure + remediation info only.
"""

import subprocess
import json
import shutil
import os
import requests
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder="static", static_url_path="")

PHONEINFOGA_BIN = shutil.which("phoneinfoga") or "/usr/local/bin/phoneinfoga"

# A handful of major platforms to check handle presence on.
# HEAD request only — we don't scrape profile content.
USERNAME_SITES = {
    "GitHub": "https://github.com/{u}",
    "Twitter/X": "https://x.com/{u}",
    "Instagram": "https://www.instagram.com/{u}/",
    "Reddit": "https://www.reddit.com/user/{u}/",
    "LinkedIn": "https://www.linkedin.com/in/{u}/",
    "Medium": "https://medium.com/@{u}",
    "TikTok": "https://www.tiktok.com/@{u}",
    "Facebook": "https://www.facebook.com/{u}",
}


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/phone-lookup", methods=["POST"])
def phone_lookup():
    """
    Runs PhoneInfoga against a single phone number the user submits about
    themselves — returns carrier/line-type/basic OSINT footprint so they can
    see what a stranger could learn from their number.
    """
    data = request.get_json(force=True)
    number = (data.get("number") or "").strip()
    if not number:
        return jsonify({"error": "Provide a phone number in E.164 format, e.g. +14155551234"}), 400

    try:
        result = subprocess.run(
            [PHONEINFOGA_BIN, "scan", "-n", number, "-o", "json"],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            return jsonify({"error": "Scan failed", "detail": result.stderr[:500]}), 500

        try:
            parsed = json.loads(result.stdout)
        except json.JSONDecodeError:
            parsed = {"raw_output": result.stdout}

        return jsonify({
            "number": number,
            "result": parsed,
            "suggestions": [
                "If the carrier/region shown surprises you, consider whether this number is tied to accounts you no longer use.",
                "Check whether this number is listed on data broker sites (see the report's opt-out links).",
                "Consider a secondary/virtual number for public-facing signups.",
            ]
        })
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Scan timed out"}), 504
    except FileNotFoundError:
        return jsonify({"error": "PhoneInfoga binary not found on server"}), 500


@app.route("/api/username-check", methods=["POST"])
def username_check():
    """
    Checks whether a single handle you provide is registered across a set of
    major platforms, so you can find and clean up old/forgotten accounts.
    """
    data = request.get_json(force=True)
    username = (data.get("username") or "").strip()
    if not username:
        return jsonify({"error": "Provide a username/handle"}), 400

    found = []
    for site, url_pattern in USERNAME_SITES.items():
        url = url_pattern.format(u=username)
        try:
            r = requests.head(url, timeout=5, allow_redirects=True,
                               headers={"User-Agent": "Mozilla/5.0"})
            exists = r.status_code < 400
        except requests.RequestException:
            exists = None  # couldn't determine
        found.append({"site": site, "url": url, "likely_exists": exists})

    return jsonify({"username": username, "results": found})


@app.route("/api/email-info", methods=["POST"])
def email_info():
    """
    No API key = no direct HIBP query. Instead, return the correct manual
    check links (HIBP web checker, Firefox Monitor) plus data-broker opt-out
    links, so the user can check themselves for free.
    """
    data = request.get_json(force=True)
    email = (data.get("email") or "").strip()
    if not email:
        return jsonify({"error": "Provide an email address"}), 400

    return jsonify({
        "email": email,
        "manual_checks": [
            {"name": "Have I Been Pwned (free web check)", "url": f"https://haveibeenpwned.com/account/{email}"},
            {"name": "Mozilla Monitor", "url": "https://monitor.mozilla.org/"},
        ],
        "cleanup_resources": [
            {"name": "Data broker opt-out guide (Yael Grauer's list)", "url": "https://github.com/yaelwrites/Big-Ass-Data-Broker-Opt-Out-List"},
            {"name": "DeleteMe (paid, automated opt-outs)", "url": "https://joindeleteme.com/"},
        ]
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
