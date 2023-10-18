# protocol_mapを関数外で定義
protocol_map = {
    0: "HOPOPT",  # IPv6 Hop-by-Hop Option
    1: "ICMP",   # Internet Control Message
    2: "IGMP",   # Internet Group Management
    3: "GGP",    # Gateway-to-Gateway
    4: "IPv4",   # IPv4 encapsulation
    5: "ST",     # Stream
    6: "TCP",    # Transmission Control
    7: "CBT",    # CBT
    8: "EGP",    # Exterior Gateway Protocol
    9: "IGP",    # any private interior gateway 
    17: "UDP",   # User Datagram
    18: "MUX",   # Multiplexing
    19: "DCN",   # DCN Measurement Subsystems
    20: "HMP",   # Host Monitoring
    21: "PRM",   # Packet Radio Measurement
    22: "XNS",   # XEROX NS IDP
    27: "RDP",   # Reliable Data Protocol
    29: "ISO",   # ISO Transport Protocol Class 4
    33: "DCCP",  # Datagram Congestion Control Protocol
    41: "IPv6",  # IPv6 encapsulation
    43: "IPv6-Route",  # Routing Header for IPv6
    44: "IPv6-Frag",  # Fragment Header for IPv6
    45: "IDRP",  # Inter-Domain Routing Protocol
    46: "RSVP",  # Reservation Protocol
    47: "GRE",   # Generic Routing Encapsulation
    50: "ESP",   # Encap Security Payload
    51: "AH",    # Authentication Header
    57: "SKIP",  # SKIP
    58: "IPv6-ICMP",  # ICMP for IPv6
    59: "IPv6-NoNxt",  # No Next Header for IPv6
    60: "IPv6-Opts",  # Destination Options for IPv6
    66: "RVD",   # MIT Remote Virtual Disk Protocol
    88: "EIGRP", # Enhanced Interior Routing Protocol (Cisco)
    89: "OSPF",  # Open Shortest Path First
    94: "IPIP",  # IP-within-IP Encapsulation Protocol
    97: "ETHERIP",  # Ethernet-within-IP Encapsulation
    98: "ENCAP",  # Yet Another IP encapsulation
    103: "PIM",  # Protocol Independent Multicast
    108: "IPCOMP",  # IP Payload Compression Protocol
    112: "VRRP",  # Virtual Router Redundancy Protocol
    115: "L2TP",  # Layer Two Tunneling Protocol
    132: "SCTP",  # Stream Control Transmission Protocol
    133: "FC",    # Fibre Channel
    135: "MPLS-in-IP",  # MPLS-in-IP
    137: "MPLS-in-UDP",  # MPLS-in-UDP
    139: "HIP",   # Host Identity Protocol
    140: "SHIM6",  # Shim6 Protocol
    141: "WESP",  # Wrapped Encapsulating Security Payload
    142: "ROHC" # Robust Header Compression
}

def ip_proto_to_name(proto_number):
    return protocol_map.get(int(proto_number), proto_number)

