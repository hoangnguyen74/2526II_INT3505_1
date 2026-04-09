import sqlite3
import time
import os

DB_FILENAME = "pagination_demo.db"
TOTAL_RECORDS = 1000000

def setup_database():
    """Tạo database và chèn 1 triệu dòng thật nhanh"""
    conn = sqlite3.connect(DB_FILENAME)
    cursor = conn.cursor()
    
    # Bật các config của SQLite để thao tác cực nhanh trên RAM/Disk
    cursor.execute("PRAGMA journal_mode = OFF")
    cursor.execute("PRAGMA synchronous = 0")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            author TEXT,
            random_data TEXT
        )
    """)
    
    cursor.execute("SELECT COUNT(*) FROM books")
    current_count = cursor.fetchone()[0]
    
    if current_count < TOTAL_RECORDS:
        records_to_insert = TOTAL_RECORDS - current_count
        print(f"[*] Đang chèn {records_to_insert:,} bản ghi vào hệ thống, vui lòng chờ khoảng 1-3 giây...")
        
        # Tạo dữ liệu giả bulk insert
        batch_size = 100000
        for _ in range(records_to_insert // batch_size):
            # Tạo 1 mảng dữ liệu lặp lại khá dài để làm bài toán thực tế hơn
            data = [
                ("Tên sách mẫu demo " + str(i), "Tác giả ABC", "Phần mô tả dài để làm tăng dung lượng DB " * 3)
                for i in range(batch_size)
            ]
            cursor.executemany("INSERT INTO books (title, author, random_data) VALUES (?, ?, ?)", data)
            conn.commit()
        print(f"[+] Hoàn tất việc tạo {TOTAL_RECORDS:,} dòng dữ liệu SQLite!")
    else:
        print(f"[*] Database đã có đủ {TOTAL_RECORDS:,} dòng. Bỏ qua bước nạp liệu.")
        
    return conn

def test_offset_pagination(conn, target_page=900000, limit=10):
    """Chiến thuật cũ: OFFSET / LIMIT"""
    print("\n--- BÀI TEST 1: KỸ THUẬT OFFSET / LIMIT ---")
    cursor = conn.cursor()
    
    start_time = time.perf_counter()
    # SQL phải mở toàn bộ các file disk, đếm bỏ qua đủ 900 ngàn dòng để lấy 10 dòng đích
    cursor.execute(f"SELECT * FROM books ORDER BY id LIMIT {limit} OFFSET {target_page}")
    results = cursor.fetchall()
    end_time = time.perf_counter()
    
    duration = end_time - start_time
    print(f"Lệnh SQL: SELECT * FROM books ORDER BY id LIMIT {limit} OFFSET {target_page}")
    print(f"Thời gian truy xuất: {duration:.5f} giây")
    return duration

def test_cursor_pagination(conn, last_id=900000, limit=10):
    """Chiến thuật tối ưu: CURSOR (Dùng thuộc tính Index trực tiếp như WHERE)"""
    print("\n--- BÀI TEST 2: KỸ THUẬT CURSOR (Chiến thuật ABC) ---")
    cursor = conn.cursor()
    
    start_time = time.perf_counter()
    # Nhờ cây B-Tree Index của khoá chính id, SQL nhảy đến vị trí đích trong tíc tắc
    cursor.execute(f"SELECT * FROM books WHERE id > {last_id} ORDER BY id LIMIT {limit}")
    results = cursor.fetchall()
    end_time = time.perf_counter()
    
    duration = end_time - start_time
    print(f"Lệnh SQL: SELECT * FROM books WHERE id > {last_id} ORDER BY id LIMIT {limit}")
    print(f"Thời gian truy xuất: {duration:.5f} giây")
    return duration

if __name__ == "__main__":
    print(f"========== BẮT ĐẦU CHƯƠNG TRÌNH SO SÁNH HIỆU NĂNG ==========")
    conn = setup_database()
    
    # Clear cache giả định
    conn.execute("PRAGMA shrink_memory")
    
    time_offset = test_offset_pagination(conn)
    time_cursor = test_cursor_pagination(conn)
    
    print("\n========== KẾT LUẬN ==========")
    # Tính toán tỷ lệ chênh lệch
    if time_cursor > 0:
        speedup = time_offset / time_cursor
        print(f"-> Chiến thuật CURSOR nhanh hơn gấp: {speedup:,.2f} LẦN so với OFFSET truyền thống.")
    else:
        print("-> CURSOR quá nhanh (dưới hệ số thời gian trễ máy tính)! Không thể đo tỷ lệ chia nhỏ.")
        
    print("\n=> GIẢI THÍCH (Dùng để trả lời khi Demo):")
    print("Mặc dù cả hai cột ID đều có Index, với lệnh OFFSET hệ CSDL vẫn có thao tác 'scan' dọc theo B-Tree")
    print("từ điểm mốc 0, đếm đủ 900 ngàn bản ghi rồi vứt đi, rất tốn Disk IO.")
    print("Ngược lại, với mệnh đề WHERE id > X, hệ thống định vị điểm X ngay lập tức với độ phức tạp O(logN).")
    
    conn.close()
