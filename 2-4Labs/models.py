# Модели базы данных (SQLAlchemy)

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class TodoList(Base):
    __tablename__ = "todo_lists"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    
    # Новые поля для подсчёта прогресса TodoList (ЛР3)
    completed_count = Column(Integer, nullable=False, default=0)  # Кол-во выполненных items
    total_count = Column(Integer, nullable=False, default=0)      # Общее кол-во items
    
    items = relationship("Item", back_populates="todo_list", cascade="all, delete-orphan")


class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    text = Column(String, nullable=True)
    is_done = Column(Boolean, nullable=False, default=False)
    todo_list_id = Column(Integer, ForeignKey("todo_lists.id"), nullable=False)
    todo_list = relationship("TodoList", back_populates="items")