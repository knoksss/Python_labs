import asyncio
from sys import stdin
from src.tasks.protocol import TaskSource
from src.working_func import create_source, print_tasks
from src.sources import FileSource, ApiSource, GeneratorSource
from src.logging_func import logging_func
from src.task_queue import TaskQueue
from src.async_classes import AsyncTaskExecutor, PrintHandler, PriorityHandler


async def async_demo() -> None:
    print("Асинхронный исполнитель")
    
    executor = AsyncTaskExecutor(max_workers=3)
    
    executor.register_handler(PriorityHandler())
    executor.register_handler(PrintHandler())
    
    sources = [
        create_source(ApiSource),
        create_source(GeneratorSource),
        create_source(FileSource, "files/tasks.txt")
    ]
    
    for source in sources:
        if source:
            await executor.add_tasks_from_source(source)
    
    print(f"Загружено задач в очередь: {executor.task_queue.qsize()}")
    
    await executor.start()
    
    while executor.task_queue.qsize() > 0: # ожидаем опустошения очереди
        await asyncio.sleep(1)
        print(f"Осталось задач: {executor.task_queue.qsize()}")
    
    await executor.stop()
    
    stats = executor.get_statistics()
    print(f"\nСтатистика:")
    print(f"Обработано: {stats['processed']}")
    print(f"Ошибок: {stats['failed']}")
    print(f"Общее время: {stats['total_time']:.2f} сек")
    print(f"Среднее время: {stats['avg_time']:.3f} сек")


def main() -> None:
    print('Список команд для использования:\n'
          '1. Получить задачи из файла\n'
          '2. Получить задачи через API\n'
          '3. Получить задачи с помощью генератора\n'
          '4. Проверить работу контракта\n'
          '5. Работа с очередью\n'
          '6. Асинхронный исполнитель задач\n'
          'Для выхода напишите: "стоп!"')
    
    for cmd in stdin:
        try:
            cmd = cmd.strip()
            if cmd.lower() in ['стоп!', 'стоп', 'exit', 'quit']:
                logging_func("Работа программы была остановлена")
                break
            if not cmd:
                print('Введите команду:')
                continue

            if cmd == '1':
                logging_func("Получить задачи из файла")
                f_source = create_source(FileSource, "files/tasks.txt")
                print_tasks(f_source)
                print("\n")

            elif cmd == '2':
                logging_func("Получить задачи через API")
                a_source = create_source(ApiSource)
                print_tasks(a_source)
                print("\n")

            elif cmd == '3':
                logging_func("Получить задачи с помощью генератора")
                g_source = create_source(GeneratorSource)
                print_tasks(g_source)
                print("\n")

            elif cmd == '4':
                logging_func("Проверить работу контракта")
                print("Проверка контракта")
                for cls in [FileSource, GeneratorSource, ApiSource]:
                    result = issubclass(cls, TaskSource)
                    print(f"{cls.__name__}: {result}")
                print("\n")

            elif cmd == '5':
                logging_func("Демонстрация работы с TaskQueue")
                source = create_source(ApiSource)
                if source:
                    queue = TaskQueue(source.get_tasks())
                    
                    print(f"\nВсего задач в очереди: {len(queue)}")
                    
                    print("\nВывод только новых задач:")
                    new_tasks = queue.filter(status="new")
                    for t in new_tasks:
                        print(f"[Фильтр] {t}")
                    
                    print("\nДелаем описание задачи в верхнем регистре:")
                    descriptions = queue.process(lambda t: t.description.upper())
                    for desc in descriptions:
                        print(f"[Обработка] {desc}")
                print("\n")
            
            elif cmd == '6':
                logging_func("Запуск асинхронного исполнителя")
                asyncio.run(async_demo())
                print("\n")
                    
            else:
                logging_func("Введена неизвестная команда")
                print(f"Неизвестная команда: '{cmd}'. Введите одну из доступных команд.")
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: Ошибка при обработке команды: {e}")


if __name__ == "__main__":
    main()