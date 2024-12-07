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
            results[port] = f"Error: {e}"

    return results

def save_results_to_json(ip_address, scan_results, port_mapping, folder):
    """
    Saves port scan results to a JSON file named after the IP address.

    :param ip_address: IP address of the target as a string
    :param scan_results: Dictionary of port scan results (port: status)
    :param port_mapping: Dictionary of port mappings (port: description)
    """
    # Build the results in a structured format
    results = {
        "ip_address": ip_address,
        "ports": []
    }

    for port, status in scan_results.items():
        if status == "Open":
            port_info = {
                "port": port,
                "status": status,
                "description": port_mapping.get(port, "Unknown service")
            }
            results["ports"].append(port_info)

    # Define the JSON file name based on the IP address
    json_file_name = f"{ip_address}.json"

    # Save the results to the JSON file
    try:
        with open(json_file_name, 'w', encoding='utf-8') as json_file:
            json.dump(results, json_file, indent=4)
        print(f"Results saved to {json_file_name}")
    except Exception as e:
        print(f"Failed to save results to {json_file_name}: {e}")
