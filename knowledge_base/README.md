# knowledge_base

The RAG corpus. One folder per team, each with two files grounded in the real squad data in ClickHouse (see `../ingestion/README.md`):

- `tactics_notes.md` — **private**, internal staff dossier: manager philosophy, concrete formation options naming real players by role, key-player dependencies, pressing/defensive shape, set-piece notes, squad depth by position, individual player tactical traits, and at least one honest exploitable weakness.
- `public_scouting.md` — **public**, what any rival's analyst could compile: general reputation/style, star names and why they're dangerous, historical trophy pedigree, formation *name* only, pundit-level strengths/weaknesses, current World Cup 2026 form, and rivalries/storylines.

Plus `shared/tactical_theory.md` — a team-agnostic glossary of formation/pressing/buildup concepts (high press, false nine, double pivot, etc.) that every team file assumes familiarity with rather than re-explaining.

Every file is real football content — real managers, real current squads, real trophy history, real recent results — written by researching each team specifically rather than templated. Individual claims are kept qualitative (no fabricated precise stats) since the actual numeric data already lives in ClickHouse.

## Editing and re-embedding

This folder is read directly off the host filesystem by `../embedding_job/` (also host-run, not containerized) — edit any file and re-run `python embed_team_docs.py` to pick up the change. No image, no rebuild, no container restart.

## Privacy mapping

`tactics_notes.md` → embedded with `visibility: private` metadata → only ever retrieved when the team is the *active* team. `public_scouting.md` → `visibility: public` → retrieved when the team is either active or an *opponent*. This mirrors the ClickHouse access-control matrix (`backend/app/access_control.py`) but for documents instead of rows — see `../architecture/ARCHITECTURE.md` § Access control.
