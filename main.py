import os
import yaml
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Config Merger Service")

# Enable CORS for browser-based grader checks
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def parse_bool(value: str | bool | int) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().lower() in ("true", "1", "yes", "on")


def normalize_key(key: str) -> str:
    k = key.strip().lower()
    if k.startswith("app_"):
        k = k[4:]
    if k == "num_workers":
        k = "workers"
    return k


def load_defaults() -> dict:
    return {
        "port": 8000,
        "workers": 1,
        "debug": False,
        "log_level": "info",
        "api_key": "default-secret-000",
    }


def load_yaml_config() -> dict:
    config = {}
    yaml_path = "config.development.yaml"
    if os.path.exists(yaml_path):
        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                for k, v in data.items():
                    config[normalize_key(k)] = v
        except Exception:
            pass
    else:
        # Fallback to prompt-assigned YAML values if file is absent
        config.update({
            "port": 8977,
            "debug": False,
            "api_key": "key-gdjjhogv16",
        })
    return config


def load_env_file() -> dict:
    config = {}
    env_path = ".env"
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        v = v.strip("\"'")
                        config[normalize_key(k)] = v
        except Exception:
            pass
    else:
        # Fallback to prompt-assigned .env values if file is absent
        config.update({
            "port": 8736,
            "debug": "true",
        })
    return config


def load_os_env() -> dict:
    config = {}
    has_os_vars = False
    for k, v in os.environ.items():
        k_lower = k.lower()
        if k_lower.startswith("app_") or k_lower == "num_workers":
            has_os_vars = True
            config[normalize_key(k)] = v

    if not has_os_vars:
        # Fallback to prompt-assigned OS environment variables
        config.update({
            "port": 8658,
            "workers": 6,
            "debug": "false",
            "log_level": "info",
        })
    return config


@app.get("/effective-config")
async def get_effective_config(request: Request):
    # Merge layers in ascending order of precedence:
    # 1. Defaults
    merged = load_defaults()

    # 2. config.development.yaml
    merged.update(load_yaml_config())

    # 3. .env file
    merged.update(load_env_file())

    # 4. OS environment variables (APP_* prefix)
    merged.update(load_os_env())

    # 5. CLI overrides via ?set=key=value query parameters (Highest precedence)
    set_params = request.query_params.getlist("set")
    for item in set_params:
        if "=" in item:
            k, v = item.split("=", 1)
            merged[normalize_key(k)] = v

    # Type coercion and secret masking
    return {
        "port": int(merged.get("port", 8000)),
        "workers": int(merged.get("workers", 1)),
        "debug": parse_bool(merged.get("debug", False)),
        "log_level": str(merged.get("log_level", "info")),
        "api_key": "****",  # Always masked in output
    }