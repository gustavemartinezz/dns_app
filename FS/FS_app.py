from flask import Flask, request, jsonify
import socket

app = Flask(__name__)

# Stores the server information
server_info = {
    'hostname': None,
    'ip': None,
    'as_ip': None,
    'as_port': None
}

@app.route('/register', methods=['PUT'])
def register():
    """Registers the server with the authoritative server"""
    try:
        data = request.get_json()
        
        server_info['hostname'] = data.get('hostname')
        server_info['ip'] = data.get('ip')
        server_info['as_ip'] = data.get('as_ip')
        server_info['as_port'] = int(data.get('as_port'))
        
        # Send the DNS registration to the authoritative server
        if register_with_as():
            return jsonify({"status": "registered"}), 201
        else:
            return jsonify({"error": "Registration failed"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

def register_with_as():
    """Sends the DNS registration via UDP to the authoritative server"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        registration = (
            f"TYPE=A\n"
            f"NAME={server_info['hostname']} "
            f"VALUE={server_info['ip']} "
            f"TTL=10"
        )
        
        sock.sendto(registration.encode(), 
                   (server_info['as_ip'], server_info['as_port']))
        sock.close()
        return True
    except Exception as e:
        print(f"Registration error: {e}")
        return False

@app.route('/fibonacci', methods=['GET'])
def fibonacci():
    """Calculates and returns the Fibonacci number"""
    try:
        number = request.args.get('number')
        
        # Verify that it is an integer
        try:
            number = int(number)
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid number format"}), 400
        
        if number < 0:
            return jsonify({"error": "Number must be positive"}), 400
        
        # Calculate Fibonacci
        result = calculate_fibonacci(number)
        
        return jsonify({
            "sequence_number": number,
            "fibonacci_number": result
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

def calculate_fibonacci(n):
    """Calculates the nth Fibonacci number"""
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090)