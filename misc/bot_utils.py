from create_bot import bot
from aiogram.types import InputFile
from aiogram import types
from aiogram.dispatcher import FSMContext
from database.models import engine
from database.db_manager import DBManager
from misc.utils import edit_text


async def send_message_or_photo(chat_id, text=None, keyboard=None, photo=None):
    if not photo:
        await bot.send_message(
            chat_id=chat_id, text=text, reply_markup=keyboard)
    else:
        await bot.send_photo(
            chat_id=chat_id, photo=InputFile(path_or_bytesio=photo),
            caption=text, reply_markup=keyboard)


async def edit_message(
    chat_id, message, addition_text=None, insertion_offset=None,
    replacement_data: dict | str = None, keyboard=None
):
    message_id = message.message_id

    if message.caption:
        source_text = message.caption
    else:
        source_text = message.text

    final_text = edit_text(
        source_text=source_text, addition_text=addition_text,
        insertion_offset=insertion_offset, replacement_data=replacement_data,)

    if not message.photo:
        await bot.edit_message_text(
            chat_id=chat_id, message_id=message_id,
            text=final_text, reply_markup=keyboard)
    else:
        await bot.edit_message_caption(
            chat_id=chat_id, message_id=message_id,
            caption=final_text, reply_markup=keyboard)


def objects_in_database_checker(model, fsm_admin, error_text, limit=None):
    def outer(func):
        async def wrapper(message: types.Message | types.CallbackQuery, state: FSMContext):
            if message.from_user.id in fsm_admin.admin_ids:
                object_id = int(message.data.split()[1])

                with DBManager(engine) as db:
                    objects = db.get(model, conditions=model.id == object_id, limit=limit)

                    if objects:
                        args = []
                        arg_names = func.__code__.co_varnames
                        args_dict = {
                            'message': message, 'callback': message,
                            'state': state, 'objects': objects, 'db': db}

                        for name in arg_names:
                            try:
                                args.append(args_dict[name])
                            except KeyError:
                                pass

                        if func.__code__.co_argcount - len(args) > 0:
                            args.append(object_id)

                        return await func(*args)
                    else:
                        await message.answer(error_text)
        return wrapper
    return outer


def main():
    pass


if __name__ == '__main__':
    main()
