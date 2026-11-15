import os
import sys

import requests
import urllib3
import yaml
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

BASE_URL = f"https://{os.getenv('OPNSENSE_HOST')}/api"
AUTH = (os.getenv("OPNSENSE_KEY"), os.getenv("OPNSENSE_SECRET"))
GRID = {"current": 1, "rowCount": -1, "searchPhrase": ""}


class ApiError(Exception):
    pass


def api(method, path, payload=None):
    resp = requests.request(
        method, f"{BASE_URL}/{path}", auth=AUTH, json=payload, verify=False, timeout=15
    )
    resp.raise_for_status()
    data = resp.json()
    if isinstance(data, dict) and data.get("result") == "failed":
        raise ApiError(f"{path}: {data.get('validations') or data}")
    return data


def find_row(path, key, value):
    for row in api("POST", path, GRID).get("rows", []):
        if row.get(key) == value:
            return row
    return None


def provision_dhcp(cfg):
    api("POST", "kea/dhcpv4/set", {
        "dhcpv4": {"general": {
            "enabled": "1",
            "interfaces": cfg["interface"],
            "fwrules": "1",
        }}
    })
    body = {"subnet4": {
        "subnet": cfg["subnet"],
        "pools": f"{cfg['range_start']} - {cfg['range_end']}",
        "option_data_autocollect": "0",
        "option_data": {
            "routers": cfg["gateway"],
            "domain_name_servers": ",".join(cfg["dns"]),
        },
        "description": cfg["description"],
    }}
    row = find_row("kea/dhcpv4/search_subnet", "subnet", cfg["subnet"])
    if row:
        api("POST", f"kea/dhcpv4/set_subnet/{row['uuid']}", body)
        print(f"[DHCP] subnet {cfg['subnet']} updated")
    else:
        api("POST", "kea/dhcpv4/add_subnet", body)
        print(f"[DHCP] subnet {cfg['subnet']} created")
    print("[DHCP] reconfigure:", api("POST", "kea/service/reconfigure"))


def provision_nat(rules):
    for r in rules:
        body = {"rule": {
            "disabled": "0",
            "interface": r["interface"],
            "ipprotocol": "inet",
            "protocol": r["protocol"],
            "source": {"network": "any"},
            "destination": {"network": "wanip", "port": str(r["external_port"])},
            "target": r["target_ip"],
            "local-port": str(r["target_port"]),
            "descr": r["description"],
            "pass": r.get("filter_rule", ""),
        }}
        row = find_row("firewall/d_nat/search_rule", "descr", r["description"])
        if row:
            api("POST", f"firewall/d_nat/set_rule/{row['uuid']}", body)
            print(f"[NAT] rule '{r['description']}' updated")
        else:
            api("POST", "firewall/d_nat/add_rule", body)
            print(f"[NAT] rule '{r['description']}' created")
    print("[NAT] apply d_nat:", api("POST", "firewall/d_nat/apply"))
    print("[NAT] apply filter:", api("POST", "firewall/filter/apply"))


def verify(cfg):
    ok = True
    if not find_row("kea/dhcpv4/search_subnet", "subnet", cfg["dhcp"]["subnet"]):
        print("[CHECK] DHCP subnet missing")
        ok = False
    for r in cfg["nat"]:
        if not find_row("firewall/d_nat/search_rule", "descr", r["description"]):
            print(f"[CHECK] NAT rule missing: {r['description']}")
            ok = False
    print("[CHECK] kea status:", api("POST", "kea/service/status").get("status"))
    return ok


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    with open(path) as f:
        cfg = yaml.safe_load(f)
    try:
        provision_dhcp(cfg["dhcp"])
        provision_nat(cfg["nat"])
        if not verify(cfg):
            sys.exit(2)
    except (requests.RequestException, ApiError) as e:
        print("ERROR:", e)
        sys.exit(1)
    print("DONE")


if __name__ == "__main__":
    main()
