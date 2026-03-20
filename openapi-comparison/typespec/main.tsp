import "@typespec/http";
import "@typespec/rest";
import "@typespec/openapi3";

using TypeSpec.Http;
using TypeSpec.Rest;

/**
 * API quản lý thư viện — Demo TypeSpec format.
 * TypeSpec compile ra OpenAPI YAML tự động.
 */
@service({
  title: "Library Management API",
})
@server("http://localhost:8000", "Local development")
namespace LibraryAPI;

// ============================================
// Models (tương tự components/schemas)
// ============================================

/** Thông tin đầy đủ của sách (có ID) */
model Book {
  /** ID tự sinh bởi server */
  id: int32;

  /** Tên sách */
  title: string;

  /** Tác giả */
  author: string;

  /** Thể loại sách */
  genre?: string;

  /** Năm xuất bản */
  year?: int32;

  /** Còn sẵn không */
  available?: boolean = true;
}

/** Dữ liệu để tạo hoặc cập nhật sách (không có ID) */
model BookCreate {
  title: string;
  author: string;
  genre?: string;
  year?: int32;
  available?: boolean = true;
}

/** Response lỗi */
model ErrorResponse {
  detail: string;
}

/** Response xóa thành công */
model DeleteResponse {
  message: string;
}

// ============================================
// Operations (endpoints)
// ============================================

@route("/books")
@tag("Books")
namespace Books {

  /** Lấy danh sách sách — hỗ trợ filter theo genre và author */
  @get
  op list(
    @query genre?: string,
    @query author?: string,
  ): Book[];

  /** Thêm sách mới vào thư viện */
  @post
  op create(@body book: BookCreate): {
    @statusCode statusCode: 201;
    @body body: Book;
  } | {
    @statusCode statusCode: 422;
    @body body: ErrorResponse;
  };

  /** Lấy chi tiết một cuốn sách */
  @get
  @route("{id}")
  op read(@path id: int32): Book | {
    @statusCode statusCode: 404;
    @body body: ErrorResponse;
  };

  /** Cập nhật thông tin sách */
  @put
  @route("{id}")
  op update(@path id: int32, @body book: BookCreate): Book | {
    @statusCode statusCode: 404;
    @body body: ErrorResponse;
  };

  /** Xóa sách khỏi thư viện */
  @delete
  @route("{id}")
  op delete(@path id: int32): DeleteResponse | {
    @statusCode statusCode: 404;
    @body body: ErrorResponse;
  };
}
