import socket
import threading
import time

class UDPClient:
    def __init__(self):
        # 創建socket用於接收path1數據
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('192.168.2.2', 5405))
        
        # 創建socket用於接收path2數據
        self.socket2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket2.bind(('192.168.2.2', 5407))
        
        # 用於追蹤接收到的封包
        self.received_packets = {}  # {seq: client_timestamp}
        self.received_packets2 = {}  # {seq: client_timestamp}
        self.total_packets = 100
        self.start_time = None  # path1開始時間
        self.start_time2 = None  # path2開始時間
        self.lock = threading.Lock()
        self.lock2 = threading.Lock()
        self.received_complete = False
        
        # 新增：期望收到的下一個序號
        self.expected_seq = 0
        
        # Server 地址
        self.server_addr = ('192.168.2.3', 5401)
        
        # 新增統計相關變數
        self.end_time = None  # path1結束時間
        self.end_time2 = None  # path2結束時間
        self.dropped_packets = 0  # 掉包數量
        self.retransmission_count = 0  # 重傳次數
        self.retransmission_time = 0  # 重傳總時間
        
        self.delayed_packets = {}  # 新增：記錄延遲包的延遲時間
    def start(self):
        # 創建path1接收線程
        receive_thread = threading.Thread(target=self.receive_packets)
        receive_thread.daemon = True
        receive_thread.start()
        
        # 創建path2接收線程
        receive_thread2 = threading.Thread(target=self.receive_packets2)
        receive_thread2.daemon = True
        receive_thread2.start()
        
        # 等待線程完成
        receive_thread.join()
        receive_thread2.join()
    
    def receive_packets(self):
        while len(self.received_packets) < self.total_packets:  # 修改終止條件
            try:
                data, addr = self.socket.recvfrom(1024)
                current_time = time.time()
                message = data.decode()
                
                # 解析封包
                seq, _ = message.split(',')  # 忽略server的timestamp
                seq = int(seq)
                
                with self.lock:
                    # 記錄第一個封包的接收時間
                    if seq == 0 and self.start_time is None:
                        self.start_time = current_time
                        
                    # 只接受期望序號的包
                    if seq == self.expected_seq:
                        self.received_packets[seq] = current_time
                        print(f"Path1 received packet {seq}")
                        
                        # 更新期望序號
                        self.expected_seq += 1
                        
                        # 發送 ACK 給 Server
                        ack_message = f"ACK,{seq}".encode()
                        self.socket.sendto(ack_message, self.server_addr)
                        print(f"Path1 sent ACK for packet {seq}")
                        
                        # 檢查是否已接收完所有封包
                        if len(self.received_packets) == self.total_packets:
                            self.end_time = current_time
                            self.print_statistics()
                    
                    # 如果收到亂序包
                    elif seq > self.expected_seq:
                        print(f"Path1 out-of-order packet {seq} received, expected {self.expected_seq}")
                        self.dropped_packets += 1  # 記錄掉包
                        
                        # 發送 ACK 給 Server
                        ack_message = f"ACK,{self.expected_seq - 1}".encode()
                        self.socket.sendto(ack_message, self.server_addr)
                        print(f"Path1 sent ACK for last in-order packet {self.expected_seq - 1}")
                        
                        # 發送重傳請求給 Server
                        resend_message = f"RESEND,{self.expected_seq}".encode()
                        self.socket.sendto(resend_message, self.server_addr)
                        self.retransmission_count += 1  # 記錄重傳次數
                        print(f"Path1 sent RESEND request for packet {self.expected_seq}")
                        
                        # 添加超時重傳機制
                        self.start_resend_timer(self.expected_seq)
            
            except Exception as e:
                print(f"Error receiving packet on path1: {e}")

    def receive_packets2(self):
        while len(self.received_packets2) < self.total_packets:
            try:
                data, addr = self.socket2.recvfrom(1024)
                current_time = time.time()
                message = data.decode()
                
                # 解析封包
                parts = message.split(',')
                seq = int(parts[0])
                
                with self.lock2:
                    # 記錄第一個封包的接收時間
                    if seq == 0 and self.start_time2 is None:
                        self.start_time2 = current_time
                        
                    self.received_packets2[seq] = current_time
                    if "DELAYED" in message:
                        delay_time = float(parts[3])
                        self.delayed_packets[seq] = delay_time  # 記錄延遲時間
                        print(f"Path2 received delayed packet {seq} with delay {delay_time:.3f}s")
                    else:
                        print(f"Path2 received packet {seq}")
                        
                    if len(self.received_packets2) == self.total_packets:
                        self.end_time2 = current_time
                        self.print_statistics2()
                        
            except Exception as e:
                print(f"Error receiving packet on path2: {e}")

    # 新增：超時重傳機制
    def start_resend_timer(self, seq):
        def resend_request():
            # 如果在超時時間後還沒收到這個序號的包，就再次發送重傳請求
            time.sleep(0.5)  # 500ms 超時
            with self.lock:
                if seq == self.expected_seq:  # 確認是否仍然需要這個包
                    resend_message = f"RESEND,{seq}".encode()
                    self.socket.sendto(resend_message, self.server_addr)
                    print(f"Path1 timeout: Resent RESEND request for packet {seq}")
        
        # 啟動超時計時器
        timer_thread = threading.Thread(target=resend_request)
        timer_thread.daemon = True
        timer_thread.start()
    
    def print_statistics(self):
        # 使用client端的時間計算總傳輸時間
        total_time = self.end_time - self.start_time
        transmission_cost = (self.total_packets - 1) * 0.1  # 100ms = 0.1s
        actual_delay = total_time - transmission_cost
        
        print("\n=== Path1 傳輸統計 ===")
        print(f"總傳輸時間: {total_time:.3f} 秒")
        print(f"實際延遲時間: {actual_delay:.3f} 秒")
        print(f"掉包數量: {self.dropped_packets} 個")
        print(f"重傳次數: {self.retransmission_count} 次")
        print(f"成功接收封包數: {len(self.received_packets)}/{self.total_packets}")
        print("===============\n")

    def print_statistics2(self):
        # 使用client端的時間計算總傳輸時間
        total_time = self.end_time2 - self.start_time2
        transmission_cost = (self.total_packets - 1) * 0.1
        
        # 計算所有延遲包的總延遲時間
        total_delay_time = sum(self.delayed_packets.values())
    
        actual_delay = total_time - transmission_cost
        
       
        print("\n=== Path2 傳輸統計 ===")
        print(f"總傳輸時間: {total_time:.3f} 秒")
        print(f"實際延遲時間: {actual_delay:.3f} 秒")
        print(f"延遲包數量: {len(self.delayed_packets)} 個")
        print(f"延遲包總延遲時間: {total_delay_time:.3f} 秒")
        print(f"成功接收封包數: {len(self.received_packets2)}/{self.total_packets}")
        print("===============\n")

    def close(self):
        """關閉socket連接"""
        if hasattr(self, 'socket'):
            self.socket.close()
        if hasattr(self, 'socket2'):
            self.socket2.close()

if __name__ == "__main__":
    client = UDPClient()
    try:
        client.start()
    except KeyboardInterrupt:
        print("\nClosing client...")
    finally:
        client.close()