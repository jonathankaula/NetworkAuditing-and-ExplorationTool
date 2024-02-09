from scapy.all import ARP, Ether, srp

def arp_mac_scan(ip):
    arp_request = ARP(pdst=ip)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")  # Broadcast MAC address

    arp_broadcast = ether/arp_request
    print(f"ARP BROADCAST PACKET: {arp_request}")
    answered_list = srp(arp_broadcast, timeout=1, verbose=False)[0]

    devices = []
    for element in answered_list:
        device = {"ip": element[1].psrc, "mac": element[1].hwsrc}
        devices.append(device)
    return devices

if __name__ == "__main__":
    target_ip = "192.168.88.246/24"  # Adjust this to your network range

    print("Scanning...")
    devices_found = arp_mac_scan(target_ip)
    print("Devices found:")
    for device in devices_found:
        print(f"IP: {device['ip']}\tMAC: {device['mac']}")
