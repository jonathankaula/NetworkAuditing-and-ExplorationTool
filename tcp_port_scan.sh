#!/bin/bash

# Function to perform Nmap scan and filter open ports
scan_and_filter_ports() {
    local target="$1"
    local output_file="${2:-open_ports.txt}"

    # Run Nmap scan and filter open ports
    open_ports=$(sudo nmap -sS -sV "$target" | grep -E '^PORT\s+STATE\s+SERVICE\s+VERSION$|^[0-9]+/tcp.*open.*|Service Info:')
    
     # Print Open Ports to terminal
    echo "Open Ports:"
    echo "$open_ports"
    
    
    # Save open ports to the specified file
    sudo touch "$output_file"
    sudo chmod 777 "$output_file"
    echo "$open_ports" > "$output_file"
    
    echo "Open_ports information saved to: $output_file"
}

# Check if the required arguments are provided
if [ $# -lt 1 ]; then
    echo "Usage: $0 <target_ip> [output_file]"
    exit 1
fi

# Call the function with supplied arguments
scan_and_filter_ports "$1" "$2"

