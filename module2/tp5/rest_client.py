#!/usr/bin/env python3
"""TP5 — MikroTik CHR REST API demo (GET / POST / PATCH / DELETE).

Targets the CHR at 192.168.56.10 over HTTPS with a self-signed cert.
Lab only: TLS verification is disabled.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import requests
import urllib3
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HERE = Path(__file__).resolve().parent
load_dotenv(HERE / ".env")

CHR_HOST = os.environ.get("CHR_HOST", "192.168.56.10")
CHR_USER = os.environ.get("CHR_USER", "api-user")
CHR_PASS = os.environ.get("CHR_PASS", "")

if not CHR_PASS:
    sys.exit("CHR_PASS is empty — fill it in module2/tp5/.env")


class MikroTikREST:
    """Thin wrapper around the RouterOS /rest endpoint."""

    def __init__(self, host: str, user: str, password: str, timeout: int = 10) -> None:
        self.base = f"https://{host}/rest"
        self.session = requests.Session()
        self.session.auth = (user, password)
        self.session.verify = False  # lab only — self-signed cert
        self.session.headers["Content-Type"] = "application/json"
        self.timeout = timeout

    def _do(self, method: str, path: str, **kwargs):
        url = f"{self.base}/{path.lstrip('/')}"
        resp = self.session.request(method, url, timeout=self.timeout, **kwargs)
        resp.raise_for_status()
        return resp.json() if resp.content else None

    def get(self, path, **kw):
        return self._do("GET", path, **kw)

    def put(self, path, payload):
        return self._do("PUT", path, json=payload)

    def patch(self, path, payload):
        return self._do("PATCH", path, json=payload)

    def delete(self, path):
        return self._do("DELETE", path)


def show(title: str, data) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    print(json.dumps(data, indent=2, ensure_ascii=False))


def main() -> None:
    cli = MikroTikREST(CHR_HOST, CHR_USER, CHR_PASS)

    # 1) GET — system resource
    show("1) GET /system/resource", cli.get("system/resource"))

    # 2) GET — interface list (trimmed)
    ifaces = cli.get("interface")
    show(
        "2) GET /interface",
        [{k: i.get(k) for k in ("name", "type", "running")} for i in ifaces],
    )

    # 3) POST — add an address from TEST-NET-2 (198.51.100.0/24, reserved for docs)
    # PUT = create (POST is for action verbs like flush/release, not add)
    created = cli.put(
        "ip/address",
        {
            "address": "198.51.100.1/24",
            "interface": "ether1",
            "comment": "tp5-test",
        },
    )
    show("3) PUT /ip/address — created", created)

    # RouterOS returns the created object (with ".id") for PUT on /ip/address.
    # Some endpoints return {"ret": "*N"} instead — accept both.
    raw_id = None
    if isinstance(created, dict):
        raw_id = created.get(".id") or created.get("ret")
    elif isinstance(created, list) and created:
        raw_id = created[0].get(".id") or created[0].get("ret")
    if not raw_id:
        raise RuntimeError(f"Unexpected PUT response: {created}")
    addr_path = f"ip/address/{raw_id}"   # literal *N, no URL-encoding

    try:
        # 4) GET — read the entry back
        show(f"4) GET /{addr_path}", cli.get(addr_path))

        # 5) PATCH — update the comment
        cli.patch(addr_path, {"comment": "tp5-patched"})
        show(f"5) PATCH /{addr_path}", cli.get(addr_path))

        # 6) GET — firewall filter rules (read-only demo)
        show("6) GET /ip/firewall/filter", cli.get("ip/firewall/filter"))
    finally:
        # 7) DELETE — cleanup
        cli.delete(addr_path)
        print(f"\n7) DELETE /{addr_path} -> done (cleanup)")


if __name__ == "__main__":
    main()
