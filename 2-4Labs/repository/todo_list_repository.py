# Repository Pattern — TodoListRepository
# Этот класс отвечает за сохранение и загрузку агрегата из базы данных
# Скрывает работу с БД от domain-слоя

from typing import Optional, List

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models import TodoList as DBTodoList, Item as DBItem
from domain.todo_list import TodoList
from domain.todo_item import TodoItem


class TodoListRepository:
    # Repository для работы с агрегатом TodoList
    # Преобразует domain-объекты в БД и обратно

    def __init__(self, session: AsyncSession):
        # Сессия базы данных для выполнения запросов
        self.session = session

    async def get_by_id(self, list_id: int) -> Optional[TodoList]:
        # Получить агрегат TodoList по ID из базы данных
        # Возвращает domain-объект, а не модель БД

        # Ищем список в БД по ID
        result = await self.session.execute(
            select(DBTodoList).where(DBTodoList.id == list_id)
        )
        db_list = result.scalar_one_or_none()

        if not db_list:
            return None

        # Создаём domain-агрегат из данных БД
        todo_list = TodoList(
            id=db_list.id,
            name=db_list.name,
        )

        # Загружаем все элементы этого списка
        items_result = await self.session.execute(
            select(DBItem).where(DBItem.todo_list_id == list_id)
        )
        db_items = items_result.scalars().all()

        # Добавляем элементы в агрегат
        for db_item in db_items:
            item = TodoItem(
                id=db_item.id,
                name=db_item.name,
                text=db_item.text,
                is_done=db_item.is_done
            )
            todo_list._items.append(item)

        # Пересчитываем счётчики из реально загруженных элементов
        todo_list._update_counts()

        return todo_list

    # Сохраняет агрегат TodoList в БД.
    # Если список новый - создаёт запись, иначе обновляет существующую.
    # Также синхронизирует все Items (добавление, обновление, удаление)
    # и сохраняет актуальные счётчики (completed_count, total_count).

    async def save(self, todo_list: TodoList) -> TodoList:
        if todo_list.id is None:
            # Создаём новый список в БД
            db_list = DBTodoList(
                name=todo_list.name,
                completed_count=todo_list.completed_count,
                total_count=todo_list.total_count
            )
            self.session.add(db_list)
            await self.session.flush()
            todo_list.set_id(db_list.id)
        else:
            # Обновляем существующий список
            result = await self.session.execute(
                select(DBTodoList).where(DBTodoList.id == todo_list.id)
            )
            db_list = result.scalar_one_or_none()

            if not db_list:
                raise ValueError(f"Список с id {todo_list.id} не найден")

            db_list.name = todo_list.name
            db_list.completed_count = todo_list.completed_count
            db_list.total_count = todo_list.total_count

        # Синхронизируем элементы (создаём, обновляем, удаляем)
        await self._sync_items(todo_list)

        # Ещё раз фиксируем счётчики перед сохранением
        db_list.completed_count = todo_list.completed_count
        db_list.total_count = todo_list.total_count

        # Сохраняем изменения в БД
        await self.session.commit()
        await self.session.refresh(db_list)

        return todo_list

    async def _sync_items(self, todo_list: TodoList) -> None:
        # Синхронизировать элементы агрегата с базой данных
        # Удаляет лишние, создаёт новые, обновляет изменённые

        # Получаем ID элементов, которые есть в агрегате
        existing_ids = {item.id for item in todo_list.items if item.id is not None}

        # Удаляем элементы, которых нет в агрегате
        # Если список пустой, удаляем все элементы списка
        if todo_list.id is not None:
            if existing_ids:
                await self.session.execute(
                    delete(DBItem).where(
                        DBItem.todo_list_id == todo_list.id,
                        DBItem.id.notin_(existing_ids)
                    )
                )
            else:
                await self.session.execute(
                    delete(DBItem).where(DBItem.todo_list_id == todo_list.id)
                )

        # Создаём или обновляем элементы
        for item in todo_list.items:
            if item.id is None:
                # Новый элемент — создаём в БД
                db_item = DBItem(
                    name=item.name,
                    text=item.text,
                    is_done=item.is_done,
                    todo_list_id=todo_list.id
                )
                self.session.add(db_item)
                await self.session.flush()
                item.id = db_item.id
            else:
                # Существующий элемент — обновляем в БД
                result = await self.session.execute(
                    select(DBItem).where(
                        DBItem.id == item.id,
                        DBItem.todo_list_id == todo_list.id
                    )
                )
                db_item = result.scalar_one_or_none()

                if db_item:
                    db_item.name = item.name
                    db_item.text = item.text
                    db_item.is_done = item.is_done

    async def delete(self, list_id: int) -> bool:
        # Удалить агрегат TodoList из базы данных
        # Возвращает True если удалено, False если не найдено

        result = await self.session.execute(
            select(DBTodoList).where(DBTodoList.id == list_id)
        )
        db_list = result.scalar_one_or_none()

        if not db_list:
            return False

        # Сначала удаляем элементы списка
        await self.session.execute(
            delete(DBItem).where(DBItem.todo_list_id == list_id)
        )

        # Потом удаляем сам список
        await self.session.delete(db_list)
        await self.session.commit()
        return True

    async def get_all(self) -> List[TodoList]:
        # Получить все агрегаты TodoList из базы данных
        # Возвращает список domain-объектов

        # Получаем все списки из БД
        result = await self.session.execute(select(DBTodoList))
        db_lists = result.scalars().all()

        todo_lists = []
        for db_list in db_lists:
            # Создаём domain-агрегат для каждого списка
            todo_list = TodoList(
                id=db_list.id,
                name=db_list.name,
            )

            # Загружаем элементы этого списка
            items_result = await self.session.execute(
                select(DBItem).where(DBItem.todo_list_id == db_list.id)
            )
            db_items = items_result.scalars().all()

            for db_item in db_items:
                item = TodoItem(
                    id=db_item.id,
                    name=db_item.name,
                    text=db_item.text,
                    is_done=db_item.is_done
                )
                todo_list._items.append(item)

            # Пересчитываем счётчики из реально загруженных элементов
            todo_list._update_counts()

            todo_lists.append(todo_list)

        return todo_lists