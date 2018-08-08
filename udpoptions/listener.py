import udp_options
import udp_usrreq

def callback(pcb, data=None, options=None, error=None):
    print(pcb)

if __name__ == "__main__":
    print("startings")
    udp_usrreq.bindaddr('0.0.0.0', 5005, callback)        
    udp_usrreq.run_loop()
