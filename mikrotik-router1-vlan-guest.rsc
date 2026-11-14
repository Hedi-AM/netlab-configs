/interface vlan add name=vlan-guest vlan-id=20 interface=bridge
/ip address add address=192.168.20.1/24 interface=vlan-guest
/ip pool add name=pool-guest ranges=192.168.20.100-192.168.20.200
