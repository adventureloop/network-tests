#!/usr/local/bin/python2.7
import os
from addr import *
from scapy.all import *
import time

def generate_fragments(generator, ip):
    nh, payload, split = generator(ip)
    packet = ip/payload
    fid=pid & 0xffffffff

    frags = []
    frags.append(IPv6ExtHdrFragment(nh=nh, id=fid, m=1)/str(packet)[:split])
    frags.append(IPv6ExtHdrFragment(nh=nh, id=fid, offset=1)/str(packet)[split:])

    return frags

def dccp_packet(sport, dport, ext):
    pkt = None

    if ext:
        pkt = bytearray(16)
    else:
        pkt = bytearray(12)

    struct.pack_into("!H", pkt, 0, sport)
    struct.pack_into("!H", pkt, 2, dport)
    if ext:
        pkt[8] = 0x80

    return bytes(pkt)

def dccp_short_packet(ip, split=8):
   return 33, dccp_packet(0x1234, 0x5678, False), split

def dccp_long_packet(ip, split=8):
   return 33, dccp_packet(0xabcd, 0xef90, True), split     

generators = [
    dccp_short_packet,
    dccp_long_packet,
]

if __name__ == "__main__":
    print "sending rfc7112 compliant and non compliant fragments"
    print "from {} to {}".format(LOCAL_ADDR6, REMOTE_ADDR6)

    # construct a template v6 packet
    pid = os.getpid()
    fid = pid & 0xffffffff
    ip = IPv6(src=LOCAL_ADDR6, dst=REMOTE_ADDR6)

    fragments = []

    for g in generators:
        frags = generate_fragments(g, ip)

        for f in frags:
            fragments.append(f)

        frags.reverse()

        for f in frags:
            fragments.append(f)

    # bundle each packet(with a frag) into an ethernet frame
    eth=[]
    for f in fragments:
            pkt=IPv6(src=LOCAL_ADDR6, dst=REMOTE_ADDR6)/f
            eth.append(Ether(src=LOCAL_MAC, dst=REMOTE_MAC)/pkt)

    eth.append(Ether(src=LOCAL_MAC, dst=REMOTE_MAC)/IPv6(src=LOCAL_ADDR6, dst=REMOTE_ADDR6, nh=33)/ dccp_packet(0xedba, 0x4321, True))

    sendp(eth, iface=LOCAL_IF)
