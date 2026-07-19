"""Pure chart-rendering functions - matplotlib, rendered server-side to PNG.

Deliberately reachable two ways: directly via the REST router (chat-panel
"chips" call these with no LLM involved, zero tokens) and later from the
LangGraph agent's chart_node for free-form questions. Same function, two
entry points - that's the "hybrid" the whole chat design is built around.
"""
import os

import matplotlib

matplotlib.use("Agg")  # headless - no display server available in a container
import matplotlib.pyplot as plt
import seaborn as sns

from app.config import get_settings
from app.db.clickhouse_client import get_client

BG = "#0a0e14"
PANEL = "#171f30"
GRID = "#2a3344"
TEXT = "#e5e7eb"
TEXT_SECONDARY = "#9ca3af"
DANGER = "#ef4444"
PITCH = "#22c55e"
INDIGO = "#6366f1"
LINE_COLORS = [DANGER, "#f59e0b", INDIGO, PITCH, "#a855f7"]


def _save(fig, filename: str) -> str:
    settings = get_settings()
    os.makedirs(settings.chart_output_dir, exist_ok=True)
    path = os.path.join(settings.chart_output_dir, filename)
    fig.savefig(path, facecolor=BG, bbox_inches="tight", dpi=150)
    plt.close(fig)
    return filename


def _style_axes(ax, title: str, xlabel: str, ylabel: str) -> None:
    ax.set_facecolor(PANEL)
    ax.set_title(title, color=TEXT, fontsize=13)
    ax.set_xlabel(xlabel, color=TEXT_SECONDARY)
    ax.set_ylabel(ylabel, color=TEXT_SECONDARY)
    ax.tick_params(colors=TEXT_SECONDARY)
    ax.grid(color=GRID, linewidth=0.5)
    for spine in ax.spines.values():
        spine.set_color(GRID)


def injury_risk_chart(team_code: str) -> str:
    """Fatigue-index trend for the squad's 5 highest-risk players.

    training_load is private data (see access_control.py) - this is only
    ever generated for the active team, never an inspected opponent.
    Derived entirely from data already in ClickHouse; no new table needed.
    """
    client = get_client()
    result = client.query(f"""
        SELECT p.name, t.week_no, t.fatigue_index
        FROM {team_code}.training_load t
        JOIN {team_code}.players p ON p.player_id = t.player_id
        ORDER BY t.week_no
    """)

    by_player = {}
    for name, week_no, fatigue_index in result.result_rows:
        by_player.setdefault(name, {})[week_no] = fatigue_index

    if not by_player:
        raise ValueError(f"No training_load data for '{team_code}' - run the ELT pipeline first")

    latest_week = max(w for series in by_player.values() for w in series)
    top_players = sorted(
        by_player.items(), key=lambda item: item[1].get(latest_week, 0), reverse=True,
    )[:5]

    fig, ax = plt.subplots(figsize=(7, 4.5), facecolor=BG)
    for (name, series), color in zip(top_players, LINE_COLORS):
        weeks = sorted(series)
        ax.plot(weeks, [series[w] for w in weeks], marker="o", label=name, color=color, linewidth=2)

    _style_axes(ax, f"Injury risk trend - {team_code.capitalize()}", "Week", "Fatigue index")
    ax.legend(facecolor=PANEL, edgecolor=GRID, labelcolor=TEXT, fontsize=8)

    return _save(fig, f"{team_code}_injury_risk.png")


def top_performers_chart(team_code: str) -> str:
    """Bar chart of the squad's top 8 players by rating_avg - public_stats,
    so this one is fine to generate for any team, active or inspected."""
    client = get_client()
    result = client.query(f"""
        SELECT p.name, s.rating_avg
        FROM {team_code}.public_stats s
        JOIN {team_code}.players p ON p.player_id = s.player_id
        ORDER BY s.rating_avg DESC
        LIMIT 8
    """)
    rows = result.result_rows
    if not rows:
        raise ValueError(f"No public_stats data for '{team_code}' - run the ELT pipeline first")

    names = [row[0] for row in rows][::-1]
    ratings = [row[1] for row in rows][::-1]

    fig, ax = plt.subplots(figsize=(7, 4.5), facecolor=BG)
    ax.barh(names, ratings, color=PITCH)
    _style_axes(ax, f"Top performers - {team_code.capitalize()}", "Rating (avg)", "")
    ax.tick_params(axis="y", colors=TEXT)

    return _save(fig, f"{team_code}_top_performers.png")


def wage_overview_chart(team_code: str) -> str:
    """Horizontal bar chart of the squad's top 10 weekly wages - salaries is
    private data (see access_control.py), so like injury_risk_chart this is
    only ever generated for the active team. Uses seaborn (over plain
    matplotlib) purely for the built-in bar-plot styling; same _style_axes
    dark-theme pass applies on top either way."""
    client = get_client()
    result = client.query(f"""
        SELECT p.name, sal.weekly_wage
        FROM {team_code}.salaries sal
        JOIN {team_code}.players p ON p.player_id = sal.player_id
        ORDER BY sal.weekly_wage DESC
        LIMIT 10
    """)
    rows = result.result_rows
    if not rows:
        raise ValueError(f"No salaries data for '{team_code}' - run the ELT pipeline first")

    names = [row[0] for row in rows][::-1]
    wages = [row[1] for row in rows][::-1]

    fig, ax = plt.subplots(figsize=(7, 4.5), facecolor=BG)
    sns.barplot(x=wages, y=names, ax=ax, color=INDIGO)
    _style_axes(ax, f"Weekly wage bill (top 10) - {team_code.capitalize()}", "Weekly wage (£)", "")
    ax.tick_params(axis="y", colors=TEXT)

    return _save(fig, f"{team_code}_wage_overview.png")


def team_comparison_chart(team_code: str, opponent_code: str) -> str:
    """Grouped bar: average rating by position, own team vs opponent.

    Opponent side only ever reads public_stats - the same table
    access_control.py leaves fully public for inspect mode - so this is
    safe to generate for any named opponent, never their private data.
    """
    client = get_client()

    def _avg_by_position(team: str) -> dict:
        rows = client.query(f"""
            SELECT p.position, avg(s.rating_avg)
            FROM {team}.public_stats s JOIN {team}.players p ON p.player_id = s.player_id
            GROUP BY p.position
        """).result_rows
        return dict(rows)

    own = _avg_by_position(team_code)
    opponent = _avg_by_position(opponent_code)
    if not own or not opponent:
        raise ValueError(f"No public_stats data for '{team_code}' or '{opponent_code}' - run the ELT pipeline first")

    positions = sorted(set(own) | set(opponent))
    x = range(len(positions))
    width = 0.35

    fig, ax = plt.subplots(figsize=(7, 4.5), facecolor=BG)
    ax.bar([i - width / 2 for i in x], [own.get(p, 0) for p in positions], width,
           label=team_code.capitalize(), color=PITCH)
    ax.bar([i + width / 2 for i in x], [opponent.get(p, 0) for p in positions], width,
           label=opponent_code.capitalize(), color=INDIGO)
    ax.set_xticks(list(x))
    ax.set_xticklabels(positions, color=TEXT_SECONDARY)

    _style_axes(ax, f"{team_code.capitalize()} vs {opponent_code.capitalize()} - avg rating by position", "", "Rating (avg)")
    ax.legend(facecolor=PANEL, edgecolor=GRID, labelcolor=TEXT, fontsize=8)

    return _save(fig, f"{team_code}_vs_{opponent_code}_comparison.png")
