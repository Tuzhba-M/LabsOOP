# Domain Entity — элемент списка дел (Item)
# Это простой класс, не связан с базой данных
# Хранит данные одного элемента списка

from dataclasses import dataclass
from typing import Optional


@dataclass
class TodoItem:
    # Элемент списка дел
    # Принадлежит агрегату TodoList, не знает о базе данных
    
    # ID элемента (заполняется при сохранении в БД)
    id: Optional[int] = None
    
    # Название элемента (обязательно)
    name: str = ""
    
    # Описание элемента (необязательно)
    text: str = ""
    
    # Статус выполнения (False = не сделано, True = сделано)
    is_done: bool = False
    
    # Нет поля todo_list_id — элемент не знает о родителе
    # Он принадлежит агрегату TodoList