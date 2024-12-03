import socket

LISTEN_PORT = 5406  # Proxy1 的監聽端口
CLIENT_IP = "192.168.2.2"  # Client 的 IP 地址
CLIENT_PORT = 5405  # Client 的端口

def udp_proxy1():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as proxy_socket:
        proxy_socket.bind(("0.0.0.0", LISTEN_PORT))
        print(f"Proxy1 listening on port {LISTEN_PORT}")

        while True:
            data, addr = proxy_socket.recvfrom(1024)  # 接收來自 Server 的數據
            print(f"Proxy1 received: {data.decode()} from {addr}")
            proxy_socket.sendto(data, (CLIENT_IP, CLIENT_PORT))  # 轉發給 Client
            print(f"Proxy1 forwarded: {data.decode()} to {CLIENT_IP}:{CLIENT_PORT}")

if __name__ == "__main__":
    udp_proxy1()
