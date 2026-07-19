"""Single entrypoint: chunk knowledge_base/ markdown -> embed into ChromaDB.

Run with: python embed_team_docs.py  (host-run, like ingestion/ - no
container, no image, edit knowledge_base/ and re-run any time)

Collections:
    {team}_full    <- knowledge_base/{team}/tactics_notes.md   (private)
    {team}_public  <- knowledge_base/{team}/public_scouting.md (public)
    shared_theory  <- knowledge_base/shared/tactical_theory.md (public, always retrieved)

Uses Chroma's default embedding function (a local sentence-transformers
model, downloaded once on first run) - no LLM API key needed, matching the
rest of this project's "as far as possible without an LLM key" build order.
Every run is a full delete-and-re-add per collection, so editing a
knowledge_base file and re-running never leaves stale chunks behind.
"""
import chromadb

from chunking import chunk_markdown
from config import CHROMA_HOST, CHROMA_PORT, KNOWLEDGE_BASE_DIR, TEAMS


def embed_file(client, collection_name: str, file_path, metadata_base: dict) -> None:
    if not file_path.exists():
        print(f"  {collection_name}: {file_path} does not exist, skipping")
        return

    chunks = chunk_markdown(file_path.read_text())
    if not chunks:
        print(f"  {collection_name}: no content in {file_path.name}, skipping")
        return

    collection = client.get_or_create_collection(collection_name)
    existing_ids = collection.get()["ids"]
    if existing_ids:
        collection.delete(ids=existing_ids)

    ids = [f"{collection_name}-{i}" for i in range(len(chunks))]
    metadatas = [dict(metadata_base, chunk_index=i) for i in range(len(chunks))]
    collection.add(ids=ids, documents=chunks, metadatas=metadatas)
    print(f"  {collection_name}: embedded {len(chunks)} chunks from {file_path.name}")


def main() -> None:
    # anonymized_telemetry=False just silences a harmless "Failed to send
    # telemetry event" warning from a client/server version quirk - purely
    # cosmetic, no effect on embedding itself.
    client = chromadb.HttpClient(
        host=CHROMA_HOST, port=CHROMA_PORT,
        settings=chromadb.config.Settings(anonymized_telemetry=False),
    )

    print("Embedding shared theory...")
    embed_file(
        client, "shared_theory",
        KNOWLEDGE_BASE_DIR / "shared" / "tactical_theory.md",
        {"team": "shared", "doc_type": "tactical_theory", "visibility": "public"},
    )

    for team in TEAMS:
        print(f"Embedding {team}...")
        embed_file(
            client, f"{team}_full",
            KNOWLEDGE_BASE_DIR / team / "tactics_notes.md",
            {"team": team, "doc_type": "tactics_notes", "visibility": "private"},
        )
        embed_file(
            client, f"{team}_public",
            KNOWLEDGE_BASE_DIR / team / "public_scouting.md",
            {"team": team, "doc_type": "public_scouting", "visibility": "public"},
        )

    print("\nDone.")


if __name__ == "__main__":
    main()
