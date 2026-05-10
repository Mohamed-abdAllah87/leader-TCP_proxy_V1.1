import sys
import socket
import threading


HEX_FILTER = ''.join([(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range(256)])

def hexdump(src, length=16, show=True):
    if isinstance(src, bytes):
        src = src.decode(errors='replace')

    results = list()
    for i in range(0, len(src), length):
        word = str(src[i:i+length])
        printable = word.translate(HEX_FILTER)
        hexa = ' '.join([f'{ord(c):02x}' for c in word])
        hexwidth = length * 3
        results.append(f'{i:04x}  {hexa:<{hexwidth}}  {printable}')

    if show:
        for line in results:
            print(line)
    else:
        return results

def receive_from(connection):
    buffer = b""
    connection.settimeout(10) 
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except Exception:
        pass
    return buffer



def request_handler(buffer):
   

    if b"User-Agent:" in buffer:
        print("[*] Intercepted User-Agent. Modifying to iPhone (iOS 17)...")
        
        iphone_ua = b"User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
        
        
        buffer = buffer.replace(b"Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0", iphone_ua)
    
    return buffer

def response_handler(buffer):
    

    return buffer

### -------------------------------------------------------

def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)
        remote_buffer = response_handler(remote_buffer)
        if len(remote_buffer):
            print(f"[<==] Sending {len(remote_buffer)} bytes to localhost.")
            client_socket.send(remote_buffer)

    while True:
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            print(f"[==>] Received {len(local_buffer)} bytes from localhost.")
            hexdump(local_buffer)

            
            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print("[==>] Sent to remote.")

        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            print(f"[<==] Received {len(remote_buffer)} bytes from remote.")
            hexdump(remote_buffer)

            
            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print("[<==] Sent to localhost.")

        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections.")
            break

def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
    except Exception as e:
        print(f"[!!] Failed to listen on {local_host}:{local_port}. Error: {e}")
        sys.exit(0)

    print(f"[*] Listening on {local_host}:{local_port}")
    server.listen(5)

    while True:
        client_socket, addr = server.accept()
        print(f"[>] Received connection from {addr[0]}:{addr[1]}")
        proxy_thread = threading.Thread(
            target=proxy_handler,
            args=(client_socket, remote_host, remote_port, receive_first)
        )
        proxy_thread.start()

def main():
    if len(sys.argv[1:]) != 5:
        print("Usage: ./leader_proxy.py [localhost] [localport] [remotehost] [remoteport] [receive_first]")
        sys.exit(0)

    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])
    receive_first = sys.argv[5].lower() == 'true'

    server_loop(local_host, local_port, remote_host, remote_port, receive_first)

if __name__ == '__main__':
    main()
