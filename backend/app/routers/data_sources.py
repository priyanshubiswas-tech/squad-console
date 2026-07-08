"""Product transparency: which tables/fields are real (and where from) vs
synthetic (and why). Surfaced in the UI as a legend/tooltip rather than
buried in docs - see the root README and ingestion/README.md for the
same breakdown in prose form.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/data-sources", tags=["data-sources"])

DATA_SOURCES = {
    "players": {
        "status": "mixed",
        "description": (
            "Real squad list (name, position, club, age, nationality) from Wikipedia's "
            "2026 FIFA World Cup squads article, cross-referenced with TheSportsDB for "
            "real photos where available. overall_rating is synthetic - no free or paid "
            "source publishes a FIFA-style rating for real players."
        ),
        "real_source": "Wikipedia (2026 FIFA World Cup squads), TheSportsDB (free tier)",
        "synthetic_fields": ["overall_rating"],
    },
    "clubs": {
        "status": "real",
        "description": "Derived from each player's real current club.",
        "real_source": "Wikipedia squad lists",
        "synthetic_fields": [],
    },
    "matches": {
        "status": "real",
        "description": "Real recent match results, including live tournament fixtures.",
        "real_source": "TheSportsDB (free tier)",
        "synthetic_fields": [],
    },
    "trophies": {
        "status": "real",
        "description": (
            "Hand-curated list of major real honours (World Cup / continental titles) - "
            "not fetched live, since no free API returns this for national teams."
        ),
        "real_source": "Hand-curated, checked against public football records",
        "synthetic_fields": [],
    },
    "public_stats": {
        "status": "synthetic",
        "description": (
            "Goals, assists, tackles etc. would need a paid API-Football key, which this "
            "project doesn't have yet. Deterministic - seeded by the real player id, so "
            "values are stable across pipeline re-runs rather than random noise."
        ),
        "real_source": None,
        "synthetic_fields": ["goals", "assists", "key_passes", "tackles", "rating_avg", "matches_played"],
    },
    "injuries": {
        "status": "synthetic",
        "description": "No free or paid source publishes real injury detail for these squads. Private to the owning team.",
        "real_source": None,
        "synthetic_fields": ["injury_type", "status", "expected_return", "severity"],
    },
    "salaries": {
        "status": "synthetic",
        "description": "Real wages aren't published anywhere free. Private to the owning team.",
        "real_source": None,
        "synthetic_fields": ["weekly_wage", "contract_until"],
    },
    "training_load": {
        "status": "synthetic",
        "description": "No free source for internal fitness/training data. Private to the owning team.",
        "real_source": None,
        "synthetic_fields": ["load_score", "fatigue_index"],
    },
    "formations": {
        "status": "mixed",
        "description": (
            "Tactical shapes are our own authoring, but lineups are built from real "
            "players grouped by real position and ranked by the synthetic overall_rating. "
            "name + suitable_vs are public; the full lineup + notes are private to the "
            "owning team."
        ),
        "real_source": "Player grouping based on Wikipedia squad data",
        "synthetic_fields": ["players_json", "notes", "suitable_vs"],
    },
}


@router.get("")
def get_data_sources() -> dict:
    return DATA_SOURCES
