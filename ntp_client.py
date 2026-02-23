#!/usr/bin/env python3
"""
Simple NTP Client
Test client to query an NTP server and display the time.
"""

import sys
import socket
import struct
import time
from datetime import datetime, timedelta


PRINT_NTP_PACKETS = True
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

NTP_PACKET_SIZE = 48
NTP_PACKET_FORMAT = "!B B B b 11I"
NTP_UNIX_OFFSET = 2208988800  # Offset between NTP epoch (1900) and Unix epoch (1970)
NTP_MAX_VALUE = (2**32)  # Maximum value for 32-bit unsigned integer


def get_current_unix_time_seconds():
    """Get the current time in seconds since the Unix epoch."""
    return time.time()

def unix_to_ntp_time_seconds(timestamp):
    """Convert a system timestamp to NTP timestamp format."""
    return int(timestamp + NTP_UNIX_OFFSET)

def ntp_to_unix_time_seconds(timestamp):
    """Convert NTP timestamp to system timestamp."""
    return int(timestamp - NTP_UNIX_OFFSET)

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
        0,           # Origin Timestamp (integer part)
        0,           # Origin Timestamp (fraction part)
        0,           # Receive Timestamp (integer part)
        0,           # Receive Timestamp (fraction part)
        int(unix_to_ntp_time_seconds(get_current_unix_time_seconds())), # Transmit Timestamp (integer part)
        0            # Transmit Timestamp (fraction part)
    )
    
    try:
        # Send request
        print(f"Querying NTP server at {host}:{port}...")
        if PRINT_NTP_PACKETS:
            print(f"NTP Request packet (hex): {data.hex()}")
        client.sendto(data, (host, port))
        
        # Receive response
        response, address = client.recvfrom(1024)
        
        if len(response) >= NTP_PACKET_SIZE:
            # Unpack response
            unpacked = struct.unpack(NTP_PACKET_FORMAT, response[0:struct.calcsize(NTP_PACKET_FORMAT)])
            
            # Extract transmit timestamp (when server sent the response)
            transmit_timestamp_int = unpacked[13]
            transmit_timestamp_frac = unpacked[14]
            
            # Convert to system time
            ntp_time = transmit_timestamp_int + (transmit_timestamp_frac / NTP_MAX_VALUE)
            system_time = ntp_to_unix_time_seconds(ntp_time)
            
            # Get local time for comparison
            local_time = get_current_unix_time_seconds()
            offset = system_time - local_time
            
            print(f"\nResponse from {address[0]}:{address[1]}")
            if PRINT_NTP_PACKETS:
                print(f"NTP Response packet (hex): {response.hex()}")

            print(f"NTP Time  : {datetime.fromtimestamp(system_time).strftime(DATETIME_FORMAT)}")
            print(f"Local Time: {datetime.fromtimestamp(local_time).strftime(DATETIME_FORMAT)}")
            print(f"Deviation : {timedelta(seconds=offset)} ({offset:.6f} seconds) {offset > 0 and 'ahead' or 'behind'} of local time")
            
            return datetime.fromtimestamp(system_time)
        else:
            print("Received invalid response")
            if PRINT_NTP_PACKETS:
                print(f"Invalid response data (hex): {response.hex()}")
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
    host = "localhost"
    port = 1123  # Default to non-privileged port
    
    # parse host
    if len(sys.argv) > 1:
        host = sys.argv[1]

    # parse port
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
         
    print(f"========== NTP Client ==========")
    get_ntp_time(host, port)
