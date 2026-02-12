# NTP Server in Python

A simple Network Time Protocol (NTP) server and client implementation in Python.

## Source Scripts

- `ntp_server.py` - The NTP server implementation
- `ntp_client.py` - A test client to query NTP servers

## Port Information

- **Port 123**: Standard NTP port (requires root/administrator privileges)
- **Port 1123**: Alternative port for testing without privileges

## Usage

### Running the Server

```bash
uv run ntp_server.py 1123
```

### Running the Client

```bash
uv run ntp_client.py localhost 1123
```

## How It Works

### NTP Protocol Basics

1. **NTP Packet**: 48 bytes containing timestamps and server information
2. **Timestamps**: 
   - Reference: When the server's clock was last set
   - Origin: Client's transmit time (from request)
   - Receive: When server received the request
   - Transmit: When server sent the response

3. **NTP Epoch**: Starts at January 1, 1900 (vs Unix epoch of January 1, 1970)

### Server Behavior

The server:
- Listens on UDP port 123 (or 1123 for non-root)
- Receives NTP requests
- Responds with current system time in NTP format
- Maintains proper NTP packet structure

### Client Behavior

The client:
- Sends an NTP request packet
- Receives the response
- Extracts the server's transmit timestamp
- Displays the time and calculates offset from local time

## Example Output

### Server:
```
NTP Server started on 0.0.0.0:1123
Waiting for NTP requests... (Press Ctrl+C to stop)
Received NTP request from 127.0.0.1:54321
Sent NTP response to 127.0.0.1:54321
```

### Client:
```
NTP Client Test
===============
Querying NTP server at localhost:1123...

Response from 127.0.0.1:1123
NTP Time: 2026-01-28 14:30:45.123456
Local Time: 2026-01-28 14:30:45.123450
Offset: 0.000006 seconds
```

## Testing with System NTP Client

You can also test the server using system NTP tools:

**Linux/macOS:**
```bash
ntpdate -q -p 1 localhost -u 1123
```

**Windows:**
```cmd
w32tm /stripchart /computer:localhost /dataonly /samples:1
```

## Linux Systemd Service

Create a systemd service

```
uv sync
sudo cp script/myntp-server.service /etc/systemd/system/myntp-server.service
sudo systemctl daemon-reload
sudo systemctl restart myntp-server.service
```

## Limitations

- Basic implementation for educational purposes
- Does not implement full NTP synchronization algorithms
- Clock discipline and filtering not implemented
- Stratum level is fixed at 2
- No authentication support

## Notes

- The server responds with the system's current time
- For production use, consider using established NTP servers like `ntpd` or `chronyd`
- This implementation is suitable for learning and local testing
