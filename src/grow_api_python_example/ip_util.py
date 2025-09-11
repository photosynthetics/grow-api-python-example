import ipaddress
import logging
import socket
from typing import List
from concurrent.futures import ThreadPoolExecutor
import psutil


def is_socket_open_single(ip: str, port: int, timeout : float = 0.1) -> bool:
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        #logging.error(f"Socket connection refused or timed out")
        return False
    except Exception as e:
        logging.error(f"Error checking socket: {e}")
        return False
    
def is_socket_open_multiple(ips : List[str], port:int, timeout: float)-> List[str]:
    try:
        results = None
        open_ips= []
        with ThreadPoolExecutor(max_workers=50) as executor:
            results= list(executor.map(lambda ip: is_socket_open_single(ip, port, timeout), ips))
        open_ips = [ip for ip, is_open in zip(ips, results) if is_open]
        return open_ips
    except Exception as e:
        return []



def get_ip_addresses_on_same_subnet(subnet: str, start: int = 0, end: int = 255) -> List[str]:
    ip_addresses = []
    for i in range(start, end + 1):
        host = f"{subnet}.{i}"
        ip_addresses.append(host)
    return ip_addresses

def get_current_network(interface_filter: str) -> str:
    # Get network interface details
    net_if_addrs = psutil.net_if_addrs()
    net_if_stats = psutil.net_if_stats()
    
    # Check if the specified interface exists
    if interface_filter and interface_filter not in net_if_addrs:
        raise ValueError(f"Interface {interface_filter} not found")
    
    # Iterate through network interfaces
    for interface, addrs in net_if_addrs.items():
        # Skip interfaces that don't match the filter (if provided)
        if interface_filter and interface != interface_filter:
            continue
        
        # Check if the interface is up
        if net_if_stats[interface].isup:
            for addr in addrs:
                if addr.family == socket.AF_INET:  # Check for IPv4
                    ip_address = addr.address
                    netmask = addr.netmask
                    # Calculate the subnet
                    network = ipaddress.ip_network(f'{ip_address}/{netmask}', strict=False)
                    return str(network)
    
    raise Exception("No active network interfaces found or interface does not have an IPv4 address")

def try_get_subnet() -> str:
    subnet = get_current_subnet("eth0")
    if subnet and subnet != "":
        return subnet
    subnet = get_current_subnet("Wi-Fi")
    if subnet and subnet != "":
        return subnet
    return ""

def get_current_subnet(interface : str)-> str:
    try:
        current_network = get_current_network(interface)
        current_subnet = current_network.split('/')[0][:-2]
        return current_subnet
    except Exception as e:  
        logging.error(f"Error getting current subnet: {e}")
        return ""
