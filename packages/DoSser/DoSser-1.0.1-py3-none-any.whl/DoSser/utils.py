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

dead = False


def set_dead():
    """
    Method to set the global variable dead to True this is used as a flag to end all the threads in the attack.
    """
    global dead
    dead = True


def send_packets(attack_packet, num_threads, limit_value, limit_choice):
    """
   Sends the packets from hosts device as well as handling the limits set by the user.

   Parameters:
   attack_packet (string): The packet to be used in the attack
   num_threads (int): The number of threads used in the attack used to calculate packets sent.
   limit_value (int): The value of the limiter chosen by the user.
   limit_choice (string): The limiter the user wants to use.
   """

    global dead
    packet_count = 0

    if limit_choice == "packet":
        while (packet_count < limit_value) and not dead:
            send(attack_packet, verbose=0)
            packet_count += 1
            sys.stdout.write(f"\r[+] Estimated packets sent {packet_count * num_threads} packets.")
            sys.stdout.flush()

    if limit_choice == "time" and limit_value == 0:
        while not dead:
            send(attack_packet, verbose=0)
            packet_count += 1
            sys.stdout.write(f"\r[+] Estimated packets sent {packet_count * num_threads} packets.")
            sys.stdout.flush()

    if limit_choice == "time":
        start_time = time.time()
        while (time.time() - start_time < limit_value) and not dead:
            send(attack_packet, verbose=0)

            packet_count += 1
            sys.stdout.write(f"\r[+] Estimated packets sent {packet_count * num_threads} packets.")
            sys.stdout.flush()

    sys.stdout.write(f"\r[+] Attack finished packets sent {packet_count * num_threads} packets. Press enter to exit.")
    sys.stdout.flush()

    sys.exit(0)


def thread_packets(attack_packet, num_threads, limit_choice, limit_value):
    """
    Handles the creation of threads for the attack as well as the logic for terminating all threads.

    Parameters:
    attack_packet (string): The packet to be used in the attack. Passed to send_packets.
    num_threads (int): The number of threads to create.
    limit_value (int): The value of the limiter chosen by the user.Passed to send_packets.
    limit_choice (string): The limiter the user wants to use. Passed to send_packets.
    """

    global dead
    dead = False  # Flag variable for threads

    print("[+] " + str(num_threads) + " Threads created")
    print("[+] Press enter to end the attack. Current limit conditions (" + limit_choice + " " + str(limit_value) + ").")

    for i in range(num_threads):  # create required amount of threads
        th = threading.Thread(target=send_packets, args=(attack_packet, num_threads, limit_value, limit_choice))
        th.start()

    input()  # Allows user to press enter to end the attack at any stage should they wish
    set_dead()


def get_my_ip():
    """
    Used to grab the hosts source IP for required attacks.

    Returns:
    string The hosts source IP.
    """

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Create socket object
    s.connect(("8.8.8.8", 80))  # Connect to the Google DNS server at IP address 8.8.8.8 and port 80
    return s.getsockname()[0]  # Retrieve the IP address of the local end of the socket and return
