class TaskError(Exception):
    pass


class TaskPriorityError(TaskError):
    pass


class TaskStatusError(TaskError):
    pass


class TaskDescriptionError(TaskError):
    pass