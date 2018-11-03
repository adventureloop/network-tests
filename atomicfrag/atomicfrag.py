#!/usr/local/bin/python2.7
import os
from addr import *
from scapy.all import *
import time

def udp_atom_fragments(ip, split=48, data="IAMSOMEPAYLOAD"):
    udp = UDP(sport=45234, dport=5005)
    packet = ip/udp/data
    fid=pid & 0xffffffff

    frag=[]
    frag.append(IPv6ExtHdrFragment(nh=17, id=fid, m=0)/str(packet))

    return frag

generators = [
    udp_atom_fragments, 
]

if __name__ == "__main__":
    print "sending atomic fragments"
    print "from {} to {}".format(LOCAL_ADDR6, REMOTE_ADDR6)

    # construct a template v6 packet
    pid=os.getpid()
    eid=pid & 0xffff
    ip = IPv6(src=LOCAL_ADDR6, dst=REMOTE_ADDR6)
    fid=pid & 0xffffffff

    frag=[]
    for g in generators:
        for f in g(ip):
            frag.append(f)

    # bundle each packet(with a frag) into an ethernet frame
    eth=[]
    for f in frag:
            pkt=IPv6(src=LOCAL_ADDR6, dst=REMOTE_ADDR6)/f
            eth.append(Ether(src=LOCAL_MAC, dst=REMOTE_MAC)/pkt)

    sendp(eth, iface=LOCAL_IF)
