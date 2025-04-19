#!/bin/sh

echo "Ждём 5 секунд, пока MinIO поднимется..."
sleep 5

echo "Запускаем Report Service..."
uvicorn main:app --host 0.0.0.0 --port 8001
