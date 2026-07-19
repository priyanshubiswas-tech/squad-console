"""Airflow DAG for the squad-console ELT pipeline.

This is deploy_elt.py's own stages (see ingestion/elt-pipeline-py-script/
deploy_elt.py) split into independent tasks, exactly as that module's
docstring anticipated - every stage there only reads/writes ClickHouse, so
no stage needs Python objects handed to it in memory here either.

INGESTION_PATH is added to sys.path (instead of installing the pipeline as
a package) so this stays a thin wrapper - the DAG re-imports nothing that
deploy_elt.py doesn't already import itself.
"""
import sys
from datetime import datetime, timedelta

from airflow import DAG
from airflow.models.baseoperator import cross_downstream
from airflow.operators.python import PythonOperator

INGESTION_PATH = "/opt/airflow/ingestion"
if INGESTION_PATH not in sys.path:
    sys.path.insert(0, INGESTION_PATH)

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


def _extract_thesportsdb() -> None:
    from db import get_client
    from fetchers import thesportsdb
    thesportsdb.fetch_all(get_client())


def _extract_wikipedia() -> None:
    from db import get_client
    from fetchers import wikipedia
    wikipedia.fetch_all(get_client())


def _load_stage(transform_module: str, table: str, columns: list) -> None:
    from db import get_client
    from load import replace_table
    import importlib
    module = importlib.import_module(f"transform.{transform_module}")
    client = get_client()
    replace_table(client, table, module.transform_all(client), columns)


def _mock_stage(generator_module: str, table: str, columns: list) -> None:
    from db import get_client
    from load import replace_table
    import importlib
    module = importlib.import_module(f"mock_generators.{generator_module}")
    client = get_client()
    replace_table(client, table, module.generate(client), columns)


def _partition() -> None:
    from db import get_client
    from partition import partition_all
    partition_all(get_client())


default_args = {
    "owner": "squad-console",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="squad_console_elt",
    description="Extract (TheSportsDB + Wikipedia) -> transform -> mock-generate -> partition",
    default_args=default_args,
    schedule="@daily",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["squad-console"],
) as dag:
    extract_thesportsdb = PythonOperator(task_id="extract_thesportsdb", python_callable=_extract_thesportsdb)
    extract_wikipedia = PythonOperator(task_id="extract_wikipedia", python_callable=_extract_wikipedia)

    transform_players = PythonOperator(
        task_id="transform_players",
        python_callable=_load_stage, op_args=["players", "players", PLAYERS_COLUMNS],
    )
    transform_clubs = PythonOperator(
        task_id="transform_clubs",
        python_callable=_load_stage, op_args=["clubs", "clubs", CLUBS_COLUMNS],
    )
    transform_matches = PythonOperator(
        task_id="transform_matches",
        python_callable=_load_stage, op_args=["matches", "matches", MATCHES_COLUMNS],
    )
    transform_trophies = PythonOperator(
        task_id="transform_trophies",
        python_callable=_load_stage, op_args=["trophies", "trophies", TROPHIES_COLUMNS],
    )

    mock_public_stats = PythonOperator(
        task_id="mock_public_stats",
        python_callable=_mock_stage, op_args=["public_stats", "public_stats", PUBLIC_STATS_COLUMNS],
    )
    mock_injuries = PythonOperator(
        task_id="mock_injuries",
        python_callable=_mock_stage, op_args=["injuries", "injuries", INJURIES_COLUMNS],
    )
    mock_salaries = PythonOperator(
        task_id="mock_salaries",
        python_callable=_mock_stage, op_args=["salaries", "salaries", SALARIES_COLUMNS],
    )
    mock_training_load = PythonOperator(
        task_id="mock_training_load",
        python_callable=_mock_stage, op_args=["training_load", "training_load", TRAINING_LOAD_COLUMNS],
    )
    mock_formations = PythonOperator(
        task_id="mock_formations",
        python_callable=_mock_stage, op_args=["formations", "formations", FORMATIONS_COLUMNS],
    )

    partition = PythonOperator(task_id="partition", python_callable=_partition)

    extract = [extract_thesportsdb, extract_wikipedia]
    transform = [transform_players, transform_clubs, transform_matches, transform_trophies]
    mock = [mock_public_stats, mock_injuries, mock_salaries, mock_training_load, mock_formations]

    # Plain `list >> list` isn't overloaded by Python - cross_downstream is
    # Airflow's helper for "every item on the left before any item on the
    # right" (a single list -> single task edge, like `mock >> partition`,
    # works directly since the right side isn't a list).
    cross_downstream(extract, transform)
    cross_downstream(transform, mock)
    mock >> partition
