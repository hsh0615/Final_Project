import socket
import time

# Proxy1 和 Proxy2 的 IP 和端口
PROXY1_IP = "192.168.2.2"
PROXY1_PORT = 5406
PROXY2_IP = "192.168.2.2"
PROXY2_PORT = 5408

def udp_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        print("UDP Server running...")
        
        # 發送數據包
        for i in range(1, 100):  # 發送 1 到 10 次
            # 發送到 Proxy1 (Path1)
            message1 = f"Path1,Packet {i}"
            server_socket.sendto(message1.encode(), (PROXY1_IP, PROXY1_PORT))
            print(f"Sent to Proxy1: {message1}")

            # 發送到 Proxy2 (Path2)
            message2 = f"Path2,Packet {i}"
            server_socket.sendto(message2.encode(), (PROXY2_IP, PROXY2_PORT))
            print(f"Sent to Proxy2: {message2}")

            time.sleep(0.1)  # 傳輸間隔 100ms

        # # 傳送完成信號
        # completion_message = "COMPLETE"
        # server_socket.sendto(completion_message.encode(), (PROXY1_IP, PROXY1_PORT))
        # server_socket.sendto(completion_message.encode(), (PROXY2_IP, PROXY2_PORT))
        # print("Sent COMPLETE signal to Proxy1 and Proxy2")

if __name__ == "__main__":
    udp_server()
