# 12-Factor Config Precedence Service

[![Render](https://img.shields.io/badge/Render-Live%20Demo-brightgreen)](https://one2-factor-config-precedence-571g.onrender.com/effective-config)

A FastAPI microservice designed to merge multiple configuration layers following 12-Factor app principles, with dynamic CLI query parameter overrides.

## 🚀 Deployed Endpoint

- **Live Service URL:** [https://one2-factor-config-precedence-571g.onrender.com/effective-config](https://one2-factor-config-precedence-571g.onrender.com/effective-config)

---

## ⚙️ Configuration Precedence Hierarchy

The service resolves configuration values across 5 distinct layers in ascending order of precedence (lowest to highest):

1. **Hardcoded Defaults** (Lowest) — `port: 8000`, `workers: 1`, `debug: false`, `log_level: info`, `api_key: default-secret-000`
2. **YAML File** — `config.development.yaml` overrides
3. **Environment File** — `.env` variables
4. **OS Environment Variables** — System environment variables with `APP_*` prefix or `NUM_WORKERS`
5. **CLI Overrides** (Highest) — Query parameters supplied via `?set=key=value`

---

## 🔑 Key Features

- **Type Coercion:**
  - `port`, `workers` → `integer`
  - `debug` → `boolean` (`true`, `1`, `yes`, `on` case-insensitively evaluate to `true`)
  - `log_level` and all other keys → `string`
- **Alias Mapping:** `NUM_WORKERS` in `.env` or OS environment variables maps to `workers`.
- **Secret Masking:** `api_key` is masked as `"****"` in all API responses.
- **CORS Enabled:** Cross-Origin Resource Sharing is enabled for browser checks.

---

## 📡 API Usage

### `GET /effective-config`

Evaluates and returns the final effective configuration payload.

#### Example Request

```bash
curl "[https://one2-factor-config-precedence-571g.onrender.com/effective-config?set=port=9000&set=debug=true&set=workers=4](https://one2-factor-config-precedence-571g.onrender.com/effective-config?set=port=9000&set=debug=true&set=workers=4)"
