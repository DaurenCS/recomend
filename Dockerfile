# Используем официальный образ Python
FROM python:3.10

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости для корректной работы faiss и torch
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    wget \
    curl \
    unzip \
    libopenblas-dev \
    libomp-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем только файл зависимостей, чтобы использовать кеш Docker
COPY requirements.txt .

# Устанавливаем pip и сначала numpy, затем остальные зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir numpy==2.0.2 && \
    pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Открываем порт
EXPOSE 8000

# Запускаем FastAPI-приложение
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
