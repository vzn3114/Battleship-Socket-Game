"""
Client Battleship Game - Giao diện GUI với Tkinter (Resizable)
Trải nghiệm tốt hơn với click chuột - CÓ THỂ THAY ĐỔI KÍCH THƯỚC
"""
import socket
import threading
import json
import tkinter as tk
from tkinter import messagebox, simpledialog
import time

class BattleshipGUI:
    def __init__(self, host='127.0.0.1', port=8080):
        self.host = host
        self.port = port
        self.socket = None
        self.username = ""
        self.opponent_name = ""
        
        # Bản đồ của mình và đối thủ
        self.my_board = [[' ' for _ in range(10)] for _ in range(10)]
        self.opponent_board = [[' ' for _ in range(10)] for _ in range(10)]
        
        # Trạng thái
        self.is_my_turn = False
        self.game_started = False
        self.game_over = False
        self.setup_mode = False
        
        # Setup ships
        self.ships_to_place = [
            ("Tàu sân bay", 5, "blue"),
            ("Tàu chiến", 4, "green"),
            ("Tàu khu trục 1", 3, "orange"),
            ("Tàu khu trục 2", 3, "orange"),
            ("Tàu ngầm", 2, "purple")
        ]
        self.current_ship_index = 0
        self.ship_direction = 'h'  # h=horizontal, v=vertical
        self.all_ship_positions = []
        
        # GUI
        self.root = tk.Tk()
        self.root.title("🚢 Battleship Game")
        self.root.geometry("1400x800")  # Kích thước ban đầu lớn hơn
        self.root.minsize(1000, 600)    # Kích thước tối thiểu
        self.root.resizable(True, True)  # ⭐ CHO PHÉP RESIZE
        
        self.my_buttons = []
        self.opponent_buttons = []
        
        # Variables để lưu widgets cần update khi resize
        self.button_width = 4
        self.button_height = 2
        
        self.create_gui()
        
        # Bind sự kiện resize
        self.root.bind('<Configure>', self.on_window_resize)
    
    def on_window_resize(self, event):
        """Xử lý khi cửa sổ thay đổi kích thước"""
        # Chỉ xử lý khi resize cửa sổ chính (không phải widget con)
        if event.widget == self.root:
            # Tính toán kích thước button mới dựa trên kích thước cửa sổ
            window_width = self.root.winfo_width()
            window_height = self.root.winfo_height()
            
            # Tính width và height cho button (chia đều không gian)
            # Trừ đi padding và space cho labels
            available_width = (window_width - 100) // 2  # Chia đôi cho 2 bảng
            available_height = window_height - 250       # Trừ header và controls
            
            # Tính kích thước button
            new_width = max(3, min(8, available_width // 60))
            new_height = max(1, min(3, available_height // 200))
            
            if new_width != self.button_width or new_height != self.button_height:
                self.button_width = new_width
                self.button_height = new_height
                self.update_button_sizes()
    
    def update_button_sizes(self):
        """Cập nhật kích thước tất cả buttons"""
        # Update my board buttons
        for row in self.my_buttons:
            for btn in row:
                btn.config(width=self.button_width, height=self.button_height)
        
        # Update opponent board buttons
        for row in self.opponent_buttons:
            for btn in row:
                btn.config(width=self.button_width, height=self.button_height)
    
    def create_gui(self):
        """Tạo giao diện - RESPONSIVE DESIGN"""
        # Main container - sử dụng pack với fill và expand
        main_frame = tk.Frame(self.root, bg="#2c3e50")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ==================== HEADER ====================
        title_frame = tk.Frame(main_frame, bg="#2c3e50")
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title = tk.Label(title_frame, text="🚢 BATTLESHIP GAME 🚢", 
                        font=("Arial", 24, "bold"), bg="#2c3e50", fg="white")
        title.pack()
        
        # Status bar
        self.status_label = tk.Label(title_frame, text="Đang kết nối...", 
                                     font=("Arial", 12), bg="#2c3e50", fg="#ecf0f1")
        self.status_label.pack()
        
        # ==================== GAME BOARDS ====================
        # Sử dụng PanedWindow để cho phép resize giữa 2 bảng
        boards_paned = tk.PanedWindow(main_frame, orient=tk.HORIZONTAL, 
                                      bg="#2c3e50", sashwidth=5, 
                                      sashrelief=tk.RAISED)
        boards_paned.pack(fill=tk.BOTH, expand=True)
        
        # Left board (My board) - Frame với scrollbar nếu cần
        left_frame = tk.Frame(boards_paned, bg="#34495e", relief=tk.RAISED, bd=2)
        boards_paned.add(left_frame, stretch="always")
        
        self.my_board_label = tk.Label(left_frame, text="BẢNG CỦA BẠN", 
                                       font=("Arial", 16, "bold"), 
                                       bg="#34495e", fg="white")
        self.my_board_label.pack(pady=10)
        
        # Container cho grid với khả năng center
        my_grid_container = tk.Frame(left_frame, bg="#34495e")
        my_grid_container.pack(fill=tk.BOTH, expand=True, pady=10)
        
        my_grid = tk.Frame(my_grid_container, bg="#34495e")
        my_grid.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Create my board với grid
        for i in range(10):
            row_buttons = []
            for j in range(10):
                btn = tk.Button(my_grid, text="", 
                               width=self.button_width, 
                               height=self.button_height,
                               bg="#3498db", fg="white",
                               font=("Arial", 10, "bold"),
                               command=lambda x=j, y=i: self.my_cell_click(x, y))
                btn.grid(row=i, column=j, padx=1, pady=1, sticky="nsew")
                row_buttons.append(btn)
            self.my_buttons.append(row_buttons)
        
        # Configure grid weights để buttons scale đều
        for i in range(10):
            my_grid.grid_rowconfigure(i, weight=1)
            my_grid.grid_columnconfigure(i, weight=1)
        
        # Right board (Opponent board)
        right_frame = tk.Frame(boards_paned, bg="#34495e", relief=tk.RAISED, bd=2)
        boards_paned.add(right_frame, stretch="always")
        
        self.opp_board_label = tk.Label(right_frame, text="BẢNG ĐỐI THỦ", 
                                        font=("Arial", 16, "bold"), 
                                        bg="#34495e", fg="white")
        self.opp_board_label.pack(pady=10)
        
        # Container cho opponent grid
        opp_grid_container = tk.Frame(right_frame, bg="#34495e")
        opp_grid_container.pack(fill=tk.BOTH, expand=True, pady=10)
        
        opp_grid = tk.Frame(opp_grid_container, bg="#34495e")
        opp_grid.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Create opponent board
        for i in range(10):
            row_buttons = []
            for j in range(10):
                btn = tk.Button(opp_grid, text="", 
                               width=self.button_width, 
                               height=self.button_height,
                               bg="#95a5a6", fg="white",
                               font=("Arial", 10, "bold"),
                               command=lambda x=j, y=i: self.opponent_cell_click(x, y))
                btn.grid(row=i, column=j, padx=1, pady=1, sticky="nsew")
                row_buttons.append(btn)
            self.opponent_buttons.append(row_buttons)
        
        # Configure grid weights
        for i in range(10):
            opp_grid.grid_rowconfigure(i, weight=1)
            opp_grid.grid_columnconfigure(i, weight=1)
        
        # ==================== CONTROL PANEL ====================
        control_frame = tk.Frame(main_frame, bg="#2c3e50", height=100)
        control_frame.pack(fill=tk.X, pady=(10, 0))
        control_frame.pack_propagate(False)  # Giữ height cố định
        
        self.ship_info_label = tk.Label(control_frame, text="", 
                                        font=("Arial", 12, "bold"), 
                                        bg="#2c3e50", fg="#f39c12")
        self.ship_info_label.pack(pady=5)
        
        # Button frame cho các nút điều khiển
        button_frame = tk.Frame(control_frame, bg="#2c3e50")
        button_frame.pack(pady=5)
        
        self.direction_btn = tk.Button(button_frame, 
                                      text="🔄 Đổi hướng (Ngang ↔️ Dọc)", 
                                      command=self.toggle_direction,
                                      font=("Arial", 10, "bold"), 
                                      bg="#e74c3c", fg="white",
                                      padx=20, pady=10,
                                      state=tk.DISABLED)
        self.direction_btn.pack(side=tk.LEFT, padx=5)
        
        # Thêm nút fullscreen toggle
        self.fullscreen_btn = tk.Button(button_frame,
                                       text="⛶ Toàn màn hình",
                                       command=self.toggle_fullscreen,
                                       font=("Arial", 10, "bold"),
                                       bg="#3498db", fg="white",
                                       padx=20, pady=10)
        self.fullscreen_btn.pack(side=tk.LEFT, padx=5)
        
        self.is_fullscreen = False
    
    def toggle_fullscreen(self):
        """Chuyển đổi chế độ toàn màn hình"""
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes('-fullscreen', self.is_fullscreen)
        
        if self.is_fullscreen:
            self.fullscreen_btn.config(text="⛶ Thoát toàn màn hình")
        else:
            self.fullscreen_btn.config(text="⛶ Toàn màn hình")
    
    def handle_result(self, data):
        """Xử lý kết quả bắn"""
        parts = data.split('|')
        result_type = parts[0]
        coords = parts[1].split(',')
        x, y = int(coords[0]), int(coords[1])
        
        if result_type == "HIT":
            self.opponent_buttons[y][x].config(bg="#e74c3c", text="💥")
            self.opponent_board[y][x] = 'X'
            messagebox.showinfo("Kết quả", "🎯 TRÚNG! Bắn tiếp!")
        else:
            self.opponent_buttons[y][x].config(bg="#7f8c8d", text="○")
            self.opponent_board[y][x] = 'O'
            messagebox.showinfo("Kết quả", "💨 TRƯỢT!")
        
        if result_type != "HIT":
            self.status_label.config(text="⏳ Đợi đối thủ đánh...")
    
    def handle_opponent_shoot(self, data):
        """Xử lý khi đối thủ bắn"""
        parts = data.split('|')
        result_type = parts[0]
        coords = parts[1].split(',')
        x, y = int(coords[0]), int(coords[1])
        
        if result_type == "HIT":
            self.my_buttons[y][x].config(bg="#e74c3c", text="💥")
            self.my_board[y][x] = 'X'
        else:
            self.my_buttons[y][x].config(bg="#7f8c8d", text="○")
            self.my_board[y][x] = 'O'
    
    def handle_game_over(self, data):
        """Xử lý game over"""
        self.game_over = True
        
        if data == "WIN":
            messagebox.showinfo("GAME OVER", "🎉 CHÚC MỪNG! BẠN THẮNG! 🎉")
            self.status_label.config(text="🏆 BẠN THẮNG!")
        else:
            messagebox.showinfo("GAME OVER", "😢 BẠN THUA! Chúc bạn may mắn lần sau!")
            self.status_label.config(text="😢 BẠN THUA!")
        
        # Đóng sau 3 giây
        self.root.after(3000, self.root.destroy)

    def my_cell_click(self, x, y):
        """Xử lý click vào bảng của mình (setup)"""
        if not self.setup_mode:
            return
        
        if self.current_ship_index >= len(self.ships_to_place):
            return
        
        ship_name, ship_size, ship_color = self.ships_to_place[self.current_ship_index]
        
        # Tính toán vị trí tàu
        positions = []
        if self.ship_direction == 'h':
            for i in range(ship_size):
                positions.append([x + i, y])
        else:
            for i in range(ship_size):
                positions.append([x, y + i])
        
        # Kiểm tra hợp lệ
        valid = True
        for pos in positions:
            px, py = pos
            if px < 0 or px > 9 or py < 0 or py > 9:
                messagebox.showerror("Lỗi", "Tàu vượt quá bảng!")
                return
            if [px, py] in self.all_ship_positions:
                messagebox.showerror("Lỗi", "Vị trí đã có tàu khác!")
                return
        
        # Đặt tàu
        self.all_ship_positions.extend(positions)
        for pos in positions:
            px, py = pos
            self.my_buttons[py][px].config(bg="#27ae60", text="■")
            self.my_board[py][px] = '■'
        
        # Chuyển sang tàu tiếp theo
        self.current_ship_index += 1
        
        if self.current_ship_index < len(self.ships_to_place):
            next_ship = self.ships_to_place[self.current_ship_index]
            self.ship_info_label.config(
                text=f"Đặt {next_ship[0]} ({next_ship[1]} ô) - Hướng: {'Ngang' if self.ship_direction == 'h' else 'Dọc'}"
            )
        else:
            # Hoàn thành setup
            self.ship_info_label.config(text="✅ Đã đặt xong tất cả tàu! Đang gửi dữ liệu...")
            self.direction_btn.config(state=tk.DISABLED)
            self.setup_mode = False
            
            # Gửi setup
            map_data = json.dumps(self.all_ship_positions)
            self.send_message(f"SETUP|{map_data}")
    
    def opponent_cell_click(self, x, y):
        """Xử lý click vào bảng đối thủ (bắn)"""
        if not self.game_started or not self.is_my_turn or self.game_over:
            return
        
        if self.opponent_board[y][x] != ' ':
            messagebox.showwarning("Cảnh báo", "Bạn đã bắn ô này rồi!")
            return
        
        # Gửi shoot
        self.send_message(f"SHOOT|{x},{y}")
        self.is_my_turn = False
        self.status_label.config(text="⏳ Đang đợi kết quả...")
    
    def toggle_direction(self):
        """Đổi hướng đặt tàu"""
        self.ship_direction = 'v' if self.ship_direction == 'h' else 'h'
        if self.current_ship_index < len(self.ships_to_place):
            ship = self.ships_to_place[self.current_ship_index]
            self.ship_info_label.config(
                text=f"Đặt {ship[0]} ({ship[1]} ô) - Hướng: {'Ngang' if self.ship_direction == 'h' else 'Dọc'}"
            )
    
    def start(self):
        """Khởi động client"""
        # Nhập thông tin
        self.username = simpledialog.askstring("Tên người chơi", 
                                               "Nhập tên của bạn:",
                                               parent=self.root)
        if not self.username:
            self.username = "Player"
        
        # Kết nối
        if not self.connect():
            messagebox.showerror("Lỗi", "Không thể kết nối đến server!")
            self.root.destroy()
            return
        
        # Gửi CONNECT
        self.send_message(f"CONNECT|{self.username}")
        self.status_label.config(text="🔍 Đang tìm đối thủ...")
        
        # Thread nhận tin nhắn
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.daemon = True
        receive_thread.start()
        
        # Chạy GUI
        self.root.mainloop()
    
    def connect(self):
        """Kết nối đến server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            return True
        except Exception as e:
            print(f"[ERROR] Lỗi kết nối: {e}")
            return False
    
    def receive_messages(self):
        """Nhận tin nhắn từ server"""
        try:
            while True:
                data = self.socket.recv(4096).decode('utf-8')
                if not data:
                    break
                self.root.after(0, self.process_message, data)
        except Exception as e:
            print(f"[ERROR] Lỗi nhận tin nhắn: {e}")
    
    def process_message(self, message):
        """Xử lý tin nhắn từ server"""
        parts = message.split('|', 1)
        command = parts[0]
        data = parts[1] if len(parts) > 1 else ""
        
        if command == "WAITING":
            self.status_label.config(text="⏳ Đang chờ đối thủ...")
        
        elif command == "MATCH_FOUND":
            self.opponent_name = data
            self.opp_board_label.config(text=f"BẢNG ĐỐI THỦ: {data}")
            self.status_label.config(text=f"✅ Đã tìm thấy đối thủ: {data}")
            self.start_setup()
        
        elif command == "GAME_START":
            self.game_started = True
            if data == "YOUR_TURN":
                self.is_my_turn = True
                self.status_label.config(text="🎯 ĐẾN LƯỢT BẠN! Click vào bảng đối thủ để bắn")
            else:
                self.is_my_turn = False
                self.status_label.config(text="⏳ Đợi đối thủ đánh...")
        
        elif command == "RESULT":
            self.handle_result(data)
        
        elif command == "OPPONENT_SHOOT":
            self.handle_opponent_shoot(data)
        
        elif command == "TURN":
            if data == "YOUR_TURN":
                self.is_my_turn = True
                if self.game_started:
                    self.status_label.config(text="🎯 ĐẾN LƯỢT BẠN! Click vào bảng đối thủ để bắn")
        
        elif command == "GAME_OVER":
            self.handle_game_over(data)
        
        elif command == "OPPONENT_DISCONNECTED":
            messagebox.showinfo("Thông báo", "Đối thủ đã ngắt kết nối!")
            self.game_over = True
            self.root.destroy()
    
    def start_setup(self):
        """Bắt đầu giai đoạn setup"""
        self.setup_mode = True
        self.direction_btn.config(state=tk.NORMAL)
        ship = self.ships_to_place[0]
        self.ship_info_label.config(
            text=f"Đặt {ship[0]} ({ship[1]} ô) - Hướng: {'Ngang' if self.ship_direction == 'h' else 'Dọc'}"
        )
        self.my_board_label.config(text="BẢNG CỦA BẠN (Click để đặt tàu)")
    
    def send_message(self, message):
        """Gửi tin nhắn đến server"""
        try:
            self.socket.send(message.encode('utf-8'))
        except Exception as e:
            print(f"[ERROR] Lỗi gửi tin nhắn: {e}")

if __name__ == "__main__":
    # Nhập thông tin server
    root = tk.Tk()
    root.withdraw()
    
    host = simpledialog.askstring("Server", 
                                  "Nhập địa chỉ server:",
                                  initialvalue="127.0.0.1")
    if not host:
        host = "127.0.0.1"
    
    port_str = simpledialog.askstring("Port", 
                                      "Nhập cổng:",
                                      initialvalue="8080")
    port = int(port_str) if port_str else 8080
    
    root.destroy()
    
    # Khởi động game
    game = BattleshipGUI(host=host, port=port)
    game.start()