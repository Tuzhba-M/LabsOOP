# Маршруты API для TodoList и Item
# Эти классы обрабатывают HTTP-запросы и вызывают Use Cases

from fastapi import FastAPI, HTTPException
from typing import List

from schemas import TodoListCreate, TodoListResponse, TodoListUpdate, ItemCreate, ItemResponse, ItemUpdate
from use_cases.todo_list_use_cases import TodoListUseCases
from database import async_session


# Вспомогательная функция — создаёт Use Cases с сессией
def get_use_cases(session):
    return TodoListUseCases(session)


#  TodoList эндпоинты

class GetAllListsEndpoint:
    # Получить все списки дел. GET /todo/

    async def __call__(self) -> List[TodoListResponse]:
        async with async_session() as session:
            use_cases = get_use_cases(session)
            lists = await use_cases.get_all_lists()

            return [
                TodoListResponse(
                    id=list_.id,
                    name=list_.name,
                    completed_count=list_.completed_count,
                    total_count=list_.total_count,
                    progress=list_.progress
                )
                for list_ in lists
            ]


class GetListEndpoint:
    # Получить один список по ID. GET /todo/{list_id}

    async def __call__(self, list_id: int) -> TodoListResponse:
        async with async_session() as session:
            use_cases = get_use_cases(session)
            todo_list = await use_cases.get_list(list_id)

            if not todo_list:
                raise HTTPException(status_code=404, detail="Список не найден")

            return TodoListResponse(
                id=todo_list.id,
                name=todo_list.name,
                completed_count=todo_list.completed_count,
                total_count=todo_list.total_count,
                progress=todo_list.progress
            )


class CreateListEndpoint:
    # Создать новый список. POST /todo/

    async def __call__(self, todo: TodoListCreate) -> TodoListResponse:
        async with async_session() as session:
            use_cases = get_use_cases(session)
            todo_list = await use_cases.create_list(name=todo.name)

            return TodoListResponse(
                id=todo_list.id,
                name=todo_list.name,
                completed_count=todo_list.completed_count,
                total_count=todo_list.total_count,
                progress=todo_list.progress
            )


class UpdateListEndpoint:
    # Обновить список по ID. PUT /todo/{list_id}

    async def __call__(self, list_id: int, todo: TodoListUpdate) -> TodoListResponse:
        async with async_session() as session:
            use_cases = get_use_cases(session)
            todo_list = await use_cases.update_list(list_id=list_id, name=todo.name)

            if not todo_list:
                raise HTTPException(status_code=404, detail="Список не найден")

            return TodoListResponse(
                id=todo_list.id,
                name=todo_list.name,
                completed_count=todo_list.completed_count,
                total_count=todo_list.total_count,
                progress=todo_list.progress
            )


class DeleteListEndpoint:
    # Удалить список по ID. DELETE /todo/{list_id}

    async def __call__(self, list_id: int) -> dict:
        async with async_session() as session:
            use_cases = get_use_cases(session)
            success = await use_cases.delete_list(list_id)

            if not success:
                raise HTTPException(status_code=404, detail="Список не найден")

            return {"message": "Список удален"}


# Item эндпоинты (через агрегат)

class CreateItemEndpoint:
    # Создать новый элемент. POST /todo/{list_id}/items

    async def __call__(self, list_id: int, item: ItemCreate) -> ItemResponse:
        async with async_session() as session:
            use_cases = get_use_cases(session)
            created_item = await use_cases.add_item(
                list_id=list_id,
                name=item.name,
                text=item.text,
                is_done=item.is_done
            )

            if not created_item:
                raise HTTPException(status_code=404, detail="Список не найден")

            return ItemResponse(
                id=created_item.id,
                name=created_item.name,
                text=created_item.text,
                is_done=created_item.is_done
            )


class UpdateItemEndpoint:
    # Обновить элемент по ID. PUT /todo/{list_id}/items/{item_id}

    async def __call__(self, list_id: int, item_id: int, item: ItemUpdate) -> ItemResponse:
        async with async_session() as session:
            use_cases = get_use_cases(session)
            updated_item = await use_cases.update_item(
                list_id=list_id,
                item_id=item_id,
                name=item.name,
                text=item.text,
                is_done=item.is_done
            )

            if not updated_item:
                raise HTTPException(status_code=404, detail="Элемент не найден")

            return ItemResponse(
                id=updated_item.id,
                name=updated_item.name,
                text=updated_item.text,
                is_done=updated_item.is_done
            )


class DeleteItemEndpoint:
    # Удалить элемент по ID. DELETE /todo/{list_id}/items/{item_id}

    async def __call__(self, list_id: int, item_id: int) -> dict:
        async with async_session() as session:
            use_cases = get_use_cases(session)
            success = await use_cases.remove_item(
                list_id=list_id,
                item_id=item_id
            )

            if not success:
                raise HTTPException(status_code=404, detail="Элемент не найден")

            return {"message": "Элемент удален"}


# Регистрация маршрутов в приложении
def init_routes(app: FastAPI, conn) -> None:
    # Подключает все маршруты к FastAPI приложению
    # conn не используется — сессия создаётся внутри endpoint'ов

    get_all = GetAllListsEndpoint()
    get_one = GetListEndpoint()
    create = CreateListEndpoint()
    update = UpdateListEndpoint()
    delete = DeleteListEndpoint()
    create_item = CreateItemEndpoint()
    update_item = UpdateItemEndpoint()
    delete_item = DeleteItemEndpoint()

    app.add_api_route(path='/todo/', methods=['GET'], endpoint=get_all.__call__, response_model=List[TodoListResponse])
    app.add_api_route(path='/todo/{list_id}', methods=['GET'], endpoint=get_one.__call__, response_model=TodoListResponse)
    app.add_api_route(path='/todo/', methods=['POST'], endpoint=create.__call__, response_model=TodoListResponse)
    app.add_api_route(path='/todo/{list_id}', methods=['PUT'], endpoint=update.__call__, response_model=TodoListResponse)
    app.add_api_route(path='/todo/{list_id}', methods=['DELETE'], endpoint=delete.__call__)

    app.add_api_route(path='/todo/{list_id}/items', methods=['POST'], endpoint=create_item.__call__, response_model=ItemResponse)
    app.add_api_route(path='/todo/{list_id}/items/{item_id}', methods=['PUT'], endpoint=update_item.__call__, response_model=ItemResponse)
    app.add_api_route(path='/todo/{list_id}/items/{item_id}', methods=['DELETE'], endpoint=delete_item.__call__)