import socket
import time

PROXY1_IP = "192.168.2.2"  # Proxy1 的 IP 地址
PROXY1_PORT = 5406  # Proxy1 的端口


def udp_server_q1():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        print("UDP Server (Q1) sending data to Proxy1...")
        for i in range(1, 11):  # 發送 1 到 10 次
            message = f"Packet {i}"
            server_socket.sendto(message.encode(), (PROXY1_IP, PROXY1_PORT))
            print(f"Sent to Proxy1: {message}")
            time.sleep(0.1)  # 傳輸間隔 100ms
            
if __name__ == "__main__":
    udp_server_q1()

