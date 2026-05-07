from src1.tasks import Task
import random


# API-заглушка, как источник задач
class ApiSource:
    # для неё реализован данный метод, который возвращает
    # данные задачи
    def get_tasks(self) -> list[Task]:
        return [
            Task(id=1, payload = {"something": 1}),
            Task(id=2, payload = {"something": 2})
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
                for line_number, line in enumerate(file, 1):
                    line = line.strip()
                    if line:
                        tasks.append(Task(line_number, {"text": line}))
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
            task_data = {
                "value": random.randint(1, 100),
                "text": f"task_{random.choice(['A', 'B', 'C'])}"
            }
            tasks.append(Task(task_id, task_data)) # добавляет задачу в список задач
        return tasks