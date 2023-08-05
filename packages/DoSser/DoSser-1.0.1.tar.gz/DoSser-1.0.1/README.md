
# DoSser

A layer 4 python-based denial of service command line utility.


## Usage/Examples
The program can be installed using pip and ran from a terminal.
```python
sudo pip install DoSser
```
```python
Dosser.py -t TARGET -p PORT -th Threads -a Attack LIMIT LIMIT_VALUE
```



## Features

- Windows/UNIX/MacOS support
- 8 Different attack modes
- Limit the attack by time or packets
- Live packet count


## Configuration options
DoSser's behaviour can be modified with the use of command-line arguments. To get an up-to-date list of all arguments use ``` DoSser --help  ```.

- -t, --target - The IP address of the target
- -p, --port
- th. --threads
- -a, --attack

Users are also required to select a limiter for there chosen attack.

- packet
- time

## Attacks
DoSser has support for a variety of layer 4 denial of service attacks.

- [ICMP flood](https://www.cloudflare.com/en-gb/learning/ddos/ping-icmp-flood-ddos-attack/)
- [SYN flood](https://www.cloudflare.com/en-gb/learning/ddos/syn-flood-ddos-attack/)
- [UDP flood](https://www.cloudflare.com/en-gb/learning/ddos/udp-flood-ddos-attack/)
- [Land attack](https://www.imperva.com/learn/ddos/land-attacks/)
- [Ping of death](https://www.cloudflare.com/en-gb/learning/ddos/ping-of-death-ddos-attack/)
- [TCP PUSH-ACK attack](https://www.cloudflare.com/en-gb/learning/ddos/what-is-an-ack-flood/)
- [Teardrop attack](https://www.okta.com/identity-101/teardrop-attack/) 
## Requirements
Users will need an installation of [Colorama](https://pypi.org/project/colorama/) and [Scapy](https://scapy.readthedocs.io/en/latest/index.html) this can be retrieved from pip using.

```
pip install colorama
```

and

```
pip install scapy
```

## License
This is code is licensed under the 
[MIT License](https://choosealicense.com/licenses/mit/)

