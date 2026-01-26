FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (needed for some python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libglib2.0-0 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ============================================
# PRE-DOWNLOAD ML MODELS (Critical for fast startup)
# ============================================
# Pre-download Silero VAD model to avoid runtime download timeout
RUN python -c "from livekit.plugins import silero; silero.VAD.load()"

COPY . .

RUN chmod +x entrypoint.sh worker_entrypoint.sh

CMD ["./entrypoint.sh"]
