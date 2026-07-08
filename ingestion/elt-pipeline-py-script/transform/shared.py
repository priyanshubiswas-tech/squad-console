"""Parsing helpers shared by more than one transform stage."""
import re
from datetime import date


def calc_age(year: int, month: int, day: int) -> int:
    born = date(year, month, day)
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def split_top_level(text: str, sep: str = "|") -> list:
    """Split on `sep` but only outside [[wikilinks]] / {{templates}} - a plain
    str.split("|") would incorrectly break on the pipe inside [[Club|Name]].
    """
    parts, depth, buf = [], 0, ""
    i = 0
    while i < len(text):
        two = text[i:i + 2]
        if two in ("[[", "{{"):
            depth += 1
            buf += two
            i += 2
            continue
        if two in ("]]", "}}"):
            depth -= 1
            buf += two
            i += 2
            continue
        if text[i] == sep and depth == 0:
            parts.append(buf)
            buf = ""
            i += 1
            continue
        buf += text[i]
        i += 1
    parts.append(buf)
    return parts


def wikilink_display(text: str) -> str:
    """[[Target|Display]] -> Display, [[Target]] -> Target, plain text -> itself."""
    match = re.match(r"\[\[([^\]]+)\]\]", text.strip())
    if not match:
        return text.strip()
    return match.group(1).split("|")[-1]


def real_squad_entries(entries: list) -> list:
    """Filter TheSportsDB's squad response down to actually-capped players.

    The endpoint also returns coaching staff attached to the national team
    entity itself. A real capped player has idTeam2 set to the (shared)
    national team id; staff entries don't have it set at all.
    """
    national_team_id = next((e["idTeam2"] for e in entries if e.get("idTeam2")), None)
    if national_team_id is None:
        return []
    return [e for e in entries if e.get("idTeam2") == national_team_id]
