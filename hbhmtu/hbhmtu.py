#!/usr/local/bin/python2.7
import os
from addr import *
from scapy.all import *
import time

def hbhmtu_udp(ip, split=48, data="IAMSOMEPAYLOAD"):
    udp = UDP(sport=45234, dport=5005)

    packet = ip/IPv6ExtHdrHopByHop(options=HBHMTU())/udp/data
    return packet

def hbhmtu_udp_raw(ip, split=48, data="IAMSOMEPAYLOAD"):
    ip = IPv6(src=LOCAL_ADDR6, dst=REMOTE_ADDR6, nh=0)
    udp = UDP(sport=45234, dport=5005)
    rawhbh = b'\x11\x00\x3E\x02\x28\x23\x00\x00'    # 17 0 expopt 2 9000 00 00
    rawhbh = b'\x11\x00\x3E\x02\x05\xdc\x00\x00'    # 17 0 expopt 2 1500 00 00

    packet = ip/rawhbh/udp/data
    return packet

generators = [
    hbhmtu_udp_raw, 
    #hbhmtu_udp, 
]

if __name__ == "__main__":
    print "hbhmtu udp datagrams"
    print "from {} to {}".format(LOCAL_ADDR6, REMOTE_ADDR6)

    # construct a template v6 packet
    ip = IPv6(src=LOCAL_ADDR6, dst=REMOTE_ADDR6)

    pkts = []
    for g in generators:
        pkts.append(g(ip))

    # bundle each packet(with a frag) into an ethernet frame
    eth=[]
    for pkt in pkts:
            eth.append(Ether(src=LOCAL_MAC, dst=REMOTE_MAC)/pkt)

    sendp(eth, iface=LOCAL_IF)

"""
class HBHMTU(Packet):  # IPv6 Hop-By-Hop Option
    name = "HBHMTU"
    fields_desc = [_OTypeField("otype", 0x01, _hbhopts),
    FieldLenField("optlen", None, length_of="optdata", fmt="B"),
    StrLenField("optdata", "",
        length_from=lambda pkt: pkt.optlen)]

    def alignment_delta(self, curpos):  # No alignment requirement
        return 0

    def extract_padding(self, p):
        return b"", p
"""
