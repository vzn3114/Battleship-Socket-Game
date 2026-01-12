"""
Client Battleship Game - Giao diện người chơi
"""
import socket
import threading
import json
import os
import sys

class BattleshipClient:
    def __init__(self, host='127.0.0.1', port=8080):
        self.host = host
        self.port = port
        self.socket = None
        self.username = ""
        self.opponent_name = ""
        
        # Bản đồ của mình (10x10)
        self.my_board = [[' ' for _ in range(10)] for _ in range(10)]
        
        # Bản đồ bắn đối thủ (10x10) - theo dõi các ô đã bắn
        self.opponent_board = [[' ' for _ in range(10)] for _ in range(10)]
        
        # Trạng thái
        self.is_my_turn = False
        self.game_started = False
        self.game_over = False
        
        # Lock cho việc in ra màn hình
        self.print_lock = threading.Lock()
    
    def connect(self):
        """Kết nối đến server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print(f"[CLIENT] Đã kết nối đến server {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"[CLIENT] Lỗi kết nối: {e}")
            return False
    
    def start(self):
        """Bắt đầu client"""
        # Nhập tên người chơi
        self.username = input("Nhập tên của bạn: ")
        
        # Kết nối
        if not self.connect():
            return
        
        # Gửi CONNECT
        self.send_message(f"CONNECT|{self.username}")
        
        # Tạo thread nhận tin nhắn
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.daemon = True
        receive_thread.start()
        
        # Chờ ghép cặp
        print("\n[CLIENT] Đang chờ đối thủ...")
        
        # Main loop
        try:
            while not self.game_over:
                pass
        except KeyboardInterrupt:
            print("\n[CLIENT] Ngắt kết nối...")
        finally:
            self.socket.close()
    
    def receive_messages(self):
        """Nhận tin nhắn từ server (chạy trên thread riêng)"""
        try:
            while True:
                data = self.socket.recv(4096).decode('utf-8')
                if not data:
                    break
                
                self.process_message(data)
        
        except Exception as e:
            print(f"\n[CLIENT] Lỗi khi nhận tin nhắn: {e}")
    
    def process_message(self, message):
        """Xử lý tin nhắn từ server"""
        parts = message.split('|', 1)
        command = parts[0]
        data = parts[1] if len(parts) > 1 else ""
        
        if command == "WAITING":
            with self.print_lock:
                print(f"\n{data}")
        
        elif command == "MATCH_FOUND":
            self.handle_match_found(data)
        
        elif command == "GAME_START":
            self.handle_game_start(data)
        
        elif command == "RESULT":
            self.handle_result(data)
        
        elif command == "OPPONENT_SHOOT":
            self.handle_opponent_shoot(data)
        
        elif command == "TURN":
            self.handle_turn(data)
        
        elif command == "GAME_OVER":
            self.handle_game_over(data)
        
        elif command == "OPPONENT_DISCONNECTED":
            with self.print_lock:
                print(f"\n{data}")
                self.game_over = True
        
        elif command == "ERROR":
            with self.print_lock:
                print(f"\n[LỖI] {data}")
    
    def handle_match_found(self, opponent_name):
        """Xử lý khi tìm thấy đối thủ"""
        self.opponent_name = opponent_name
        with self.print_lock:
            print(f"\n{'='*50}")
            print(f"Đã tìm thấy đối thủ: {opponent_name}")
            print(f"{'='*50}")
        
        # Bắt đầu setup (xếp tàu)
        self.setup_ships()
    
    def setup_ships(self):
        """Giai đoạn xếp tàu"""
        with self.print_lock:
            print("\n=== GIAI ĐOẠN XẾP TÀU ===")
            print("Bạn cần xếp các tàu trên bảng 10x10 (tọa độ từ 0-9)")
            print("Các loại tàu:")
            print("  - 1 tàu 5 ô")
            print("  - 1 tàu 4 ô")
            print("  - 2 tàu 3 ô")
            print("  - 1 tàu 2 ô")
            print("\nLưu ý: Tàu có thể xếp ngang hoặc dọc")
        
        ships = [
            ("Tàu sân bay", 5),
            ("Tàu chiến", 4),
            ("Tàu khu trục 1", 3),
            ("Tàu khu trục 2", 3),
            ("Tàu ngầm", 2)
        ]
        
        all_positions = []
        
        for ship_name, ship_size in ships:
            while True:
                with self.print_lock:
                    self.display_my_board()
                    print(f"\nĐặt {ship_name} (kích thước: {ship_size} ô)")
                
                try:
                    start_x = int(input("  Tọa độ X bắt đầu (0-9): "))
                    start_y = int(input("  Tọa độ Y bắt đầu (0-9): "))
                    direction = input("  Hướng (h=ngang, v=dọc): ").lower()
                    
                    # Tính các ô
                    positions = []
                    if direction == 'h':
                        for i in range(ship_size):
                            positions.append([start_x + i, start_y])
                    elif direction == 'v':
                        for i in range(ship_size):
                            positions.append([start_x, start_y + i])
                    else:
                        print("Hướng không hợp lệ!")
                        continue
                    
                    # Kiểm tra hợp lệ
                    valid = True
                    for pos in positions:
                        x, y = pos
                        if x < 0 or x > 9 or y < 0 or y > 9:
                            print("Tọa độ vượt quá bảng!")
                            valid = False
                            break
                        if [x, y] in all_positions:
                            print("Vị trí đã có tàu khác!")
                            valid = False
                            break
                    
                    if valid:
                        all_positions.extend(positions)
                        # Đánh dấu trên bảng
                        for pos in positions:
                            self.my_board[pos[1]][pos[0]] = '■'
                        break
                
                except ValueError:
                    print("Nhập không hợp lệ!")
                except Exception as e:
                    print(f"Lỗi: {e}")
        
        with self.print_lock:
            self.display_my_board()
            print("\nĐã xếp xong tất cả tàu!")
            print("Đang gửi dữ liệu lên server...")
        
        # Gửi setup lên server
        map_data = json.dumps(all_positions)
        self.send_message(f"SETUP|{map_data}")
    
    def handle_game_start(self, data):
        """Xử lý khi game bắt đầu"""
        self.game_started = True
        
        with self.print_lock:
            print(f"\n{'='*50}")
            print("GAME BẮT ĐẦU!")
            print(f"{'='*50}")
        
        if data == "YOUR_TURN":
            self.is_my_turn = True
            with self.print_lock:
                print("\nĐến lượt bạn!")
            self.make_move()
        else:
            self.is_my_turn = False
            with self.print_lock:
                print("\nĐợi đối thủ đánh...")
    
    def handle_turn(self, data):
        """Xử lý khi đến lượt"""
        if data == "YOUR_TURN":
            self.is_my_turn = True
            with self.print_lock:
                print("\n" + "="*50)
                print("ĐẾN LƯỢT BẠN!")
                print("="*50)
            self.make_move()
    
    def make_move(self):
        """Thực hiện nước đi"""
        with self.print_lock:
            self.display_boards()
        
        while self.is_my_turn and not self.game_over:
            try:
                x = int(input("\nNhập tọa độ X để bắn (0-9): "))
                y = int(input("Nhập tọa độ Y để bắn (0-9): "))
                
                if x < 0 or x > 9 or y < 0 or y > 9:
                    print("Tọa độ không hợp lệ!")
                    continue
                
                if self.opponent_board[y][x] != ' ':
                    print("Bạn đã bắn ô này rồi!")
                    continue
                
                # Gửi shoot
                self.send_message(f"SHOOT|{x},{y}")
                self.is_my_turn = False
                break
            
            except ValueError:
                print("Nhập không hợp lệ!")
            except Exception as e:
                print(f"Lỗi: {e}")
    
    def handle_result(self, data):
        """Xử lý kết quả bắn của mình"""
        parts = data.split('|')
        result_type = parts[0]
        coords = parts[1].split(',')
        x, y = int(coords[0]), int(coords[1])
        
        with self.print_lock:
            if result_type == "HIT":
                self.opponent_board[y][x] = 'X'  # Trúng
                print(f"\n🎯 TRÚNG! Bắn tiếp!")
            else:
                self.opponent_board[y][x] = 'O'  # Trượt
                print(f"\n💨 TRƯỢT!")
            
            if result_type != "HIT":
                print("Đợi đối thủ đánh...")
    
    def handle_opponent_shoot(self, data):
        """Xử lý khi đối thủ bắn"""
        parts = data.split('|')
        result_type = parts[0]
        coords = parts[1].split(',')
        x, y = int(coords[0]), int(coords[1])
        
        with self.print_lock:
            if result_type == "HIT":
                self.my_board[y][x] = 'X'  # Bị trúng
                print(f"\n💥 Đối thủ TRÚNG TÀU CỦA BẠN!")
            else:
                self.my_board[y][x] = 'O'  # Trượt
                print(f"\n🌊 Đối thủ bắn trượt")
    
    def handle_game_over(self, data):
        """Xử lý khi game kết thúc"""
        self.game_over = True
        
        with self.print_lock:
            print("\n" + "="*50)
            print("GAME OVER!")
            print("="*50)
            
            if data == "WIN":
                print("🎉 CHÚC MỪNG! BẠN THẮNG! 🎉")
            else:
                print("😢 BẠN THUA! Chúc bạn may mắn lần sau!")
            
            print("="*50)
        
        self.socket.close()
    
    def display_my_board(self):
        """Hiển thị bảng của mình"""
        print("\n=== BẢNG CỦA BẠN ===")
        print("    " + " ".join([str(i) for i in range(10)]))
        print("  +" + "-" * 21 + "+")
        for i, row in enumerate(self.my_board):
            print(f"{i} | " + " ".join(row) + " |")
        print("  +" + "-" * 21 + "+")
    
    def send_message(self, message):
        """Gửi tin nhắn đến server"""
        try:
            self.socket.send(message.encode('utf-8'))
        except Exception as e:
            print(f"[CLIENT] Lỗi khi gửi tin nhắn: {e}")

if __name__ == "__main__":
    # Nhập địa chỉ server
    print("=== BATTLESHIP GAME CLIENT ===")
    host = input("Nhập địa chỉ server (Enter = 127.0.0.1): ").strip() or "127.0.0.1"
    port_input = input("Nhập cổng (Enter = 8080): ").strip()
    port = int(port_input) if port_input else 8080
    
    client = BattleshipClient(host=host, port=port)
    client.start()
