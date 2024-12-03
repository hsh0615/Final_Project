import socket
import random
import time

LISTEN_PORT = 5408  # Proxy2 的監聽端口
CLIENT_IP = "192.168.2.2"
CLIENT_PORT = 5407  # 轉發到 Client 的端口
DELAY_RATE = 0.05  # 延遲概率 50%
DELAY_TIME = 0.5  # 延遲時間 500 毫秒

def udp_proxy2():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as proxy_socket:
        proxy_socket.bind(("0.0.0.0", LISTEN_PORT))
        print(f"Proxy2 (Path2) listening on port {LISTEN_PORT}")

        while True:
            data, addr = proxy_socket.recvfrom(1024)  # 接收來自 Server 的數據
                #break  # 可選：結束 Proxy 運行
            if random.random() < DELAY_RATE:
                # 模擬延遲並加標記
                delay_start = time.time()
                time.sleep(DELAY_TIME)
                delay_time = time.time() - delay_start  # 計算實際延遲時間
                delayed_data = f"{data.decode()},DELAYED,{delay_time:.3f}"
                proxy_socket.sendto(delayed_data.encode(), (CLIENT_IP, CLIENT_PORT))
                print(f"Proxy2 delayed {delay_time:.3f}s and forwarded: {delayed_data}")
            else:
                # 正常轉發數據
                proxy_socket.sendto(data, (CLIENT_IP, CLIENT_PORT))
                print(f"Proxy2 forwarded: {data.decode()} to {CLIENT_IP}:{CLIENT_PORT}")

if __name__ == "__main__":
    udp_proxy2()
