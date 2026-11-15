# TP7 - OPNsense zero-touch provisioning

Simulated scenario: a fresh OPNsense 26.7 firewall (KVM/libvirt VM, WAN on the
default NAT network, LAN on a host-only network, LAN IP 192.168.1.1) is
configured entirely by script, with no manual change in the web UI.

## What the script does
`zero_touch_provision.py` reads `config.yaml` and, through the OPNsense REST API:
1. Enables the Kea DHCPv4 service on LAN, creates or updates the subnet with its
   pool, gateway and DNS servers, then reconfigures the service.
2. Creates or updates the destination NAT rule (WAN port 8080 to
   192.168.1.10:8080), then applies the NAT and filter changes.
3. Re-reads the configuration to check everything exists.

It can be run repeatedly: existing objects are found first (by subnet or rule
description) and updated instead of duplicated. HTTP errors and API validation
failures stop the script with a clear message and a non-zero exit code.

Note: OPNsense 26.7 has no legacy `dhcpv4` API module, so DHCP uses the Kea
module (`/api/kea/dhcpv4`) and port forwarding uses `/api/firewall/d_nat`.

## Usage
    python3 -m venv .venv && . .venv/bin/activate
    pip install -r requirements.txt
    # create .env (never committed):
    #   OPNSENSE_HOST, OPNSENSE_KEY, OPNSENSE_SECRET
    python zero_touch_provision.py

## Files
- `config.yaml`: DHCP range, DNS, NAT rule
- `zero_touch_provision.py`: orchestration script
- `api_check.py`: first authenticated API call
- `screenshots/`: DHCP and NAT rule as seen in the OPNsense UI
