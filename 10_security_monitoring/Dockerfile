FROM python:3.11-slim

WORKDIR /app

# Cài dependencies trước (tận dụng Docker layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY main.py .

# Tạo thư mục logs (dùng khi chạy local, trong K8s dùng stdout)
RUN mkdir -p logs

EXPOSE 8000

# LOG_TO_FILE=false → chỉ ghi ra stdout (Promtail thu thập)
ENV LOG_TO_FILE=false

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
