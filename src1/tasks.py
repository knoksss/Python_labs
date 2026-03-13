from typing import Protocol, runtime_checkable, Any
from dataclasses import dataclass


# создаём класс данных, который благодаря декоратору
# автоматически получает __init__, __repr__ и __eq__
@dataclass
class Task:
    id: int
    payload: Any


# декоратор позволяет проверять соответствие протоколу во время работы
# объявляем протокол под названием TaskSource, который имеет метод get_task()
# и любой объект, имеющий данный метод, считается полходящим под протокол
@runtime_checkable
class TaskSource(Protocol):
    def get_tasks(self) -> list[Task]:
        ...