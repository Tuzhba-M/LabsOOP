# Use Cases — бизнес-логика работы с агрегатом
# Этот класс реализует паттерн: Получить агрегат - вызвать метод - сохранить
# Соединяет Repository и domain-слой

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from domain.todo_list import TodoList
from domain.todo_item import TodoItem
from repository.todo_list_repository import TodoListRepository


class TodoListUseCases:
    # Use Cases для работы с TodoList
    # Реализует бизнес-логику через агрегат и repository

    def __init__(self, session: AsyncSession):
        # Сессия базы данных
        self.session = session
        # Repository для работы с БД
        self.repository = TodoListRepository(session)

    # Операции со списками (TodoList)

    async def create_list(self, name: str) -> TodoList:
        # Создать новый список дел
        if not name.strip():
            raise ValueError("Название не может быть пустым")

        todo_list = TodoList(name=name)
        return await self.repository.save(todo_list)

    async def get_list(self, list_id: int) -> Optional[TodoList]:
        # Получить список по ID
        return await self.repository.get_by_id(list_id)

    async def get_all_lists(self) -> List[TodoList]:
        # Получить все списки
        return await self.repository.get_all()

    async def update_list(self, list_id: int, name: str) -> Optional[TodoList]:
        # Обновить название списка
        if not name.strip():
            raise ValueError("Название не может быть пустым")

        todo_list = await self.repository.get_by_id(list_id)
        if not todo_list:
            return None

        todo_list.name = name
        return await self.repository.save(todo_list)

    async def delete_list(self, list_id: int) -> bool:
        # Удалить список
        return await self.repository.delete(list_id)

    # Операции с элементами (Item) — через агрегат

    async def add_item(
        self,
        list_id: int,
        name: str,
        text: str = "",
        is_done: bool = False
    ) -> Optional[TodoItem]:
        # Добавить элемент в список через агрегат
        # Паттерн: Get Aggregate → Call Method → Save

        # 1. Получаем агрегат из БД
        todo_list = await self.repository.get_by_id(list_id)
        if not todo_list:
            return None

        # 2. Вызываем метод агрегата (единственный способ добавить Item)
        item = todo_list.add_item(name=name, text=text, is_done=is_done)

        # 3. Сохраняем изменения через Repository
        await self.repository.save(todo_list)

        return item

    async def update_item(
        self,
        list_id: int,
        item_id: int,
        name: Optional[str] = None,
        text: Optional[str] = None,
        is_done: Optional[bool] = None
    ) -> Optional[TodoItem]:
        # Обновить элемент через агрегат
        # Паттерн: Get Aggregate → Call Method → Save

        todo_list = await self.repository.get_by_id(list_id)
        if not todo_list:
            return None

        todo_list.update_item(item_id=item_id, name=name, text=text, is_done=is_done)
        await self.repository.save(todo_list)

        return todo_list.get_item(item_id)

    async def remove_item(self, list_id: int, item_id: int) -> bool:
        # Удалить элемент через агрегат
        # Паттерн: Get Aggregate → Call Method → Save

        todo_list = await self.repository.get_by_id(list_id)
        if not todo_list:
            return False

        todo_list.remove_item(item_id)
        await self.repository.save(todo_list)

        return True

    async def mark_item_completed(self, list_id: int, item_id: int) -> Optional[TodoItem]:
        # Отметить элемент как выполненный через агрегат
        # Паттерн: Get Aggregate → Call Method → Save

        todo_list = await self.repository.get_by_id(list_id)
        if not todo_list:
            return None

        todo_list.mark_completed(item_id)
        await self.repository.save(todo_list)

        return todo_list.get_item(item_id)

    async def mark_item_uncompleted(self, list_id: int, item_id: int) -> Optional[TodoItem]:
        # Отметить элемент как невыполненный через агрегат
        # Паттерн: Get Aggregate → Call Method → Save

        todo_list = await self.repository.get_by_id(list_id)
        if not todo_list:
            return None

        todo_list.mark_uncompleted(item_id)
        await self.repository.save(todo_list)

        return todo_list.get_item(item_id)