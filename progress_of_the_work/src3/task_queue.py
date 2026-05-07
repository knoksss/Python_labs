from src3.tasks.task import Task

class TaskQueue:
    def __init__(self, tasks=None) -> None:
        # если задачи не переданы, создаём пустой список, иначе копируем
        if tasks is None:
            self.tasks = []
        else:
            self.tasks = list(tasks)

    def add_task(self, task: Task) -> None:
        # длобавляем задачу в конец очереди
        self.tasks.append(task)

    def __iter__(self):
        # перебираем все задачи по очереди
        for task in self.tasks:
            yield task

    def __len__(self) -> int:
        # возвращаем количество задач
        return len(self.tasks)

    def filter(self, status=None, priority=None):
        # фильтруем задачи по статусу (без учёта регистра) и приоритету
        for task in self.tasks:
            if status is not None and task.status != status.lower():
                continue
            if priority is not None and task.priority != priority:
                continue
            yield task

    def process(self, func, tasks=None):
        # применяем функцию к каждой задаче из указанного списка (или ко всем)
        if tasks is None:
            tasks = self

        for task in tasks:
            yield func(task)
