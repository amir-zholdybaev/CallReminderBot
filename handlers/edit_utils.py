from aiogram import types
from aiogram.dispatcher.filters.state import StatesGroup, State
from create_bot import bot, OWNER_ID
from misc.validators import FSMValidator
from misc.task_manager import TaskManager
from misc.bot_utils import edit_message
from database.db_manager import DBManager
from misc.emojis import white_check_mark
from database.models import engine, Person, PhoneNumber, PastTripDate
from keyboards.admin_kb import (
    create_cancel_changes_kb, create_trip_status_kb, create_edit_kb,
    create_person_data_fields_kb, create_edit_delete_field_kb)
from templates.text_templates import Notifier


class FSMEditAdmin(StatesGroup):
    admin_ids = [OWNER_ID]

    full_name = State()    # ФИО человека
    phone_number = State()    # номер телефона
    region = State()    # регион проживания
    passport_photo = State()    # фото паспорта
    departure_date = State()    # дата вылета в умру
    notes = State()    # заметки
    call_date = State()    # дата звонка человеку
    past_trip_date = State()    # дата прошлой поездки
    adding_phone_number = State()   # для добавления номера телефона
    adding_past_trip_date = State()     # для добавления даты вылета в умру

    validator = FSMValidator()
    person_id = None
    field_id = None
    message_in_progress = None
    old_notification = None


FSMEditAdmin.person_checker_args = (Person, FSMEditAdmin, 'ЭТОТ ЧЕЛОВЕК УЖЕ УДАЛЕН', 1)


def set_fsm_edit_admin_attrs(message, person_id, field_id=None):
    FSMEditAdmin.person_id = person_id
    FSMEditAdmin.field_id = field_id
    FSMEditAdmin.message_in_progress = message


async def update_notification_message(message, notification_text, keyboard=None):
    if FSMEditAdmin.old_notification:
        await FSMEditAdmin.old_notification.delete()

    FSMEditAdmin.old_notification = await message.answer(
        text=notification_text, reply_markup=keyboard)


async def prepare_data_editing(state, callback, person_id, notification_text):
    await state.set()
    await bot.edit_message_reply_markup(
        chat_id=OWNER_ID, message_id=callback.message.message_id,
        reply_markup=create_cancel_changes_kb(person_id))

    await update_notification_message(
        callback.message, notification_text, types.ReplyKeyboardRemove())


async def start_editing(
    callback: types.CallbackQuery, model, id_to_compare,
    db, person_id, update_state, notification_text
):
    field_id = None

    if len(callback.data.split(' ~')) > 1:
        field_id = id_to_compare

    set_fsm_edit_admin_attrs(callback.message, person_id, field_id)

    data_list = db.get(model, conditions=model.id == id_to_compare, limit=1)

    if data_list:
        await prepare_data_editing(update_state, callback, person_id, notification_text)
    else:
        await callback.answer('ЭТИ ДАННЫЕ УЖЕ УДАЛЕНЫ')


async def finish_editing(state, message, notification_text):
    current_state = await state.get_state()

    if current_state is None:
        return

    await state.finish()
    await bot.edit_message_reply_markup(
        chat_id=OWNER_ID, message_id=FSMEditAdmin.message_in_progress.message_id,
        reply_markup=create_edit_kb(FSMEditAdmin.person_id))

    await update_notification_message(message, notification_text, create_trip_status_kb())


async def finish_editing_if_valid(state, message, notification):
    await FSMEditAdmin.validator.switch_state_if_valid(state, 'finish')

    if FSMEditAdmin.validator.is_valid:
        await bot.edit_message_reply_markup(
            chat_id=OWNER_ID, message_id=FSMEditAdmin.message_in_progress.message_id,
            reply_markup=create_edit_kb(FSMEditAdmin.person_id))

    if FSMEditAdmin.old_notification:
        await FSMEditAdmin.old_notification.delete()

    FSMEditAdmin.old_notification = await FSMEditAdmin.validator.send_validation_result_message(
        message.chat.id, success_message=notification, keyboard=create_trip_status_kb())


async def update_person_data(message, model, updates, id_to_compare, state):
    if message.from_user.id in FSMEditAdmin.admin_ids:
        with DBManager(engine) as db:
            db.update(model, updates, conditions=model.id == id_to_compare)
            await bot.delete_message(chat_id=OWNER_ID, message_id=message.message_id)
            await finish_editing(
                state, message, f'{white_check_mark} Изменено на {message.text} {white_check_mark}')


def validate_data_field(message, model, current_time_deviation_sign=None):
    if model == PhoneNumber:
        valid_data_list = FSMEditAdmin.validator.check(phone_numbers=message.text)
    else:
        valid_data_list = FSMEditAdmin.validator.check(
            dates=message.text, current_time_deviation_sign=current_time_deviation_sign)

    if valid_data_list:
        return valid_data_list[0]


async def update_person_data_field(
    message, model, field_key, updates, id_to_compare,
    state, current_time_deviation_sign=None
):

    if message.from_user.id in FSMEditAdmin.admin_ids:
        valid_data = validate_data_field(message, model, current_time_deviation_sign)

        if valid_data:
            with DBManager(engine) as db:
                updates[field_key] = valid_data

                db.update(model, updates, conditions=model.id == id_to_compare)

                TaskManager.reset_all_tasks_execution_status()

        await bot.delete_message(chat_id=OWNER_ID, message_id=message.message_id)
        await finish_editing_if_valid(
            state, message, f'{white_check_mark} Изменено на {message.text} {white_check_mark}')


async def add_person_data_field(
    message, model, field_key, records_data,
    state, current_time_deviation_sign=None
):
    if message.from_user.id in FSMEditAdmin.admin_ids:
        valid_data = validate_data_field(message, model, current_time_deviation_sign)

        if valid_data:
            with DBManager(engine) as db:
                records_data[field_key] = valid_data
                db.insert(model, records_data)

        await bot.delete_message(chat_id=OWNER_ID, message_id=message.message_id)
        await finish_editing_if_valid(
            state, message, f'{white_check_mark} Добавлено: {message.text} {white_check_mark}')


async def delete_person_data_field(callback, model, db):
    field_id = int(callback.data.split(" ~")[2])

    data_field_list = db.get(model, conditions=model.id == field_id, limit=1)

    if data_field_list:
        db.delete(model, conditions=model.id == field_id)

        await bot.edit_message_reply_markup(
            chat_id=OWNER_ID, message_id=callback.message.message_id,
            reply_markup=create_edit_kb(FSMEditAdmin.person_id))

        await update_notification_message(
            callback.message, 'ДАННЫЕ УДАЛЕНЫ', create_trip_status_kb())
    else:
        await callback.answer('ЭТИ ДАННЫЕ УЖЕ УДАЛЕНЫ')


async def handle_field_deletion(callback, model, db):
    await edit_message(
        chat_id=OWNER_ID, message=callback.message,
        replacement_data={
            Notifier.delete_confirmation_question: Notifier.delete_success_message})

    await delete_person_data_field(callback, model, db)


async def handle_field_deletion_undo(callback, field_name, person_id):
    await edit_message(
        chat_id=OWNER_ID, message=callback.message,
        replacement_data={
            Notifier.delete_confirmation_question: Notifier.delete_cancelled_message})

    await send_selected_field_keyboard(callback, field_name, person_id)


def create_field_values_keyboard(callback: types.CallbackQuery, model, receiving_columns, field_type):
    if callback.from_user.id in FSMEditAdmin.admin_ids:
        set_fsm_edit_admin_attrs(callback.message, callback.data.split()[1])

        with DBManager(engine) as db:
            fields = db.get(model, columns=receiving_columns,
                            conditions=model.person_id == FSMEditAdmin.person_id)

            if fields:
                field_values = []

                if model == PastTripDate:
                    for field in fields:
                        field_values.append((field[0].strftime('%Y-%m-%d'), field[1]))

                    fields = field_values

            person_data_fields_kb = create_person_data_fields_kb(FSMEditAdmin.person_id, fields, field_type)

            return person_data_fields_kb


async def send_field_values_keyboard(callback, keyboard):
    await bot.edit_message_reply_markup(
        chat_id=OWNER_ID, message_id=callback.message.message_id,
        reply_markup=keyboard)


async def send_selected_field_keyboard(callback: types.CallbackQuery, field_type, person_id):
    set_fsm_edit_admin_attrs(callback.message, int(callback.data.split()[1]),
                             callback.data.split(" ~")[2])

    await bot.edit_message_reply_markup(
        chat_id=OWNER_ID,
        message_id=callback.message.message_id,
        reply_markup=create_edit_delete_field_kb(
            field_type, person_id, callback.data.split(" ~")[2],
            callback.data.split(" ~")[1])
    )
