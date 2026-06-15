# Инициализация модуля domain
# Делает папку domain модулем Python и экспортирует классы

from domain.todo_item import TodoItem
from domain.todo_list import TodoList

# Эти классы можно импортировать из модуля domain
__all__ = ['TodoItem', 'TodoList']