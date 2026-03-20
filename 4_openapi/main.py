"""
Book Management API — FastAPI Demo
===================================
Demo cho buổi 4: API Specification & OpenAPI

Chạy server:
    uvicorn demo.main:app --reload

Swagger UI:     http://localhost:8000/docs
ReDoc:          http://localhost:8000/redoc
OpenAPI JSON:   http://localhost:8000/openapi.json
"""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

# ============================================
# Pydantic Models (tương ứng components/schemas)
# ============================================

class BookCreate(BaseModel):
    """Schema để tạo hoặc cập nhật sách (không có id)"""
    title: str
    author: str
    genre: Optional[str] = None
    year: Optional[int] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Dế Mèn Phiêu Lưu Ký",
                    "author": "Tô Hoài",
                    "genre": "fiction",
                    "year": 1941
                }
            ]
        }
    }


class Book(BaseModel):
    """Schema đầy đủ của sách (có id)"""
    id: int
    title: str
    author: str
    genre: Optional[str] = None
    year: Optional[int] = None


# ============================================
# In-memory database (dữ liệu mẫu)
# ============================================

books_db: list[dict] = [
    {
        "id": 1,
        "title": "Dế Mèn Phiêu Lưu Ký",
        "author": "Tô Hoài",
        "genre": "fiction",
        "year": 1941,
    },
    {
        "id": 2,
        "title": "Số Đỏ",
        "author": "Vũ Trọng Phụng",
        "genre": "fiction",
        "year": 1936,
    },
    {
        "id": 3,
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "genre": "technology",
        "year": 2008,
    },
]

# Auto-increment ID
next_id = 4

# ============================================
# FastAPI App
# ============================================

app = FastAPI(
    title="Book Management API",
    description="API quản lý sách cho thư viện — Demo buổi 4: OpenAPI Specification",
    version="1.0.0",
    contact={
        "name": "API Support",
        "email": "support@example.com",
    },
)


# ============================================
# Endpoints
# ============================================

@app.get(
    "/books",
    response_model=list[Book],
    summary="Lấy danh sách sách",
    description="Trả về danh sách tất cả sách trong thư viện. Có thể lọc theo thể loại.",
    tags=["Books"],
)
def get_books(
    genre: Optional[str] = Query(
        None,
        description="Lọc sách theo thể loại",
        example="fiction",
    )
):
    if genre:
        return [b for b in books_db if b.get("genre") == genre]
    return books_db


@app.get(
    "/books/{id}",
    response_model=Book,
    summary="Lấy chi tiết sách",
    description="Trả về thông tin chi tiết của một cuốn sách theo ID",
    tags=["Books"],
    responses={
        404: {
            "description": "Không tìm thấy sách",
            "content": {
                "application/json": {
                    "example": {"detail": "Book not found"}
                }
            },
        }
    },
)
def get_book_by_id(id: int):
    for book in books_db:
        if book["id"] == id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")


@app.post(
    "/books",
    response_model=Book,
    status_code=201,
    summary="Thêm sách mới",
    description="Tạo một cuốn sách mới trong thư viện",
    tags=["Books"],
    responses={
        422: {"description": "Dữ liệu không hợp lệ"},
    },
)
def create_book(book: BookCreate):
    global next_id
    new_book = {
        "id": next_id,
        "title": book.title,
        "author": book.author,
        "genre": book.genre,
        "year": book.year,
    }
    books_db.append(new_book)
    next_id += 1
    return new_book


@app.put(
    "/books/{id}",
    response_model=Book,
    summary="Cập nhật thông tin sách",
    description="Cập nhật toàn bộ thông tin của một cuốn sách",
    tags=["Books"],
    responses={
        404: {
            "description": "Không tìm thấy sách",
            "content": {
                "application/json": {
                    "example": {"detail": "Book not found"}
                }
            },
        },
        422: {"description": "Dữ liệu không hợp lệ"},
    },
)
def update_book(id: int, book: BookCreate):
    for i, b in enumerate(books_db):
        if b["id"] == id:
            books_db[i] = {
                "id": id,
                "title": book.title,
                "author": book.author,
                "genre": book.genre,
                "year": book.year,
            }
            return books_db[i]
    raise HTTPException(status_code=404, detail="Book not found")


@app.delete(
    "/books/{id}",
    summary="Xóa sách",
    description="Xóa một cuốn sách khỏi thư viện",
    tags=["Books"],
    responses={
        404: {
            "description": "Không tìm thấy sách",
            "content": {
                "application/json": {
                    "example": {"detail": "Book not found"}
                }
            },
        },
    },
)
def delete_book(id: int):
    for i, b in enumerate(books_db):
        if b["id"] == id:
            books_db.pop(i)
            return {"message": "Book deleted successfully"}
    raise HTTPException(status_code=404, detail="Book not found")

# python -m uvicorn main:app --reload
