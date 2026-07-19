FROM apache/airflow:2.10.4-python3.11

# Built with repo root as context so this can reach the ingestion
# pipeline's own requirements file directly - one dependency list, not two.
COPY --chown=airflow:root ingestion/elt-pipeline-py-script/requirements.txt /tmp/ingestion-requirements.txt
RUN pip install --no-cache-dir -r /tmp/ingestion-requirements.txt
