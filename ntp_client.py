#!/usr/bin/env python3
"""
Simple NTP Client
Test client to query an NTP server and display the time.
"""

import socket
import struct
import time
from datetime import datetime


NTP_PACKET_FORMAT = "!B B B b 11I"
NTP_UNIX_OFFSET = 2208988800  # Offset between NTP epoch (1900) and Unix epoch (1970)

def get_modular_delta(t_new, t_old, modulus=2**32):
    """
    Calculates the signed difference (t_new - t_old) 
    accounting for a single 32-bit overflow.
    """
    diff = t_new - t_old

    if diff > modulus / 2:
        diff -= modulus
    elif diff < -modulus / 2:
        diff += modulus
        
    return diff

def get_current_unix_time_seconds():
    """Get the current time in seconds since the Unix epoch."""
    return time.time()

def ntp_to_unix_time_seconds(timestamp):
    """Convert NTP timestamp to system timestamp."""
    return timestamp - NTP_UNIX_OFFSET

def unix_to_ntp_time_seconds(timestamp):
    """Convert NTP timestamp to system timestamp."""
    return timestamp + NTP_UNIX_OFFSET

def get_ntp_time(host='localhost', port=123):
    """
    Query an NTP server and get the time.
    
    Args:
        host: NTP server address
        port: NTP server port
        
    Returns:
        datetime: The time from the NTP server
    """
    # Create UDP socket
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(5)
    
    # Create NTP request packet
    # LI (0), Version (4), Mode (3 = client)
    li_vn_mode = (0 << 6) | (4 << 3) | 3
    
    # Build request (48 bytes, mostly zeros)
    data = struct.pack(
        NTP_PACKET_FORMAT,
        li_vn_mode,  # LI, Version, Mode
        0,           # Stratum
        0,           # Poll
        0,           # Precision
        0,           # Root Delay
        0,           # Root Dispersion
        0,           # Reference ID
        0,           # Reference Timestamp (integer part)
        0,           # Reference Timestamp (fraction part)
        int(get_current_unix_time_seconds() + NTP_UNIX_OFFSET),  # Origin Timestamp (integer part)
        0,           # Origin Timestamp (fraction part)
        0,           # Receive Timestamp (integer part)
        0,           # Receive Timestamp (fraction part)
        0,           # Transmit Timestamp (integer part)
        0            # Transmit Timestamp (fraction part)
    )
    
    try:
        # Send request
        print(f"Querying NTP server at {host}:{port}...")
        client.sendto(data, (host, port))
        
        # Receive response
        response, address = client.recvfrom(1024)
        
        if len(response) >= 48:
            # Unpack response
            unpacked = struct.unpack(NTP_PACKET_FORMAT, response[0:struct.calcsize(NTP_PACKET_FORMAT)])
            
            # Extract transmit timestamp (when server sent the response)
            t0 = unpacked[9]
            t1 = unpacked[11]
            t2 = unpacked[13]
            t3 = unix_to_ntp_time_seconds(get_current_unix_time_seconds())
            
            
            # Convert to system time
            
            # Get local time for comparison
            t1_t0 = get_modular_delta(t1, t0)
            t2_t3 = get_modular_delta(t2, t3)
            offset = (t1_t0 + t2_t3)/2
            
            print(f"\nResponse from {address[0]}:{address[1]}")
            print(f"t0: {t0}, t1: {t1}, t2: {t2}, t3: {t3}")
            local_time = get_current_unix_time_seconds()
            system_time = local_time + offset
            print(f"NTP Time: {datetime.fromtimestamp(system_time).strftime('%Y-%m-%d %H:%M:%S.%f')}")
            print(f"Local Time: {datetime.fromtimestamp(local_time).strftime('%Y-%m-%d %H:%M:%S.%f')}")
            print(f"Offset: {offset:.6f} seconds")
            
            return datetime.fromtimestamp(system_time)
        else:
            print("Received invalid response")
            return None
            
    except socket.timeout:
        print("Request timed out")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        client.close()
        

if __name__ == "__main__":
    import sys
    host = "localhost"
    port = 1123  # Default to non-privileged port
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        host = sys.argv[1]

    if len(sys.argv) > 2:
        port = int(sys.argv[2])
         
    print(f"NTP Client Test")
    print(f"===============")
    get_ntp_time(host, port)
