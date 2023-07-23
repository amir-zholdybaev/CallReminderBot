import asyncio
import aioschedule as sch
from create_bot import dp
from aiogram import executor
from database.models import engine, Base
from handlers import client, admin, states, edit_person
from misc.tasks import remind_to_call, update_persons_departure_status
from misc.task_manager import TaskManager
from sqlalchemy.engine import Engine
from sqlalchemy import event


async def run_daily_tasks(time):
    manager = TaskManager()
    manager.create_task(sch.every().day.at(time), remind_to_call)
    manager.create_task(sch.every().day.at(time), update_persons_departure_status)
    await manager.run(interval=5)


async def on_startup(_):
    Base.metadata.create_all(engine)

    if engine.driver == 'pysqlite':
        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    asyncio.create_task(run_daily_tasks('09:00'))
    await asyncio.sleep(6)
    TaskManager.reset_all_tasks_execution_status()

    print('Бот вышел в онлайн!')


def main():
    client.register_client_handlers(dp)
    admin.register_admin_handlers(dp)
    states.register_states_handlers(dp)
    edit_person.register_edit_person_handlers(dp)

    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)


if __name__ == '__main__':
    main()
