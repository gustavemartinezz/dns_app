import socket

DNS_RECORDS_FILE = 'dns_records.txt'

def load_records():
    try:
        with open(DNS_RECORDS_FILE, 'r') as f:
            records = {}
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split()
                    name = value = ttl = None
                    for part in parts:
                        if part.startswith('NAME='):
                            name = part.split('=', 1)[1]
                        elif part.startswith('VALUE='):
                            value = part.split('=', 1)[1]
                        elif part.startswith('TTL='):
                            ttl = part.split('=', 1)[1]
                    if name and value:
                        records[name] = {'value': value, 'ttl': ttl or '10'}
            return records
    except FileNotFoundError:
        return {}

def save_record(name, value, ttl):
    with open(DNS_RECORDS_FILE, 'a') as f:
        f.write(f"TYPE=A NAME={name} VALUE={value} TTL={ttl}\n")

def handle_dns_request(data, addr, sock):
    try:
        request = data.decode().strip()
        name = value = ttl = None
        for part in request.split():
            if part.startswith('NAME='):
                name = part.split('=', 1)[1]
            elif part.startswith('VALUE='):
                value = part.split('=', 1)[1]
            elif part.startswith('TTL='):
                ttl = part.split('=', 1)[1]

        if value:  # Registration
            save_record(name, value, ttl or '10')
            print(f"Registered: {name} -> {value}")
        else:  # Query
            records = load_records()
            if name in records:
                record = records[name]
                response = f"TYPE=A\nNAME={name} VALUE={record['value']} TTL={record['ttl']}"
                sock.sendto(response.encode(), addr)
                print(f"Query resolved: {name} -> {record['value']}")
    except Exception as e:
        print(f"Error: {e}")

def main():
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
