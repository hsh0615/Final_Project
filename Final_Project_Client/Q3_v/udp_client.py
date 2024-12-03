import socket
from collections import defaultdict

# 客戶端監聽的端口
PATH1_PORT = 5405  # 用於接收 Proxy1 (Path1) 的數據
PATH2_PORT = 5407  # 用於接收 Proxy2 (Path2) 的數據

# 初始化存儲和統計數據
received_packets = {"Path1": [], "Path2": []}
expected_packets = {"Path1": set(), "Path2": set()}  # 預期收到的數據包序號

# 初始化統計數據
stats = {
    "Path1": {"received": 0, "missing": 0},
    "Path2": {"received": 0, "missing": 0, "delayed": 0, "total_delay_time": 0.0},
}

def udp_client():
    # 為 Path1 和 Path2 分別創建套接字
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket1, \
         socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket2:
        
        client_socket1.bind(("0.0.0.0", PATH1_PORT))
        client_socket2.bind(("0.0.0.0", PATH2_PORT))
        print(f"UDP Client listening on ports {PATH1_PORT} (Path1) and {PATH2_PORT} (Path2)")

        try:
            while True:
                # 同時監聽兩個端口
                client_socket1.settimeout(0.1)
                client_socket2.settimeout(0.1)
                try:
                    data1, addr1 = client_socket1.recvfrom(1024)
                    process_packet("Path1", data1.decode())
                except socket.timeout:
                    pass

                try:
                    data2, addr2 = client_socket2.recvfrom(1024)
                    process_packet("Path2", data2.decode())
                except socket.timeout:
                    pass

        except KeyboardInterrupt:
            # 當用戶按下 Ctrl+C 時，停止接收並打印統計信息
            print("\nReception stopped. Calculating statistics...")
            print_statistics()

def process_packet(path, packet):
    global stats  # 使用全局變量 stats
    try:
        # 檢測是否延遲數據
        is_delayed = "DELAYED" in packet

        # 解析數據
        if is_delayed:
            packet_info, delay_time = packet.replace(",DELAYED", "").rsplit(",", 1)
            delay_time = float(delay_time)  # 提取延遲時間
        else:
            packet_info = packet
            delay_time = 0.0

        _, seq = packet_info.split(",Packet ")
        seq = int(seq)

        # 存儲接收到的數據包序號
        received_packets[path].append(seq)
        expected_packets[path].add(seq)

        # 更新統計數據
        stats[path]["received"] += 1
        if is_delayed and path == "Path2":
            stats[path]["delayed"] += 1
            stats[path]["total_delay_time"] += delay_time

        print(f"{path} received: {packet}")

    except Exception as e:
        print(f"Error processing packet on {path}: {e}")

def print_statistics():
    for path in received_packets:
        received_set = set(received_packets[path])
        expected_set = expected_packets[path]

        # 計算丟包數據
        total_expected = max(expected_set) if expected_set else 0
        missing_packets = total_expected - len(received_set)

        # 更新統計數據
        stats[path]["missing"] = missing_packets

        # 打印統計數據
        print(f"--- {path} Statistics ---")
        print(f"Total Expected: {total_expected}")
        print(f"Received: {stats[path]['received']}")
        print(f"Missing: {stats[path]['missing']}")
        print(f"Loss Rate: {(stats[path]['missing'] / total_expected) * 100:.2f}%")
        if path == "Path2":
            print(f"Delayed: {stats[path]['delayed']} packets")
            print(f"Total Delay Time: {stats[path]['total_delay_time']:.3f} seconds")
            if stats[path]['delayed'] > 0:
                print(f"Average Delay: {stats[path]['total_delay_time'] / stats[path]['delayed']:.3f} seconds")
        print("-----------------------")

if __name__ == "__main__":
    udp_client()
