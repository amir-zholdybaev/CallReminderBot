import asyncio
import aioschedule


class Task:
    def __init__(self, function, *args, **kwargs):
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_completed = True

    async def run(self):
        await self.function(*self.args, **self.kwargs)
        self.is_completed = True


class TaskManager:
    tasks = []
    all_tasks_completed = True

    @classmethod
    def create_task(cls, when_time_comes, func, *args, **kwargs):
        when_time_comes.do(func, *args, **kwargs)
        cls.tasks.append(Task(func, *args, **kwargs))

    @classmethod
    async def run(cls, interval=2):
        while True:
            await aioschedule.run_pending()
            await asyncio.sleep(interval)

            if not cls.all_tasks_completed:
                for task in cls.tasks:
                    if not task.is_completed:
                        await task.run()

                cls.all_tasks_completed = True

    @classmethod
    def reset_tasks_execution_status(cls, funcs):
        for task in cls.tasks:
            if task.function in funcs:
                task.is_completed = False

        cls.all_tasks_completed = False

    @classmethod
    def reset_all_tasks_execution_status(cls):
        for task in cls.tasks:
            task.is_completed = False

        cls.all_tasks_completed = False


def main():
    pass


if __name__ == '__main__':
    main()
