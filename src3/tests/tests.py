import pytest
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src2.tasks.task import Task
from src2.errors import TaskStatusError, TaskPriorityError, TaskDescriptionError


# тесты создания задач
class TestTaskCreation:
    def test_create_valid_task(self):
        # создание корректной задачи
        task = Task(1, "Описание задачи", 3, "new")
        assert task.id == 1
        assert task.description == "Описание задачи"
        assert task.priority == 3
        assert task.status == "new"
        assert isinstance(task.creation_time, datetime)
    
    def test_create_with_default_status(self):
        # со статусом меньше
        task = Task(1, "Описание", 3)
        assert task.status == "new"
    
    def test_create_with_empty_description(self):
        # с пустым описанием
        with pytest.raises(TaskDescriptionError, match="не может быть пустым"):
            Task(1, "", 3)
    
    def test_create_with_whitespace_description(self):
        # с описанием из пробелов
        with pytest.raises(TaskDescriptionError, match="не может быть пустым"):
            Task(1, "   ", 3)
    
    def test_create_with_invalid_priority_low(self):
        # приоритет ниже допустимого
        with pytest.raises(TaskPriorityError, match="от 1 до 5"):
            Task(1, "Описание", 0)
    
    def test_create_with_invalid_priority_high(self):
        # приоритет выше допустимого
        with pytest.raises(TaskPriorityError, match="от 1 до 5"):
            Task(1, "Описание", 6)
    
    def test_create_with_invalid_priority_type(self):
        # приоритет не int
        with pytest.raises(TaskPriorityError, match="целым числом"):
            Task(1, "Описание", "высокий")
    
    def test_create_with_invalid_status(self):
        # задача с некорректным статусом
        with pytest.raises(TaskStatusError, match="должен быть одним из"):
            Task(1, "Описание", 3, "unknown")
    
    def test_create_with_status_uppercase(self):
        # статус в верхнем регистре
        task = Task(1, "Описание", 3, "IN_PROGRESS")
        assert task.status == "in_progress"


# тест свойств @property
class TestTaskProperties:
    def test_id_readonly(self):
        # id только для чтения
        task = Task(1, "Описание", 3)
        assert task.id == 1
        
        with pytest.raises(AttributeError):
            task.id = 100
    
    def test_creation_time_readonly(self):
        # время создания только для чтения
        task = Task(1, "Описание", 3)
        assert isinstance(task.creation_time, datetime)
        
        with pytest.raises(AttributeError):
            task.creation_time = datetime.now()
    
    def test_is_ready_for_new_task(self):
        # новая задача не готова
        task = Task(1, "Описание", 3, "new")
        assert task.is_ready is False
    
    def test_is_ready_for_in_progress_task(self):
        # новая задача не готова (в процессе)
        task = Task(1, "Описание", 3, "in_progress")
        assert task.is_ready is False
    
    def test_is_ready_for_done_task(self):
        # новая задача готова
        task = Task(1, "Описание", 3, "done")
        assert task.is_ready is True


# тест жизненного цикла задачи
class TestTaskLifecycle:
    def test_start_new_task(self):
        # запуск новой задачи
        task = Task(1, "Описание", 3, "new")
        task.start()
        assert task.status == "in_progress"
    
    def test_start_already_started_task(self):
        # запуск уже запущенной задачи
        task = Task(1, "Описание", 3, "in_progress")
        with pytest.raises(TaskStatusError, match="Нельзя начать выполнение завершённой задачи"):
            task.start()
    
    def test_start_done_task(self):
        # запуск завершённой задачи
        task = Task(1, "Описание", 3, "done")
        with pytest.raises(TaskStatusError, match="Нельзя начать"):
            task.start()
    
    def test_complete_in_progress_task(self):
        # завершение задачи, которая нааходилась в работе
        task = Task(1, "Описание", 3, "in_progress")
        task.complete()
        assert task.status == "done"
    
    def test_complete_done_task(self):
        # заверешение завершённой задачи
        task = Task(1, "Описание", 3, "done")
        with pytest.raises(TaskStatusError, match="уже закончена"):
            task.complete()


# изменение атрибутов
class TestTaskValidation:
    def test_set_valid_priority(self):
        # установка корректного приоритета
        task = Task(1, "Описание", 3)
        task.priority = 5
        assert task.priority == 5
    
    def test_set_invalid_priority(self):
        # установка некорректного приоритета
        task = Task(1, "Описание", 3)
        with pytest.raises(TaskPriorityError, match="от 1 до 5"):
            task.priority = 10
    
    def test_set_priority_non_int(self):
        # установка не целочисленного приоритета
        task = Task(1, "Описание", 3)
        with pytest.raises(TaskPriorityError, match="целым числом"):
            task.priority = "высокий"
    
    def test_set_valid_status(self):
        # установка корректного статуса
        task = Task(1, "Описание", 3)
        task.status = "done"
        assert task.status == "done"
    
    def test_set_invalid_status(self):
        # установка некорректного статуса
        task = Task(1, "Описание", 3)
        with pytest.raises(TaskStatusError, match="должен быть одним из"):
            task.status = "unknown"
    
    def test_set_status_uppercase(self):
        # статус в верхнем регистре
        task = Task(1, "Описание", 3)
        task.status = "IN_PROGRESS"
        assert task.status == "in_progress"
    
    def test_set_valid_description(self):
        # корректное описание
        task = Task(1, "Описание", 3)
        task.description = "Новое описание"
        assert task.description == "Новое описание"
    
    def test_set_empty_description(self):
        # пустое описание
        task = Task(1, "Описание", 3)
        with pytest.raises(TaskDescriptionError, match="не может быть пустым"):
            task.description = ""


# сравнение задач
class TestTaskEquality:
    def test_task_repr(self):
        task = Task(1, "Описание", 3, "new")
        repr_str = repr(task)
        assert "id: 1" in repr_str
        assert "description: 'Описание'" in repr_str
        assert "priority: 3" in repr_str
        assert "status: 'new'" in repr_str
    
    def test_different_tasks_have_different_ids(self):
        task1 = Task(1, "Описание", 3)
        task2 = Task(2, "Описание", 3)
        assert task1.id != task2.id


# data дескрипторы
class TestDataDescriptor:
    def test_data_descriptor_cannot_be_overridden_in_dict(self):
        task = Task(1, "Описание", 3)
        
        # пытаемся обойти дескриптор через __dict__
        task.__dict__['priority'] = 100
        
        # при чтении через атрибут всё равно вызывается дескриптор
        # и возвращается значение из _priority
        assert task.priority == 3


# non-data дескриптор (@property)
class TestNonDataDescriptor:
    def test_property_can_be_overridden_in_dict(self):
        task = Task(1, "Описание", 3)
        
        original_id = task.id
        
        # обходим property через __dict__
        task.__dict__['_id'] = 999
        
        # теперь task.id возвращает значение из __dict__
        assert task.id == 999
        assert task.id != original_id