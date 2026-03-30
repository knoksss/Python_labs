from datetime import datetime
from src2.errors import TaskStatusError
from src2.user_descriptors import DescriptionDescriptor, PriorityDescriptor, StatusDescriptor


class Task:

    description = DescriptionDescriptor()
    priority = PriorityDescriptor()
    status = StatusDescriptor()

    def __init__(self, task_id: int, description: str, priority: int, status: str = "new"):
        self._id = task_id
        self.description = description
        self.priority = priority
        self.status = status
        self._creation_time = datetime.now()

    @property
    def id(self) -> int:
        return self._id
    
    @property
    def creation_time(self) -> datetime:
        return self._creation_time
    
    @property
    def is_ready(self) -> bool:
        return self.status == "done"

    def start(self) -> None:
        if self.status == "done" or self.status == "in_progress":
            raise TaskStatusError("Нельзя начать выполнение завершённой задачи")
        else:
            self.status = "in_progress"

    def complete(self) -> None:
        if self.status == "done":
            raise TaskStatusError("Задача уже закончена")
        elif self.status == "new":
            raise TaskStatusError("Нельзя завершить задачу, которая не была начата")
        else:
            self.status = "done"

    def __repr__(self) -> str:
        return (f"id: {self._id}; description: '{self.description}'; "
                f"priority: {self.priority}; status: '{self.status}'; "
                f"creation time: {self._creation_time}")