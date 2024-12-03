import socket
import time
import random
import select

# Proxy1 和 Proxy2 的 IP 和端口
PROXY1_IP = "192.168.2.2"
PROXY1_PORT = 5406
PROXY2_IP = "192.168.2.2" 
PROXY2_PORT = 5408

# Go-Back-N parameters
WINDOW_SIZE = 4
TIMEOUT = 1  # 1 second timeout

def udp_server():
    # 創建套接字用於發送數據和接收ACK
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        # 綁定接收端口
        server_socket.bind(('', 5401))
        server_socket.setblocking(False)
        print("UDP Server running...")

        # 先測試 Proxy1
        print("Testing Proxy1...")
        total_packets = 100
        base = 0  # 窗口起始位置
        next_seq_num = 0  # 下一個要發送的序號
        window = {}  # 存儲已發送但未確認的包
        
        while base < total_packets:
            # 發送窗口內的數據包
            while next_seq_num < min(base + WINDOW_SIZE, total_packets):
                packet = f"{next_seq_num},{time.time()}"
                server_socket.sendto(packet.encode(), (PROXY1_IP, PROXY1_PORT))
                window[next_seq_num] = {
                    'data': packet,
                    'time': time.time()
                }
                print(f"Sent packet {next_seq_num} to Proxy1")
                next_seq_num += 1
                time.sleep(0.1)  # 控制發送速率

            # 使用select監聽socket
            ready = select.select([server_socket], [], [], 0.1)
            
            if ready[0]:
                try:
                    data, addr = server_socket.recvfrom(1024)
                    message = data.decode()
                    
                    if message.startswith("ACK"):
                        ack_num = int(message.split(",")[1])
                        print(f"Received ACK for packet {ack_num} from client")
                        # 收到ACK，移動窗口
                        while base <= ack_num:
                            if base in window:
                                del window[base]
                            base += 1
                            
                    elif message.startswith("RESEND"):
                        print("Received RESEND request from client")
                        next_seq_num = base  # 重置發送序號
                        
                except socket.error:
                    pass
            
            # 檢查超時
            current_time = time.time()
            if window and base in window:
                if current_time - window[base]['time'] > TIMEOUT:
                    print(f"Timeout for packet {base}, resending window to Proxy1")
                    next_seq_num = base  # 重置發送序號

        # 測試 Proxy2
        print("\nTesting Proxy2...")
        total_packets = 100
        next_seq_num = 0

        while next_seq_num < total_packets:
            packet = f"{next_seq_num},{time.time()}"
            server_socket.sendto(packet.encode(), (PROXY2_IP, PROXY2_PORT))
            print(f"Sent packet {next_seq_num} to Proxy2")
            next_seq_num += 1
            time.sleep(0.1)  # 控制發送速率

if __name__ == "__main__":
    udp_server()
