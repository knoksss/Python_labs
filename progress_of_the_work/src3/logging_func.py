import datetime

# функция логирования, которая записывает данные в файл на
# русском языке с указанием времени
def logging_func(command) -> None:
    with open('shell.log', 'a', encoding='utf-8') as f:
        # записывает текущее время в формате год-месяц-дата час-минуты-секунды
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{time}] {command}\n") # записывает команду, которая поступила и время