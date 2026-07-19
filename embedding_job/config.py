import os
from pathlib import Path

from dotenv import load_dotenv

# Host-run, like ingestion/elt-pipeline-py-script - so knowledge_base/ can be
# edited and re-embedded with no image/container in the loop. Connects to
# Chroma's published host port, never the in-network hostname "chroma" that
# the backend container will eventually use.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

CHROMA_HOST = "localhost"
CHROMA_PORT = int(os.environ.get("CHROMA_HOST_PORT", "8001"))

TEAMS = [t.strip() for t in os.environ.get(
    "TEAMS", "england,france,brazil,argentina,spain,germany,portugal"
).split(",") if t.strip()]

KNOWLEDGE_BASE_DIR = Path(__file__).resolve().parent.parent / "knowledge_base"
