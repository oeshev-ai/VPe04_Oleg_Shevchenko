# Server Time API

Простой тестовый бэкенд на FastAPI. Эндпоинт `GET /time` возвращает текущее время сервера.

## Запуск локально

```powershell
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Сервер слушает `http://127.0.0.1:8000`. Интерактивная документация: `http://127.0.0.1:8000/docs`.

## Запуск в Docker

```powershell
docker build -t server-time .
docker run --rm -p 8000:8000 server-time
```

## Пример ответа

```http
GET /time
```

```json
{
  "server_time": "2026-11-17T23:08:50+07:00",
  "timezone": "Новосибирское стандартное время",
  "unix": 1794931730
}
```

- `server_time` — локальное время сервера в формате ISO 8601
- `timezone` — название часового пояса
- `unix` — время в секундах с 1 января 1970 года (UTC)
