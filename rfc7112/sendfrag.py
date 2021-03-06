#!/usr/local/bin/python2.7
import os
from addr import *
from scapy.all import *
import time

# ip in ip
def ip6_fragments(ip, split=16):
    packet = IPv6(src=LOCAL_ADDR6, dst=REMOTE_ADDR6)
    fid=pid & 0xffffffff

    frag=[]
    frag.append(IPv6ExtHdrFragment(nh=41, id=fid, m=1)/str(packet)[:split])
    frag.append(IPv6ExtHdrFragment(nh=41, id=fid, offset=2)/str(packet)[split:])

    return frag
"""
def ip6_ooo_fragments(ip):
    frags = ip6_fragments(ip)
    frags.reverse()
    return frags
"""

# ip4 in ip6
def ip4_fragments(ip, split=16):
    packet = IP(src="192.168.1.1", dst="192.168.40.1")
    fid=pid & 0xffffffff

    frag=[]
    frag.append(IPv6ExtHdrFragment(nh=4, id=fid, m=1)/str(packet)[:split])
    frag.append(IPv6ExtHdrFragment(nh=4, id=fid, offset=2)/str(packet)[split:])

    return frag

# ip4 in ip6
def ip4_opt_fragments(ip, split=24):
    packet = IP(src="192.168.1.1", dst="192.168.40.1", 
        options=IPOption('\x83\x03\x10\x83\x03\x10'))
    fid=pid & 0xffffffff

    frag=[]
    frag.append(IPv6ExtHdrFragment(nh=4, id=fid, m=1)/str(packet)[:split])
    frag.append(IPv6ExtHdrFragment(nh=4, id=fid, offset=2)/str(packet)[split:])

    return frag

def udp_fragments(ip, split=48, data="IAMSOMEPAYLOAD"):
    udp = UDP(sport=45234, dport=5005)
    packet = ip/udp/data
    fid=pid & 0xffffffff

    frag=[]
    frag.append(IPv6ExtHdrFragment(nh=17, id=fid, m=1)/str(packet)[40:split])
    frag.append(IPv6ExtHdrFragment(nh=17, id=fid, offset=2)/str(packet)[split:])

    return frag

def tcp_fragments(ip, split=56):
    tcp = TCP(sport=45234, dport=5005, flags='S', seq=1000)
    packet = ip/tcp
    fid=pid & 0xffffffff

    frag=[]
    frag.append(IPv6ExtHdrFragment(nh=6, id=fid, m=1)/str(packet)[40:split])
    frag.append(IPv6ExtHdrFragment(nh=6, id=fid, offset=2)/str(packet)[split:])

    return frag

def tcp_opt_fragments(ip, split=64):
    tcp = TCP(sport=45234, dport=5005, flags='S', seq=1000, 
        options=[("NOP", None), (19, "\xff\xff\xff\xff\xff\xff")])
    
    packet = ip/tcp
    fid=pid & 0xffffffff

    frag=[]
    frag.append(IPv6ExtHdrFragment(nh=6, id=fid, m=1)/str(packet)[40:split])
    frag.append(IPv6ExtHdrFragment(nh=6, id=fid, offset=3)/str(packet)[split:])

    return frag

def gre_fragments(ip, split=16):
    gre = GRE()
    packet = ip/gre

    fid=pid & 0xffffffff

    frag=[]
    frag.append(IPv6ExtHdrFragment(nh=6, id=fid, m=1)/str(packet)[40:split])
    frag.append(IPv6ExtHdrFragment(nh=6, id=fid, offset=2)/str(packet)[split:])

    return frag

generators = [
    ip6_fragments,
    ip4_fragments,
    ip4_opt_fragments,
    udp_fragments, 
    tcp_fragments, 
    tcp_opt_fragments, 
    gre_fragments,
]

if __name__ == "__main__":
    print "sending rfc7112 compliant and non compliant fragments"
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
