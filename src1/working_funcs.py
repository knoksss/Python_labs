from src1.sources import FileSource, ApiSource, GeneratorSource
from src1.tasks import TaskSource


# функция для создания источника задач, которая сначала проверяет
# является ли этот класс источником задач или же нет
def create_source(source_class, *args, **kwargs) -> TaskSource|None:
    if issubclass(source_class, TaskSource):
        print(f"Класс {source_class.__name__} подходит под протокол, создаем экземпляр")
        return source_class(*args, **kwargs)
    else:
        print(f"Error: Класс {source_class.__name__} не подходит под протокол")
        return None


# функция для вывода задач, которая сначала проверяет принадлежит ли
# данный источник задач нужному классу, если нет, то выводит ошибку
def print_tasks(source_class: TaskSource) -> None:
    if not isinstance(source_class, TaskSource):
        raise TypeError(f"{type(source_class).__name__} не подходит под протокол")

    tasks = source_class.get_tasks() # если ошибки не последовало, то пользуемся методом get_tasks()
    for task in tasks:
        print(f"[{task.id}] {task.payload}")



if __name__ == "__main__":
    create_source(ApiSource) # создаём источник задач
    create_source(FileSource, "files/tasks.txt")
    create_source(GeneratorSource)
    
    # список источников задач
    sources = [
        ApiSource(),
        FileSource("files/tasks.txt"),
        GeneratorSource()
    ]
    
    # проходимся по каждому источнику из нашего списка, чтобы
    # проверить его на соответствие протоколу
    for source in sources:
        if isinstance(source, TaskSource):
            print(f"Объект {source} - валидный источник")
