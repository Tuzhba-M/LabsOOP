# Pydantic схемы для валидации данных

from pydantic import BaseModel
from typing import Optional


# TodoList схемы
class TodoListCreate(BaseModel):
    name: str


class TodoListUpdate(BaseModel):
    name: Optional[str] = None


class TodoListResponse(BaseModel):
    id: int
    name: str
    completed_count: int      # Кол-во выполненных (из БД)
    total_count: int          # Общее кол-во (из БД)
    progress: float           # Прогресс в процентах (вычисляемое поле)

    class Config:
        from_attributes = True


# Item схемы
class ItemCreate(BaseModel):
    name: str
    text: Optional[str] = None
    is_done: bool = False


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    text: Optional[str] = None
    is_done: Optional[bool] = None


class ItemResponse(BaseModel):
    id: int
    name: str
    text: Optional[str]
    is_done: bool

    class Config:
        from_attributes = True