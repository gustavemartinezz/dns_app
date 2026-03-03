from flask import Flask, request, jsonify
import socket
import requests

app = Flask(__name__)

@app.route('/fibonacci', methods=['GET'])
def fibonacci():
    # Get the parameters
    hostname = request.args.get('hostname')
    fs_port = request.args.get('fs_port')
    number = request.args.get('number')
    as_ip = request.args.get('as_ip')
    as_port = request.args.get('as_port')
    
    # Verify that all parameters are present
    if not all([hostname, fs_port, number, as_ip, as_port]):
        return jsonify({"error": "Missing parameters"}), 400
    
    try:
        number = int(number)
    except ValueError:
        return jsonify({"error": "Invalid number format"}), 400
    
    # Step 1: Make a DNS query to the authoritative server
    fs_ip = dns_query(hostname, as_ip, int(as_port))
    if not fs_ip:
        return jsonify({"error": "DNS lookup failed"}), 400
    
    # Step 2: Request the Fibonacci number from the FS server
    try:
        response = requests.get(f"http://{fs_ip}:{fs_port}/fibonacci?number={number}")
        if response.status_code == 200:
            result = response.json()
            return jsonify(result), 200
        else:
            return jsonify({"error": "FS error"}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 400

def dns_query(hostname, as_ip, as_port):
    """Sends a DNS query via UDP to the authoritative server"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        query = f"TYPE=A\nNAME={hostname}"
        sock.sendto(query.encode(), (as_ip, as_port))
        
        data, _ = sock.recvfrom(1024)
        response = data.decode()
        
        # Parse the response: "TYPE=A\nNAME=hostname VALUE=IP TTL=10"
        for line in response.split('\n'):
            if line.startswith('VALUE='):
                ip = line.split('=')[1]
                return ip
        return None
    except Exception as e:
        print(f"DNS query error: {e}")
        return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)