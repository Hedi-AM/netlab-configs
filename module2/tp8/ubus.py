import os
from pathlib import Path
import requests

ENV_FILE = Path(__file__).parent / ".env"
NULL_SESSION = "0" * 32


def load_env():
    env = {}
    for line in ENV_FILE.read_text().splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v
    return env


ENV = load_env()
HOST = ENV["OPENWRT_HOST"]
PW = ENV["OPENWRT_PASSWORD"]


def call(host, session, obj, method, args=None):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "call",
        "params": [session, obj, method, args or {}],
    }
    resp = requests.post(f"http://{host}/ubus", json=payload, timeout=4)
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        raise RuntimeError(data["error"])
    code, *rest = data["result"]
    if code != 0:
        raise RuntimeError(f"ubus {obj}.{method} failed, code {code}")
    return rest[0] if rest else {}


def login(host=HOST):
    r = call(host, NULL_SESSION, "session", "login",
             {"username": "root", "password": PW})
    return r["ubus_rpc_session"]


def set_host(new_host):
    lines = ENV_FILE.read_text().splitlines()
    out = [f"OPENWRT_HOST={new_host}" if l.startswith("OPENWRT_HOST=") else l
           for l in lines]
    ENV_FILE.write_text("\n".join(out) + "\n")
