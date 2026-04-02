"""
Book Management API — FastAPI Demo
===================================
Demo cho buổi 5: Data Modeling, Resource Design & Pagination

Chạy server:
    uvicorn main:app --reload

Swagger UI:     http://localhost:8000/docs
ReDoc:          http://localhost:8000/redoc
OpenAPI JSON:   http://localhost:8000/openapi.json
"""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

# ============================================
# Pydantic Models (Data Modeling)
# ============================================

class BookCreate(BaseModel):
    title: str
    author: str
    genre: Optional[str] = None
    year: Optional[int] = None

class Book(BaseModel):
    id: int
    title: str
    author: str
    genre: Optional[str] = None
    year: Optional[int] = None

class User(BaseModel):
    id: int
    name: str
    email: str

class BorrowRecord(BaseModel):
    id: int
    user_id: int
    book_id: int
    borrow_date: date
    return_date: Optional[date] = None

class Review(BaseModel):
    id: int
    book_id: int
    user_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: str
    created_at: int # Timestamp để demo cursor pagination

# Các schema trả về cho phân trang
class BookPagination(BaseModel):
    data: List[Book]
    page: int
    size: int
    total_pages: int
    total_items: int

class ReviewPagination(BaseModel):
    data: List[Review]
    next_cursor: Optional[int] = None

# ============================================
# In-memory database (dữ liệu mẫu)
# ============================================

books_db: list[dict] = [
    {"id": 1, "title": "Dế Mèn Phiêu Lưu Ký", "author": "Tô Hoài", "genre": "fiction", "year": 1941},
    {"id": 2, "title": "Số Đỏ", "author": "Vũ Trọng Phụng", "genre": "fiction", "year": 1936},
    {"id": 3, "title": "Clean Code", "author": "Robert C. Martin", "genre": "technology", "year": 2008},
    {"id": 4, "title": "The Pragmatic Programmer", "author": "Andrew Hunt", "genre": "technology", "year": 1999},
    {"id": 5, "title": "Design Patterns", "author": "Erich Gamma", "genre": "technology", "year": 1994},
]
next_id = 6

users_db: list[dict] = [
    {"id": 1, "name": "Nguyễn Văn A", "email": "a@example.com"},
    {"id": 2, "name": "Trần Thị B", "email": "b@example.com"}
]

borrowings_db: list[dict] = [
    {"id": 1, "user_id": 1, "book_id": 1, "borrow_date": date(2023, 10, 1), "return_date": date(2023, 10, 15)},
    {"id": 2, "user_id": 1, "book_id": 2, "borrow_date": date(2023, 11, 1), "return_date": None},
    {"id": 3, "user_id": 2, "book_id": 3, "borrow_date": date(2023, 12, 5), "return_date": None},
]

# Dữ liệu reviews có created_at để demo cursor pagination
reviews_db: list[dict] = [
    {"id": 5, "book_id": 1, "user_id": 1, "rating": 5, "comment": "Đọc lại vẫn hay", "created_at": 1699111032},
    {"id": 4, "book_id": 3, "user_id": 1, "rating": 5, "comment": "Must read for devs", "created_at": 1699024632},
    {"id": 3, "book_id": 2, "user_id": 2, "rating": 3, "comment": "Tạm được", "created_at": 1698938232},
    {"id": 2, "book_id": 1, "user_id": 1, "rating": 4, "comment": "Khá hay", "created_at": 1698851832},
    {"id": 1, "book_id": 1, "user_id": 2, "rating": 5, "comment": "Tuyệt vời", "created_at": 1698765432},
]


# ============================================
# FastAPI App
# ============================================

app = FastAPI(
    title="Library Management API",
    description="API quản lý thư viện — Demo buổi 5: Data Modeling, Resource Design, và Pagination",
    version="1.0.0",
)


# ============================================
# 1. Offset / Limit Pagination Endpoint
# ============================================
@app.get(
    "/books",
    response_model=List[Book],
    summary="Lấy danh sách sách (Offset/Limit Pagination)",
    tags=["Books"],
)
def get_books(
    offset: int = Query(0, ge=0, description="Số lượng bản ghi bỏ qua từ đầu"),
    limit: int = Query(10, ge=1, le=100, description="Số lượng bản ghi tối đa lấy về")
):
    """
    Sử dụng offset và limit để phân trang.
    Ví dụ: Lấy 2 cuốn sách đầu tiên (offset=0, limit=2)
    """
    return books_db[offset : offset + limit]


# ============================================
# 2. Page-based Pagination Endpoint
# ============================================
@app.get(
    "/books/search",
    response_model=BookPagination,
    summary="Tìm kiếm sách (Page-based Pagination)",
    tags=["Books"],
)
def search_books(
    keyword: str = Query(..., description="Từ khóa tìm kiếm theo tiêu đề hoặc tác giả"),
    page: int = Query(1, ge=1, description="Số thứ tự trang (bắt đầu từ 1)"),
    size: int = Query(2, ge=1, le=50, description="Kích thước một trang")
):
    """
    Tìm kiếm sách theo từ khóa và trả về dữ liệu phân trang thân thiện.
    Bản chất bên dưới vẫn tính toán offset: offset = (page - 1) * size
    """
    kw = keyword.lower()
    filtered = [
        b for b in books_db 
        if kw in b["title"].lower() or kw in b["author"].lower()
    ]
    
    total_items = len(filtered)
    total_pages = (total_items + size - 1) // size
    
    offset = (page - 1) * size
    data = filtered[offset : offset + size]
    
    return {
        "data": data,
        "page": page,
        "size": size,
        "total_pages": total_pages,
        "total_items": total_items
    }


@app.get("/books/{id}", response_model=Book, tags=["Books"])
def get_book_by_id(id: int):
    for book in books_db:
        if book["id"] == id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")


@app.post("/books", response_model=Book, status_code=201, tags=["Books"])
def create_book(book: BookCreate):
    global next_id
    new_book = {"id": next_id, **book.model_dump()}
    books_db.append(new_book)
    next_id += 1
    return new_book


# ============================================
# 3. Resource Tree (Nested Resource)
# /users/{id}/borrowings
# ============================================
@app.get(
    "/users/{user_id}/borrowings",
    response_model=List[BorrowRecord],
    summary="Lấy danh sách sách đang mượn của User",
    tags=["Users & Borrowing"],
)
def get_user_borrowings(user_id: int):
    """
    Demo thiết kế Endpoint theo Resource Tree:
    /users/{user_id}/borrowings thể hiện mối quan hệ 'borrowings' thuộc về 'user_id'.
    """
    user_exists = any(u["id"] == user_id for u in users_db)
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found")
        
    user_borrowings = [b for b in borrowings_db if b["user_id"] == user_id]
    return user_borrowings


# ============================================
# 4. Cursor-based Pagination Endpoint
# /reviews
# ============================================
@app.get(
    "/reviews",
    response_model=ReviewPagination,
    summary="Lấy danh sách review (Cursor-based Pagination)",
    tags=["Reviews"],
)
def get_reviews(
    cursor: Optional[int] = Query(None, description="Timestamp của record cuối cùng ở lần lấy trước"),
    limit: int = Query(2, ge=1, le=10, description="Kích thước batch lấy ra")
):
    """
    Demo Cursor-based Pagination (phù hợp cho Endless Scroll).
    Dựa vào `created_at` timestamp thay vì offset. Mảng `reviews_db` luôn được sắp xếp mới nhất ở đầu.
    """
    # Nếu không có cursor, lấy từ đầu tiên
    start_index = 0
    if cursor is not None:
        # Tìm vị trí của phần tử CÓ created_at nhỏ hơn cursor 
        # (hoặc nhỏ hơn/bằng nếu logic strict, ở đây giả sử created_at là duy nhất để demo)
        found = False
        for i, rev in enumerate(reviews_db):
            if rev["created_at"] < cursor:
                start_index = i
                found = True
                break
        if not found:
            return {"data": [], "next_cursor": None}

    # Cắt mảng từ start_index với số lượng limit
    sliced_data = reviews_db[start_index : start_index + limit]
    
    # Xác định next_cursor
    next_cursor = None
    if len(sliced_data) > 0:
        last_item = sliced_data[-1]
        # Kiểm tra xem có phần tử nào đằng sau last_item không (còn dữ liệu)
        # Trong thực tế DB, query LIMIT limit + 1 để check next cursor
        last_item_index = start_index + len(sliced_data) - 1
        if last_item_index + 1 < len(reviews_db):
            next_cursor = last_item["created_at"]

    return {
        "data": sliced_data,
        "next_cursor": next_cursor
    }
