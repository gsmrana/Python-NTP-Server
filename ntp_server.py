#!/usr/bin/env python3
"""
Simple NTP Server Implementation
This server responds to NTP client requests with the current system time.
"""

import socket
import struct
import time
import sys

# NTP packet format (48 bytes)
# First byte contains Leap Indicator (2 bits), Version (3 bits), and Mode (3 bits)
NTP_PACKET_FORMAT = "!B B B b 11I"
NTP_DELTA = 2208988800  # Offset between NTP epoch (1900) and Unix epoch (1970)

def system_to_ntp_time(timestamp):
    """Convert a system timestamp to NTP timestamp format."""
    return int(timestamp + NTP_DELTA)

def create_ntp_response(data):
    """
    Create an NTP response packet.
    
    Args:
        data: The received NTP request packet
        
    Returns:
        bytes: NTP response packet
    """
    # Unpack the request
    unpacked = struct.unpack(NTP_PACKET_FORMAT, data[0:struct.calcsize(NTP_PACKET_FORMAT)])
    
    # Get current time
    current_time = time.time()
    ntp_time = system_to_ntp_time(current_time)
    
    # Build response packet
    # LI (0), Version (4), Mode (4 = server)
    li_vn_mode = (0 << 6) | (4 << 3) | 4
    
    # Stratum (2 = secondary reference)
    stratum = 2
    
    # Poll interval (6 = 64 seconds)
    poll = 6
    
    # Precision (-20 = ~1 microsecond)
    precision = -20
    
    # Root delay and dispersion (0 for simplicity)
    root_delay = 0
    root_dispersion = 0
    
    # Reference identifier (fake GPS)
    ref_id = int.from_bytes(b'GPS\x00', byteorder='big')
    
    # Reference timestamp (when server clock was last set)
    ref_timestamp_int = ntp_time
    ref_timestamp_frac = int((current_time % 1) * 2**32)
    
    # Origin timestamp (from client request)
    origin_timestamp_int = unpacked[10]
    origin_timestamp_frac = unpacked[11]
    
    # Receive timestamp (when request arrived)
    recv_timestamp_int = ntp_time
    recv_timestamp_frac = int((current_time % 1) * 2**32)
    
    # Transmit timestamp (when response is sent)
    current_time = time.time()
    ntp_time = system_to_ntp_time(current_time)
    transmit_timestamp_int = ntp_time
    transmit_timestamp_frac = int((current_time % 1) * 2**32)
    
    # Pack the response
    response = struct.pack(
        NTP_PACKET_FORMAT,
        li_vn_mode,
        stratum,
        poll,
        precision,
        root_delay,
        root_dispersion,
        ref_id,
        ref_timestamp_int,
        ref_timestamp_frac,
        origin_timestamp_int,
        origin_timestamp_frac,
        recv_timestamp_int,
        recv_timestamp_frac,
        transmit_timestamp_int,
        transmit_timestamp_frac
    )
    
    return response

def run_ntp_server(host='0.0.0.0', port=123):
    """
    Run the NTP server.
    
    Args:
        host: Host address to bind to (default: 0.0.0.0 for all interfaces)
        port: Port to listen on (default: 123, standard NTP port)
    """
    # Create UDP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        # Bind to address and port
        server_socket.bind((host, port))
        print(f"NTP Server started on {host}:{port}")
        print("Waiting for NTP requests... (Press Ctrl+C to stop)")
        
        while True:
            try:
                # Receive data from client
                data, address = server_socket.recvfrom(1024)
                
                # Check if it's a valid NTP request (48 bytes minimum)
                if len(data) >= 48:
                    print(f"Received NTP request from {address[0]}:{address[1]}")
                    
                    # Create and send response
                    response = create_ntp_response(data)
                    server_socket.sendto(response, address)
                    print(f"Sent NTP response to {address[0]}:{address[1]}")
                else:
                    print(f"Received invalid packet from {address[0]}:{address[1]} (size: {len(data)} bytes)")
                    
            except Exception as e:
                print(f"Error handling request: {e}")
                continue
                
    except PermissionError:
        print(f"Error: Permission denied. Port {port} requires root/administrator privileges.")
        print("Try running with sudo (Linux/Mac) or as Administrator (Windows)")
        print("Or use a port > 1024, e.g., run_ntp_server(port=1123)")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nShutting down NTP server...")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)
    finally:
        server_socket.close()
        print("NTP Server stopped")

if __name__ == "__main__":
    # Note: Port 123 requires root/admin privileges
    # For testing without privileges, use a higher port like 1123
    port = 1123

    # Parse command line arguments
    if len(sys.argv) > 1:
        port = int(sys.argv[1])      
    
    run_ntp_server(port=port)
