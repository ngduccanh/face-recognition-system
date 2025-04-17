import sqlite3

# Kết nối đến database attendance_system.db
conn = sqlite3.connect('attendance_system.db')
cursor = conn.cursor()

# Tạo bảng 'users' để lưu trữ thông tin khuôn mặt và người dùng
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    face_encoding BLOB NOT NULL
)
""")

# Tạo bảng 'attendance' để lưu trữ thông tin điểm danh
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
""")

# Lưu thay đổi và đóng kết nối
conn.commit()
conn.close()

print("[INFO] Đã tạo bảng 'users' và 'attendance'.")