"""Extract stage: real, full 26-man World Cup squads from Wikipedia.

TheSportsDB's national-team profiles only have ~9-10 currently-tagged
players each - real, but not a full squad. Wikipedia's tournament squad-list
article has the complete real squad per team in a consistent wikitext
template ({{nat fs g player|...}}), one line per player. Section index is
resolved by team name at fetch time rather than hardcoded, since Wikipedia
page structure can change.
"""
import requests

from config import TEAMS
from transform.shared import DISPLAY_NAME

API_URL = "https://en.wikipedia.org/w/api.php"
SQUADS_PAGE = "2026_FIFA_World_Cup_squads"

# Wikimedia's API rejects requests with generic/default User-Agent strings
# (e.g. plain "python-requests/x.x") with a 403 - a descriptive UA identifying
# the project is required. See https://meta.wikimedia.org/wiki/User-Agent_policy
HEADERS = {"User-Agent": "squad-console-ingestion/1.0 (https://github.com/priyanshubiswas-tech/squad-console)"}


def resolve_section_index(team_code: str) -> str:
    resp = requests.get(API_URL, params={
        "action": "parse", "page": SQUADS_PAGE, "prop": "sections", "format": "json",
    }, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    sections = resp.json()["parse"]["sections"]
    target = DISPLAY_NAME[team_code].lower()
    for section in sections:
        if section["line"].strip().lower() == target:
            return section["index"]
    raise RuntimeError(f"Could not find a '{DISPLAY_NAME[team_code]}' section on {SQUADS_PAGE}")


def fetch_and_dump_team(client, team_code: str) -> None:
    from fetchers.thesportsdb import dump_raw  # reuse the same raw-dump writer

    section = resolve_section_index(team_code)
    url = f"{API_URL}?action=parse&page={SQUADS_PAGE}&prop=wikitext&section={section}&format=json"
    resp = requests.get(API_URL, params={
        "action": "parse", "page": SQUADS_PAGE, "prop": "wikitext", "section": section, "format": "json",
    }, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    wikitext = resp.json()["parse"]["wikitext"]["*"]
    dump_raw(client, team_code, "wikipedia_squad", url, wikitext)
    print(f"  fetched {team_code}/wikipedia_squad ({len(wikitext)} bytes, section {section})")


def fetch_all(client) -> None:
    print(f"Extract: Wikipedia squad lists, {len(TEAMS)} teams")
    for team_code in TEAMS:
        fetch_and_dump_team(client, team_code)
