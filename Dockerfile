FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    SYNTUTOR_HOST=0.0.0.0

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Bake the models into the image so cold starts don't download them at runtime.
RUN python -m spacy download en_core_web_md \
    && python -c "import benepar; benepar.download('benepar_en3')"

COPY server/ ./server/
COPY index.html login.html ./
COPY css/ ./css/
COPY js/ ./js/

EXPOSE 8000

CMD ["python", "server/app.py"]
