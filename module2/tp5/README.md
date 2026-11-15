# TP5 — MikroTik CHR REST API

Python client for the RouterOS v7 REST API over HTTPS.

## Prerequisites
- CHR at 192.168.56.10 (libvirt network: lab-mgmt, bridge virbr50)
- RouterOS user: api-user (group full)
- www-ssl enabled with certificate rest-cert
- Python 3.10+

## Setup
    cd module2/tp5
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

## Run
    python rest_client.py

Expected sequence:
1. GET /system/resource  -> board-name CHR, version 7.x, architecture x86_64
2. GET /interface        -> ether1, lo, ...
3. POST /ip/address      -> creates 198.51.100.1/24 on ether1
4. GET /ip/address/*N    -> read back
5. PATCH /ip/address/*N  -> comment becomes tp5-patched
6. GET /ip/firewall/filter
7. DELETE /ip/address/*N -> cleanup

## Security notes
- verify=False because CHR uses a self-signed cert. Lab only.
- .env is gitignored. Never commit real credentials.

## Files
- rest_client.py    : full CRUD demo
- requirements.txt  : requests, python-dotenv
- .env              : host/user/password (gitignored)

## Screenshots required
Save to module2/tp5/screenshots/:
- 01-chr-ip-address.png     : virsh console -> /ip address print
- 02-chr-www-ssl.png        : /ip service print detail where name=www-ssl
- 03-chr-certificate.png    : /certificate print where name=rest-cert
- 04-curl-rest.png          : curl -k -u api-user:... https://192.168.56.10/rest/system/resource
- 05-python-rest-client.png : full output of python rest_client.py
