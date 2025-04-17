import face_recognition
import os
import sqlite3
import numpy as np

# Thư mục chứa ảnh
image_folder = "dataset"

# Kết nối đến cơ sở dữ liệu SQLite
conn = sqlite3.connect('attendance_system.db')
cursor = conn.cursor()

# Lặp qua tất cả các ảnh trong thư mục
for person_name in os.listdir(image_folder):
    person_folder = os.path.join(image_folder, person_name)

    if os.path.isdir(person_folder):  # Nếu là thư mục chứa ảnh
        for image_name in os.listdir(person_folder):
            if image_name.endswith(".jpg") or image_name.endswith(".png"):
                image_path = os.path.join(person_folder, image_name)

                # Lấy user_id từ tên ảnh (loại bỏ phần đuôi .jpg hoặc .png)
                user_id = os.path.splitext(image_name)[0]
                print(f"[INFO] Đang xử lý: {image_name}, user_id = {user_id}")

                # Kiểm tra xem người dùng đã tồn tại chưa
                cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
                existing_user = cursor.fetchone()

                if existing_user:
                    print(f"[INFO] Người dùng '{user_id}' đã tồn tại. Bỏ qua thêm mới.")
                    continue  # Không thêm lại

                # Load ảnh và tìm mã hóa khuôn mặt
                image = face_recognition.load_image_file(image_path)
                encodings = face_recognition.face_encodings(image)

                if len(encodings) > 0:
                    # Mã hóa khuôn mặt đầu tiên trong ảnh
                    face_encoding = encodings[0]

                    # Thêm mã hóa khuôn mặt vào database
                    cursor.execute("INSERT INTO users (id, username, face_encoding) VALUES (?, ?, ?)",
                                   (user_id, person_name, face_encoding.tobytes()))
                    print(f"[INFO] Đã thêm {person_name} với user_id {user_id} vào database.")
                    break  # ✅ Thêm 1 ảnh là đủ, không cần thêm nhiều

# Lưu thay đổi vào database và đóng kết nối
conn.commit()
conn.close()

print("[INFO] Đã mã hóa xong khuôn mặt và lưu vào database.")
