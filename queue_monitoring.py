#TODO: pep8
import socket
import sys
import cisco
import time
import re

STATSD_SERVER_IP = sys.argv[1]
STATSD_PORT = 8125
STATSD_SERVER = (STATSD_SERVER_IP,STATSD_PORT)

hostname = socket.gethostname()
statsd_socket = cisco.CiscoSocket(socket.AF_INET,socket.SOCK_DGRAM)
queue_command = "show queuing interface"
interface_name = re.compile("^Ethernet(\d{1}/\d{1,2}).*")
qos_group = re.compile(".*?qos-group (\d{1}).*?")
pkt_received = re.compile(".*?Pkts received over the port             : (\d+).*?")
pkt_sent = re.compile(".*?Pkts sent to the port                   : (\d+).*?")
pkt_discard = re.compile(".*?Pkts discarded on ingress               : (\d+).*?")

def send_queue_info(port,qg,action,counter):
    port = port.replace('/','-')
    #TODO: replace + with join()[if possible]
    port = 'Ethernet' + port
    msg = hostname + '-' + port + '-qg' + qg + '-' + action
    #statsd gauge
    msg = msg+':'+counter+'|g'
    statsd_socket.sendto(msg,STATSD_SERVER)

while True:
    output = cisco.CLI(queue_command).get_output()
#    output = output.get_output()
    for line in output:
        if interface_name.match(line):
            interface = interface_name.findall(line)[0]
        elif qos_group.match(line):
            qg = qos_group.findall(line)[0]
        elif pkt_received.match(line):
            counter = pkt_received.findall(line)[0]
            send_queue_info(interface,qg,'received',counter)
        elif pkt_sent.match(line):
            counter = pkt_sent.findall(line)[0]
            send_queue_info(interface,qg,'sent',counter)
        elif pkt_discard.match(line):
            counter = pkt_discard.findall(line)[0]
            send_queue_info(interface,qg,'discard',counter)
    time.sleep(3)
statsd_socket.close()
