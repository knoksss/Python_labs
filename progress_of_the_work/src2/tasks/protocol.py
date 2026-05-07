from typing import Protocol, runtime_checkable
from src2.tasks.task import Task

# декоратор позволяет проверять соответствие протоколу во время работы
# объявляем протокол под названием TaskSource, который имеет метод get_task()
# и любой объект, имеющий данный метод, считается полходящим под протокол
@runtime_checkable
class TaskSource(Protocol):
    def get_tasks(self) -> list[Task]:
        ...