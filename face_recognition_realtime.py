import os
import face_recognition
import cv2
import sqlite3
import numpy as np
from datetime import datetime, timedelta

# Kết nối đến cơ sở dữ liệu SQLite
conn = sqlite3.connect('attendance_system.db')
cursor = conn.cursor()

# Truy vấn tất cả người dùng và mã hóa khuôn mặt từ bảng 'users'
cursor.execute("SELECT id, username, face_encoding FROM users")
users = cursor.fetchall()

# Tạo danh sách các mã hóa khuôn mặt và tên người
known_face_encodings = []
known_face_names = []

# Tạo dictionary lưu thời gian điểm danh cuối của từng người
last_attendance_time = {}

# Thời gian cuối cùng hiển thị thông báo
last_notification_time = datetime.now() - timedelta(seconds=5)

for user in users:
    known_face_names.append(user[1])
    known_face_encodings.append(np.frombuffer(user[2], dtype=np.float64))

video_capture = cv2.VideoCapture(0)
video_capture.set(3, 640)
video_capture.set(4, 480)

imgBackground = cv2.imread('Resources/background.png')

folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

modeType = 0  # 0: active, 2: vừa điểm danh, 3: đã điểm danh trước đó
modeChangedTime = datetime.now()
current_user_info = None

while True:
    ret, frame = video_capture.read()
    if not ret:
        break

    modeType = 0
    current_time = datetime.now()

    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = small_frame[:, :, ::-1]

    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"

        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = face_distances.argmin() if len(face_distances) > 0 else -1
        if best_match_index != -1 and matches[best_match_index]:
            name = known_face_names[best_match_index]

            user_id = users[best_match_index][0]
            current_time = datetime.now()

            if user_id not in last_attendance_time or (current_time - last_attendance_time[user_id]) > timedelta(seconds=60):
                timestamp = current_time.strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute("INSERT INTO attendance (user_id, timestamp) VALUES (?, ?)", (user_id, timestamp))
                conn.commit()

                last_attendance_time[user_id] = current_time
                print(f"[INFO] Đã ghi điểm danh cho {name} vào {timestamp}")

                modeType = 2
                modeChangedTime = current_time
                current_user_info = (user_id, name)
            else:
                modeType = 3
                modeChangedTime = current_time

        else:
            modeType = 0

        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
        cv2.putText(frame, name, (left + 6, bottom - 6),
                    cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

    imgDisplay = imgBackground.copy()

    if imgDisplay.shape[0] >= 162 + frame.shape[0] and imgDisplay.shape[1] >= 55 + frame.shape[1]:
        imgDisplay[162:162 + frame.shape[0], 55:55 + frame.shape[1]] = frame

    if modeType >= 0 and modeType < len(imgModeList):
        imgDisplay[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    if modeType == 2 and current_user_info is not None:
        user_id, name = current_user_info
        try:
            # Chỉnh lại đường dẫn ảnh
            student_image_path = os.path.join('dataset', name, f"{user_id}.jpg")
            if os.path.exists(student_image_path):
                student_img = cv2.imread(student_image_path)
                if student_img is not None:
                    student_img = cv2.resize(student_img, (216, 216))
                    imgDisplay[100:316, 875:875 + 216] = student_img

                    cv2.putText(imgDisplay, f"Name: {name}", (875, 340),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
                    cv2.putText(imgDisplay, f"ID: {user_id}", (875, 370),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
                else:
                    print(f"[ERROR] Ảnh {student_image_path} bị lỗi, không đọc được.")
            else:
                print(f"[ERROR] Không tìm thấy ảnh: {student_image_path}")
        except Exception as e:
            print(f"[ERROR] Không thể hiển thị thông tin sinh viên: {e}")

    cv2.imshow("Face Attendance", imgDisplay)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
conn.close()