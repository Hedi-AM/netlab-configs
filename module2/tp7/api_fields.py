import os, requests, urllib3
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()
BASE_URL = f"https://{os.getenv('OPNSENSE_HOST')}/api"
AUTH = (os.getenv("OPNSENSE_KEY"), os.getenv("OPNSENSE_SECRET"))

def flat(o, p=""):
    if isinstance(o, dict):
        if o and all(isinstance(v, dict) and "selected" in v for v in o.values()):
            print(f"{p} => {len(o)} options, selected: {[k for k, v in o.items() if v['selected']]}")
            return
        for k, v in o.items():
            flat(v, f"{p}.{k}")
    else:
        print(f"{p} = {o}")

for path in ["kea/dhcpv4/get_subnet", "kea/service/status", "firewall/d_nat/get_rule", "firewall/d_nat/apply"]:
    r = requests.get(f"{BASE_URL}/{path}", auth=AUTH, verify=False, timeout=5)
    print(f"\n##### {path} -> {r.status_code}")
    try:
        flat(r.json())
    except ValueError:
        print(r.text[:200])

r = requests.get(f"{BASE_URL}/kea/dhcpv4/get", auth=AUTH, verify=False, timeout=5)
print("\n##### kea/dhcpv4/get general")
flat(r.json()["dhcpv4"]["general"], "general")
