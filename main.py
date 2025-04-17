from fastapi import FastAPI, HTTPException
import sqlite3

app = FastAPI()

# Hàm kết nối đến database
def get_db_connection():
    conn = sqlite3.connect('attendance_system.db')
    conn.row_factory = sqlite3.Row
    return conn

# API để lấy danh sách điểm danh
@app.get("/attendance-list")
def get_attendance():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT users.id AS user_id, users.username, attendance.timestamp
            FROM attendance
            JOIN users ON attendance.user_id = users.id
        """)
        rows = cursor.fetchall()
        conn.close()

        attendance_list = [
            {
                "user_id": row["user_id"],
                "username": row["username"],
                "timestamp": row["timestamp"]
            }
            for row in rows
        ]
        return {"attendance": attendance_list}

    except Exception as e:
        print(f"[ERROR] Lỗi khi lấy danh sách điểm danh: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# API để lấy danh sách người dùng
@app.get("/users")
async def get_users():
    try:
        conn = sqlite3.connect("attendance_system.db")
        conn.row_factory = sqlite3.Row  # ✅ Quan trọng!
        cursor = conn.cursor()

        # Truy vấn DISTINCT để loại bỏ trùng
        cursor.execute("SELECT DISTINCT id, username FROM users")
        rows = cursor.fetchall()
        conn.close()

        # Chuyển dữ liệu thành danh sách dictionary
        users = [{"id": row["id"], "name": row["username"]} for row in rows]

        return {"users": users}

    except Exception as e:
        print(f"[ERROR] Lỗi khi lấy danh sách người dùng: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
