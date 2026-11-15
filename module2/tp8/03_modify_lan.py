import sys
import time
import ubus

if len(sys.argv) != 2:
    sys.exit("usage: python 03_modify_lan.py NEW_IP")
new_ip = sys.argv[1]
old = ubus.HOST

sid = ubus.login(old)
print("Before:", ubus.call(old, sid, "uci", "get",
      {"config": "network", "section": "lan", "option": "ipaddr"}))

print("uci set:", ubus.call(old, sid, "uci", "set", {
    "config": "network", "section": "lan", "values": {"ipaddr": new_ip + "/24"}}))
print("uci commit:", ubus.call(old, sid, "uci", "commit", {"config": "network"}))

try:
    ubus.call(old, sid, "network", "reload")
except Exception as e:
    print("reload sent (connection dropped as expected):", type(e).__name__)

print(f"Waiting for {new_ip} ...")
for _ in range(30):
    try:
        sid2 = ubus.login(new_ip)
        break
    except Exception:
        time.sleep(2)
else:
    sys.exit("New IP not reachable")

print("After (uci):", ubus.call(new_ip, sid2, "uci", "get",
      {"config": "network", "section": "lan", "option": "ipaddr"}))
dump = ubus.call(new_ip, sid2, "network.interface", "dump")
lan = next(i for i in dump["interface"] if i["interface"] == "lan")
print("After (live):", [f'{a["address"]}/{a["mask"]}' for a in lan.get("ipv4-address", [])])
ubus.set_host(new_ip)
print("OPENWRT_HOST updated to", new_ip)
