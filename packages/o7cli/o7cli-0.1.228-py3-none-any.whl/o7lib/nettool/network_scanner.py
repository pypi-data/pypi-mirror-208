# COMMENTED OUT BECAUSE IT CREATE LINT ERRORS FOR RELEASE, TO BE MOVED
#""" Ip scanner module """
# import subprocess
# import argparse
# import re

# import scapy.all as scapy


# def scan(ip):

#     arp_request = scapy.ARP(pdst=ip)
#     broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
#     arp_request_broadcast = broadcast / arp_request

#     scapy.srp(arp_request_broadcast, timeout=1, verbose=True)

#     answered, unanswered = scapy.srp(arp_request_broadcast, timeout=1.0, verbose=False)

#     print(answered)
#     print(answered.summary())
#     # print(unanswered)

#     # clients_list = []
#     # for element in answered_list:
#     #     client_dict = {"ip": element[1].psrc, "mac": element[1].hwsrc}
#     #     clients_list.append(client_dict)
#     # return clients_list

# if __name__ == '__main__':

#     scan('192.168.25.1/24')
