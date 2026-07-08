"""Single entrypoint for the whole ELT pipeline:

    Extract (TheSportsDB + Wikipedia)  ->  raw_data_store       [fetchers/]
    Transform (real)                   ->  squad_data_store      [transform/]
    Mock-generate (synthetic, keyed to real player_ids)          [mock_generators/]
    Partition                          ->  the 7 per-team databases [partition.py]

Run with: python deploy_elt.py  (or `docker compose run --rm ingestion`)

Every stage is a plain function that only reads/writes ClickHouse - no stage
hands the next one Python objects in memory. That's deliberate: it's what
lets each stage become an independent Airflow task later (fetch, transform,
mock-generate, partition, plus a scheduled re-fetch to keep data fresh
without needing a paid API key refreshed by hand) without restructuring
this code, just wrapping each function call below in an operator.
"""
from db import get_client
from fetchers import thesportsdb, wikipedia
from load import replace_table
from mock_generators import formations, injuries, public_stats, salaries, training_load
from partition import partition_all
from transform import clubs, matches, players, trophies

PLAYERS_COLUMNS = [
    "player_id", "name", "position", "club", "age",
    "overall_rating", "nationality", "photo_url", "team_code", "source",
]
CLUBS_COLUMNS = ["club_id", "name", "league", "team_code"]
MATCHES_COLUMNS = ["match_id", "opponent", "date", "result", "goals_for", "goals_against", "team_code"]
TROPHIES_COLUMNS = ["trophy_id", "name", "year", "team_code"]
PUBLIC_STATS_COLUMNS = [
    "player_id", "goals", "assists", "key_passes",
    "tackles", "rating_avg", "matches_played", "team_code",
]
INJURIES_COLUMNS = ["player_id", "injury_type", "status", "expected_return", "severity", "team_code"]
SALARIES_COLUMNS = ["player_id", "weekly_wage", "contract_until", "team_code"]
TRAINING_LOAD_COLUMNS = ["player_id", "week_no", "load_score", "fatigue_index", "team_code"]
FORMATIONS_COLUMNS = ["formation_id", "name", "players_json", "notes", "suitable_vs", "team_code"]


def main() -> None:
    client = get_client()

    print("\n=== EXTRACT: TheSportsDB + Wikipedia -> raw_data_store ===")
    thesportsdb.fetch_all(client)
    wikipedia.fetch_all(client)

    print("\n=== TRANSFORM: raw_data_store -> squad_data_store (real fields) ===")
    replace_table(client, "players", players.transform_all(client), PLAYERS_COLUMNS)
    replace_table(client, "clubs", clubs.transform_all(client), CLUBS_COLUMNS)
    replace_table(client, "matches", matches.transform_all(client), MATCHES_COLUMNS)
    replace_table(client, "trophies", trophies.transform_all(client), TROPHIES_COLUMNS)

    print("\n=== MOCK-GENERATE: synthetic fields with no free source, keyed to real player_ids ===")
    replace_table(client, "public_stats", public_stats.generate(client), PUBLIC_STATS_COLUMNS)
    replace_table(client, "injuries", injuries.generate(client), INJURIES_COLUMNS)
    replace_table(client, "salaries", salaries.generate(client), SALARIES_COLUMNS)
    replace_table(client, "training_load", training_load.generate(client), TRAINING_LOAD_COLUMNS)
    replace_table(client, "formations", formations.generate(client), FORMATIONS_COLUMNS)

    print("\n=== PARTITION: squad_data_store -> per-team databases ===")
    partition_all(client)

    print("\nDone.")


if __name__ == "__main__":
    main()
