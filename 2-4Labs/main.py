# Главный файл приложения

from fastapi import FastAPI
import uvicorn
from database import init_db
from routes.todo_list import init_routes as init_todo_routes

# Создание приложения
app = FastAPI(title="TodoList API")

# Инициализация маршрутов
def bootstrap(app: FastAPI):
    init_todo_routes(app, None)

# Создание таблиц при запуске
@app.on_event("startup")
async def on_startup():
    await init_db()
    bootstrap(app)
    print("База данных инициализирована!")

# Запуск сервера
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)