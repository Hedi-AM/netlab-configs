/ip dhcp-server add name=dhcp-lab interface=ether1 address-pool=pool-guest disabled=no
/ip dhcp-server network add address=192.168.10.0/24 gateway=192.168.10.254 dns-server=1.1.1.1
