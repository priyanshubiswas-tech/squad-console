"""The three chip reports: a fixed text template (never LLM-generated) whose
numbers come from a live ClickHouse query every time it's called, plus a
matplotlib/seaborn chart. Return shape - {"text": ..., "chart_filename": ...}
- is deliberately identical to what the future LangGraph composer will
return ({text, chart_url}), so the frontend chat window renders a chip
answer and an LLM answer through the exact same code path.

Tenant scoping: this app is one ClickHouse *database* per team, not a
tenant_id column, so the team can't be bound as a query parameter (SQL
parameter binding targets values, not table/database identifiers - not a
ClickHouse-specific limitation, this is true of parameterized queries in
general). `team_code` here is always a value that has already passed
`get_active_team`'s allow-list check against `settings.team_list`; every
query below trusts that and interpolates it directly as an identifier.
Never call these with a team_code that hasn't been through that check.

Where a query filters or limits by an actual *value* (not an identifier),
that value IS bound as a real ClickHouse query parameter - see the `LIMIT`
in top_performers_report for the contrast.
"""
from datetime import date, timedelta
from statistics import mean

from app.charts.generators import injury_risk_chart, top_performers_chart, wage_overview_chart


def fitness_report(client, team_code: str) -> dict:
    fatigue_rows = client.query(f"""
        SELECT p.name, t.week_no, t.fatigue_index
        FROM {team_code}.training_load t
        JOIN {team_code}.players p ON p.player_id = t.player_id
        ORDER BY t.week_no
    """).result_rows

    injury_rows = client.query(f"""
        SELECT p.name, i.injury_type, i.severity, i.expected_return
        FROM {team_code}.injuries i
        JOIN {team_code}.players p ON p.player_id = i.player_id
    """).result_rows

    by_player = {}
    for name, week_no, fatigue in fatigue_rows:
        by_player.setdefault(name, {})[week_no] = fatigue

    latest_week = max(w for series in by_player.values() for w in series)
    prev_week = latest_week - 1

    latest_avg = mean(series[latest_week] for series in by_player.values() if latest_week in series)
    prev_values = [series[prev_week] for series in by_player.values() if prev_week in series]
    prev_avg = mean(prev_values) if prev_values else latest_avg
    trend_pct = ((latest_avg - prev_avg) / prev_avg * 100) if prev_avg else 0.0

    top_name, top_series = max(by_player.items(), key=lambda item: item[1].get(latest_week, 0))
    top_fatigue = top_series[latest_week]

    injury_lines = "\n".join(
        f"- {name}: {injury_type} ({severity}), back {expected_return}"
        for name, injury_type, severity, expected_return in injury_rows
    ) or "None reported."

    direction = "up" if trend_pct >= 0 else "down"
    text = (
        f"🏥 Fitness & Injury Risk Report — {team_code.capitalize()}\n\n"
        f"{len(injury_rows)} player(s) currently sidelined.\n"
        f"Squad average fatigue index (week {latest_week}): {latest_avg:.2f} "
        f"({direction} {abs(trend_pct):.1f}% vs week {prev_week}).\n"
        f"Highest risk right now: {top_name} (fatigue {top_fatigue:.2f}).\n\n"
        f"Current injuries:\n{injury_lines}"
    )
    return {"text": text, "chart_filename": injury_risk_chart(team_code)}


def top_performers_report(client, team_code: str) -> dict:
    # `limit` is an actual value, not an identifier - bound as a real
    # ClickHouse query parameter, unlike team_code above.
    rows = client.query(f"""
        SELECT p.name, s.goals, s.assists, s.rating_avg, s.matches_played
        FROM {team_code}.public_stats s
        JOIN {team_code}.players p ON p.player_id = s.player_id
        ORDER BY s.rating_avg DESC
        LIMIT {{limit:UInt8}}
    """, parameters={"limit": 5}).result_rows

    avg_rating = client.query(f"SELECT avg(rating_avg) FROM {team_code}.public_stats").result_rows[0][0]
    top_name, top_goals, top_assists, top_rating, top_matches = rows[0]

    lines = "\n".join(
        f"{i}. {name} — {rating:.2f} avg ({goals}g, {assists}a, {matches} matches)"
        for i, (name, goals, assists, rating, matches) in enumerate(rows, start=1)
    )

    text = (
        f"⭐ Top Performers Report — {team_code.capitalize()}\n\n"
        f"Leading the squad: {top_name}, rated {top_rating:.2f} with {top_goals} goals "
        f"and {top_assists} assists across {top_matches} matches.\n"
        f"Squad average rating: {avg_rating:.2f}.\n\n"
        f"Top 5:\n{lines}"
    )
    return {"text": text, "chart_filename": top_performers_chart(team_code)}


def financial_report(client, team_code: str) -> dict:
    rows = client.query(f"""
        SELECT p.name, sal.weekly_wage, sal.contract_until
        FROM {team_code}.salaries sal
        JOIN {team_code}.players p ON p.player_id = sal.player_id
        ORDER BY sal.weekly_wage DESC
    """).result_rows

    total_wage = sum(row[1] for row in rows)
    top_name, top_wage, _ = rows[0]

    cutoff = date.today() + timedelta(days=365)
    expiring = [name for name, _, contract_until in rows if contract_until <= cutoff]
    expiring_line = f": {', '.join(expiring)}." if expiring else "."

    text = (
        f"💰 Financial Overview — {team_code.capitalize()}\n\n"
        f"Weekly wage bill: £{total_wage:,}.\n"
        f"Highest earner: {top_name} (£{top_wage:,}/week).\n"
        f"{len(expiring)} contract(s) expiring within 12 months{expiring_line}"
    )
    return {"text": text, "chart_filename": wage_overview_chart(team_code)}
