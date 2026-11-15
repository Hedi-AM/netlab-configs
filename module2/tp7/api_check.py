import os, sys, json, requests, urllib3
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()
BASE_URL = f"https://{os.getenv('OPNSENSE_HOST')}/api"
AUTH = (os.getenv("OPNSENSE_KEY"), os.getenv("OPNSENSE_SECRET"))

resp = requests.get(f"{BASE_URL}/core/system/status", auth=AUTH, verify=False, timeout=5)
resp.raise_for_status()
print("STATUS OK:", json.dumps(resp.json())[:300])

candidates = [
    "dhcpv4/settings/get",
    "dhcpv4/service/status",
    "kea/dhcpv4/get",
    "kea/dhcpv4/search_subnet",
    "dnsmasq/settings/get",
    "dnsmasq/service/status",
    "firewall/d_nat/search_rule",
    "firewall/source_nat/search_rule",
    "firewall/filter/apply",
]
for path in candidates:
    try:
        r = requests.get(f"{BASE_URL}/{path}", auth=AUTH, verify=False, timeout=5)
        print(f"{r.status_code}  {path}  {r.text[:80].replace(chr(10), ' ')}")
    except requests.RequestException as e:
        print("ERR", path, e)
