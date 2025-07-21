CeDRI IPB demonstrator
======================

.. _CeDRI IPB demonstrator:

This use case represents a flexible production scenario, in which some different asset will interact to realize production plans. This page will detail the use case in relation to its development and implementation and the results obtained.

.. note::

    All the resources developed in the case study are available in the `SMIA repository on GitHub <https://github.com/ekhurtado/SMIA/tree/cedri_ipb_demonstrator/use_cases/cedri_ipb_demonstrator>`_. The use case was validated with SMIA version 0.3.0.


Description of the use case
---------------------------

TODO


Development of the use case
---------------------------

TODO

Deployment of the use case
--------------------------

For this use case it has been decided to deploy SMIA using the Docker Compose method, as it offers the possibility of a self-contained deployment. This way, everything necessary is added in the ``docker-compose-yml`` file and the complete use case can be deployed with a simple command, as Docker Compose takes care of starting the containers and enabling communication between them. All the necessary infrastructure has also been added, as well as the dependency between them using the ``depends_on`` attributes.

.. dropdown:: ``docker-compose.yml`` file of the use case
    :octicon:`file-code;1em;sd-text-primary`

    .. code:: yaml

        services:

          # ----------------------------------------
          # AAS Infrastructure services (from BaSyx)
          # ----------------------------------------
          aas-env:
            image: eclipsebasyx/aas-environment:2.0.0-SNAPSHOT
            container_name: aas-env
            environment:
              - SERVER_PORT=8081
            volumes:
              - ./aas:/application/aas
              - ./basyx/aas-env.properties:/application/application.properties
            ports:
              - '8081:8081'
            restart: always
            depends_on:
              aas-registry:
                condition: service_healthy
              sm-registry:
                condition: service_healthy
              mongo:
                condition: service_healthy
          aas-registry:
            image: eclipsebasyx/aas-registry-log-mongodb:2.0.0-SNAPSHOT
            container_name: aas-registry
            ports:
              - '8082:8080'
            environment:
              - SERVER_PORT=8080
            volumes:
              - ./basyx/aas-registry.yml:/workspace/config/application.yml
            restart: always
            depends_on:
              mongo:
                condition: service_healthy
          sm-registry:
            image: eclipsebasyx/submodel-registry-log-mongodb:2.0.0-SNAPSHOT
            container_name: sm-registry
            ports:
              - '8083:8080'
            environment:
              - SERVER_PORT=8080
            volumes:
              - ./basyx/sm-registry.yml:/workspace/config/application.yml
            restart: always
            depends_on:
              mongo:
                condition: service_healthy
          mongo:
            image: mongo:5.0.10
            container_name: mongo
            environment:
              MONGO_INITDB_ROOT_USERNAME: mongoAdmin
              MONGO_INITDB_ROOT_PASSWORD: mongoPassword
            restart: always
            healthcheck:
              test: mongo
              interval: 10s
              timeout: 5s
              retries: 5
          aas-web-ui:
            image: eclipsebasyx/aas-gui:SNAPSHOT
            container_name: aas-ui
            ports:
              - '3000:3000'
            environment:
              AAS_REGISTRY_PATH: http://localhost:8082/shell-descriptors
              SUBMODEL_REGISTRY_PATH: http://localhost:8083/submodel-descriptors
              AAS_REPO_PATH: http://localhost:8081/shells
              SUBMODEL_REPO_PATH: http://localhost:8081/submodels
              CD_REPO_PATH: http://localhost:8081/concept-descriptions
              AAS_DISCOVERY_PATH: http://localhost:8084/lookup/shells
              PRIMARY_COLOR: '#347EE1'
              LOGO_PATH: SMIA_logo.ico
            restart: always
            depends_on:
              aas-env:
                condition: service_healthy
            volumes:
              - ./logo:/usr/src/app/dist/Logo


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

          smia-kb:
            image: ekhurtado/smia-tools:latest-smia-kb
            container_name: smia-kb
            ports:
              - '8090:8080'
            environment:
              - AAS_ENV_IP=http://aas-env:8081
              #- SELF_EXTRACT_CSS=yes
            depends_on:   # It does not depend on the AAS environment, but is added to correctly obtain all the data during the start-up
              aas-env:
                condition: service_healthy
            # volumes:
            #   - ./smia_kb:/smia_kb
            healthcheck:
              test: wget --no-verbose --tries=1 --spider http://smia-kb:8080/api/v3/ui/ || exit 1
              interval: 10s
              timeout: 5s
              retries: 5
              start_period: 5s

          smia-ism:
            image: ekhurtado/smia-tools:latest-smia-ism
            container_name: smia-ism
            environment:
              - AAS_MODEL_NAME=SMIA_InfrastructureServicesManager.aasx
              - AGENT_ID=smia-ism@ejabberd
              - AGENT_PSSWD=gciscedri1234
              - SMIA_KB_IP=http://smia-kb:8080
            depends_on:
              xmpp-server:
                condition: service_healthy
              smia-kb:
                condition: service_healthy
            healthcheck:
              test: exit 0
              start_period: 15s
            volumes:
              - ./aas:/smia_archive/config/aas


          # -----------------------------
          # CeDRI Infrastructure services
          # -----------------------------
          nodered:
            image: nodered/node-red
            container_name: nodered
            ports:
              - 1880:1880
            volumes:
              - ./nodered:/data

          # -------------------------
          # SMIA instances for assets
          # -------------------------
          smia-industrial-robot:
            image: ekhurtado/smia:latest-alpine
            container_name: smia-industrial-robot
            environment:
              - AAS_MODEL_NAME=CeDRI_IndustrialRobot_instance.aasx
              - AGENT_ID=smia-cedri-industrial-robot@ejabberd
              - AGENT_PSSWD=gciscedri1234
            depends_on:
              xmpp-server:
                condition: service_healthy
              smia-ism:
                condition: service_healthy
            volumes:
              - ./aas:/smia_archive/config/aas

          smia-punching-machine-a:
            image: ekhurtado/smia:latest-alpine
            container_name: smia-punching-machine-a
            environment:
              - AAS_MODEL_NAME=CeDRI_PunchingMachine_instanceA.aasx
              - AGENT_ID=smia-punchingmachine-a@ejabberd
              - AGENT_PSSWD=gciscedri1234
            depends_on:
              xmpp-server:
                condition: service_healthy
              smia-ism:
                condition: service_healthy
            volumes:
              - ./aas:/smia_archive/config/aas

          smia-punching-machine-b:
            image: ekhurtado/smia:latest-alpine
            container_name: smia-punching-machine-b
            environment:
              - AAS_MODEL_NAME=CeDRI_PunchingMachine_instanceB.aasx
              - AGENT_ID=smia-punchingmachine-b@ejabberd
              - AGENT_PSSWD=gciscedri1234
            depends_on:
              xmpp-server:
                condition: service_healthy
              smia-ism:
                condition: service_healthy
            volumes:
              - ./aas:/smia_archive/config/aas

          smia-indexed-line-a:
            image: ekhurtado/smia:latest-alpine
            container_name: smia-indexed-line-a
            environment:
              - AAS_MODEL_NAME=CeDRI_IndexedLine_instanceA.aasx
              - AGENT_ID=smia-indexedline-a@ejabberd
              - AGENT_PSSWD=gciscedri1234
            depends_on:
              xmpp-server:
                condition: service_healthy
              smia-ism:
                condition: service_healthy
            volumes:
              - ./aas:/smia_archive/config/aas

          smia-indexed-line-b:
            image: ekhurtado/smia:latest-alpine
            container_name: smia-indexed-line-b
            environment:
              - AAS_MODEL_NAME=CeDRI_IndexedLine_instanceB.aasx
              - AGENT_ID=smia-indexedline-b@ejabberd
              - AGENT_PSSWD=gciscedri1234
            depends_on:
              xmpp-server:
                condition: service_healthy
              smia-ism:
                condition: service_healthy
            volumes:
              - ./aas:/smia_archive/config/aas

          smia-hi-operator:
            image: ekhurtado/smia-tools:latest-smia-hi
            container_name: smia-hi-operator
            environment:
              - AAS_MODEL_NAME=CeDRI_Operator_instance.aasx
              - AGENT_ID=smia-hi-operator@ejabberd
              - AGENT_PSSWD=gciscedri1234
            depends_on:
              xmpp-server:
                condition: service_healthy
              smia-ism:
                condition: service_healthy
            volumes:
              - ./aas:/smia_archive/config/aas
            ports:
              - 10010:10000

          # SMIA Planning Execution
          smia-pe:
            image: ekhurtado/smia-tools:latest-smia-pe
            container_name: smia-pe
            environment:
              - AAS_MODEL_NAME=SMIA_PE_CeDRI_ScenarioA.aasx
              #- AAS_MODEL_NAME=SMIA_PE_CeDRI_ScenarioB.aasx
              - AGENT_ID=smia-pe@ejabberd
              - AGENT_PSSWD=gciscedri1234
            depends_on:
              xmpp-server:
                condition: service_healthy
              smia-ism:
                condition: service_healthy
            volumes:
              - ./aas:/smia_archive/config/aas
            ports:
              - 10000:10000



Use case results
----------------

TODO