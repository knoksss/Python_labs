from src2.tasks.task import Task
import random
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# API-заглушка, как источник задач
class ApiSource:
    # для неё реализован данный метод, который возвращает
    # данные задачи
    def get_tasks(self) -> list[Task]:
        return [
            Task(1, "something", 1),
            Task(2, "something", 3)
        ]


# источник задач из файла
class FileSource:
    # в иницилизации прописываем имя файла, из которого далее
    # будут взяты данные
    def __init__(self, filename: str):
        self.filename = filename
    
    # также присутввует метод источника задач, в котором
    # открывается файл и пронумерованно записывает все задачи
    def get_tasks(self) -> list[Task]:
        tasks = [] # пустой список, в который записываются задачи
        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                for line_number, line, priority in enumerate(file, 1):
                    line = line.strip()
                    if line:
                        tasks.append(Task(line_number, {"text": line}, priority))
        except FileNotFoundError:
            print(f"Файл {self.filename} не найден")
            return []
        
        return tasks
    

# источник задач - генератор
class GeneratorSource:
    # метод источника задач
    def get_tasks(self) -> list[Task]:
        tasks = []
        # создаёт 5 рандомных задачи, при помощи библиотеки random
        for i in range(5):
            task_id = random.randint(1, 100)
            task_data = random.choice(['A', 'B', 'C'])
            pr = random.randint(1, 5)
            tasks.append(Task(task_id, task_data, pr)) # добавляет задачу в список задач
        return tasks