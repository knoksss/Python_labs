import asyncio
from sys import stdin
from src.tasks.task import Task
from src.task_queue import TaskQueue
from src.sources import FileSource, ApiSource, GeneratorSource
from src.logging_func import logging_func
from src.async_classes import AsyncTaskExecutor, PrintHandler, PriorityHandler


task_queue = TaskQueue()


def show_menu() -> None:
    print('\nМеню:')
    print('1. Добавить задачу вручную')
    print('2. Загрузить задачи из файла')
    print('3. Загрузить задачи из API')
    print('4. Загрузить задачи из генератора')
    print('5. Показать все задачи')
    print('6. Изменить приоритет задачи')
    print('7. Изменить статус задачи')
    print('8. Запустить задачу (start)')
    print('9. Завершить задачу (complete)')
    print('10. Асинхронный исполнитель')
    print('стоп. Выход')


def main() -> None:
    show_menu()
    
    for cmd in stdin:
        cmd = cmd.strip()
        
        if cmd.lower() in ['стоп', 'exit', 'quit']:
            logging_func("Работа программы остановлена")
            break
        
        if cmd == '1':
            try:
                task_id = int(input("ID: "))
                desc = input("Описание: ")
                priority = int(input("Приоритет (1-5): "))
                status = input("Статус (new/in_progress/done): ") or "new"
                task = Task(task_id, desc, priority, status)
                task_queue.add_task(task)
                print(f"Задача {task_id} добавлена")
            except Exception as e:
                print(f"Ошибка: {e}")
        
        elif cmd == '2':
            filename = input("Имя файла (Enter для files/tasks.txt): ") or "files/tasks.txt"
            source = FileSource(filename)
            for task in source.get_tasks():
                task_queue.add_task(task)
            print("Задачи загружены из файла")
        
        elif cmd == '3':
            source = ApiSource()
            for task in source.get_tasks():
                task_queue.add_task(task)
            print("Задачи загружены из API")
        
        elif cmd == '4':
            source = GeneratorSource()
            for task in source.get_tasks():
                task_queue.add_task(task)
            print("Задачи загружены из генератора")
        
        elif cmd == '5':
            if len(task_queue) == 0:
                print("Нет задач")
            else:
                for task in task_queue:
                    print(f"ID:{task.id} | {task.description} | Приор:{task.priority} | {task.status}")
                print(f"Всего: {len(task_queue)}")
        
        elif cmd == '6':
            task_id = int(input("ID задачи: "))
            for task in task_queue:
                if task.id == task_id:
                    task.priority = int(input("Новый приоритет (1-5): "))
                    print("Приоритет изменён")
                    break
            else:
                print("Задача не найдена")
        
        elif cmd == '7':
            task_id = int(input("ID задачи: "))
            for task in task_queue:
                if task.id == task_id:
                    task.status = input("Новый статус (new/in_progress/done): ")
                    print("Статус изменён")
                    break
            else:
                print("Задача не найдена")
        
        elif cmd == '8':
            task_id = int(input("ID задачи: "))
            for task in task_queue:
                if task.id == task_id:
                    task.start()
                    print(f"Задача запущена. Статус: {task.status}")
                    break
            else:
                print("Задача не найдена")
        
        elif cmd == '9':
            task_id = int(input("ID задачи: "))
            for task in task_queue:
                if task.id == task_id:
                    task.complete()
                    print(f"Задача завершена. Статус: {task.status}")
                    break
            else:
                print("Задача не найдена")
        
        elif cmd == '10':
            async def run():
                executor = AsyncTaskExecutor(max_workers=3)
                executor.register_handler(PriorityHandler())
                executor.register_handler(PrintHandler())
                
                for task in task_queue:
                    await executor.task_queue.put(task)
                
                print(f"Загружено задач: {executor.task_queue.qsize()}")
                await executor.start()
                
                while executor.task_queue.qsize() > 0:
                    await asyncio.sleep(1)
                
                await executor.stop()
                stats = executor.get_statistics()
                print(f"Обработано: {stats['processed']}, Ошибок: {stats['failed']}")
            
            asyncio.run(run())
        
        else:
            print("Неизвестная команда")
        
        print()
        show_menu()


if __name__ == "__main__":
    main()