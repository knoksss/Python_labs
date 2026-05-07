from src2.errors import TaskDescriptionError, TaskPriorityError, TaskStatusError


class PriorityDescriptor:
    # дескриптор для проверки правильности приоритета операции
    # объявляем максимальное и минимальное значение приоритета операции
    def __init__(self, min_val: int = 1, max_val: int = 5):
        self.min_val = min_val
        self.max_val = max_val
    
    # описываем магический метод get для возможности получения значения - приоритета задачи
    def __get__(self, instance, owner):
        if instance is None: return self
        else:
            return instance.__dict__.get('_priority', self.min_val)

    # описываем магический метод set для валидации приоритета задачи
    def __set__(self, instance, value) -> None:
        if not isinstance(value, int):
            raise TaskPriorityError(f"Приоритет должен быть целым числом, получен {type(value).__name__}")
        elif value < self.min_val or value > self.max_val:
            raise TaskPriorityError(f"Приоритет должен быть от {self.min_val} до {self.max_val}, получен {value}")
        else:
            instance.__dict__['_priority'] = value


class StatusDescriptor:
    # дескриптор для проверки правильности статуса задачи
    # объявление возможных статусов задач
    AVAILABLE_STATUSES = ["new", "in_progress", "done"]

    # прописываем метод get
    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get('_status', 'new')

    # прописываем метод set также для валидации
    def __set__(self, instance, value) -> None:
        normalized_value = value.lower()
        if normalized_value in self.AVAILABLE_STATUSES:
            instance.__dict__['_status'] = normalized_value
        else:
            raise TaskStatusError(f"Статус должен быть одним из {self.AVAILABLE_STATUSES}, получен '{value}'")


class DescriptionDescriptor:
    # дескриптор для проверки корректности описания задачи
    # метод get
    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get('_description', '')

    #  метод set, в котором также реализована валидация
    def __set__(self, instance, value) -> None:
        if not isinstance(value, str):
            raise TaskDescriptionError(f"Описание должно быть строкой, получен {type(value).__name__}")
        if not value.strip():
            raise TaskDescriptionError("Описание не может быть пустым или состоять из пробелов")
        instance.__dict__['_description'] = value.strip()
