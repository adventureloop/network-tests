#/usr/bin/env python2.7

import sys

import udp_options
import udp_usrreq

import packet_generators

# Test all UDP Options packet generators
if __name__ == "__main__":
    src = "192.168.0.1"
    dst = "192.168.0.1"

    if len(sys.argv) > 1:
        src = sys.argv[2]
    if len(sys.argv) > 2:
        dst = sys.argv[3]

    for generator in packet_generators.generators:
        opts = generator() 
        print(opts)
        udp_usrreq.udp_output("Hello Options Space on a packet\n", 
            {"src":src, "dst":dst, "sport":2500, "dport":2600}, 
            options=opts)
