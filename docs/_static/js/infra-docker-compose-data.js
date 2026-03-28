/**
 * Infrastructure Docker Compose Data
 * ====================================
 * This file embeds the content of infrastructure-docker-compose.yml and ejabberd.yml
 * as JavaScript constants, so they can be read by the SMIA Environment Builder
 * without needing HTTP fetch() (which fails with file:// protocol due to CORS).
 *
 * IMPORTANT: If you modify the YAML files in _static/files/, update the
 * corresponding constants here to keep them in sync.
 */

const INFRA_DOCKER_COMPOSE_YAML = `# ----------------------------------------
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

smia-i-kb:
  image: ekhurtado/smia-tools:latest-smia-kb
  container_name: smia-kb
  ports:
    - '8090:8080'
  environment:
    - AAS_ENV_IP=http://aas-env:8081
    #- SELF_EXTRACT_CSS=yes
  depends_on:
    aas-env:
      condition: service_healthy
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
    smia-i-kb:
      condition: service_healthy
  healthcheck:
    test: exit 0
    start_period: 15s
  volumes:
    - ./aas:/smia_archive/config/aas
`;


const EJABBERD_YAML = `###
###              ejabberd configuration file
###
### The parameters used in this configuration file are explained at
###
###       https://docs.ejabberd.im/admin/configuration
###
### The configuration file is written in YAML.
### *******************************************************
### *******           !!! WARNING !!!               *******
### *******     YAML IS INDENTATION SENSITIVE       *******
### ******* MAKE SURE YOU INDENT SECTIONS CORRECTLY *******
### *******************************************************
### Refer to http://en.wikipedia.org/wiki/YAML for the brief description.
###

hosts:
  - localhost
  - ejabberd

loglevel: info

ca_file: /opt/ejabberd/conf/cacert.pem

certfiles:
  - /opt/ejabberd/conf/server.pem

## If you already have certificates, list them here
# certfiles:
#  - /etc/letsencrypt/live/domain.tld/fullchain.pem
#  - /etc/letsencrypt/live/domain.tld/privkey.pem

listen:
  -
    port: 5222
    ip: "::"
    module: ejabberd_c2s
    max_stanza_size: 262144
    shaper: c2s_shaper
    access: c2s
    starttls_required: true
  -
    port: 5223
    ip: "::"
    module: ejabberd_c2s
    max_stanza_size: 262144
    shaper: c2s_shaper
    access: c2s
    tls: true
  -
    port: 5269
    ip: "::"
    module: ejabberd_s2s_in
    max_stanza_size: 524288
    shaper: s2s_shaper
  -
    port: 5443
    ip: "::"
    module: ejabberd_http
    tls: true
    request_handlers:
      /admin: ejabberd_web_admin
      /api: mod_http_api
      /bosh: mod_bosh
      /captcha: ejabberd_captcha
      /upload: mod_http_upload
      /ws: ejabberd_http_ws
  -
    port: 5280
    ip: "::"
    module: ejabberd_http
    request_handlers:
      /admin: ejabberd_web_admin
      /.well-known/acme-challenge: ejabberd_acme
  -
    port: 3478
    ip: "::"
    transport: udp
    module: ejabberd_stun
    use_turn: true
    ## The server's public IPv4 address:
    # turn_ipv4_address: "203.0.113.3"
    ## The server's public IPv6 address:
    # turn_ipv6_address: "2001:db8::3"
  -
    port: 1883
    ip: "::"
    module: mod_mqtt
    backlog: 1000

s2s_use_starttls: optional

acl:
  local:
    user_regexp: ""
  loopback:
    ip:
      - 127.0.0.0/8
      - ::1/128

access_rules:
  local:
    allow: local
  c2s:
    deny: blocked
    allow: all
  announce:
    allow: admin
  configure:
    allow: admin
  muc_create:
    allow: local
  pubsub_createnode:
    allow: local
  trusted_network:
    allow: loopback

api_permissions:
  "console commands":
    from:
      - ejabberd_ctl
    who: all
    what: "*"
  "admin access":
    who:
      access:
        allow:
          - acl: loopback
          - acl: admin
      oauth:
        scope: "ejabberd:admin"
        access:
          allow:
            - acl: loopback
            - acl: admin
    what:
      - "*"
      - "!stop"
      - "!start"
  "public commands":
    who:
      ip: 127.0.0.1/8
    what:
      - status
      - connected_users_number

shaper:
  normal:
    rate: 3000
    burst_size: 20000
  fast: 100000

shaper_rules:
  max_user_sessions: 10
  max_user_offline_messages:
    5000: admin
    100: all
  c2s_shaper:
    none: admin
    normal: all
  s2s_shaper: fast

modules:
  mod_adhoc: {}
  mod_admin_extra: {}
  mod_announce:
    access: announce
  mod_avatar: {}
  mod_blocking: {}
  mod_bosh: {}
  mod_caps: {}
  mod_carboncopy: {}
  mod_client_state: {}
  mod_configure: {}
  mod_disco: {}
  mod_fail2ban: {}
  mod_http_api: {}
  mod_http_upload:
    put_url: https://@HOST@:5443/upload
    custom_headers:
      "Access-Control-Allow-Origin": "https://@HOST@"
      "Access-Control-Allow-Methods": "GET,HEAD,PUT,OPTIONS"
      "Access-Control-Allow-Headers": "Content-Type"
  mod_last: {}
  mod_mam:
    ## Mnesia is limited to 2GB, better to use an SQL backend
    ## For small servers SQLite is a good fit and is very easy
    ## to configure. Uncomment this when you have SQL configured:
    ## db_type: sql
    assume_mam_usage: true
    default: always
  mod_mqtt: {}
  mod_muc:
    access:
      - allow
    access_admin:
      - allow: admin
    access_create: muc_create
    access_persistent: muc_create
    access_mam:
      - allow
    default_room_options:
      mam: true
  mod_muc_admin: {}
  mod_offline:
    access_max_user_messages: max_user_offline_messages
  mod_ping: {}
  mod_privacy: {}
  mod_private: {}
  mod_proxy65:
    access: local
    max_connections: 5
  mod_pubsub:
    access_createnode: pubsub_createnode
    plugins:
      - flat
      - pep
    force_node_config:
      ## Avoid buggy clients to make their bookmarks public
      storage:bookmarks:
        access_model: whitelist
  mod_push: {}
  mod_push_keepalive: {}
  mod_register:
    ## Only accept registration requests from the "trusted"
    ## network (see access_rules section above).
    ## Think twice before enabling registration from any
    ## address. See the Jabber SPAM Manifesto for details:
    ## https://github.com/ge0rg/jabber-spam-fighting-manifesto
    ip_access: all
  mod_roster:
    versioning: true
  mod_s2s_dialback: {}
  mod_shared_roster: {}
  mod_stream_mgmt:
    resend_on_timeout: if_offline
  mod_stun_disco: {}
  mod_vcard: {}
  mod_vcard_xupdate: {}
  mod_version:
    show_os: false

### Local Variables:
### mode: yaml
### End:
### vim: set filetype=yaml tabstop=8`;
