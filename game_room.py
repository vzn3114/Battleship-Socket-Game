"""
Game Room - Quản lý phòng chơi cho 2 người chơi
"""
import json

class GameRoom:
    """Class quản lý một phòng chơi với 2 người chơi"""
    
    def __init__(self, room_id, player1_socket, player1_name, player2_socket, player2_name):
        self.room_id = room_id
        self.player1_socket = player1_socket
        self.player1_name = player1_name
        self.player2_socket = player2_socket
        self.player2_name = player2_name
        
        # Bản đồ tàu của mỗi người (lưu trữ tọa độ các ô có tàu)
        self.player1_map = set()  # Set các tuple (x, y)
        self.player2_map = set()
        
        # Các ô đã bị bắn
        self.player1_hit = set()  # Ô của player1 bị bắn trúng
        self.player2_hit = set()  # Ô của player2 bị bắn trúng
        
        # Trạng thái setup
        self.player1_ready = False
        self.player2_ready = False
        
        # Lượt chơi (1 hoặc 2)
        self.current_turn = 1
        
        # Số ô tàu ban đầu (để kiểm tra game over)
        self.player1_ship_count = 0
        self.player2_ship_count = 0
        
        # Trạng thái game
        self.game_started = False
        self.game_over = False
    
    def set_player_map(self, player_num, map_data):
        """
        Lưu bản đồ tàu của người chơi
        map_data: list of tuples [(x1,y1), (x2,y2), ...]
        """
        if player_num == 1:
            self.player1_map = set(map_data)
            self.player1_ship_count = len(map_data)
            self.player1_ready = True
        else:
            self.player2_map = set(map_data)
            self.player2_ship_count = len(map_data)
            self.player2_ready = True
    
    def is_both_ready(self):
        """Kiểm tra cả 2 người chơi đã sẵn sàng chưa"""
        return self.player1_ready and self.player2_ready
    
    def process_shoot(self, player_num, x, y):
        """
        Xử lý bắn
        Trả về: (is_hit, is_game_over, winner)
        """
        if self.game_over:
            return False, True, None
        
        # Player 1 bắn vào bản đồ của Player 2
        if player_num == 1:
            target_map = self.player2_map
            target_hit = self.player2_hit
            is_hit = (x, y) in target_map
            
            if is_hit:
                self.player2_hit.add((x, y))
                # Kiểm tra game over
                if len(self.player2_hit) == self.player2_ship_count:
                    self.game_over = True
                    return True, True, 1
                # Trúng thì KHÔNG đổi lượt (được bắn tiếp)
                return is_hit, False, None
            else:
                # Trượt thì mới đổi lượt
                self.current_turn = 2
                return is_hit, False, None
        
        # Player 2 bắn vào bản đồ của Player 1
        else:
            target_map = self.player1_map
            target_hit = self.player1_hit
            is_hit = (x, y) in target_map
            
            if is_hit:
                self.player1_hit.add((x, y))
                # Kiểm tra game over
                if len(self.player1_hit) == self.player1_ship_count:
                    self.game_over = True
                    return True, True, 2
                # Trúng thì KHÔNG đổi lượt (được bắn tiếp)
                return is_hit, False, None
            else:
                # Trượt thì mới đổi lượt
                self.current_turn = 1
                return is_hit, False, None
    
    def is_player_turn(self, player_num):
        """Kiểm tra có phải lượt của người chơi này không"""
        return self.current_turn == player_num
    
    def get_opponent_socket(self, player_num):
        """Lấy socket của đối thủ"""
        if player_num == 1:
            return self.player2_socket
        else:
            return self.player1_socket
    
    def get_opponent_name(self, player_num):
        """Lấy tên của đối thủ"""
        if player_num == 1:
            return self.player2_name
        else:
            return self.player1_name
    
    def get_player_socket(self, player_num):
        """Lấy socket của người chơi"""
        if player_num == 1:
            return self.player1_socket
        else:
            return self.player2_socket
