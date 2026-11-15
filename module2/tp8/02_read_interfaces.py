import json
import ubus

sid = ubus.login()
dump = ubus.call(ubus.HOST, sid, "network.interface", "dump")
print(json.dumps(dump, indent=2))

print("\n--- Summary ---")
for i in dump["interface"]:
    ips = [f'{a["address"]}/{a["mask"]}' for a in i.get("ipv4-address", [])]
    print(f'{i["interface"]}: up={i["up"]} device={i.get("l3_device")} ipv4={ips}')

lan = next(i for i in dump["interface"] if i["interface"] == "lan")
dev = ubus.call(ubus.HOST, sid, "network.device", "status", {"name": lan["l3_device"]})
st = dev.get("statistics", {})
print(f'\n{lan["l3_device"]} link up={dev.get("up")} '
      f'rx_bytes={st.get("rx_bytes")} tx_bytes={st.get("tx_bytes")}')
