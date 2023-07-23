from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from create_bot import bot, OWNER_ID
from .states import FSMAdmin
from keyboards.admin_kb import (
    create_booking_kb, create_trip_status_kb,
    create_details_kb, create_edit_delete_person_kb,
    create_edit_kb, create_delete_confirmation_keyboard
)
from database.models import engine
from database.db_manager import DBManager
from templates.text_templates import get_person_partial_info_text, get_person_full_info_text, Notifier
from database.models import Person
from misc.bot_utils import send_message_or_photo, edit_message, objects_in_database_checker
from handlers.edit_utils import FSMEditAdmin
from misc.emojis import not_entry_sign, red_car
# import hashlib

FSMAdmin.person_checker_args = (Person, FSMAdmin, 'ЭТОТ ЧЕЛОВЕК УЖЕ УДАЛЕН', 1)


async def show_persons_partial_info(persons, message):
    if persons:
        for person in persons:
            await message.answer(
                get_person_partial_info_text(person),
                reply_markup=create_details_kb(person.id))
    else:
        await message.answer(f'{not_entry_sign} Здесь нет записей!')


# @dp.message_handler(commands=["start"])
async def send_booking_keyboard(message: types.Message):
    if message.from_user.id in FSMAdmin.admin_ids:
        await bot.send_message(
            message.from_user.id, 'Чего надо хозяин?',
            reply_markup=create_booking_kb())


# @dp.message_handler(commands=["Посмотреть"])
async def send_trip_status_keyboard(message: types.Message):
    if message.from_user.id in FSMAdmin.admin_ids:
        await bot.send_message(
            message.from_user.id, f'{red_car} Статус поездки ',
            reply_markup=create_trip_status_kb())


# @dp.message_handler(commands=["Готовые_к_поездке"])
async def show_persons_ready_for_trip(message: types.Message):
    if message.from_user.id in FSMAdmin.admin_ids:
        with DBManager(engine) as db:
            not_departed_persons = db.get(Person, conditions=Person.is_departed == False)
            await show_persons_partial_info(not_departed_persons, message)


# @dp.message_handler(commands=["Уже_выехали/съездили"])
async def show_departed_persons(message: types.Message):
    if message.from_user.id in FSMAdmin.admin_ids:
        with DBManager(engine) as db:
            departed_persons = db.get(Person, conditions=Person.is_departed == True)
            await show_persons_partial_info(departed_persons, message)


# @dp.callback_query_handler(Text(startswith='details'))
@objects_in_database_checker(*FSMAdmin.person_checker_args)
async def show_person_details(callback: types.CallbackQuery, objects, person_id):
    person = objects[0]

    person_full_info_text = get_person_full_info_text(person)

    await send_message_or_photo(
        OWNER_ID, text=person_full_info_text,
        keyboard=create_edit_delete_person_kb(person_id),
        photo=person.passport_photo)

    await callback.answer('Полная информация: ')


# @dp.callback_query_handler(Text(startswith='edit_person'))
@objects_in_database_checker(*FSMAdmin.person_checker_args)
async def edit_person_data(callback: types.CallbackQuery, person_id):
    FSMEditAdmin.person_id = person_id

    await bot.edit_message_reply_markup(
        chat_id=OWNER_ID,
        message_id=callback.message.message_id,
        reply_markup=create_edit_kb(person_id))


# @dp.callback_query_handler(Text(startswith='try_delete'))
@objects_in_database_checker(*FSMAdmin.person_checker_args)
async def handle_delete_button(callback: types.CallbackQuery, person_id):
    await edit_message(
        chat_id=OWNER_ID, message=callback.message,
        addition_text=Notifier.delete_confirmation_question,
        replacement_data={
            Notifier.delete_cancelled_message: '',
            Notifier.delete_success_message: ''},
        keyboard=create_delete_confirmation_keyboard(person_id, 'person'))


# @dp.callback_query_handler(Text(startswith='delete_person'))
@objects_in_database_checker(*FSMAdmin.person_checker_args)
async def delete_person(callback: types.CallbackQuery, db, person_id):
    db.delete(Person, conditions=Person.id == person_id)

    await edit_message(
        chat_id=OWNER_ID, message=callback.message,
        replacement_data={
            Notifier.delete_confirmation_question: Notifier.delete_success_message})


# @dp.callback_query_handler(Text(startswith='abort_deletion'))
@objects_in_database_checker(*FSMAdmin.person_checker_args)
async def abort_person_deletion(callback: types.CallbackQuery, person_id):
    await edit_message(
        chat_id=OWNER_ID, message=callback.message,
        replacement_data={
            Notifier.delete_confirmation_question: Notifier.delete_cancelled_message},
        keyboard=create_edit_delete_person_kb(person_id))


# @dp.message_handler(commands=["Назад"])
async def go_back(message: types.Message):
    if message.from_user.id in FSMAdmin.admin_ids:
        await bot.send_message(
            message.from_user.id,
            'Чего надо хозяин?',
            reply_markup=create_booking_kb())


def register_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(send_booking_keyboard, commands=["start"])
    dp.register_message_handler(send_trip_status_keyboard, commands=["Посмотреть"])
    dp.register_message_handler(show_persons_ready_for_trip, commands=["Готовые_к_поездке"])
    dp.register_message_handler(show_departed_persons, commands=["Уже_выехали/съездили"])
    dp.register_callback_query_handler(show_person_details, Text(startswith='details'))
    dp.register_callback_query_handler(edit_person_data, Text(startswith='edit_person'))
    dp.register_callback_query_handler(handle_delete_button, Text(startswith='try_delete'))
    dp.register_callback_query_handler(delete_person, Text(startswith='delete_person'))
    dp.register_callback_query_handler(abort_person_deletion, Text(startswith='abort_deletion_person'))
    dp.register_message_handler(go_back, commands=["Назад"])


def main():
    pass


if __name__ == '__main__':
    main()
