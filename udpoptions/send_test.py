import udp_options
import udp_usrreq

if __name__ == "__main__":
    opts = { 'UDPOPT_TIME': (0x11223344, 0x55667788), 
             'UDPOPT_MSS': 0x1122,
             'UDPOPT_ECHOREQ':0xabcd,
             'UDPOPT_ECHORES':0xabcd
    }
    udp_usrreq.udp_output("Hello Options Space on a packet\n", 
        {"src":"10.0.0.1", "dst":"10.0.1.1", "sport":2500, "dport":2600}, 
        options=opts)
