# SPDX-License-Identifier: BSD-2-Clause-FreeBSD
# 
# Copyright (c) 2018 Tom Jones <tj@enoti.me>
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

from scapy.all import IP
from scapy.all import UDP 
from scapy.all import *

import udp_options

listening = {}

def internetchecksum(pkt):
    if len(pkt) % 2 != 0:
        a = bytearray(pkt)
        a.append(0)
        pkt = bytes(a) # python is such a cluster fuck

    databytes = struct.unpack("!{}H".format(int(len(pkt)/2)), pkt)
    total = 0
    for b in databytes:
        total = total + b

    while total > 0xFFFF:
        high = 0xFFFF0000 & total
        low = 0x0000FFFF & total

        high = high >> 16

        total = low + high
    return total ^ 0xFFFF

def udpchksum(src, dst, sprt, dprt, data):
    sourceaddr = str(bytearray([ int(x) for x in src.split(".")]))
    destaddr = str(bytearray([ int(x) for x in dst.split(".")]))
    proto = 17
    udplen = 8 + len(data)
    sport = sprt
    dport = dprt
    cksum = 0

    pkt = struct.pack("!4s4sBBHHHHH{}s".format(len(data)),
	sourceaddr, destaddr,
	0, proto, udplen,
	sport, dport,
	udplen, cksum,
	data)

    return internetchecksum(pkt)

def udp_output(data, pcb, options=None):
    ip = IP(src=pcb['src'], dst=pcb['dst'])
    udp = UDP(sport=pcb['sport'], dport=pcb['dport'])

    optpkt = ip/udp/data
    optpkt.getlayer(1).len = len(optpkt.getlayer(1)) #force UDP len

    chksum = optpkt[UDP].chksum #capture correct checksum
    udplen = optpkt[UDP].len    #capture correct length
    #udplen = len(data) + 8

    if options != None:
        optbuf = udp_options.udp_addoptions(options)
        optpkt = (optpkt/str(optbuf))

    optpkt.getlayer(1).chksum = udpchksum(pcb['src'],pcb['dst'], pcb['sport'],
	pcb['dport'], data)
    optpkt.getlayer(1).len = udplen

    print("output: data {} udplen {} optlen {}".format(len(data), udplen, len(optbuf)))
    send(optpkt)

def udp_input(pkt):
    ip = pkt[IP]
    udp = pkt[UDP]
    options = None

    print("ip len {}, udp len {}".format(ip.len, udp.len))
    if ip.len != udp.len+20:
        print(pkt.show())
        pay = pkt[Raw].load
        opt = pkt[Padding].load
        options = udp_options.udp_dooptions(bytearray(opt)) 

        print("udp len {}, options len {}".format(len(pay), len(opt)))
        print(options)

        print("here")
        if 'UDPOPT_ECHORES' in options:
            print("and here")
            reqtoken = options['UDPOPT_ECHORES']

            resopt = {
                'UDPOPT_TIME': (0x11223344, 0x55667788),
                'UDPOPT_ECHORES':reqtoken
            }
            udp_output("",
                {'src':ip.dst,'dst':ip.src,'sport':udp.dport,'dport':udp.sport}, 
                options=resopt)
    else:
        print("no options")

    pcb_hdr = (ip.dst, udp.dport)
    if pcb_hdr in listening:
        proc = listening[pcb_hdr]
        proc['callback'](proc, data, options)

def icmp_input(pkt):
    icmp = pkt[ICMP]
    if icmp.type == 3:
        ip = pkt['IP in ICMP']
        udp = pkt['UDP in ICMP']

        pcb_hdr = (ip.src, udp.sport)
        if pcb_hdr in listening:
            proc = listening[pcb_hdr]
            proc['callback'](proc, data, options, 
                {'type':icmp.type, 'code':icmp.code})
        print("ICMP Packet type {} code {}".format(icmp.type, icmp.code))
    else:
        print("ICMP Packet type {} code {}".format(icmp.type, icmp.code))

def pkt_input(pkt=None):
    if ICMP in pkt:
        icmp_input(pkt)
    if UDP in pkt:
        udp_input(pkt)

def run_loop():
    sniff(prn= lambda x: pkt_input(x), filter="icmp or (udp and port 2500)")

def bindaddr(addr, port, cb):
    pcb_hdr = (addr, port)
    if not pcb_hdr in listening:
        listening[pcb_hdr] = cb
        return pcb_hdr
    else:
        return None

if __name__ == "__main__":
    run_loop()
    print("All done!")
