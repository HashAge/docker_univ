FROM python:3.9

WORKDIR /app

# Устанавливаем переменные среды
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

# Копируем только requirements.txt сначала для кэширования
COPY ./app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальное содержимое папки app
COPY ./app .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
