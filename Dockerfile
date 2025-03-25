# Используем официальный образ Python
FROM python:3.10

WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    wget \
    curl \
    unzip \
    libopenblas-dev \
    libomp-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем только файл зависимостей
COPY requirements.txt .

# Устанавливаем pip и зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt --index-url https://download.pytorch.org/whl/cpu

# Копируем весь проект
COPY . .

EXPOSE 10000

ENV PORT=10000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
