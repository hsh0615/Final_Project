import socket
import random

LISTEN_PORT = 5406  # Proxy1 的監聽端口
CLIENT_IP = "192.168.2.2"
CLIENT_PORT = 5405  # 轉發到 Client 的端口
DROP_RATE = 0.1  # 丟包率 10%

def udp_proxy1():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as proxy_socket:
        proxy_socket.bind(("0.0.0.0", LISTEN_PORT))
        print(f"Proxy1 (Path1) listening on port {LISTEN_PORT}")

        while True:
            data, addr = proxy_socket.recvfrom(1024)  # 接收來自 Server 的數據
            if data.decode() == "COMPLETE":
                # 傳遞完成信號
                proxy_socket.sendto(data, (CLIENT_IP, CLIENT_PORT))
                print("Proxy1 received COMPLETE and forwarded to Client")
                #break  # 可選：結束 Proxy 運行
            if random.random() < DROP_RATE:
                # 模擬丟包
                print(f"Proxy1 dropped packet: {data.decode()} from {addr}")
                continue
            # 正常轉發到 Client
            proxy_socket.sendto(data, (CLIENT_IP, CLIENT_PORT))
            print(f"Proxy1 forwarded: {data.decode()} to {CLIENT_IP}:{CLIENT_PORT}")

if __name__ == "__main__":
    udp_proxy1()
