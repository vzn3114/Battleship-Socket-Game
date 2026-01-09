# Game "Bắn Tàu" (Battleship) 🚢

## 📋 Mục lục
- [Tổng quan](#tổng-quan)
- [Cài đặt](#cài-đặt)
- [Hướng dẫn chạy](#hướng-dẫn-chạy)
- [Cấu trúc dự án](#cấu-trúc-dự-án)
- [Giao thức truyền thông](#giao-thức-truyền-thông)
- [Kỹ thuật lập trình](#kỹ-thuật-lập-trình)

---

## 🎮 Tổng quan

### 1. Tổng quan mô hình Multi Client-Server
Trong game này, Server đóng vai trò là "Trọng Tài" và "Người Mai Mối". Các Client (Người chơi) không bao giờ gửi dữ liệu trực tiếp cho nhau (P2P), mà mọi hành động đều phải đi qua Server.

**Server:**
- Chấp nhận kết nối từ hàng loạt Client (sử dụng Multi-threading)
- Ghép cặp 2 Client rảnh rỗi vào một phòng chơi (Room/Session)
- Lưu trữ vị trí tàu của cả 2 người chơi (Đây là điểm mấu chốt: Client A không biết bản đồ của Client B, chỉ Server biết)
- Xử lý logic bắn: Kiểm tra tọa độ bắn có trúng tàu không

**Client:**
- Giao diện để người chơi xếp tàu và chọn tọa độ bắn
- Gửi yêu cầu bắn (Shoot Request) lên Server
- Nhận kết quả (Shoot Result) từ Server để hiển thị (Trúng/Trượt)
---

## 📦 Cài đặt

### Yêu cầu hệ thống
- **Python:** 3.7 trở lên
- **Hệ điều hành:** Windows, macOS, hoặc Linux
- **Thư viện:** Chỉ sử dụng thư viện chuẩn của Python (không cần cài thêm)

### Các bước cài đặt

1. **Clone hoặc tải dự án về máy:**
```bash
git clone <repository-url>
cd Battleship-Socket-Game
```

2. **Kiểm tra Python:**
```bash
python --version
```
hoặc
```bash
python3 --version
```

3. **Sẵn sàng chạy!** (Không cần cài đặt thêm gói nào)

---

## 🚀 Hướng dẫn chạy

### Chạy Server

Mở terminal/cmd và chạy:

```bash
python server.py
```

Server sẽ khởi động và lắng nghe tại cổng **8080**.

**Output mẫu:**
```
[SERVER] Server đang chạy tại 0.0.0.0:8080
[SERVER] Đang chờ kết nối từ các client...
```

### Chạy Client (Người chơi)

Có **2 phiên bản client** để bạn lựa chọn:

#### 🎨 Phiên bản GUI (Khuyên dùng - Dễ thao tác hơn!)

Mở **2 terminal/cmd riêng biệt** và chạy:

```bash
python client_gui.py
```

**Ưu điểm:**
- ✅ Giao diện đồ họa đẹp mắt
- ✅ Click chuột để đặt tàu và bắn
- ✅ Hiển thị trực quan màu sắc
- ✅ Dễ sử dụng cho người mới

#### ⌨️ Phiên bản Console (Truyền thống)

```bash
python client.py
```

**Ưu điểm:**
- ✅ Nhẹ, chạy trên mọi terminal
- ✅ Phù hợp cho server không có GUI

**Lưu ý:** 
- Nếu server chạy trên máy khác, nhập địa chỉ IP của máy server khi được hỏi
- Mặc định server chạy tại `127.0.0.1:8080` (localhost)

### Gameplay

#### Với Client GUI (client_gui.py):
1. **Kết nối:** Nhập tên người chơi
2. **Chờ ghép cặp:** Chờ đối thủ kết nối
3. **Xếp tàu:** 
   - Click chuột trên bảng bên trái để đặt tàu
   - Dùng nút "Đổi hướng" để chuyển ngang/dọc
   - Đặt lần lượt 5 con tàu (5ô, 4ô, 3ô, 3ô, 2ô)
4. **Chơi:** 
   - Đến lượt bạn: Click vào bảng bên phải (bảng đối thủ) để bắn
   - Màu đỏ 💥 = Trúng, Màu xám ○ = Trượt
5. **Thắng:** Phá hủy hết tàu đối thủ!

#### Với Client Console (client.py):
1. **Kết nối:** Nhập tên người chơi
2. **Chờ ghép cặp:** Đợi đối thủ
3. **Xếp tàu:** Nhập tọa độ và hướng (h/v) cho từng tàu
4. **Chơi:** Nhập tọa độ X, Y để bắn (0-9)
5. **Thắng:** Người đầu tiên phá hủy hết tàu thắng!

---

## 📁 Cấu trúc dự án

```
Battleship-Socket-Game/
│
├── README.md           # File hướng dẫn này
├── server.py           # Server chính (Multi-threaded)
├── client.py           # Client console (Terminal)
├── client_gui.py       # Client GUI (Tkinter) ⭐ Khuyên dùng
└── game_room.py        # Class quản lý phòng chơi
```

### Chi tiết các file:

#### `server.py`
- **Chức năng:** Server TCP đa luồng
- **Nhiệm vụ:**
  - Lắng nghe kết nối từ client
  - Tạo thread riêng cho mỗi client
  - Ghép cặp người chơi
  - Xử lý logic game (kiểm tra trúng/trượt)
  - Broadcasting kết quả đến cả 2 người chơi

#### `client.py`
- **Chức năng:** Giao diện người chơi (Console)
- **Tính năng:**
  - Kết nối đến server
  - Giao diện console để xếp tàu
  - Hiển thị 2 bảng (bản đồ của mình & bảng bắn)
  - Xử lý input và hiển thị kết quả

#### `client_gui.py` ⭐ 
- **Chức năng:** Giao diện người chơi (GUI với Tkinter)
- **Tính năng:**
  - Giao diện đồ họa trực quan
  - Click chuột để đặt tàu và bắn
  - Hiển thị màu sắc rõ ràng (xanh=tàu, đỏ=trúng, xám=trượt)
  - Nút đổi hướng đặt tàu
  - Trải nghiệm người dùng tốt hơn

#### `game_room.py`
- **Chức năng:** Class quản lý trạng thái game
- **Lưu trữ:**
  - Thông tin 2 người chơi
  - Bản đồ tàu của cả 2 (Server giữ bí mật)
  - Trạng thái game (lượt chơi, điểm số)
  - Logic kiểm tra thắng/thua

---

## 🔌 Giao thức truyền thông

### 2. Thiết kế Giao thức (Protocol) - Luồng dữ liệu Socket
Đây là phần quan trọng nhất bạn cần báo cáo. Bạn cần quy định các "gói tin" (message) gửi qua lại. Chúng ta sẽ dùng giao thức TCP để đảm bảo tính tin cậy (không bị mất lượt đi).

**Quy ước gói tin:** `COMMAND|DATA`

### Giai đoạn 1: Kết nối & Ghép cặp (Handshake)

| Bước | Người gửi | Gói tin | Ý nghĩa |
|------|-----------|---------|---------|
| 1 | Client A | `CONNECT\|UserA` | A yêu cầu kết nối |
| 2 | Server | - | Đưa A vào hàng đợi |
| 3 | Client B | `CONNECT\|UserB` | B yêu cầu kết nối |
| 4 | Server → A | `MATCH_FOUND\|UserB` | Thông báo đã tìm thấy đối thủ |
| 4 | Server → B | `MATCH_FOUND\|UserA` | Thông báo đã tìm thấy đối thủ |

### Giai đoạn 2: Xếp tàu (Setup Phase)

| Bước | Người gửi | Gói tin | Ý nghĩa |
|------|-----------|---------|---------|
| 1 | Client A | `SETUP\|[[0,0],[0,1],[0,2],...]` | A gửi vị trí tàu |
| 2 | Server | - | Lưu bản đồ A, đợi B |
| 3 | Client B | `SETUP\|[[1,1],[1,2],...]` | B gửi vị trí tàu |
| 4 | Server → A | `GAME_START\|YOUR_TURN` | Game bắt đầu, A đi trước |
| 4 | Server → B | `GAME_START\|WAIT` | Game bắt đầu, B chờ |

### Giai đoạn 3: Chơi game (Gameplay Loop)

**Ví dụ:** A bắn vào ô (3, 5)

| Bước | Người gửi | Gói tin | Ý nghĩa |
|------|-----------|---------|---------|
| 1 | Client A | `SHOOT\|3,5` | A bắn tọa độ (3,5) |
| 2 | Server | - | Kiểm tra trong bản đồ B |
| 3a | Server → A | `RESULT\|HIT\|3,5` | Thông báo A: trúng! |
| 3b | Server → B | `OPPONENT_SHOOT\|HIT\|3,5` | Thông báo B: bị bắn trúng |
| 4 | Server | - | Kiểm tra game over |
| 5 | Server → B | `TURN\|YOUR_TURN` | Đến lượt B |

**Nếu trượt:** Gói tin sẽ là `RESULT|MISS|3,5`

**Nếu game over:**
- Server → Winner: `GAME_OVER|WIN`
- Server → Loser: `GAME_OVER|LOSE`
---

## 💻 Kỹ thuật lập trình

### 3. Các kỹ thuật Lập trình cần áp dụng

#### A. Kỹ thuật Socket (TCP/IP)
- Sử dụng thư viện `socket` của Python
- **Bind & Listen:** Server mở cổng (vd: 8080) và lắng nghe
- **Accept:** Chấp nhận kết nối và trả về một đối tượng socket riêng cho từng Client

**Code mẫu (Server):**
```python
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 8080))
server_socket.listen(10)
client_socket, address = server_socket.accept()
```

#### B. Kỹ thuật Đa luồng (Multi-threading) - Bắt buộc
Vì đây là Multi-Client, Server không thể phục vụ từng người một cách tuần tự.

- Khi có 1 Client kết nối (`server.accept()`), Server phải tạo ra một **Thread mới** (Luồng mới) để quản lý riêng việc nhận/gửi tin nhắn cho Client đó
- Luồng chính (Main Thread) tiếp tục quay lại lắng nghe các kết nối mới

**Code mẫu:**
```python
client_thread = threading.Thread(
    target=self.handle_client,
    args=(client_socket, address)
)
client_thread.daemon = True
client_thread.start()
```

#### C. Quản lý trạng thái (State Management)
- Bạn cần một **Class GameRoom** trên Server
- Class này chứa 2 đối tượng Client (Player 1, Player 2) và trạng thái bàn cờ của họ
- Việc này giúp Server biết ai đang đấu với ai để chuyển tin nhắn cho đúng người

**Cấu trúc GameRoom:**
```python
class GameRoom:
    - player1_socket, player2_socket
    - player1_map, player2_map  # Bản đồ tàu (Server giữ bí mật)
    - current_turn              # Lượt chơi
    - game_started, game_over   # Trạng thái
```

---
