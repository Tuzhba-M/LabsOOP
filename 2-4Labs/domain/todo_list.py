# Domain Aggregate — список дел (TodoList)
# Это главный класс, который управляет элементами (Items)
# Не связан с базой данных — чистое ООП

from dataclasses import dataclass, field
from typing import List, Optional
from domain.todo_item import TodoItem


@dataclass
class TodoList:
    # Агрегат списка дел
    # Инкапсулирует работу с элементами внутри себя
    
    # ID списка (заполняется при сохранении в БД)
    id: Optional[int] = None
    
    # Название списка (обязательно)
    name: str = ""
    
    # Список элементов внутри агрегата (скрыт от внешнего изменения)
    _items: List[TodoItem] = field(default_factory=list)
    
    # Счётчик выполненных элементов (для прогресса)
    _completed_count: int = 0
    
    # Счётчик всех элементов (для прогресса)
    _total_count: int = 0
    

    # Свойства для чтения (только чтение, нельзя изменить снаружи)
    
    @property
    def items(self) -> List[TodoItem]:
        # Возвращает копию списка элементов — нельзя изменить снаружи
        return list(self._items)
    
    @property
    def completed_count(self) -> int:
        # Количество выполненных элементов
        return self._completed_count
    
    @property
    def total_count(self) -> int:
        # Общее количество элементов
        return self._total_count
    
    @property
    def progress(self) -> float:
        # Прогресс выполнения в процентах (0.0 — 100.0)
        if self._total_count == 0:
            return 0.0
        return round((self._completed_count / self._total_count) * 100, 2)
    

    # Методы агрегата (единственный способ изменить элементы)
    
    def add_item(self, name: str, text: str = "", is_done: bool = False) -> TodoItem:
        # Добавить новый элемент в список
        # Это единственный способ добавить Item — через агрегат
        if not name.strip():
            raise ValueError("Название не может быть пустым")
        
        # Создаём новый элемент
        item = TodoItem(name=name, text=text, is_done=is_done)
        self._items.append(item)
        
        # Обновляем счётчики
        self._update_counts()
        
        return item
    

    def remove_item(self, item_id: int) -> None:
        # Удалить элемент из списка по ID
        # Это единственный способ удалить Item — через агрегат
        
        before_count = len(self._items)
        self._items = [i for i in self._items if i.id != item_id]
        
        # Если ничего не удалилось — ошибка
        if len(self._items) == before_count:
            raise ValueError(f"Элемент с id {item_id} не найден")
        
        # Обновляем счётчики
        self._update_counts()
    

    def mark_completed(self, item_id: int) -> None:
        # Отметить элемент как выполненный
        # Меняет is_done на True и обновляет прогресс
        item = self.get_item(item_id)
        item.is_done = True
        self._update_counts()
    

    def mark_uncompleted(self, item_id: int) -> None:
        # Отметить элемент как невыполненный
        # Меняет is_done на False и обновляет прогресс
        item = self.get_item(item_id)
        item.is_done = False
        self._update_counts()
    

    def update_item(
        self,
        item_id: int,
        name: Optional[str] = None,
        text: Optional[str] = None,
        is_done: Optional[bool] = None,
    ) -> None:
        # Обновить данные элемента по ID
        # Можно изменить название, описание или статус
        
        item = self.get_item(item_id)
        
        if name is not None:
            if not name.strip():
                raise ValueError("Название не может быть пустым")
            item.name = name
        
        if text is not None:
            item.text = text
        
        if is_done is not None:
            item.is_done = is_done
        
        self._update_counts()
    

    def get_item(self, item_id: int) -> TodoItem:
        # Получить элемент по ID
        # Возвращает элемент или ошибку, если не найден
        for item in self._items:
            if item.id == item_id:
                return item
        raise ValueError(f"Элемент с id {item_id} не найден")
    

    def _update_counts(self) -> None:
        # Обновить счётчики выполненных и общих элементов
        # Вызывается автоматически при любом изменении элементов
        self._total_count = len(self._items)
        self._completed_count = sum(1 for item in self._items if item.is_done)
    

    def set_id(self, id: int) -> None:
        # Установить ID списка (при сохранении в БД)
        self.id = id