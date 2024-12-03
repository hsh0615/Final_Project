import socket

LISTEN_PORT = 5407  # Client 的監聽端口

def udp_client():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        client_socket.bind(("0.0.0.0", LISTEN_PORT))
        print(f"UDP Client listening on port {LISTEN_PORT}")

        for _ in range(10):  # 預期接收 10 個數據包
            data, addr = client_socket.recvfrom(1024)  # 接收數據
            print(f"Client received: {data.decode()} from {addr}")

if __name__ == "__main__":
    udp_client()
