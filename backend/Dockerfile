FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Chroma's Python client computes query embeddings *locally* (not
# server-side) using this same default model embedding_job uses server-side
# - pre-download it into the image now, at build time (normal internet
# access here), so the container never has to fetch it on first request
# (that previously caused an httpx.ReadTimeout on the first /api/chat call).
RUN python -c "from chromadb.utils import embedding_functions; embedding_functions.DefaultEmbeddingFunction()(['warmup'])"

COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
