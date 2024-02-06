import socket
import struct
from typing import List
import time
from dataclasses import dataclass
import dataclasses
import random
from io import BytesIO



# DNS server information (Google's public DNS server)
DNS_SERVER_IP = '8.8.8.8'
DNS_SERVER_PORT = 53
TYPE_A = 1
CLASS_IN = 1



@dataclass
class DNSHeader:
    id: int
    flags: int
    qdcount: int = 0
    ancount: int = 0
    nscount: int = 0
    arcount: int = 0
        
@dataclass
class DNSQuestion:
    name: bytes
    type_: int 
    class_: int 
    
@dataclass
class DNSRecord:
    name: bytes
    type_: int
    class_: int
    ttl: int
    data: bytes
       
@dataclass
class DNSPacket:
    header: DNSHeader
    questions: List[DNSQuestion]
    answers: List[DNSRecord]
    authorities: List[DNSRecord]
    additionals: List[DNSRecord]
    
 
    
    

    
# Function to send a DNS query to the server
def send_dns_query(query_message):
    # Create a UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Set a timeout for receiving the response
    client_socket.settimeout(5)

    # Send the DNS query to the DNS server
    client_socket.sendto(query_message, (DNS_SERVER_IP, DNS_SERVER_PORT))

    return client_socket
  
    
# Function to receive and process the DNS response
def receive_and_process_response(client_socket):
    try:
        # Receive the DNS response
        response_message, server_address = client_socket.recvfrom(1024)
        
        #print(response_message)
        
        packet_reader = BytesIO(response_message)
        
        packet = dns_packet_parser(response_message)
        
        
        print("\n\n================HEADER======================")
        print("header.ID = ",hex(packet.header.id))
        print("header.QDCOUNT = ",packet.header.qdcount)
        print("header.ANCOUNT = ",packet.header.ancount)
        print("header.NSCOUNT = ",packet.header.nscount)
        print("header.ARCOUNT = ",packet.header.arcount)
        
        print("\n================QUESTION======================")
        print("question.QNAME = ",[question.name for question in packet.questions])
        print("question.QTYPE = ",[question.type_ for question in packet.questions])
        print("question.QCLASS = ",[question.class_ for question in packet.questions])
        
        
        print("\n================ANSWERS======================") 
        ans_no = 1
        for answer in packet.answers:
            if answer.type_ == 1:
                print(f"answer{ans_no}.NAME = ",answer.name)
                print(f"answer{ans_no}.TYPE = ",answer.type_)
                print(f"answer{ans_no}.CLASS = ",answer.class_)
                print(f"answer{ans_no}.TTL = ",answer.ttl)
                print(f"answer{ans_no}.DATA = ",rdata_to_ip(answer.data))
                print("\n")
                ans_no+=1
        print("AUTHORITIES = ",packet.authorities)
        print("ADDITIONALS = ",packet.additionals)
        
       
    except Exception as e:
    
        print(e)
        
       
# Function to convert a DNS header to binary format      
def get_header_bytes(header):
    fields = dataclasses.astuple(header)
    return struct.pack("!HHHHHH", *fields)

# Function to convert a DNS question to binary format
def get_question_bytes(question):
    return question.name + struct.pack("!HH", question.type_, question.class_)
    
# Function to build a DNS query packet  
def build_query(hostname, record_type):
    name = get_encoded_hostname(hostname)
    id = random.randint(0, 65535)
    RECURSION_DESIRED = 1 << 8
    header = DNSHeader(id=id, qdcount=1, flags=RECURSION_DESIRED)
    question = DNSQuestion(name=name, type_=record_type, class_=CLASS_IN)
    return get_header_bytes(header) + get_question_bytes(question)
   
# Function to encode a hostname into DNS-compliant binary format
def get_encoded_hostname(hostname):
    encoded = b""
    for segment in hostname.encode("ascii").split(b"."):
        encoded += bytes([len(segment)]) + segment
    return encoded + b"\x00"      
        
# Function to decode a DNS-encoded name
def simple_name_decoder(packet_reader):
    segments = []
    while (length := packet_reader.read(1)[0]) != 0:
        segments.append(packet_reader.read(length))
    return b".".join(segments)
      
# Function to parse a DNS header         
def header_parser(packet_reader):
    items = struct.unpack("!HHHHHH", packet_reader.read(12))
 
    return DNSHeader(*items)    

 
def question_parser(packet_reader):
    name = simple_name_decoder(packet_reader)
    data = packet_reader.read(4)
    type_, class_ = struct.unpack("!HH", data)
    return DNSQuestion(name, type_, class_)
    
def name_decoder(packet_reader):
    segments = []
    while (length := packet_reader.read(1)[0]) != 0:
        if length & 0b1100_0000:
            segments.append(compressed_name_decoder(length, packet_reader))
            break
        else:
            segments.append(packet_reader.read(length))
    return b".".join(segments)

# Function to decode a compressed DNS-encoded name
def compressed_name_decoder(length, packet_reader):
    pointer_bytes = bytes([length & 0b0011_1111]) + packet_reader.read(1)
    pointer = struct.unpack("!H", pointer_bytes)[0]
    current_position = packet_reader.tell()
    packet_reader.seek(pointer)
    result = name_decoder(packet_reader)
    packet_reader.seek(current_position)
    return result
    
# Function to parse a DNS resource record (answer, authority, or additional) 
def record_parser(packet_reader):
    name = name_decoder(packet_reader)
    data = packet_reader.read(10)
    type_, class_, ttl, data_len = struct.unpack("!HHIH", data)
    data = packet_reader.read(data_len)
    return DNSRecord(name, type_, class_, ttl, data)
    
# Function to parse a complete DNS packet from binary data    
def dns_packet_parser(data):
    packet_reader = BytesIO(data)
    header = header_parser(packet_reader)
    questions = [question_parser(packet_reader) for _ in range(header.qdcount)]
    answers = [record_parser(packet_reader) for _ in range(header.ancount)]
    authorities = [record_parser(packet_reader) for _ in range(header.nscount)]
    additionals = [record_parser(packet_reader) for _ in range(header.arcount)]

    return DNSPacket(header, questions, answers, authorities, additionals)    

 # Function to parse an IP address in rdata
def rdata_to_ip(ip):
    return ".".join([str(x) for x in ip])
    
               
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python my-dns-client.py <hostname>")
        sys.exit(1)

    hostname = sys.argv[1]

    print("Preparing DNS query...")
    dns_query = build_query(hostname,TYPE_A)

    print("Contacting DNS server...")
    retry_count = 0

    while retry_count < 3:
        try:
            print(f"Sending DNS query (attempt {retry_count + 1} of 3)...")
            client_socket = send_dns_query(dns_query)

            print("Processing DNS response...")
            receive_and_process_response(client_socket)
            break
        except:
            retry_count += 1
            time.sleep(5)  # Wait for 5 seconds before retrying

    if retry_count == 3:
        print("Max retry count reached. DNS query failed.")   

