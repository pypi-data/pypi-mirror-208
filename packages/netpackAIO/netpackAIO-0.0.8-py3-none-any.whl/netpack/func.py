import threading
from bs4 import BeautifulSoup
import requests
import ipaddress
import socket
import struct
import random
from contextlib import closing
import platform
import subprocess
import re
import time


class NetPack(object):
    class ServerLocation(object):
        AFRINIC = 'whois.afrinic.net'
        ARIN = 'whois.arin.net'
        APNIC = 'whois.apnic.net'
        LACNIC = 'whois.lacnic.net'
        RIPE_NCC = 'whois.ripe.net'
        IANA = 'whois.iana.org'
        RADB = 'https://www.radb.net/query?keywords='

    FLAG_HELP = """
        For query_flags
        ARIN: https://www.arin.net/resources/registry/whois/rws/cli/#using-flags
        AFRINIC: https://www.afrinic.net/support/whois/manual
        APNIC: https://www.apnic.net/manage-ip/using-whois/searching/query-options/
        RIPR_NCC: https://apps.db.ripe.net/docs/13.Types-of-Queries/
        LACNIC & IANA, no specific instructions
    """
    WHOIS_PORT = 43
    SOCKET_TIMEOUT = 5

    @staticmethod
    def is_valid_ipv4(ip: str) -> bool:
        try:
            ipaddress.IPv4Address(ip)
            return True
        except ipaddress.AddressValueError:
            return False

    @staticmethod
    def is_valid_ipv6_address(ipv6: str) -> bool:
        try:
            ipaddress.IPv6Address(ipv6)
            return True
        except ipaddress.AddressValueError:
            return False

    @staticmethod
    def is_cidr_ipv4(cidr_str: str) -> bool:
        try:
            ipaddress.IPv4Network(cidr_str, strict=False)
            return True
        except ValueError:
            return False

    @staticmethod
    def inr(server: str, ipv4v6: str, query_flags: str = None) -> str:

        try:
            # Establish a TCP connection to the whois server
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(NetPack.SOCKET_TIMEOUT)
            s.connect((server, NetPack.WHOIS_PORT))

            # Send the query string and receive the response
            s.sendall((query_flags if query_flags else '' + ' ' + ipv4v6 + ' \r\n').encode('utf-8'))

            # Receive the response from the WHOIS server
            response = b''
            while True:
                data = s.recv(1024)
                if not data:
                    break
                response += data
            s.close()
        except Exception as e:
            return e.__str__()

            # Print the response
        return response.decode('utf-8')

    @staticmethod
    def radb(ip):
        # Make a request to the webpage
        url = NetPack.ServerLocation.RADB + ip
        response = requests.get(url)

        # Parse the HTML content
        soup = BeautifulSoup(response.content, "html.parser")

        # Find the title tag and extract its text
        radb_information_meta = soup.find_all("pre")

        # You can extract the information by below code.
        radb_information = ''
        for item in radb_information_meta:
            radb_information += item.text + '\r\r\n\n'

        return radb_information

    @staticmethod
    def _calculate_checksum(data):
        # Calculate the number of 16-bit words in the data
        count_to = (len(data) // 2) * 2
        total = 0
        count = 0

        # Iterate through each pair of bytes (16 bits) in the data
        while count < count_to:
            # Combine the two bytes into a single 16-bit word
            this_val = data[count + 1] * 256 + data[count]
            # Add the 16-bit word to the running total
            total += this_val
            # Ensure the total doesn't exceed 32 bits
            total &= 0xffffffff
            # Move to the next pair of bytes
            count += 2

        # If there's an odd number of bytes, add the last byte to the total
        if count_to < len(data):
            total += data[len(data) - 1]
            total &= 0xffffffff

        # Fold the 32-bit total into 16 bits by adding the high 16 bits to the low 16 bits
        total = (total >> 16) + (total & 0xffff)
        total += (total >> 16)

        # Take the one's complement of the final 16-bit total
        answer = ~total
        # Ensure the answer doesn't exceed 16 bits
        answer &= 0xffff

        return answer

    @staticmethod
    def _icmp_ping_os(host, packet_size, interval, timeout, packet_num):
        # Sends ICMP echo requests to the specified host and returns the average latency and success rate as a tuple

        # Determine the operating system
        system = platform.system()

        if system == 'Windows':
            # For Windows
            command = ['ping', '-n', str(packet_num), '-l', str(packet_size), '-w', str(int(timeout * 1000)), host]
            output = subprocess.run(command, capture_output=True, text=True)
            result = output.stdout
        elif system == 'Darwin':
            # For macOS
            command = ['ping', '-c', str(packet_num), '-s', str(packet_size), '-i', str(interval), '-t', str(timeout),
                       host]
            output = subprocess.run(command, capture_output=True, text=True)
            result = output.stdout
        elif system == 'Linux':
            # For Linux
            command = ['ping', '-c', str(packet_num), '-s', str(packet_size), '-i', str(interval), '-W', str(timeout),
                       host]
            output = subprocess.run(command, capture_output=True, text=True)
            result = output.stdout
        else:
            raise OSError(f"Unsupported operating system: {system}")

        # Parse the ping result to calculate average latency and success rate
        latency_sum = 0
        received_count = 0
        lines = result.split('\n')
        for line in lines:
            if 'time=' in line:
                try:
                    latency = float(re.search(r'time=([0-9.]+)', line).group(1))
                    latency_sum += latency
                    received_count += 1
                except (ValueError, AttributeError):
                    pass

        average_latency = (latency_sum / received_count) if received_count > 0 else None
        success_rate = (received_count / packet_num) * 100

        return average_latency, success_rate

    @staticmethod
    def _icmp_ping_sock(host, packet_size, interval, timeout, packet_num):
        # Sends ICMP echo requests to the specified host and returns the average latency and success rate as a tuple
        if packet_size < 8:
            packet_size = 8
        payload = b'\x00' * (packet_size-8)
        icmp_protocol = socket.getprotobyname("icmp")
        icmp_echo = 8
        packet_id = random.randint(1, 0xffff)
        packet = struct.pack("!BBHHH", icmp_echo, 0, 0, packet_id, 1) + payload
        # Adds the ICMP checksum to the packet
        packet = struct.pack("!BBHHH", icmp_echo, 0, socket.htons(NetPack._calculate_checksum(packet)), packet_id, 1) + payload

        sent_count = 0
        received_count = 0
        total_latency = 0

        # Sends 10 ICMP echo requests
        for _ in range(packet_num):
            # Creates a raw socket for sending ICMP packets
            with closing(socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp_protocol)) as sock:
                # Sets the timeout for the socket
                sock.settimeout(timeout)
                # Sends the ICMP packet to the specified host
                sock.sendto(packet, (host, 1))

                # Records the start time and counts the packets being sent out.
                sent_count += 1
                start_time = time.time()

                try:
                    # Receives the ICMP response from the host
                    _, addr = sock.recvfrom(1024)
                    end_time = time.time()
                    # Calculates the latency and counts the received packets
                    received_count += 1
                    total_latency += end_time - start_time
                except socket.timeout:
                    # If no response is received within the timeout period, ignores the packet
                    pass

                # Waits for the specified interval before sending the next packet
                time.sleep(max(0, interval - (time.time() - start_time)))

        # Calculates the average latency and success rate
        return (total_latency / received_count) * 1000 if received_count > 0 else None, received_count / sent_count * 100

    @staticmethod
    def _tcp_ping(host, packet_size, interval, timeout, packet_num):
        # Initialize variables to keep track of packets sent, received and total latency
        sent_count = 0
        received_count = 0
        total_latency = 0

        # Create a TCP socket object and set the timeout
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)

            # Loop through the packet_num iterations to send packets to the target host
            for _ in range(packet_num):
                # Increment the packet counter and record the start time
                sent_count += 1
                start_time = time.time()

                # Construct the TCP ACK packet
                tcp_header = struct.pack('!HHIIBBHHH', 12345, 0, 0, 0, 5, 16, 8192, 0, 0)
                tcp_header += b'\x00' * (packet_size - len(tcp_header))

                # Set the ACK flag in the TCP header
                tcp_header = struct.pack('!BBHI', tcp_header[0], 0x10, 0, 12345) + tcp_header[4:]

                # Calculate the checksum for the packet
                ip_header = struct.pack('!BBHHHBBH4s4s', 69, 0, len(tcp_header) + 20, 12345, 0, 64, 6, 0,
                                        socket.inet_aton('127.0.0.1'), socket.inet_aton(host))
                checksum = NetPack._calculate_checksum(ip_header + tcp_header)
                tcp_header = tcp_header[:16] + struct.pack('H', checksum) + tcp_header[18:]

                try:
                    # Send the packet to the target host on port 80
                    sock.sendto(tcp_header, (host, 80))

                    # Wait for the response packet
                    response_packet, addr = sock.recvfrom(packet_size)

                    # Record the end time and calculate the latency
                    end_time = time.time()
                    received_count += 1
                    total_latency += end_time - start_time
                # Handle timeout and socket error exceptions
                except socket.timeout:
                    pass
                    # print(f"Socket timeout occurred.")
                except socket.error as e:
                    print(f"Socket error occurred: {e}")

                # Wait for the specified interval time before sending the next packet
                time.sleep(max(0, interval - (time.time() - start_time)))

        # Calculate the average latency and packet loss percentage and return as a tuple
        return (total_latency / received_count) * 1000 if received_count > 0 else None, received_count / sent_count * 100

    @staticmethod
    def ping(host, ping_type='os', packet_size=64, protocol="icmp", interval=0.5, timeout=1, packet_num=5):
        # Try to get address information for the given host
        try:
            socket.getaddrinfo(host, None, socket.AF_INET6)
            address_family = socket.AF_INET6  # Use IPv6 address family if available
        except socket.gaierror:
            address_family = socket.AF_INET  # Otherwise, use IPv4 address family

        # Depending on the protocol, call the corresponding ping function
        if protocol.lower() == "icmp":
            # ICMP protocol is only supported for IPv4
            if address_family == socket.AF_INET6:
                raise ValueError("ICMP is not supported for IPv6 addresses in this implementation.")
            if ping_type == 'sock':
                return NetPack._icmp_ping_sock(host, packet_size, interval, timeout, packet_num)
            else:
                return NetPack._icmp_ping_os(host, packet_size, interval, timeout, packet_num)
        elif protocol.lower() == "tcp":
            # Use TCP protocol for both IPv4 and IPv6
            return NetPack._tcp_ping(host, packet_size, interval, timeout, packet_num)
        else:
            # Raise an error if an unsupported protocol is given
            raise ValueError("Unsupported protocol. Please use 'icmp' or 'tcp'.")

    @staticmethod
    def multiple_ping(hosts, ping_type='os', packet_size=64, protocol="icmp", interval=0.5, timeout=1, packet_num=5):
        multiping_results = {}

        # Define a function to ping a host and store the result in the results dictionary
        def ping_host(ip):

            latency, success_rate = NetPack.ping(ip, ping_type, packet_size, protocol, interval, timeout, packet_num)
            multiping_results[ip] = {'success_rate': success_rate, 'latency': latency}

        # Create a thread for each host and start them all simultaneously
        threads = []
        for host in hosts:
            t = threading.Thread(target=ping_host, args=(host,))
            threads.append(t)
            t.start()

        # Wait for all threads to finish before returning the results dictionary
        for t in threads:
            t.join()

        return multiping_results
