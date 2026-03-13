import pytest
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src1.tasks import Task, TaskSource
from src1.sources import FileSource, ApiSource, GeneratorSource
from src1.working_funcs import create_source, print_tasks


class TestTaskBasics:
    def test_task(self):
        task = Task(id=10, payload={"x": 1})
        assert task.id == 10
        assert task.payload == {"x": 1}

    def test_task_equality(self):
        same1 = Task(id=1, payload="data")
        same2 = Task(id=1, payload="data")
        other_id = Task(id=2, payload="data")
        other_payload = Task(id=1, payload="other")
        assert same1 == same2
        assert same1 != other_id
        assert same1 != other_payload

    def test_task_accepts(self):
        Task(id=1, payload="строка")
        Task(id=2, payload=123)
        Task(id=3, payload=[1, 2, 3])
        Task(id=4, payload={"k": "v"})


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
        assert tasks[0].payload == {"text": "first"}
        assert tasks[1].id == 3
        assert tasks[1].payload == {"text": "second"}
        assert tasks[2].id == 4
        assert tasks[2].payload == {"text": "third"}

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
            assert isinstance(task.payload, dict)
            assert "value" in task.payload
            assert "text" in task.payload
            assert task.payload["text"].startswith("task_")


class TestApiSourceBehaviour:
    def test_api_source(self):
        api = ApiSource()
        tasks = api.get_tasks()

        assert len(tasks) == 2
        assert tasks[0] == Task(id=1, payload={"something": 1})
        assert tasks[1] == Task(id=2, payload={"something": 2})
        assert all(isinstance(t, Task) for t in tasks)


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
        assert "{'something': 1}" in out
        assert "[2]" in out
        assert "{'something': 2}" in out

    def test_print_tasks_rejects(self):
        class NoGetTasks:
            pass

        with pytest.raises(TypeError, match="не подходит под протокол"):
            print_tasks(NoGetTasks())
