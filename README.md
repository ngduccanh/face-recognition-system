1.Chạy file requirements.txt để cài đặt thư viện
2. Thêm ảnh vào thư mục dataset theo câu trúc: dataset/Tên/msv.jpg
3. Nếu chưa có file database -> chạy file create_database.py
4. Chạy file encode_faces.py để mã hóa hình ảnh và lưu vào database
5. Chạy file face_recognition_realtime.py để chạy hệ thống điểm danh
6. Chạy file main.py bằng câu lệnh "uvicorn main:app --reload" để truy cập danh sách người dùng, danh sách điểm danh
