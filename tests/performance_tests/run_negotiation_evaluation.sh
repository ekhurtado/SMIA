#!/bin/bash

# --- CONFIGURATION ---
IMAGE_NAME="ekhurtado/smia-use-cases:latest-smia-performance-test"
AAS_DIR="./aas"
AAS_ARCHIVE_DIR="/smia_archive/config/aas"
TESTS_PATH="./tests/negotiation_test"
METRICS_FOLDER="metrics"
COMPOSE_FILE="docker-compose-generated.yml"
AASX_REQUESTER_FILE="SMIA_demo_1.aasx"
AASX_RECEIVER_FILE="SMIA_TransportRobot_1.aasx"

# Arrays with test scenarios (e.g., 3 instances, then 5)
NUM_NEGOTIATIONS=3   # 30
SCENARIOS=(1 2 4 8) 
#SCENARIOS=(1 2 4 8 16 32 64) 


cleanup_on_interrupt() {
    echo ""
    echo "==================================================="
    echo ">>> Ctrl+C detected! Canceling execution..."
    echo "==================================================="

    # 1. Stop containers if the compose file exists
    if [ -f "$COMPOSE_FILE" ]; then
        echo "Stopping active containers..."
        docker-compose -f $COMPOSE_FILE down
    fi

    for N in "${SCENARIOS[@]}"; do
        for (( i=1; i<=N; i++ )); do
          docker rm --force smia-$i
        done
    done

    # 2. Cleanup of 'ready' temporary files so they don't affect the next run
    echo "Cleaning up temporary files..."
    rm -rf "$AAS_DIR/$METRICS_FOLDER"
    
    echo ">>> Environment clean. Exiting."
    exit 130 # Standard exit code for script interruptions (128 + 2)
}

# Activate 'trap':
# When the script receives SIGINT (Ctrl+C) or SIGTERM, it will execute 'cleanup_on_interrupt'
trap cleanup_on_interrupt SIGINT SIGTERM

# --- FUNCTIONS ---

# Function to generate the YAML header (The XMPP server)
generate_header() {
    local target_ids_string=$1

cat <<EOF > $COMPOSE_FILE
services:
  # ----------------------------
  # SMIA Infrastructure services
  # ----------------------------
  xmpp-server:
    image: ghcr.io/processone/ejabberd
    container_name: ejabberd
    environment:
      - ERLANG_NODE_ARG=admin@ejabberd
      - ERLANG_COOKIE=dummycookie123
      - CTL_ON_CREATE=! register admin localhost asd
    ports:
      - "5222:5222"
      - "5269:5269"
      - "5280:5280"
      - "5443:5443"
    volumes:
      - ./xmpp_server/ejabberd.yml:/opt/ejabberd/conf/ejabberd.yml
    healthcheck:
      test: netstat -nl | grep -q 5222
      start_period: 5s
      interval: 5s
      timeout: 5s
      retries: 10

  # --------------
  # SMIA instances
  # --------------
  smia-negotiation-requester:
    image: ekhurtado/smia-use-cases:latest-negotiation-requester
    container_name: smia-negotiation-requester
    environment:
      - AAS_MODEL_NAME=$AASX_REQUESTER_FILE
      - AGENT_ID=smia-negotiation-requester@ejabberd
      - AGENT_PSSWD=gcis1234
      - METRICS_FOLDER=$AAS_ARCHIVE_DIR/$METRICS_FOLDER
      - NUM_NEGOTIATIONS=$NUM_NEGOTIATIONS
      - TARGET_IDS=$target_ids_string
    depends_on:
      xmpp-server:
        condition: service_healthy
    volumes:
      - $AAS_DIR:$AAS_ARCHIVE_DIR


EOF
}

# Function to add a SMIA instance to the YAML
add_client_to_yaml() {
    local id=$1
cat <<EOF >> $COMPOSE_FILE
  smia-$id:
    image: ekhurtado/smia-use-cases:latest-smia-performance-test
    container_name: smia-$id
    environment:
      - AAS_MODEL_NAME=$AASX_RECEIVER_FILE
      - AGENT_ID=smia-$id@ejabberd
      - AGENT_PSSWD=gcis1234
      - METRICS_FOLDER=$AAS_ARCHIVE_DIR/$METRICS_FOLDER
    depends_on:
      xmpp-server:
        condition: service_healthy
    volumes:
      - $AAS_DIR:$AAS_ARCHIVE_DIR

EOF
}

# --- MAIN LOOP ---

mkdir -p $AAS_DIR/$METRICS_FOLDER
echo "Generated metrics folder: $AAS_DIR/$METRICS_FOLDER"

mkdir -p $TESTS_PATH
echo "Generated metrics persistence folder: $TESTS_PATH"

for N in "${SCENARIOS[@]}"; do
    echo "=== Preparing scenario with $N SMIA instances ==="

    mkdir -p $TESTS_PATH/test_${N}_instances
    
    # 1. Clean previous environment and add dynamic environmental
    rm -f $AAS_DIR/$METRICS_FOLDER/*

    TARGET_IDS=""
    for (( i=1; i<=N; i++ )); do
        TARGET_IDS+="smia-$i@ejabberd,"
    done
    
    # 2. Dynamically generate docker-compose.yml
    echo "Generating $COMPOSE_FILE..."
    generate_header "$TARGET_IDS"
    
    for (( i=1; i<=N; i++ )); do
        add_client_to_yaml "$i"
    done

    # 3. Launch infrastructure
    echo "Launching containers..."
    # --remove-orphans is key here because the number of containers changes
    docker-compose -f $COMPOSE_FILE up -d --remove-orphans

    # 4. Wait for completion (Sentinel File Logic)
    echo "Waiting for $NUM_NEGOTIATIONS negotiations to be completed by $N SMIA instances..."
    while true; do
        FINISHED_COUNT=$(ls $AAS_DIR/$METRICS_FOLDER/ready-* 2>/dev/null | wc -l)
        if [ -f "$AAS_DIR/$METRICS_FOLDER/ready-smia-negotiation-requester-metrics.csv" ]; then
            echo ">>> Global Controller reported completion! Stopping scenario..."
            break
        fi
        sleep 2
    done

    # 5. Shut everything down
    echo "Stopping scenario..."
    docker-compose -f $COMPOSE_FILE down
    rm -f $AAS_DIR/$METRICS_FOLDER/ready-*
    echo "Scenario $N completed."
    echo ""
    sleep 3

    # 6. Copy obtained metrics to persistence folder and remove temporary folder
    #cp -r "$AAS_DIR/$METRICS_FOLDER"/* "$TESTS_PATH/test_${N}_instances/"
    full_metrics_file="$TESTS_PATH/test_${N}_instances/full_metrics.csv"
    for source_file in "$AAS_DIR/$METRICS_FOLDER"/*.csv; do
        # Verify file exists (in case glob * fails)
        [ -e "$source_file" ] || continue

        # Extract only the name (e.g., app-1-metrics.csv)
        filename=$(basename "$source_file")
        dest_file="$TESTS_PATH/test_${N}_instances/$filename"

        if [ -f "$dest_file" ]; then
            # CASE A: File ALREADY EXISTS -> Append
            # Use 'tail -n +2' to print from line 2 to the end
            # (skipping the header) and append it (>>) to the destination.
            tail -n +2 "$source_file" >> "$dest_file"
        else
            # CASE B: File DOES NOT EXIST -> Copy normally
            cp "$source_file" "$dest_file"
        fi

        # --- FULL FILE ---
        if [ ! -f "$full_metrics_file" ]; then
            head -n 1 "$source_file" > "$full_metrics_file"
        fi
        # Append content of current to global (always WITHOUT header)
        tail -n +2 "$source_file" >> "$full_metrics_file"

    done
    echo "Metrics files copied to persistence folder $TESTS_PATH/test_${N}_instances"
done