/ip firewall filter add chain=input connection-state=established,related action=accept comment="allow established"
/ip firewall filter add chain=input protocol=icmp action=accept comment="allow icmp"
/ip firewall filter add chain=input in-interface=ether1 action=drop comment="drop rest"
