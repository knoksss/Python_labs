import asyncio
from typing import Protocol
from datetime import datetime
from src.tasks.task import Task
from src.tasks.protocol import TaskSource
from src.logging_func import logging_func


class TaskHandler(Protocol): # протокол обработчика задач
    async def can_handle(self, task: Task) -> bool: # проверяет можно ли выполнить задачу
        ...
    
    async def handle(self, task: Task) -> None: # выполняет задачу
        ...


class AsyncTaskExecutor: # асинхронный исполнитель задач
    def __init__(self, max_workers: int = 3):
        self.task_queue: asyncio.Queue[Task] = asyncio.Queue()
        self.handlers: list[TaskHandler] = []
        self.max_workers = max_workers
        self._workers: list[asyncio.Task] = []
        self._running = False
        self._statistics = {
            'processed': 0,
            'failed': 0,
            'total_time': 0.0
        }
    
    def register_handler(self, handler: TaskHandler) -> None: # добавляем новый обработчик
        self.handlers.append(handler)
        logging_func(f"Зарегистрирован обработчик: {handler.__class__.__name__}")
    
    async def add_tasks_from_source(self, source: TaskSource) -> None: # добавление задач в очередь
        tasks = source.get_tasks()
        for task in tasks:
            await self.task_queue.put(task)
            logging_func(f"Добавлена задача {task.id}: {task.description}")
        logging_func(f"Добавлено {len(tasks)} задач из {source.__class__.__name__}")
    
    async def _process_task(self, task: Task) -> None: # обработка одной задачи
        start_time = datetime.now()
        
        try:
            # поиск подходящего обработчика
            for handler in self.handlers:
                if await handler.can_handle(task):
                    logging_func(f"Задача {task.id} принята обработчиком {handler.__class__.__name__}")
                    task.start()
                    await handler.handle(task)
                    task.complete()
                    self._statistics['processed'] += 1
                    break
            else:
                logging_func(f"Не найден обработчик для задачи {task.id}")
                self._statistics['failed'] += 1
        
        except Exception as e:
            logging_func(f"Ошибка при обработке задачи {task.id}: {e}", exc_info=True)
            self._statistics['failed'] += 1
        
        finally:
            elapsed = (datetime.now() - start_time).total_seconds()
            self._statistics['total_time'] += elapsed
            logging_func(f"Задача {task.id} завершена за {elapsed:.2f} сек")
    
    async def _worker(self, worker_id: int) -> None: # извлечение задач из очереди и их выполнение
        logging_func(f"работник {worker_id} запущен")
        while self._running:
            try:
                # асинхронное ожидание задачи с таймаутом
                task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                await self._process_task(task)
                self.task_queue.task_done()
            
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging_func(f"работник {worker_id} ошибка: {e}")
        
        logging_func(f"работник {worker_id} остановлен")
    
    async def start(self) -> None: # запускает исполнителя
        if not self.handlers:
            logging_func("Нет зарегистрированных обработчиков!")
            return
        
        self._running = True
        self._workers = [
            asyncio.create_task(self._worker(i))
            for i in range(self.max_workers)
        ]
        logging_func(f"Асинхронный исполнитель запущен с {self.max_workers} работниками")
    
    async def stop(self) -> None: # останавливаем исполнителя и ожидаем завершения всех задач
        self._running = False
        
        # ожидаем завершения всех работников
        await asyncio.gather(*self._workers, return_exceptions=True)
        
        # если остались задачи в очереди
        remaining = self.task_queue.qsize()
        if remaining:
            logging_func(f"Осталось необработанных задач: {remaining}")
        
        logging_func(f"Исполнитель остановлен. Статистика: {self._statistics}")
    
    def get_statistics(self) -> dict: # возвращаем статистику выполнения
        return {
            **self._statistics,
            'queue_size': self.task_queue.qsize(),
            'avg_time': self._statistics['total_time'] / max(1, self._statistics['processed'])
        }


# пример обработчика
class PrintHandler: # обработчик, который выводит сведения о задаче
    async def can_handle(self, task: Task) -> bool: # может обработать любую задачу
        return True
    
    async def handle(self, task: Task) -> None: # выводит задачу
        await asyncio.sleep(0.5)  # имитация работы
        print(f"Обработана задача: {task}")


class PriorityHandler: # обработчик для задач с высоким приоритетом
    async def can_handle(self, task: Task) -> bool: # обработка задач с приоритетами 4 и 5
        return task.priority >= 4
    
    async def handle(self, task: Task) -> None: # выполнение задачи с высоким приоритетом
        await asyncio.sleep(0.3)
        print(f"Высокий приоритет! Задача {task.id} (приоритет {task.priority})")