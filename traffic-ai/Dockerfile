FROM ubuntu:24.04

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV SUMO_HOME=/usr/share/sumo
ENV SUMO_GUI=0

# Install SUMO, Python 3, and essentials
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    sumo \
    sumo-tools \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create virtualenv and install python dependencies
COPY requirements.txt ./
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt && \
    /opt/venv/bin/pip install --no-cache-dir onnx onnxruntime

ENV PATH="/opt/venv/bin:$PATH"

# Copy simulation models, networks, and scripts
COPY . /app/

ENV BACKEND_URL="http://backend:3000/api/traffic"
ENV PENDING_AMB_URL="http://backend:3000/api/pending-ambulance"

CMD ["python3", "run_marl_corridor.py"]
