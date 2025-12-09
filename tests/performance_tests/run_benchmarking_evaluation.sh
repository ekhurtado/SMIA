#!/bin/bash

# --- CONFIGURATION ---
SMIA_IMAGE_NAME="ekhurtado/smia-use-cases:latest-smia-performance-test"
FA3ST_IMAGE_NAME="fraunhoferiosb/faaast-service"
NOVAAS_IMAGE_NAME="benchmarking:novaas"
AAS_DIR="./aas"
AAS_ARCHIVE_DIR="/smia_archive/config/aas"
TESTS_PATH="./tests/benchmarking_test"
METRICS_FOLDER="metrics"
COMPOSE_FILE="docker-compose-generated.yml"

NOVAAS_PROJECT_DIR="./novaas_source_code/novaas-master"
NOVAAS_AAS_DIR=$NOVAAS_PROJECT_DIR/files/model
NOVAAS_HEALTH_URL="http://localhost:1872/dashboard/environment"
FA3ST_HEALTH_URL="https://localhost/api/v3.0/shells"

SMIA_CSV="smia_metrics.csv"
NOVAAS_CSV="novaas_metrics.csv"
FA3ST_CSV="fa3st_metrics.csv"

# Arrays with different AAS models
NUM_ITERATIONS=3   # 30
AAS_MODELS=("SMIA_test_16_sm.aasx" "SMIA_test_32_sm.aasx" "SMIA_test_64_sm.aasx") 
#AAS_MODELS=("SMIA_test_1_sm.aasx" "SMIA_test_2_sm.aasx" "SMIA_test_4_sm.aasx" "SMIA_test_8_sm.aasx" "SMIA_test_16_sm.aasx" "SMIA_test_32_sm.aasx" "SMIA_test_64_sm.aasx") 


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

    docker rm --force benchmarking-smia
    docker rm --force benchmarking-fa3st
    docker rm --force benchmarking-novaas

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
cat <<EOF > $COMPOSE_FILE
services:
  

EOF
}

# Function to add a SMIA instance to the YAML
add_smia_to_docker_compose() {
    local id=$1
    local aasx_file_name=$2

cat <<EOF >> $COMPOSE_FILE
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
  # SMIA instance
  # --------------
  benchmarking-smia-$id:
    image: $SMIA_IMAGE_NAME
    container_name: benchmarking-smia-$id
    environment:
      - AAS_MODEL_NAME=$aasx_file_name
      - AGENT_ID=benchmarking-smia-$id@ejabberd
      - AGENT_PSSWD=gcis1234
      - METRICS_FOLDER=$AAS_ARCHIVE_DIR/$METRICS_FOLDER
    depends_on:
      xmpp-server:
        condition: service_healthy
    volumes:
      - $AAS_DIR:$AAS_ARCHIVE_DIR

EOF
}

add_fa3st_to_docker_compose() {
    local aas_model=$1

cat <<EOF >> $COMPOSE_FILE
  # ---------------
  # FA3ST instance
  # ---------------
  benchmarking-fa3st:
    image: $FA3ST_IMAGE_NAME
    container_name: benchmarking-fa3st
    volumes:
      - $AAS_DIR:/app/resources/
    environment:
      - faaast_model=/app/resources/$aas_model
      - faaast_config=/app/resources/fa3st_config.json
    ports:
      - 443:443

EOF
}

add_novaas_to_docker_compose() {
    local aas_model=$1

cat <<EOF >> $COMPOSE_FILE
  # ---------------
  # NOVAAS instance
  # ---------------
  benchmarking-novaas:
    build: 
        context: $NOVAAS_PROJECT_DIR
        args: 
            - "AAS_VERSION=V3"
            - "AAS_MODEL=$aas_model"
    container_name: benchmarking-novaas
    image: $NOVAAS_IMAGE_NAME
    environment:
        - "PORT_FORWARDING=1872" 
        - "HOST=localhost"
        - "BROKER_SERVICE_HOST=localhost"
        - "BROKER_SERVICE_PORT=1883"
        - "REPO_LOCATION=https://gitlab.com/novaas/catalog/nova-school-of-science-and-technology/novaas"
    ports:
        - "1872:1880"

EOF
}



# --- MAIN LOOP ---

mkdir -p $AAS_DIR/$METRICS_FOLDER
echo "Generated metrics folder: $AAS_DIR/$METRICS_FOLDER"

mkdir -p $TESTS_PATH
echo "Generated metrics persistence folder: $TESTS_PATH"

for (( iter=1; iter<=NUM_ITERATIONS; iter++ )); do
    # The test is performed NUM_ITERATIONS times
    echo "########################################"
    echo "Performing benchmarking test number $iter"
    echo "########################################"


    for AAS in "${AAS_MODELS[@]}"; do
        echo "=== Preparing scenario with FA3ST, NOVAAS and SMIA instances associating model $AAS ==="

        AAS_MODEL_NAME="${AAS%.*}"
        mkdir -p $TESTS_PATH/test_${AAS_MODEL_NAME}
        
        # 1. Clean previous environment
        rm -f $AAS_DIR/$METRICS_FOLDER/*
        
        # 2. Dynamically generate docker-compose.yml
        echo "Generating $COMPOSE_FILE..."
        generate_header
        
        # NOVAAS need to build the image
        add_novaas_to_docker_compose "$AAS"
        echo "Construyendo imagen NOVAAS..."
        cp -fr $AAS_DIR/$AAS $NOVAAS_AAS_DIR/model.aasx
        docker-compose -f $COMPOSE_FILE build

        # Add the remaining instances
        add_smia_to_docker_compose "$iter" "$AAS" 
        add_fa3st_to_docker_compose "$AAS"

        START_TS=$(date +%s.%4N)

        # 3. Launch infrastructure
        echo "Launching containers..."
        # --remove-orphans is key here because the number of containers changes
        docker-compose -f $COMPOSE_FILE up -d --remove-orphans

        # 4. Wait for completion (Sentinel File Logic)
        echo "Waiting for all instances to be ready..."
        FLAG_SMIA_DONE=false
        FLAG_NOVAAS_DONE=false
        FLAG_FA3ST_DONE=false
        while true; do
            if [ "$FLAG_SMIA_DONE" = false ]; then
                FINISHED_COUNT=$(ls $AAS_DIR/$METRICS_FOLDER/ready-* 2>/dev/null | wc -l)
                if [ "$FINISHED_COUNT" -ge "1" ]; then
                    echo ">>> SMIA finished!"
                    FLAG_SMIA_DONE=true
                fi
            fi

            if [ "$FLAG_NOVAAS_DONE" = false ]; then
                NOVAAS_HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$NOVAAS_HEALTH_URL")
                if [ "$NOVAAS_HTTP_CODE" == "200" ]; then
                    NOVAAS_READY_TS=$(date +%s.%4N)
                    echo ">>> NOVAAS finished!"
                    FLAG_NOVAAS_DONE=true
                fi
            fi

            if [ "$FLAG_FA3ST_DONE" = false ]; then
                FA3ST_HTTP_CODE=$(curl -k -s -o /dev/null -w "%{http_code}" "$FA3ST_HEALTH_URL")
                if [ "$FA3ST_HTTP_CODE" == "200" ]; then
                    echo ">>> FA3ST finished!"
                    FA3ST_READY_TS=$(date +%s.%4N)
                    FLAG_FA3ST_DONE=true
                fi
            fi

            if [ "$FLAG_SMIA_DONE" = true ] && [ "$FLAG_NOVAAS_DONE" = true ] && [ "$FLAG_FA3ST_DONE" = true ]; then
                break
            fi

            sleep 0.1
        done

        # 5. Shut everything down
        echo "Stopping scenario..."
        docker-compose -f $COMPOSE_FILE down
        rm -f $AAS_DIR/$METRICS_FOLDER/ready-*
        echo "Scenario $AAS completed."
        echo ""
        sleep 3

        # 6. Copy obtained metrics to persistence folder and remove temporary folder
        if [ -f "$TESTS_PATH/test_${AAS_MODEL_NAME}/$SMIA_CSV" ]; then
            # CASE A: File ALREADY EXISTS -> Append
            # Use 'tail -n +2' to print from line 2 to the end
            # (skipping the header) and append it (>>) to the destination.
            tail -n +2 "$AAS_DIR/$METRICS_FOLDER/benchmarking-smia-$iter-metrics.csv" >> "$TESTS_PATH/test_${AAS_MODEL_NAME}/$SMIA_CSV"
        else
            # CASE B: File DOES NOT EXIST -> Copy normally
            cp "$AAS_DIR/$METRICS_FOLDER/benchmarking-smia-$iter-metrics.csv" "$TESTS_PATH/test_${AAS_MODEL_NAME}/$SMIA_CSV"
        fi

        if [ ! -f "$TESTS_PATH/test_${AAS_MODEL_NAME}/$NOVAAS_CSV" ]; then
            # CASE File DOES NOT EXIST
            echo "Instance,Timestamp,Description" > "$TESTS_PATH/test_${AAS_MODEL_NAME}/$NOVAAS_CSV"
        fi
        echo "novaas-$iter,$START_TS,NOVAAS started" >> "$TESTS_PATH/test_${AAS_MODEL_NAME}/$NOVAAS_CSV"
        echo "novaas-$iter,$NOVAAS_READY_TS,NOVAAS ready" >>  "$TESTS_PATH/test_${AAS_MODEL_NAME}/$NOVAAS_CSV"

        if [ ! -f "$TESTS_PATH/test_${AAS_MODEL_NAME}/$FA3ST_CSV" ]; then
            # CASE File DOES NOT EXIST
            echo "Instance,Timestamp,Description" > "$TESTS_PATH/test_${AAS_MODEL_NAME}/$FA3ST_CSV"
        fi
        echo "fa3st-$iter,$START_TS,FA3ST started" >> "$TESTS_PATH/test_${AAS_MODEL_NAME}/$FA3ST_CSV"
        echo "fa3st-$iter,$FA3ST_READY_TS,FA3ST ready" >>  "$TESTS_PATH/test_${AAS_MODEL_NAME}/$FA3ST_CSV"

        echo "Metrics files copied to persistence folder $TESTS_PATH/test_${AAS_MODEL_NAME}"
        
    done
done