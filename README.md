# Self-Footprint Checker

A tool for checking what's publicly exposed about **your own** phone number, email, and usernames — not a lookup tool for other people. Each check takes one identifier at a time and returns exposure info + cleanup suggestions. Nothing is stored or cross-referenced.

## Single-platform deployment (Render)

Everything — frontend and backend — runs as one Flask app in one Docker container on Render. No Netlify, no separate frontend host, one URL.

### Deploy
1. Push this folder to a GitHub repo.
2. On [render.com](https://render.com) → New → Web Service → connect the repo.
3. Root directory: leave blank if this is the repo root, or set to wherever this folder lives. Render auto-detects the `Dockerfile`.
4. Instance type: **Free**.
5. Deploy. Render gives you one URL, e.g. `https://footprint-checker.onrender.com` — that serves both the UI and the API.

Note: Render's free tier spins down after ~15 min idle; the first request after that takes ~30–60s to wake up.

## Local testing
```bash
cd backend
pip install -r requirements.txt
python app.py   # serves UI + API on http://localhost:10000
```
(Needs the `phoneinfoga` CLI installed locally for the phone-lookup endpoint to work; the Docker image installs it automatically for you on Render.)

## What each check does
- **Phone**: runs PhoneInfoga's OSINT scan against the number (carrier, line type, associated public footprint) so you can see what a stranger could learn.
- **Email**: no HIBP API key required — links to HIBP's free web checker and Mozilla Monitor, plus data-broker opt-out resources.
- **Username**: checks handle presence across ~8 major platforms via HEAD request, so you can find and close old accounts.

## Scope, on purpose
This intentionally does **not**: chain phone → identity → relationship graphs, scrape social profile content, or accept batch/other-people's input. If you extend it, keep new checks in that same single-identifier, self-directed shape.
