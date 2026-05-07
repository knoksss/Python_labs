import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src3.tasks.task import Task
from src3.task_queue import TaskQueue


def build_queue() -> TaskQueue:
    queue = TaskQueue()
    queue.add_task(Task(1, "Первая задача", 5, "new"))
    queue.add_task(Task(2, "Вторая задача", 2, "done"))
    queue.add_task(Task(3, "Третья задача", 4, "in_progress"))
    queue.add_task(Task(4, "Четвертая задача", 3, "new"))
    return queue


def test_queue_supports_repeated_iteration():
    queue = build_queue()

    first_pass = [task.id for task in queue]
    second_pass = [task.id for task in queue]

    assert first_pass == [1, 2, 3, 4]
    assert second_pass == [1, 2, 3, 4]


def test_filter_by_status_is_lazy_and_correct():
    queue = build_queue()

    filtered = queue.filter(status="new")

    assert filtered.__class__.__name__ == "generator"
    assert [task.id for task in filtered] == [1, 4]


def test_filter_by_priority_range():
    queue = build_queue()

    filtered = queue.filter(priority=4)

    assert [task.id for task in filtered] == [3]


def test_process_returns_generator():
    queue = build_queue()

    processed = queue.process(lambda task: task.description.upper())

    assert processed.__class__.__name__ == "generator"
    assert list(processed) == [
        "ПЕРВАЯ ЗАДАЧА",
        "ВТОРАЯ ЗАДАЧА",
        "ТРЕТЬЯ ЗАДАЧА",
        "ЧЕТВЕРТАЯ ЗАДАЧА",
    ]


def test_queue_is_compatible_with_standard_python_constructs():
    queue = build_queue()

    assert len(list(queue)) == 4
    assert sum(task.priority for task in queue) == 14


def test_generator_stops_correctly():
    queue = build_queue()
    iterator = queue.filter(status="done")

    assert next(iterator).id == 2

    try:
        next(iterator)
        assert False, "Генератор должен был завершиться"
    except StopIteration:
        assert True
