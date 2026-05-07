from sys import stdin
from src3.tasks.protocol import TaskSource
from src3.working_func import create_source, print_tasks
from src3.sources import FileSource, ApiSource, GeneratorSource
from src3.logging_func import logging_func
from src3.task_queue import TaskQueue

def main() -> None:
    # выводим список команд, котрорыми может воспользоваться пользователь
    print('Список команд для использования:\n'
          '1. Получить задачи из файла(исп. 1)\n'
          '2. Получить задачи через API(исп. 2)\n'
          '3. Получить задачи с помощью генератора(исп. 3)\n'
          '4. Проверить работу контракта(исп. 4)\n'
          '5. Работа с очередью (фильтрация и обработка)\n'
          'Для выхода напишите: "стоп!"')
    
    # принимаем команды из входного потока
    for cmd in stdin:
        try:
            cmd = cmd.strip()
            # если встретили команду остановки, то завершаем
            # работу программы и записываем в shell.log
            if cmd.lower() in ['стоп!', 'стоп', 'exit', 'quit']:
                logging_func("Работа программы была остановлена")
                break
            # если команда не была введена, то ожидаем её(если был нажат enter просто так, к примеру)
            if not cmd:
                print('Введите команду:')
                continue

            if cmd == '1':
                # логируем команду, а после создаём источник и выводим все задачи,
                # которые в нём есть
                logging_func("Получить задачи из файла")
                f_source = create_source(FileSource, "files/tasks.txt")
                print_tasks(f_source)

            elif cmd == '2':
                # аналогично предыдущему, только тут API-заглушка
                logging_func("Получить задачи через API")
                a_source = create_source(ApiSource)
                print_tasks(a_source)

            elif cmd == '3':
                # аналогично первому случаю, только здесь генератор
                logging_func("Получить задачи с помощью генератора")
                g_source = create_source(GeneratorSource)
                print_tasks(g_source)

            elif cmd == '4':
                # проверяем верно ли у нас работает контракт,
                # что у источника есть метод get_tasks()
                logging_func("Проверить работу контракта")
                print("Проверка контракта")
                for cls in [FileSource, GeneratorSource, ApiSource]:
                    result = issubclass(cls, TaskSource)
                    print(f"  {cls.__name__}: {result}")

            elif cmd == '5':
                logging_func("Демонстрация работы с TaskQueue")
                source = create_source(ApiSource)
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
                    
            else:
                # если была введена неверная комана, то также логируем и выводим сообщение
                logging_func("Введена неизвестная команда")
                print(f"Неизвестная команда: '{cmd}'. Введите одну из доступных команд.")
        
        except KeyboardInterrupt:
            break

        except Exception as e:
            print(f"Error: Ошибка при обработке команды: {e}")


if __name__ == "__main__":
    main()