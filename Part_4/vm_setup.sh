#!/usr/bin/env bash
set -euo pipefail

sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y docker.io docker-compose curl jq
sudo systemctl enable docker
sudo systemctl start docker

BASE=/opt/pipeline-monitoring
sudo mkdir -p "$BASE/deploy/prometheus" "$BASE/deploy/grafana/provisioning/datasources" "$BASE/deploy/grafana/provisioning/dashboards" "$BASE/deploy/grafana/dashboards" "$BASE/deploy/loki" "$BASE/deploy/promtail"

cat <<'EOF' | sudo tee "$BASE/docker-compose.yml" >/dev/null
services:
  loki:
    image: grafana/loki:3.3.2
    command: -config.file=/etc/loki/loki.yml
    ports:
      - "3100:3100"
    volumes:
      - ./deploy/loki/loki.yml:/etc/loki/loki.yml:ro
      - loki-data:/loki
    restart: unless-stopped

  promtail:
    image: grafana/promtail:3.3.2
    command: -config.file=/etc/promtail/promtail.yml
    volumes:
      - ./deploy/promtail/promtail.yml:/etc/promtail/promtail.yml:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - promtail-positions:/tmp
    depends_on:
      - loki
      - prometheus
      - grafana
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:v2.55.1
    command:
      - --config.file=/etc/prometheus/prometheus.yml
      - --storage.tsdb.path=/prometheus
      - --web.enable-lifecycle
    ports:
      - "9090:9090"
    volumes:
      - ./deploy/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    restart: unless-stopped

  grafana:
    image: grafana/grafana-oss:11.4.0
    environment:
      GF_SECURITY_ADMIN_USER: admin
      GF_SECURITY_ADMIN_PASSWORD: admin123
      GF_USERS_ALLOW_SIGN_UP: "false"
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
      - ./deploy/grafana/provisioning:/etc/grafana/provisioning:ro
      - ./deploy/grafana/dashboards:/var/lib/grafana/dashboards:ro
    restart: unless-stopped

volumes:
  loki-data:
  prometheus-data:
  grafana-data:
  promtail-positions:
EOF

cat <<'EOF' | sudo tee "$BASE/deploy/prometheus/prometheus.yml" >/dev/null
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: pipeline-app
    metrics_path: /metrics
    scheme: https
    static_configs:
      - targets:
          - flask2510-fbbwapfbg6c3hyhm.francecentral-01.azurewebsites.net:443

  - job_name: prometheus
    static_configs:
      - targets:
          - localhost:9090
EOF

cat <<'EOF' | sudo tee "$BASE/deploy/grafana/provisioning/datasources/datasource.yml" >/dev/null
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    uid: prometheus
  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
    uid: loki
EOF

cat <<'EOF' | sudo tee "$BASE/deploy/grafana/provisioning/dashboards/dashboards.yml" >/dev/null
apiVersion: 1

providers:
  - name: Pipeline dashboards
    folder: Pipeline Project
    type: file
    disableDeletion: false
    editable: true
    options:
      path: /var/lib/grafana/dashboards
EOF

cat <<'EOF' | sudo tee "$BASE/deploy/grafana/dashboards/pipeline-overview.json" >/dev/null
{
  "uid": "pipeline-overview",
  "title": "Pipeline Project Overview",
  "schemaVersion": 39,
  "version": 1,
  "refresh": "30s",
  "time": {
    "from": "now-6h",
    "to": "now"
  },
  "panels": [
    {
      "id": 1,
      "type": "timeseries",
      "title": "Request rate",
      "datasource": {
        "type": "prometheus",
        "uid": "prometheus"
      },
      "gridPos": { "h": 9, "w": 12, "x": 0, "y": 0 },
      "targets": [
        { "expr": "sum(rate(pipeline_http_requests_total[5m]))", "refId": "A" }
      ]
    },
    {
      "id": 2,
      "type": "timeseries",
      "title": "95th percentile latency",
      "datasource": {
        "type": "prometheus",
        "uid": "prometheus"
      },
      "gridPos": { "h": 9, "w": 12, "x": 12, "y": 0 },
      "targets": [
        {
          "expr": "histogram_quantile(0.95, sum(rate(pipeline_http_request_duration_seconds_bucket[5m])) by (le))",
          "refId": "A"
        }
      ]
    }
  ]
}
EOF

cat <<'EOF' | sudo tee "$BASE/deploy/loki/loki.yml" >/dev/null
auth_enabled: false

server:
  http_listen_port: 3100

common:
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    kvstore:
      store: inmemory

schema_config:
  configs:
    - from: 2024-01-01
      store: boltdb-shipper
      object_store: filesystem
      schema: v13
      index:
        prefix: index_
        period: 24h

storage_config:
  boltdb_shipper:
    active_index_directory: /loki/index
    cache_location: /loki/cache
    shared_store: filesystem
  filesystem:
    directory: /loki/chunks

compactor:
  working_directory: /loki/compactor

limits_config:
  retention_period: 168h
EOF

cat <<'EOF' | sudo tee "$BASE/deploy/promtail/promtail.yml" >/dev/null
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: docker-containers
    static_configs:
      - targets:
          - localhost
        labels:
          job: docker-containers
          __path__: /var/lib/docker/containers/*/*-json.log
    pipeline_stages:
      - docker: {}
EOF

cd "$BASE"
sudo docker-compose up -d
