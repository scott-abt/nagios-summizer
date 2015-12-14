#!/usr/bin/env python

"""
Print out JSON of all down hosts for the itstatus page.
Reqires Nagios & mk-livestatus
Tested on RHEL6 & python 2.6

author:
sgardne@uark.edu
"""

from __future__ import division
from json import encoder
import socket

import cgitb
cgitb.enable()
print("Content-Type: text/html\n\n")

def get_sock_info(request):
    sock_path = '/var/spool/nagios/cmd/live'
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    sock.connect(sock_path)
    sock.send(request)
    sock.shutdown(socket.SHUT_WR)
    result = sock.recv(10000000)
    result_list = [ line.split(';') for line in result.split('\n')[:-1] ]
    return result_list

try:

    host_list = get_sock_info("GET hosts\nColumns: host_name state\n")
    down_list = get_sock_info("GET hosts\nFilter: state != 0\nColumns: "
            "host_name state\n")

    total_down = float(len(down_list))
    total_hosts = float(len(host_list))

    percent = 100 - (total_down / total_hosts * 100)

    message = ""

    if int(percent) == 100:
        message = 'All connections are available'
    else:
        message = str(int(total_down))
        if int(total_down) == 1:
            message += " connection is unavailable"
        else:
            message += " connections are unavailable"

    # Print JSON string including host names and % up.

    enc = encoder.JSONEncoder(sort_keys=True)
    
    down_list = ([ {"host": name} for (name, value) in down_list ])
    message_dict = {'health': percent, 'down': down_list, 'message': message}
    print(enc.encode(message_dict))
    
except Exception as e:
    print("There was a problem {0}".format(e))

