import asyncio
import time

from netpack.func import NetPack

ips = ['8.8.8.8', '8.8.8.9', '8.8.8.10', '8.8.8.11', '8.8.8.12', '8.8.8.13']
# ips = ['8.8.8.8']
while True:
    results = NetPack.multiple_ping(ips, 64, 'os', "icmp", 0.2, 1, 5)
    print(results)
    time.sleep(5)
