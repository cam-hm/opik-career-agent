#!/bin/bash
# ============================================
# Deploy LiveKit Agent Worker to GCE
# ============================================
# Uses startup script to run Docker + Cloud SQL Proxy

set -e

# Configuration
PROJECT_ID="gen-lang-client-0508840012"
REGION="asia-southeast1"
ZONE="asia-southeast1-b"
INSTANCE_NAME="opik-agent-worker"
MACHINE_TYPE="e2-standard-2"  # 2 vCPU, 8GB RAM
IMAGE_NAME="gcr.io/${PROJECT_ID}/opik-agent-backend:latest"
CLOUD_SQL_CONNECTION="gen-lang-client-0508840012:asia-southeast1:opik-db"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== Deploying LiveKit Agent Worker to GCE ===${NC}"
echo "Project: ${PROJECT_ID}"
echo "Zone: ${ZONE}"
echo "Instance: ${INSTANCE_NAME}"
echo ""

# Step 1: Build and push image
echo -e "${YELLOW}Step 1: Building and pushing Docker image...${NC}"
cd "$(dirname "$0")"
docker build -t ${IMAGE_NAME} .
docker push ${IMAGE_NAME}
echo -e "${GREEN}✅ Image pushed${NC}"

# Step 2: Delete existing instance
echo -e "${YELLOW}Step 2: Checking for existing instance...${NC}"
if gcloud compute instances describe ${INSTANCE_NAME} --zone=${ZONE} --project=${PROJECT_ID} &>/dev/null; then
    echo "Deleting existing instance..."
    gcloud compute instances delete ${INSTANCE_NAME} --zone=${ZONE} --project=${PROJECT_ID} --quiet
fi

# Step 3: Create startup script
echo -e "${YELLOW}Step 3: Creating startup script...${NC}"

STARTUP_SCRIPT=$(cat <<'STARTUP_EOF'
#!/bin/bash
set -e

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
fi

# Wait for Docker daemon
sleep 5

# Authenticate with GCR
gcloud auth configure-docker gcr.io --quiet

# Create /cloudsql directory if not exists
mkdir -p /cloudsql
chmod 777 /cloudsql

# Fetch secrets from Secret Manager
LIVEKIT_API_KEY=$(gcloud secrets versions access latest --secret="livekit-api-key")
LIVEKIT_API_SECRET=$(gcloud secrets versions access latest --secret="livekit-api-secret")
GOOGLE_API_KEY=$(gcloud secrets versions access latest --secret="google-api-key")
CARTESIA_API_KEY=$(gcloud secrets versions access latest --secret="cartesia-api-key")
OPIK_API_KEY=$(gcloud secrets versions access latest --secret="opik-api-key")

# ============================================
# CLOUD SQL PROXY (idempotent - handles reboot)
# ============================================
echo "Starting Cloud SQL Proxy..."
docker pull gcr.io/cloud-sql-connectors/cloud-sql-proxy:2.14.0

# Stop and remove existing container if exists
docker stop cloud-sql-proxy 2>/dev/null || true
docker rm cloud-sql-proxy 2>/dev/null || true

docker run -d --name cloud-sql-proxy \
    --restart=always \
    -v /cloudsql:/cloudsql \
    gcr.io/cloud-sql-connectors/cloud-sql-proxy:2.14.0 \
    --unix-socket /cloudsql \
    gen-lang-client-0508840012:asia-southeast1:opik-db

# Wait for proxy to be ready
sleep 5

# ============================================
# LIVEKIT AGENT WORKER (idempotent - handles reboot)
# ============================================
echo "Starting LiveKit Agent Worker..."
docker pull gcr.io/gen-lang-client-0508840012/opik-agent-backend:latest

# Stop and remove existing container if exists
docker stop opik-worker 2>/dev/null || true
docker rm opik-worker 2>/dev/null || true

docker run -d --name opik-worker \
    --restart=always \
    -v /cloudsql:/cloudsql \
    -e LIVEKIT_URL=wss://opik-agent-k5ebvg43.livekit.cloud \
    -e LIVEKIT_API_KEY="$LIVEKIT_API_KEY" \
    -e LIVEKIT_API_SECRET="$LIVEKIT_API_SECRET" \
    -e GOOGLE_API_KEY="$GOOGLE_API_KEY" \
    -e CARTESIA_API_KEY="$CARTESIA_API_KEY" \
    -e OPIK_API_KEY="$OPIK_API_KEY" \
    -e DATABASE_URL="postgresql+asyncpg://postgres:opik_password_123@/interviewer?host=/cloudsql/gen-lang-client-0508840012:asia-southeast1:opik-db" \
    -e GEMINI_MODEL=models/gemini-2.5-flash \
    -e SHADOW_MODEL=models/gemini-2.5-flash \
    -e OPIK_ENABLED=true \
    -e OPIK_WORKSPACE=opik-agent \
    -e "OPIK_PROJECT_NAME=Opik Career Agent" \
    -e PYTHONUNBUFFERED=1 \
    gcr.io/gen-lang-client-0508840012/opik-agent-backend:latest \
    bash worker_entrypoint.sh

echo "Worker started!"
STARTUP_EOF
)

# Step 4: Create GCE instance
echo -e "${YELLOW}Step 4: Creating GCE instance...${NC}"
gcloud compute instances create ${INSTANCE_NAME} \
    --project=${PROJECT_ID} \
    --zone=${ZONE} \
    --machine-type=${MACHINE_TYPE} \
    --network-interface=network-tier=PREMIUM,subnet=default \
    --maintenance-policy=MIGRATE \
    --provisioning-model=STANDARD \
    --scopes=https://www.googleapis.com/auth/cloud-platform \
    --tags=http-server,https-server \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=30GB \
    --boot-disk-type=pd-balanced \
    --labels=app=opik-agent,component=worker \
    --metadata=startup-script="${STARTUP_SCRIPT}"

echo -e "${GREEN}✅ Instance created${NC}"

# Step 5: Wait and show status
echo -e "${YELLOW}Waiting for instance to initialize (60s)...${NC}"
sleep 60

echo ""
echo -e "${GREEN}=== Deployment Complete ===${NC}"
echo ""
gcloud compute instances describe ${INSTANCE_NAME} --zone=${ZONE} --format="table(name,status,networkInterfaces[0].accessConfigs[0].natIP)"
echo ""
echo "Commands:"
echo "  View serial logs:  gcloud compute instances get-serial-port-output ${INSTANCE_NAME} --zone=${ZONE}"
echo "  SSH:               gcloud compute ssh ${INSTANCE_NAME} --zone=${ZONE}"
echo "  Docker logs:       gcloud compute ssh ${INSTANCE_NAME} --zone=${ZONE} --command='sudo docker logs opik-worker -f'"
echo "  Restart worker:    gcloud compute ssh ${INSTANCE_NAME} --zone=${ZONE} --command='sudo docker restart opik-worker'"
