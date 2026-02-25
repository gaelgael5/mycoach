"""Google Calendar integration for MyCoach."""
import os
import json
from pathlib import Path
from typing import Optional, List
from datetime import datetime, date, timedelta

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ── Config ───────────────────────────────────────────────────

SCOPES = ["https://www.googleapis.com/auth/calendar"]

TOKEN_PATH = Path(__file__).parent.parent.parent / "data" / "google_token.json"
CREDENTIALS_PATH = Path(__file__).parent.parent.parent / "data" / "google_credentials.json"

GOOGLE_CLIENT_ID     = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
REDIRECT_URI         = os.getenv("MYCOACH_URL", "http://localhost:8000") + "/auth/google-calendar/callback"


def _client_config() -> dict:
    """Build OAuth2 client config from env vars."""
    return {
        "web": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uris": [REDIRECT_URI],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }


# ── Token management ─────────────────────────────────────────

def load_credentials() -> Optional[Credentials]:
    """Load stored credentials from disk."""
    if not TOKEN_PATH.exists():
        return None
    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    # Refresh if expired
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            save_credentials(creds)
        except Exception:
            return None
    return creds if creds and creds.valid else None


def save_credentials(creds: Credentials):
    """Save credentials to disk."""
    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_PATH.write_text(creds.to_json())


def is_connected() -> bool:
    """Check if Google Calendar is connected and authorized."""
    return load_credentials() is not None


def revoke():
    """Disconnect Google Calendar."""
    if TOKEN_PATH.exists():
        TOKEN_PATH.unlink()


# ── OAuth2 flow ──────────────────────────────────────────────

def get_auth_url() -> str:
    """Generate the Google OAuth2 authorization URL."""
    flow = Flow.from_client_config(_client_config(), scopes=SCOPES)
    flow.redirect_uri = REDIRECT_URI
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )
    return auth_url


def handle_callback(code: str):
    """Exchange the authorization code for credentials."""
    flow = Flow.from_client_config(_client_config(), scopes=SCOPES)
    flow.redirect_uri = REDIRECT_URI
    flow.fetch_token(code=code)
    save_credentials(flow.credentials)


# ── Calendar API ─────────────────────────────────────────────

def _service():
    creds = load_credentials()
    if not creds:
        raise ValueError("Google Calendar not connected. Authorize first.")
    return build("calendar", "v3", credentials=creds)


def list_upcoming_events(days: int = 30, calendar_id: str = "primary") -> List[dict]:
    """Return upcoming events for the next N days."""
    now = datetime.utcnow().isoformat() + "Z"
    end = (datetime.utcnow() + timedelta(days=days)).isoformat() + "Z"

    result = _service().events().list(
        calendarId=calendar_id,
        timeMin=now,
        timeMax=end,
        maxResults=50,
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    events = []
    for e in result.get("items", []):
        start = e["start"].get("dateTime", e["start"].get("date", ""))
        end_t = e["end"].get("dateTime",   e["end"].get("date",   ""))
        events.append({
            "id":          e["id"],
            "title":       e.get("summary", "(sans titre)"),
            "start":       start,
            "end":         end_t,
            "description": e.get("description", ""),
            "color":       e.get("colorId", ""),
            "html_link":   e.get("htmlLink", ""),
        })
    return events


def create_event(
    title: str,
    start_dt: datetime,
    duration_minutes: int,
    description: str = "",
    calendar_id: str = "primary",
    color_id: str = "2"   # 2 = sage green
) -> dict:
    """Create a Google Calendar event and return the created event dict."""
    end_dt = start_dt + timedelta(minutes=duration_minutes)

    event = {
        "summary": title,
        "description": description,
        "start": {"dateTime": start_dt.isoformat(), "timeZone": "Europe/Paris"},
        "end":   {"dateTime": end_dt.isoformat(),   "timeZone": "Europe/Paris"},
        "colorId": color_id,
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "popup", "minutes": 60},
                {"method": "email", "minutes": 1440},  # 24h before
            ],
        },
    }

    created = _service().events().insert(calendarId=calendar_id, body=event).execute()
    return {
        "id":        created["id"],
        "html_link": created.get("htmlLink", ""),
        "title":     created.get("summary", ""),
        "start":     created["start"].get("dateTime", ""),
    }


def delete_event(event_id: str, calendar_id: str = "primary"):
    """Delete a Google Calendar event."""
    _service().events().delete(calendarId=calendar_id, eventId=event_id).execute()
