/ip dns set allow-remote-requests=yes servers=1.1.1.1,8.8.8.8
/ip firewall nat add chain=dstnat protocol=udp dst-port=53 action=redirect to-ports=53
