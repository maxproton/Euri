import socket

def quick_port_scan(ip_address, ports):
    results = {}

    # Set a short timeout for quick scanning
    timeout = 0.5

    for port in ports:
        try:
            # Create a socket object
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # Set the timeout
                s.settimeout(timeout)
                # Attempt to connect
                result = s.connect_ex((ip_address, port))
                # Check the result: 0 means open
                if result == 0:
                    results[port] = "Open"
                else:
                    results[port] = "Closed"
        except Exception as e:
            results[port] = f"[Error] {e}"

    return results

