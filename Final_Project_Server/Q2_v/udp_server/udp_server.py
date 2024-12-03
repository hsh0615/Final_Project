import socket
import time

PROXY2_IP = "192.168.2.2"  # Proxy2 的 IP 地址
PROXY2_PORT = 5408  # Proxy2 的端口

def udp_server_q2():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        print("UDP Server (Q2) sending data to Proxy2...")
        for i in range(1, 11):  # 發送 1 到 10 次
            message = f"Packet {i}"
            server_socket.sendto(message.encode(), (PROXY2_IP, PROXY2_PORT))
            print(f"Sent to Proxy2: {message}")
            time.sleep(0.1)  # 傳輸間隔 100ms
            
if __name__ == "__main__":
    udp_server_q2()
