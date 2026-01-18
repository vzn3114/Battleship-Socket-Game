"""
Server Battleship Game - Multi-threaded TCP Server
Đóng vai trò Trọng Tài và Mai Mối
"""
import socket
import threading
import json
from game_room import GameRoom

class BattleshipServer:
    def __init__(self, host='0.0.0.0', port=8080):
        self.host = host
        self.port = port
        self.server_socket = None
        
        # Hàng đợi người chơi chờ ghép cặp
        self.waiting_players = []  # [(socket, username), ...]
        self.waiting_lock = threading.Lock()
        
        # Danh sách các phòng chơi
        self.rooms = {}  # {room_id: GameRoom}
        self.room_counter = 0
        self.rooms_lock = threading.Lock()
        
        # Map socket -> (room_id, player_num, username)
        self.player_info = {}  # {socket: (room_id, player_num, username)}
        self.player_info_lock = threading.Lock()
    
    def start(self):
        """Khởi động server"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(10)
        
        print(f"[SERVER] Server đang chạy tại {self.host}:{self.port}")
        print("[SERVER] Đang chờ kết nối từ các client...")
        
        try:
            while True:
                client_socket, address = self.server_socket.accept()
                print(f"[SERVER] Kết nối mới từ {address}")
                
                # Tạo thread mới cho mỗi client
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
        
        except KeyboardInterrupt:
            print("\n[SERVER] Đang tắt server...")
        finally:
            self.server_socket.close()
    
    def handle_client(self, client_socket, address):
        """Xử lý một client (chạy trên thread riêng)"""
        try:
            while True:
                data = client_socket.recv(4096).decode('utf-8')
                if not data:
                    break
                
                print(f"[SERVER] Nhận từ {address}: {data}")
                self.process_message(client_socket, data)
        
        except Exception as e:
            print(f"[SERVER] Lỗi với client {address}: {e}")
        finally:
            self.disconnect_client(client_socket)
            print(f"[SERVER] Client {address} đã ngắt kết nối")
    
    def process_message(self, client_socket, message):
        """Xử lý tin nhắn từ client"""
        parts = message.split('|', 1)
        command = parts[0]
        data = parts[1] if len(parts) > 1 else ""
        
        if command == "CONNECT":
            self.handle_connect(client_socket, data)
        
        elif command == "SETUP":
            self.handle_setup(client_socket, data)
        
        elif command == "SHOOT":
            self.handle_shoot(client_socket, data)
    
    def handle_connect(self, client_socket, username):
        """Xử lý kết nối và ghép cặp"""
        print(f"[SERVER] Player {username} đang chờ ghép cặp...")
        
        with self.waiting_lock:
            # Nếu có người đang chờ -> Ghép cặp
            if len(self.waiting_players) > 0:
                opponent_socket, opponent_name = self.waiting_players.pop(0)
                
                # Tạo phòng chơi mới
                with self.rooms_lock:
                    self.room_counter += 1
                    room_id = self.room_counter
                    
                    room = GameRoom(
                        room_id,
                        opponent_socket, opponent_name,
                        client_socket, username
                    )
                    self.rooms[room_id] = room
                    
                    # Lưu thông tin người chơi
                    with self.player_info_lock:
                        self.player_info[opponent_socket] = (room_id, 1, opponent_name)
                        self.player_info[client_socket] = (room_id, 2, username)
                
                print(f"[SERVER] Ghép cặp: {opponent_name} vs {username} (Room {room_id})")
                
                # Thông báo cho cả 2 người
                self.send_message(opponent_socket, f"MATCH_FOUND|{username}")
                self.send_message(client_socket, f"MATCH_FOUND|{opponent_name}")
            
            else:
                # Chưa có ai -> Thêm vào hàng đợi
                self.waiting_players.append((client_socket, username))
                self.send_message(client_socket, "WAITING|Đang chờ đối thủ...")
    
    def handle_setup(self, client_socket, map_data):
        """Xử lý giai đoạn setup (xếp tàu)"""
        with self.player_info_lock:
            if client_socket not in self.player_info:
                return
            
            room_id, player_num, username = self.player_info[client_socket]
        
        room = self.rooms.get(room_id)
        if not room:
            return
        
        # Parse map data: "[(0,0),(0,1),(0,2),...]"
        try:
            map_positions = json.loads(map_data)  # List of [x, y]
            map_tuples = [tuple(pos) for pos in map_positions]
            room.set_player_map(player_num, map_tuples)
            
            print(f"[SERVER] {username} đã setup {len(map_tuples)} ô tàu")
            
            # Kiểm tra cả 2 đã sẵn sàng chưa
            if room.is_both_ready():
                room.game_started = True
                print(f"[SERVER] Room {room_id} bắt đầu game!")
                
                # Player 1 đi trước
                self.send_message(room.player1_socket, "GAME_START|YOUR_TURN")
                self.send_message(room.player2_socket, "GAME_START|WAIT")
        
        except Exception as e:
            print(f"[SERVER] Lỗi khi parse map data: {e}")
    
    def handle_shoot(self, client_socket, coordinates):
        """Xử lý bắn"""
        with self.player_info_lock:
            if client_socket not in self.player_info:
                return
            
            room_id, player_num, username = self.player_info[client_socket]
        
        room = self.rooms.get(room_id)
        if not room or not room.game_started:
            return
        
        # Kiểm tra lượt
        if not room.is_player_turn(player_num):
            self.send_message(client_socket, "ERROR|Chưa đến lượt bạn!")
            return
        
        # Parse tọa độ "x,y"
        try:
            x, y = map(int, coordinates.split(','))
            
            # Xử lý bắn
            is_hit, is_game_over, winner = room.process_shoot(player_num, x, y)
            
            result_type = "HIT" if is_hit else "MISS"
            
            # Gửi kết quả cho người bắn
            self.send_message(client_socket, f"RESULT|{result_type}|{x},{y}")
            
            # Gửi thông báo cho đối thủ
            opponent_socket = room.get_opponent_socket(player_num)
            self.send_message(opponent_socket, f"OPPONENT_SHOOT|{result_type}|{x},{y}")
            
            print(f"[SERVER] {username} bắn ({x},{y}) -> {result_type}")
            
            # Kiểm tra game over
            if is_game_over:
                winner_socket = room.get_player_socket(winner)
                loser_socket = room.get_opponent_socket(winner)
                
                self.send_message(winner_socket, "GAME_OVER|WIN")
                self.send_message(loser_socket, "GAME_OVER|LOSE")
                
                print(f"[SERVER] Game over! Player {winner} thắng!")
            
            else:
                # Thông báo lượt chơi mới (chỉ khi trượt - đổi lượt)
                if not is_hit:
                    next_player_socket = room.get_player_socket(room.current_turn)
                    self.send_message(next_player_socket, "TURN|YOUR_TURN")
                else:
                    # Trúng thì thông báo tiếp tục bắn
                    self.send_message(client_socket, "TURN|YOUR_TURN")
        
        except Exception as e:
            print(f"[SERVER] Lỗi khi xử lý shoot: {e}")
    
    def send_message(self, client_socket, message):
        """Gửi tin nhắn đến client"""
        try:
            client_socket.send(message.encode('utf-8'))
            print(f"[SERVER] Gửi: {message}")
        except Exception as e:
            print(f"[SERVER] Lỗi khi gửi tin nhắn: {e}")
    
    def disconnect_client(self, client_socket):
        """Xử lý ngắt kết nối"""
        # Xóa khỏi hàng đợi
        with self.waiting_lock:
            self.waiting_players = [(s, n) for s, n in self.waiting_players if s != client_socket]
        
        # Xóa khỏi player_info và thông báo cho đối thủ
        with self.player_info_lock:
            if client_socket in self.player_info:
                room_id, player_num, username = self.player_info[client_socket]
                del self.player_info[client_socket]
                
                room = self.rooms.get(room_id)
                if room:
                    opponent_socket = room.get_opponent_socket(player_num)
                    self.send_message(opponent_socket, "OPPONENT_DISCONNECTED|Đối thủ đã ngắt kết nối")
        
        try:
            client_socket.close()
        except:
            pass

if __name__ == "__main__":
    server = BattleshipServer(host='0.0.0.0', port=8080)
    server.start()
