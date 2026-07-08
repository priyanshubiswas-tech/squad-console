"""Load stage: structured rows -> squad_data_store (master), truncate-and-reload."""
from config import CLICKHOUSE_MASTER_DB


def replace_table(client, table: str, rows: list, column_order: list) -> None:
    full_table = f"{CLICKHOUSE_MASTER_DB}.{table}"
    client.command(f"TRUNCATE TABLE {full_table}")
    if not rows:
        print(f"  {full_table}: 0 rows (nothing to load)")
        return
    data = [[row[col] for col in column_order] for row in rows]
    client.insert(full_table, data, column_names=column_order)
    print(f"  {full_table}: loaded {len(rows)} rows")
