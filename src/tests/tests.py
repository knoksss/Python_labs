import pytest
import sys
from pathlib import Path
from datetime import datetime
import asyncio

# добавляем корневую директорию проекта в путь для импорта
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# импортируем необходимые классы и исключения
from src.tasks.task import Task
from src.task_queue import TaskQueue
from src.errors import TaskStatusError, TaskPriorityError, TaskDescriptionError
from src.tasks.protocol import TaskSource
from src.sources import FileSource, ApiSource, GeneratorSource
from src.working_func import create_source, print_tasks
from src.tasks.task import Task
from src.async_classes import AsyncTaskExecutor, PrintHandler, PriorityHandler


def build_queue() -> TaskQueue:
    # вспомогательная функция для создания очереди задач с тестовыми данными
    queue = TaskQueue()
    # добавляем задачи с разными статусами для проверки фильтрации
    queue.add_task(Task(1, "Первая задача", 5, "new")) # новая, высокий приоритет
    queue.add_task(Task(2, "Вторая задача", 2, "done")) # завершённая
    queue.add_task(Task(3, "Третья задача", 4, "in_progress")) # в процессе
    queue.add_task(Task(4, "Четвертая задача", 3, "new")) # новая, средний приоритет
    return queue


# тесты класса Task
class TestTaskBasics:
    def test_task(self):
        task = Task(10, "тестовое описание", 3, "new")
        assert task.id == 10
        assert task.description == "тестовое описание"
        assert task.priority == 3
    
    def test_task_equality(self):
        task1 = Task(1, "data", 3, "new")
        task2 = Task(1, "data", 3, "new")
        # задачи считаются разными объектами, даже если поля одинаковые
        assert task1.id == task2.id
        assert task1.description == task2.description
    
    def test_task_accepts(self):
        # описание должно быть строкой
        Task(1, "строка", 3, "new")
        # приоритет должен быть числом от 1 до 5
        Task(2, "число", 5, "new")


class TestTaskSourceProtocol:
    def test_isinstance_checks(self):
        api = ApiSource()
        file_src = FileSource("dummy.txt")
        gen = GeneratorSource()
        assert isinstance(api, TaskSource)
        assert isinstance(file_src, TaskSource)
        assert isinstance(gen, TaskSource)

    def test_random_class(self):
        class SomethingElse:
            pass
        assert not isinstance(SomethingElse(), TaskSource)


class TestFileSourceBehaviour:
    def test_reads_non_empty(self, tmp_path):
        path = tmp_path / "tasks.txt"
        path.write_text("first\n\n second \nthird\n", encoding="utf-8")
        
        src = FileSource(str(path))
        tasks = src.get_tasks()
        
        assert len(tasks) == 3
        
        assert tasks[0].id == 1
        assert tasks[0].description == "first"

    def test_empty_file(self, tmp_path):
        path = tmp_path / "empty.txt"
        path.write_text("", encoding="utf-8")

        src = FileSource(str(path))
        assert src.get_tasks() == []

    def test_missing_file_print(self, capsys):
        src = FileSource("no_such_file.txt")
        tasks = src.get_tasks()

        out = capsys.readouterr().out
        assert tasks == []
        assert "Файл no_such_file.txt не найден" in out


class TestGeneratorSourceBehaviour:
    def test_generator(self):
        gen = GeneratorSource()
        tasks = gen.get_tasks()

        assert len(tasks) == 5
        assert all(isinstance(t, Task) for t in tasks)

    def test_generated_payload(self):
        tasks = GeneratorSource().get_tasks()
        for task in tasks:
            assert isinstance(task.id, int)
            assert isinstance(task.description, str)


class TestApiSourceBehaviour:
    def test_api_source(self):
        api = ApiSource()
        tasks = api.get_tasks()
        
        assert len(tasks) == 2
        assert tasks[0].id == 1
        assert tasks[0].description == "something"
        assert tasks[0].priority == 1


class TestCreateSourceFunction:
    def test_create_source(self, capsys):
        src = create_source(ApiSource)

        out = capsys.readouterr().out
        assert isinstance(src, ApiSource)
        assert "Класс ApiSource подходит под протокол" in out


class TestPrintTasksFunction:
    def test_print_tasks(self, capsys):
        src = ApiSource()
        print_tasks(src)
        
        out = capsys.readouterr().out
        assert "[1]" in out
        assert "something" in out
        assert "1" in out  # приоритет

    def test_print_tasks_rejects(self):
        class NoGetTasks:
            pass

        with pytest.raises(TypeError, match="не подходит под протокол"):
            print_tasks(NoGetTasks())


# тесты создания задач
class TestTaskCreation:
    # тестирование корректности создания объектов Task
    def test_create_valid_task(self):
        # создание корректной задачи со всеми параметрами
        task = Task(1, "Описание задачи", 3, "new")
        # проверяем, что все атрибуты установлены правильно
        assert task.id == 1
        assert task.description == "Описание задачи"
        assert task.priority == 3
        assert task.status == "new"
        assert isinstance(task.creation_time, datetime)  # время создания должно быть datetime
    
    def test_create_with_default_status(self):
        # создание задачи со статусом по умолчанию (должен быть 'new')
        task = Task(1, "Описание", 3)
        assert task.status == "new"  # статус не передан, значит должен быть "new"
    
    def test_create_with_empty_description(self):
        # создание задачи с пустым описанием должно вызывать ошибку
        with pytest.raises(TaskDescriptionError, match="не может быть пустым"):
            Task(1, "", 3)
    
    def test_create_with_whitespace_description(self):
        # создание задачи с описанием из пробелов должно вызывать ошибку
        with pytest.raises(TaskDescriptionError, match="не может быть пустым"):
            Task(1, "   ", 3)
    
    def test_create_with_invalid_priority_low(self):
        # создание задачи с приоритетом ниже минимального (1)
        with pytest.raises(TaskPriorityError, match="от 1 до 5"):
            Task(1, "Описание", 0)
    
    def test_create_with_invalid_priority_high(self):
        # создание задачи с приоритетом выше максимального (5)
        with pytest.raises(TaskPriorityError, match="от 1 до 5"):
            Task(1, "Описание", 6)
    
    def test_create_with_invalid_priority_type(self):
        # создание задачи с приоритетом не целого типа
        with pytest.raises(TaskPriorityError, match="целым числом"):
            Task(1, "Описание", "высокий")
    
    def test_create_with_invalid_status(self):
        # создание задачи с некорректным статусом
        with pytest.raises(TaskStatusError, match="должен быть одним из"):
            Task(1, "Описание", 3, "unknown")
    
    def test_create_with_status_uppercase(self):
        # создание задачи со статусом в верхнем регистре (должен привестись к нижнему)
        task = Task(1, "Описание", 3, "IN_PROGRESS")
        assert task.status == "in_progress"


# тест свойств @property
class TestTaskProperties:
    # тестирование свойств только для чтения
    def test_id_readonly(self):
        # проверка, что id доступен только для чтения
        task = Task(1, "Описание", 3)
        assert task.id == 1
        
        # попытка изменить id должна вызвать ошибку
        with pytest.raises(AttributeError):
            task.id = 100
    
    def test_creation_time_readonly(self):
        # проверка, что время создания доступно только для чтения
        task = Task(1, "Описание", 3)
        assert isinstance(task.creation_time, datetime)
        
        # попытка изменить время создания должна вызвать ошибку
        with pytest.raises(AttributeError):
            task.creation_time = datetime.now()
    
    def test_is_ready_for_new_task(self):
        # новая задача не должна считаться готовой (завершённой)
        task = Task(1, "Описание", 3, "new")
        assert task.is_ready is False
    
    def test_is_ready_for_in_progress_task(self):
        # задача в процессе выполнения не должна считаться готовой
        task = Task(1, "Описание", 3, "in_progress")
        assert task.is_ready is False
    
    def test_is_ready_for_done_task(self):
        # завершённая задача должна считаться готовой
        task = Task(1, "Описание", 3, "done")
        assert task.is_ready is True


# тест жизненного цикла задачи
class TestTaskLifecycle:
    # тестирование методов start() и complete()
    def test_start_new_task(self):
        # запуск новой задачи должен перевести её в статус "in_progress"
        task = Task(1, "Описание", 3, "new")
        task.start()
        assert task.status == "in_progress"
    
    def test_start_already_started_task(self):
        # повторный запуск уже запущенной задачи должен вызвать ошибку
        task = Task(1, "Описание", 3, "in_progress")
        with pytest.raises(TaskStatusError, match="Нельзя начать выполнение завершённой задачи"):
            task.start()
    
    def test_start_done_task(self):
        # запуск завершённой задачи должен вызвать ошибку
        task = Task(1, "Описание", 3, "done")
        with pytest.raises(TaskStatusError, match="Нельзя начать"):
            task.start()
    
    def test_complete_in_progress_task(self):
        # завершение задачи, находящейся в работе
        task = Task(1, "Описание", 3, "in_progress")
        task.complete()
        assert task.status == "done"
    
    def test_complete_done_task(self):
        # попытка завершить уже завершённую задачу должна вызвать ошибку
        task = Task(1, "Описание", 3, "done")
        with pytest.raises(TaskStatusError, match="уже закончена"):
            task.complete()
    
    def test_complete_new_task(self):
        # попытка завершить новую задачу (не начатую) должна вызвать ошибку
        task = Task(1, "Описание", 3, "new")
        with pytest.raises(TaskStatusError, match="Нельзя завершить задачу, которая не была начата"):
            task.complete()


# тесты изменения атрибутов через дескрипторы
class TestTaskValidation:
    # тестирование валидации при установке значений через дескрипторы
    def test_set_valid_priority(self):
        # установка корректного значения приоритета
        task = Task(1, "Описание", 3)
        task.priority = 5
        assert task.priority == 5
    
    def test_set_invalid_priority(self):
        # установка некорректного приоритета должна вызвать ошибку
        task = Task(1, "Описание", 3)
        with pytest.raises(TaskPriorityError, match="от 1 до 5"):
            task.priority = 10
    
    def test_set_priority_non_int(self):
        # установка не целочисленного приоритета должна вызвать ошибку
        task = Task(1, "Описание", 3)
        with pytest.raises(TaskPriorityError, match="целым числом"):
            task.priority = "высокий"
    
    def test_set_valid_status(self):
        # установка корректного статуса
        task = Task(1, "Описание", 3)
        task.status = "done"
        assert task.status == "done"
    
    def test_set_invalid_status(self):
        # установка некорректного статуса должна вызвать ошибку
        task = Task(1, "Описание", 3)
        with pytest.raises(TaskStatusError, match="должен быть одним из"):
            task.status = "unknown"
    
    def test_set_status_uppercase(self):
        # установка статуса в верхнем регистре (должен привестись к нижнему)
        task = Task(1, "Описание", 3)
        task.status = "IN_PROGRESS"
        assert task.status == "in_progress"
    
    def test_set_valid_description(self):
        # установка корректного описания
        task = Task(1, "Описание", 3)
        task.description = "Новое описание"
        assert task.description == "Новое описание"
    
    def test_set_empty_description(self):
        # установка пустого описания должна вызвать ошибку
        task = Task(1, "Описание", 3)
        with pytest.raises(TaskDescriptionError, match="не может быть пустым"):
            task.description = ""


# тесты представления задач
class TestTaskRepresentation:
    # тестирование метода __repr__
    def test_task_repr(self):
        # проверка строкового представления задачи
        task = Task(1, "Описание", 3, "new")
        repr_str = repr(task)
        assert "id: 1" in repr_str
        assert "description: 'Описание'" in repr_str
        assert "priority: 3" in repr_str
        assert "status: 'new'" in repr_str
    
    def test_different_tasks_have_different_ids(self):
        # проверка, что у разных задач разные идентификаторы
        task1 = Task(1, "Описание", 3)
        task2 = Task(2, "Описание", 3)
        assert task1.id != task2.id


# тесты дескрипторов: data и non-data
class TestDataDescriptor:
    # тестирование работы data-дескриптора
    def test_data_descriptor_cannot_be_overridden_in_dict(self):
        # data-дескриптор имеет приоритет при чтении, даже если значение есть в __dict__
        task = Task(1, "Описание", 3)
        
        # пытаемся обойти дескриптор, записав значение напрямую в __dict__
        task.__dict__['priority'] = 100
        
        # при чтении через атрибут всё равно вызывается дескриптор
        # и возвращается значение из _priority (3), а не из __dict__
        assert task.priority == 3


class TestNonDataDescriptor:
    # тестирование работы non-data дескриптора
    def test_property_can_be_overridden_in_dict(self):
        # non-data дескриптор (property) можно обойти через __dict__
        task = Task(1, "Описание", 3)
        
        original_id = task.id  # сохраняем оригинальный id
        
        # обходим property через __dict__
        task.__dict__['_id'] = 999
        
        # теперь task.id возвращает значение из __dict__, а не через property
        assert task.id == 999
        assert task.id != original_id


# тесты очереди задач
class TestTaskQueue:
    def test_queue_supports_repeated_iteration(self):
        # проверка, что по очереди можно итерироваться несколько раз
        queue = build_queue()

        first_pass = [task.id for task in queue]
        second_pass = [task.id for task in queue]

        # оба прохода должны дать одинаковый результат
        assert first_pass == [1, 2, 3, 4]
        assert second_pass == [1, 2, 3, 4]

    def test_filter_by_status_is_lazy_and_correct(self):
        # проверка, что filter() возвращает ленивый генератор и правильно фильтрует по статусу
        queue = build_queue()

        filtered = queue.filter(status="new")

        # проверяем, что возвращается именно генератор
        assert filtered.__class__.__name__ == "generator"
        # проверяем, что отфильтровались только задачи со статусом "new" (id 1 и 4)
        assert [task.id for task in filtered] == [1, 4]

    def test_filter_by_priority_range(self):
        # проверка фильтрации по приоритету
        queue = build_queue()

        filtered = queue.filter(priority=4)

        # должна остаться только задача с приоритетом 4 (id 3)
        assert [task.id for task in filtered] == [3]

    def test_process_returns_generator(self):
        # проверка, что process() возвращает ленивый генератор
        queue = build_queue()

        # применяем функцию преобразования описания в верхний регистр
        processed = queue.process(lambda task: task.description.upper())

        # проверяем, что возвращается генератор
        assert processed.__class__.__name__ == "generator"
        # проверяем результат преобразования
        assert list(processed) == [
            "ПЕРВАЯ ЗАДАЧА",
            "ВТОРАЯ ЗАДАЧА",
            "ТРЕТЬЯ ЗАДАЧА",
            "ЧЕТВЕРТАЯ ЗАДАЧА",
        ]

    def test_queue_is_compatible_with_standard_python_constructs(self):
        # проверка совместимости очереди со стандартными конструкциями Python
        queue = build_queue()

        # len() должна работать
        assert len(list(queue)) == 4
        # sum() с генератором должна работать
        assert sum(task.priority for task in queue) == 14  # 5+2+4+3=14

    def test_generator_stops_correctly(self):
        # проверка, что генератор правильно сигнализирует об окончании (StopIteration)
        queue = build_queue()
        iterator = queue.filter(status="done")

        # получаем первую (и единственную) задачу со статусом "done"
        assert next(iterator).id == 2

        # попытка получить следующий элемент должна вызвать StopIteration
        with pytest.raises(StopIteration):
            next(iterator)
    
    def test_add_task_to_queue(self):
        # проверка добавления задачи в очередь
        queue = TaskQueue()
        task = Task(5, "Новая задача", 3, "new")
        
        initial_size = len(queue.tasks)
        queue.add_task(task)
        
        # размер должен увеличиться на 1
        assert len(queue.tasks) == initial_size + 1
        # последняя задача в очереди должна быть добавленной
        assert queue.tasks[-1] == task
    
    def test_filter_by_multiple_criteria(self):
        # проверка фильтрации по нескольким критериям
        queue = build_queue()
        
        # фильтруем по статусу "new" И приоритету 3
        filtered = queue.filter(status="new", priority=3)
        
        # должна остаться только задача 4 (new, priority=3)
        result = list(filtered)
        assert len(result) == 1
        assert result[0].id == 4
        assert result[0].status == "new"
        assert result[0].priority == 3
    
    def test_filter_no_matches(self):
        # проверка фильтрации, когда нет подходящих задач
        queue = build_queue()
        
        # фильтруем по несуществующему приоритету
        filtered = queue.filter(priority=10)
        
        # должен вернуться пустой генератор
        assert list(filtered) == []
    
    def test_process_empty_queue(self):
        # проверка обработки пустой очереди
        queue = TaskQueue()
        
        processed = queue.process(lambda task: task.description)
        
        # должен вернуться пустой генератор
        assert list(processed) == []


# вспомогательные функции
class MockSource:
    # мок-источник задач для тестирования
    def __init__(self, tasks: list[Task]):
        self._tasks = tasks
    
    def get_tasks(self) -> list[Task]:
        return self._tasks


class ErrorHandler:
    # обработчик, который всегда вызывает ошибку
    async def can_handle(self, task: Task) -> bool:
        return True
    
    async def handle(self, task: Task) -> None:
        raise ValueError("Тестовая ошибка")


class TestAsyncTaskExecutor:
    # тестирование создания исполнителя
    def test_create_executor(self):
        # создание исполнителя с работниками по умолчанию
        executor = AsyncTaskExecutor()
        assert executor.max_workers == 3
        assert len(executor.handlers) == 0
        assert executor.task_queue.qsize() == 0
    
    def test_create_executor_with_custom_workers(self):
        # создание исполнителя с указанным количеством работников
        executor = AsyncTaskExecutor(max_workers=5)
        assert executor.max_workers == 5
    
    def test_register_handler(self):
        # регистрация обработчика
        executor = AsyncTaskExecutor()
        handler = PrintHandler()
        
        executor.register_handler(handler)
        
        assert len(executor.handlers) == 1
        assert executor.handlers[0] == handler
    
    def test_register_multiple_handlers(self):
        # регистрация нескольких обработчиков
        executor = AsyncTaskExecutor()
        handler1 = PrintHandler()
        handler2 = PriorityHandler()
        
        executor.register_handler(handler1)
        executor.register_handler(handler2)
        
        assert len(executor.handlers) == 2
    
    @pytest.mark.asyncio
    async def test_add_tasks_from_source(self):
        # добавление задач из источника
        executor = AsyncTaskExecutor()
        tasks = [Task(1, "Задача 1", 3, "new"), Task(2, "Задача 2", 4, "new")]
        source = MockSource(tasks)
        
        await executor.add_tasks_from_source(source)
        
        assert executor.task_queue.qsize() == 2
    
    @pytest.mark.asyncio
    async def test_process_single_task(self):
        # обработка одной задачи
        executor = AsyncTaskExecutor(max_workers=1)
        executor.register_handler(PrintHandler())
        
        task = Task(1, "Тест", 3, "new")
        source = MockSource([task])
        await executor.add_tasks_from_source(source)
        
        await executor.start()
        await asyncio.sleep(1)
        await executor.stop()
        
        stats = executor.get_statistics()
        assert stats['processed'] == 1
        assert stats['failed'] == 0
        assert task.status == "done"
    
    @pytest.mark.asyncio
    async def test_process_multiple_tasks(self):
        # обработка нескольких задач
        executor = AsyncTaskExecutor(max_workers=2)
        executor.register_handler(PrintHandler())
        
        tasks = [Task(1, "Задача 1", 3, "new"), Task(2, "Задача 2", 4, "new")]
        source = MockSource(tasks)
        await executor.add_tasks_from_source(source)
        
        await executor.start()
        while executor.task_queue.qsize() > 0:
            await asyncio.sleep(0.1)
        await executor.stop()
        
        stats = executor.get_statistics()
        assert stats['processed'] == 2
    
    @pytest.mark.asyncio
    async def test_priority_handler_only_high_priority(self):
        # проверка, что PriorityHandler обрабатывает только высокий приоритет
        executor = AsyncTaskExecutor(max_workers=1)
        executor.register_handler(PriorityHandler())
        executor.register_handler(PrintHandler())
        
        tasks = [
            Task(1, "Низкий", 2, "new"),
            Task(2, "Высокий", 5, "new")
        ]
        source = MockSource(tasks)
        await executor.add_tasks_from_source(source)
        
        await executor.start()
        while executor.task_queue.qsize() > 0:
            await asyncio.sleep(0.1)
        await executor.stop()
        
        stats = executor.get_statistics()
        assert stats['processed'] == 2
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        executor = AsyncTaskExecutor(max_workers=1)
        executor.register_handler(ErrorHandler())
        
        task = Task(1, "Тест", 3, "new")
        source = MockSource([task])
        await executor.add_tasks_from_source(source)
        
        await executor.start()
        await asyncio.sleep(0.5)
        await executor.stop()

        await asyncio.sleep(0.1)
        
        stats = executor.get_statistics()
        assert stats['failed'] == 0
    
    @pytest.mark.asyncio
    async def test_statistics(self):
        # проверка сбора статистики
        executor = AsyncTaskExecutor()
        executor.register_handler(PrintHandler())
        
        tasks = [Task(1, "Задача", 3, "new")]
        source = MockSource(tasks)
        await executor.add_tasks_from_source(source)
        
        await executor.start()
        while executor.task_queue.qsize() > 0:
            await asyncio.sleep(0.1)
        await executor.stop()
        
        stats = executor.get_statistics()
        assert 'processed' in stats
        assert 'failed' in stats
        assert 'total_time' in stats
        assert 'avg_time' in stats
    
    @pytest.mark.asyncio
    async def test_start_and_stop(self):
        executor = AsyncTaskExecutor()
        
        assert executor._running is False
        
        await executor.start()
        await asyncio.sleep(0.1)
        assert executor._running is False
        
        await executor.stop()
        await asyncio.sleep(0.1)
        assert executor._running is False