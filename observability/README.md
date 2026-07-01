# Observability Stack

**Port:** Grafana `:4000` | Prometheus `:9090` | Tempo `:3200` | Loki `:3100` | OTel Collector `:4317/4318`

> Isolated from the main compose. Run separately via `DOCKER-COMPOSE.observability.yml`.

---

## Tech Stack

| Component | Image | Version | Role |
|---|---|---|---|
| **OTel Collector** | `otel/opentelemetry-collector-contrib` | `0.96.0` | Central telemetry router (receives, processes, fans-out) |
| **Grafana Tempo** | `grafana/tempo` | `2.4.1` | Distributed trace storage and query engine |
| **Grafana Loki** | `grafana/loki` | `2.9.4` | Log aggregation backend |
| **Prometheus** | `prom/prometheus` | `v2.51.1` | Time-series metrics storage with exemplar support |
| **Grafana** | `grafana/grafana` | `10.4.1` | Unified visualization — traces, metrics, logs |

---

## Architecture

```
jobhunter-api (FastAPI)
 ├── OTLP gRPC (traces + logs) ──► otel-collector:4317
 │                                    ├── traces ──► tempo:4317
 │                                    └── logs   ──► loki:3100/loki/api/v1/push
 └── /metrics (Prometheus format) ◄── prometheus:9090 (scrape)

grafana ──► tempo (traces)
        ──► loki  (logs, trace_id derived field → tempo)
        ──► prometheus (metrics)
```

**Tail Sampling** (in OTel Collector): always keeps 100% of error traces + slow traces (>2 s); probabilistically keeps 10% of normal traffic.

---

## Quick Start

### Prerequisites
The observability stack attaches to the existing `jobhunter_jobhunter_network`. The main stack must be up first:

```bash
docker compose up -d
```

### 1. Configure credentials

```bash
cp observability/.env.example observability/.env
# Edit observability/.env — set GF_SECURITY_ADMIN_PASSWORD
```

### 2. Start the observability stack

```bash
docker compose -f DOCKER-COMPOSE.observability.yml up -d
```

### 3. Restart collector after config changes

```bash
docker compose -f DOCKER-COMPOSE.observability.yml up -d --force-recreate otel-collector
```

### 4. Stop the stack

```bash
docker compose -f DOCKER-COMPOSE.observability.yml down
```

To also wipe all stored data (traces, logs, metrics):

```bash
docker compose -f DOCKER-COMPOSE.observability.yml down -v
```

---

## Service Access

| Service | URL | Credentials |
|---|---|---|
| Grafana | http://localhost:4000 | `admin` / `GF_SECURITY_ADMIN_PASSWORD` from `.env` |
| Prometheus | http://localhost:9090 | None (internal) |
| Tempo | http://localhost:3200 | None (internal) |
| Loki | http://localhost:3100 | None (internal) |
| OTel Collector Health | http://localhost:13133 | None |
| OTel Collector zPages | http://localhost:55679/debug/tracez | None |

---

## Environment Variables

### `observability/.env`

| Variable | Default | Description |
|---|---|---|
| `GF_SECURITY_ADMIN_USER` | `admin` | Grafana admin username |
| `GF_SECURITY_ADMIN_PASSWORD` | _(required)_ | Grafana admin password |

### `orchestration/.env`

| Variable | Default | Description |
|---|---|---|
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `http://otel-collector:4317` | OTLP gRPC endpoint for the API to export to |

---

## Directory Structure

```
observability/
├── otel-collector-config.yml   # Receivers, processors (tail sampling, mask_ip), exporters
├── tempo-config.yml            # Tempo storage and query config
├── loki-config.yml             # Loki storage and ingestion config
├── prometheus-config.yml       # Scrape targets (api:8000, collector:8889, tempo:3200)
├── .env.example                # Env template for Grafana credentials
├── .env                        # Active credentials (not committed)
└── grafana/
    ├── datasources/
    │   └── datasources.yml     # Auto-provisioned: Tempo, Loki, Prometheus datasources
    └── dashboards/
        ├── dashboards.yml      # Dashboard provider config
        └── jobhunter.json      # JobHunter Observability dashboard
```

---

## Grafana Dashboards

Navigate to **http://localhost:4000 → Dashboards → JobHunter Observability**.

The dashboard surfaces:
- **Auth metrics**: login rate, failure rate by reason, JWT validation latency
- **Resume pipeline**: upload count, generation rate, failure rate, processing duration p95
- **AI engine**: request rate by provider, duration p95, failure rate
- **MinIO**: upload and download counts with result labels
- **Infrastructure**: request rate, error rate, latency — all from the FastAPI auto-instrumentation

### Trace → Log correlation

In any Grafana panel showing Tempo traces, click a `trace_id` to open the trace. From any span, click **Logs for this span** to pivot directly to Loki and see all structured JSON logs carrying that `trace_id`.

---

## Operational Procedures

### Verify all Prometheus scrape targets are healthy

Open http://localhost:9090/targets - All three jobs (`jobhunter-orchestration`, `otel-collector`, `tempo`) must show **State: UP**.

### Verify OTel Collector is healthy

```bash
curl http://localhost:13133
# Expected: HTTP 200 OK
```

### Check collector pipeline stats (zPages)

Open http://localhost:55679/debug/tracez — shows active spans and pipeline processing stats.

### View live API logs

```bash
docker logs jobhunter-api -f
```

### View collector logs

```bash
docker logs jobhunter-otel-collector -f
```

### Force Grafana to reload provisioned dashboards

```bash
docker compose -f DOCKER-COMPOSE.observability.yml restart grafana
```

### Apply a config change to any service

Edit the relevant config file in `observability/`, then force-recreate only that service:

```bash
# Example: collector config changed
docker compose -f DOCKER-COMPOSE.observability.yml up -d --force-recreate otel-collector

# Example: Loki config changed
docker compose -f DOCKER-COMPOSE.observability.yml up -d --force-recreate loki
```

---

## Troubleshooting

### OTel Collector fails to start with `invalid keys` error

**Cause:** The `attributes` processor does not support `pattern` or `replacement` keys — only `action`, `key`, `value`, and `from_attribute`.

**Fix:** Use `action: hash` without `pattern`/`replacement`:

```yaml
attributes/mask_ip:
  actions:
    - key: client_ip
      action: hash
```

---

### API logs show `Transient error StatusCode.UNAVAILABLE` on startup

**Cause:** The API container started before the OTel Collector was ready. The exporter retries with exponential backoff automatically.

**Action:** Wait 30–60 seconds. Once the collector is healthy, the errors stop and traces start flowing. This is not a fatal error.

---

### Prometheus targets show `State: DOWN`

**Checks:**
1. Is the API container running? `docker ps | grep jobhunter-api`
2. Is the API on the same network as Prometheus? Both must be on `jobhunter_jobhunter_network`.
3. Does `/metrics` respond? `curl http://localhost:8000/metrics`
4. Check the `api` hostname in `prometheus-config.yml` matches the container name in `DOCKER-COMPOSE.yml`.

---

### No traces appearing in Tempo

**Checks:**
1. Verify collector is healthy: `curl http://localhost:13133`
2. Check collector logs for export errors: `docker logs jobhunter-otel-collector`
3. Confirm `OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317` in `orchestration/.env`.
4. Tail sampling may be dropping 90% of normal traffic — generate at least 10 requests or trigger an error to guarantee a kept trace.

---

### No logs appearing in Loki

**Checks:**
1. The API must be sending logs over OTLP (the `loki` exporter in the collector handles this pipeline).
2. Check the Grafana Loki datasource is provisioned: **Grafana → Configuration → Data Sources → Loki** should show URL `http://loki:3100`.
3. Check the collector logs pipeline: `docker logs jobhunter-otel-collector | grep loki`.

---

### Grafana shows `No data` on a panel

**Checks:**
1. Confirm the correct time range is selected (set to **Last 15 minutes** or **Last 1 hour**).
2. Confirm at least one API request has been made since the stack booted.
3. Verify the datasources are correctly provisioned: **Grafana → Configuration → Data Sources**.

---

### `jobhunter_jobhunter_network` not found on observability stack startup

**Cause:** The main compose stack is not running, so the external network does not exist.

**Fix:**
```bash
# Start the main stack first
docker compose up -d
# Then start observability
docker compose -f DOCKER-COMPOSE.observability.yml up -d
```
