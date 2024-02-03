#!/bin/bash

# Function to perform Nmap ping scan and filter live hosts
scan_live_hosts() {
    local target="$1"
    local output_file="${2:-live_hosts.txt}"

    # Run Nmap ping scan and filter IP addresses
    local ip_addresses=$(sudo nmap -sn "$target" | grep -oE '([0-9]{1,3}\.){3}[0-9]{1,3}')
    
    # Print IP addresses to the terminal
    echo "Live hosts:"
    echo "$ip_addresses"
    
    # Save IP addresses to the specified file
    sudo chmod 777 "$output_file"
    echo "$ip_addresses" > "$output_file"
    
    # Add necessary permissions to the output file


    echo "Live hosts saved to: $output_file"
}

# Check if the required arguments are provided
if [ $# -lt 1 ]; then
    echo "Usage: $0 <target_ip_or_range> [output_file]"
    exit 1
fi

# Call the function with supplied arguments
scan_live_hosts "$1" "$2"

