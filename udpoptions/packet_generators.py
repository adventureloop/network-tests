#/usr/bin/env python2.7

#
# Packet Generators for use with scapy tests.
# The udp_options libraries handle making the option space most of the time.
#

import udp_options
import udp_usrreq

# - option space with invalid options               
# todo

# option space with valid options (OCS, NOP, EOL) 
def generate_option_space_with_valid_options():
    return  {}

# - option space with:                              
#        - OCS                                     
#                - passing                         
#                - failing                         

def generate_options_space_with_ocs_passing():
    return {}

def generate_options_space_with_ocs_failing():
    return {}

# TIME                                    
def generate_options_space_with_time(tsval=0x11223344, tsecr=0x55667788):
    return {
        'UDPOPT_TIME': (tsval, tsecr)
        }

# MSS                                     
#   default = 1500
def generate_options_space_with_mss(mss=0x05dc):
    return {
        'UDPOPT_MSS': mss,
        }

# REQ                                     
def generate_options_space_with_req(token=0x1234):
    return {
        'UDPOPT_ECHOREQ': token,
        }

# RES                                     
def generate_options_space_with_res(token=0x5678):
    return {
        'UDPOPT_ECHORES': token,
        }

# REQ and RES
def generate_options_space_with_req_and_res(reqtoken=0x1234, restoken=0x5678):
    return {
        'UDPOPT_ECHOREQ': reqtoken,
        'UDPOPT_ECHORES': restoken,
        }

##### Not Implemented yet
#        - ACS                                     
#                - passing                         
#                - failing                         
#        - Lite*                                   
#        - Frag*                                   
#        - AE*                                     
def generate_options_space_with_any_option(mss=0x05dc, tsval=0x11223344,
    tsecr=55667788, reqtoken=0x1234, restoken=5678):
    return {
        'UDPOPT_MSS': mss,
        'UDPOPT_TIME': (tsval, tsecr),
        'UDPOPT_ECHOREQ': reqtoken
        }

# TIME MSS REQ                            
def generate_options_space_with_time_mss_and_req(mss=0x05dc, tsval=0x11223344,
    tsecr=55667788, reqtoken=0x1234):
        return generate_options_space_with_any_option(restoken=None)

# TIME MSS REQ RES                        
def generate_options_space_with_time_mss_req_and_res():
        return generate_options_space_with_any_option()

generators = [
    generate_option_space_with_valid_options,
    generate_options_space_with_ocs_passing,
    generate_options_space_with_ocs_failing,
    generate_options_space_with_time,
    generate_options_space_with_mss,
    generate_options_space_with_req,
    generate_options_space_with_res,
    generate_options_space_with_req_and_res,
    generate_options_space_with_any_option,
    generate_options_space_with_time_mss_and_req,
    generate_options_space_with_time_mss_req_and_res
]
