import socket

DNS_RECORDS_FILE = 'dns_records.txt'

def load_records():
    """Loads DNS records from file"""
    try:
        with open(DNS_RECORDS_FILE, 'r') as f:
            records = {}
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split()
                    if len(parts) >= 3 and parts[0] == 'TYPE=A':
                        # Parse: TYPE=A NAME=hostname VALUE=IP TTL=10
                        name = None
                        value = None
                        ttl = None
                        for part in parts[1:]:
                            if part.startswith('NAME='):
                                name = part.split('=')[1]
                            elif part.startswith('VALUE='):
                                value = part.split('=')[1]
                            elif part.startswith('TTL='):
                                ttl = part.split('=')[1]
                        if name and value:
                            records[name] = {'value': value, 'ttl': ttl}
            return records
    except FileNotFoundError:
        return {}

def save_record(name, value, ttl):
    """Saves a DNS record"""
    with open(DNS_RECORDS_FILE, 'a') as f:
        f.write(f"TYPE=A NAME={name} VALUE={value} TTL={ttl}\n")

def handle_dns_request(data, addr, sock):
    """Handles DNS requests"""
    try:
        request = data.decode().strip()
        lines = request.split('\n')
        
        # Check if it is a registration or a query
        if 'VALUE=' in request:  # It is a registration
            name = None
            value = None
            ttl = None
            for line in lines:
                if line.startswith('NAME='):
                    name = line.split('=')[1]
                elif line.startswith('VALUE='):
                    value = line.split('=')[1]
                elif line.startswith('TTL='):
                    ttl = line.split('=')[1]
            
            if name and value and ttl:
                save_record(name, value, ttl)
                print(f"Registered: {name} -> {value}")
                return  # No response for registration
        else:  # It is a DNS query
            name = None
            for line in lines:
                if line.startswith('NAME='):
                    name = line.split('=')[1]
            
            if name:
                records = load_records()
                if name in records:
                    record = records[name]
                    response = (
                        f"TYPE=A\n"
                        f"NAME={name} VALUE={record['value']} TTL={record['ttl']}"
                    )
                    sock.sendto(response.encode(), addr)
                    print(f"Query resolved: {name} -> {record['value']}")
    except Exception as e:
        print(f"Error handling request: {e}")

def main():
    """Starts the DNS server"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', 53533))
    
    print("Authoritative Server listening on port 53533...")
    
    try:
        while True:
            data, addr = sock.recvfrom(1024)
            handle_dns_request(data, addr, sock)
    except KeyboardInterrupt:
        print("Server stopped")
    finally:
        sock.close()

if __name__ == '__main__':
    main()