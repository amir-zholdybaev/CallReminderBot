from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from create_bot import bot, OWNER_ID
from keyboards.admin_kb import (
    create_edit_kb, create_edit_delete_person_kb,
    create_delete_confirmation_keyboard)
from database.db_manager import DBManager
from database.models import engine, Person, PhoneNumber, PastTripDate
from misc.photo_manager import PhotoManager
from misc.bot_utils import edit_message, objects_in_database_checker
from handlers.edit_utils import (
    FSMEditAdmin, start_editing, finish_editing, update_person_data,
    create_field_values_keyboard, send_field_values_keyboard, send_selected_field_keyboard,
    update_person_data_field, handle_field_deletion, handle_field_deletion_undo,
    set_fsm_edit_admin_attrs, prepare_data_editing, add_person_data_field)
from misc.emojis import (
    telephone, memo, handset, airplane, house_with_garden,
    date, necktie, x_sign, camera_with_flash, white_check_mark)
from templates.text_templates import Notifier


# @dp.callback_query_handler(Text(startswith='passport_photo'))
@objects_in_database_checker(*FSMEditAdmin.person_checker_args)
async def start_edit_passport_photo(callback: types.CallbackQuery, db, person_id):
    await start_editing(callback, Person, person_id, db, person_id,
                        FSMEditAdmin.passport_photo, f'{camera_with_flash} Загрузите фото паспорта')


# @dp.callback_query_handler(state="*", Text(startswith='cancel'))
async def cancel_changes(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id in FSMEditAdmin.admin_ids:
        await finish_editing(state, callback.message, f'{x_sign} Изменение отменено {x_sign}')


# @dp.message_handler(content_types=['photo'], state=FSMAdmin.passport_photo)
async def edit_passport_photo(message: types.Message, state: FSMContext):
    if message.from_user.id in FSMEditAdmin.admin_ids:
        passport_photo = PhotoManager(photo=message.photo[-1], photo_id=message.from_user.id)

        with DBManager(engine) as db:
            photo = PhotoManager.photos.get(key=message.from_user.id)

            if photo:
                await photo.download()
                photo.delete()

            db.update(Person, {'passport_photo': passport_photo.path},
                      conditions=Person.id == FSMEditAdmin.person_id)

            await finish_editing(
                state, message, f'{white_check_mark} Фото паспорта изменено {white_check_mark}')


# @dp.callback_query_handler(Text(startswith='full_name'))
@objects_in_database_checker(*FSMEditAdmin.person_checker_args)
async def start_edit_full_name(callback: types.CallbackQuery, db, person_id):
    await start_editing(callback, Person, person_id, db, person_id,
                        FSMEditAdmin.full_name, f'{necktie} Введите новое ФИО')


# @dp.message_handler(state=FSMEditAdmin.full_name)
async def edit_full_name(message: types.Message, state: FSMContext):
    await update_person_data(message, Person, {'full_name': message.text},
                             FSMEditAdmin.person_id, state)


# @dp.callback_query_handler(Text(startswith='phone_numbers'))
@objects_in_database_checker(*FSMEditAdmin.person_checker_args)
async def send_phone_numbers_keyboard(callback: types.CallbackQuery):
    person_data_fields_kb = create_field_values_keyboard(
        callback, PhoneNumber, ['phone_number', 'id'], 'phone_number')

    await send_field_values_keyboard(callback, person_data_fields_kb)


# @dp.callback_query_handler(Text(startswith='phone_number'))
@objects_in_database_checker(*FSMEditAdmin.person_checker_args)
async def choose_phone_number(callback: types.CallbackQuery, person_id):
    await send_selected_field_keyboard(callback, 'phone_number', person_id)


# @dp.callback_query_handler(Text(startswith='edit_phone_number'))
@objects_in_database_checker(*FSMEditAdmin.person_checker_args)
async def start_edit_phone_number(callback: types.CallbackQuery, db, person_id):
    field_id = int(callback.data.split(' ~')[2])

    await start_editing(callback, PhoneNumber, field_id, db, person_id,
                        FSMEditAdmin.phone_number, f'{telephone} Введите новый номер телефона')


# @dp.message_handler(state=FSMEditAdmin.phone_number)
async def edit_phone_number(message: types.Message, state: FSMContext):
    await update_person_data_field(
        message=message, model=PhoneNumber, field_key='phone_number',
        updates={'phone_number': 'target_field'}, id_to_compare=FSMEditAdmin.field_id,
        state=state, current_time_deviation_sign=None)


# @dp.callback_query_handler(Text(startswith='try_remove_field'))
@objects_in_database_checker(*FSMEditAdmin.person_checker_args)
async def handle_delete_field_button(callback: types.CallbackQuery, person_id):
    field_type = callback.data.split()[2]
    field_value = callback.data.split(' ~')[1]
    field_id = int(callback.data.split(' ~')[2])

    await edit_message(
        chat_id=OWNER_ID, message=callback.message,
        addition_text=Notifier.delete_confirmation_question,
        replacement_data={
            Notifier.delete_cancelled_message: '',
            Notifier.delete_success_message: ''},
        keyboard=create_delete_confirmation_keyboard(
            person_id, field_type, field_value=field_value, field_id=field_id))


# @dp.callback_query_handler(Text(startswith='abort_deletion_phone_number'))
@objects_in_database_checker(*FSMEditAdmin.person_checker_args)
async def abort_phone_number_deletion(callback: types.CallbackQuery, person_id):
    await handle_field_deletion_undo(callback, 'phone_number', person_id)


# @dp.callback_query_handler(Text(startswith='delete_phone_number'))
@objects_in_database_checker(*FSMEditAdmin.person_checker_args)
async def delete_phone_number(callback: types.CallbackQuery, db):
    await handle_field_deletion(callback, PhoneNumber, db)


# @dp.callback_query_handler(Text(startswith='region'))
@objects_in_database_checker(*FSMEditAdmin.person_checker_args)
async def start_edit_region(callback: types.CallbackQuery, db, person_id):
    await start_editing(callback, Person, person_id, db, person_id,
                        FSMEditAdmin.region, f'{house_with_garden} Введите название региона')


# @dp.message_handler(state=FSMEditAdmin.region)
async def edit_region(message: types.Message, state: FSMContext):
    await update_person_data(message, Person, {'region': message.text},
                             FSMEditAdmin.person_id, state)


# @dp.callback_query_handler(Text(startswith='departure_date'))
@objects_in_database_checker(*FSMEditAdmin.person_checker_args)
async def start_edit_departure_date(callback: types.CallbackQuery, db, person_id):
    await start_editing(callback, Person, person_id, db, person_id, FSMEditAdmin.departure_date,
                        f'{airplane} Введите дату вылета в умру в формате гггг-мм-дд')


# @dp.message_handler(state=FSMEditAdmin.departure_date)
async def edit_departure_date(message: types.Message, state: FSMContext):
    await update_person_data_field(
        message=message, model=Person, field_key='departure_date',
        updates={'departure_date': 'target_field', 'is_departed': False},
        id_to_compare=FSMEditAdmin.person_id, state=state, current_time_deviation_sign='>=')


# @dp.callback_query_handler(Text(startswith='call_date'))
@objects_in_database_checker(*FSMEditAdmin.person_checker_args)
async def start_edit_call_date(callback: types.CallbackQuery, db, person_id):
    await start_editing(callback, Person, person_id, db, person_id, FSMEditAdmin.call_date,
                        f'{handset} Введите дату звонка клиенту в формате гггг-мм-дд')


# @dp.message_handler(state=FSMEditAdmin.call_date)
async def edit_call_date(message: types.Message, state: FSMContext):
    await update_person_data_field(
        message=message, model=Person, field_key='call_date',
        updates={'call_date': 'target_field', 'was_dialed': False},
        id_to_compare=FSMEditAdmin.person_id, state=state, current_time_deviation_sign='>=')


# @dp.callback_query_handler(Text(startswith='past_trip_dates'))
@objects_in_database_checker(*FSMEditAdmin.person_checker_args)
async def send_past_trip_dates_keyboard(callback: types.CallbackQuery):
    person_data_fields_kb = create_field_values_keyboard(
        callback, PastTripDate, ['trip_date', 'id'], 'past_trip_date')

    await send_field_values_keyboard(callback, person_data_fields_kb)


# @dp.callback_query_handler(Text(startswith='past_trip_date'))
@objects_in_database_checker(*FSMEditAdmin.person_checker_args)
async def choose_past_trip_date(callback: types.CallbackQuery, person_id):
    await send_selected_field_keyboard(callback, 'past_trip_date', person_id)


# @dp.callback_query_handler(Text(startswith='edit_past_trip_date'))
@objects_in_database_checker(*FSMEditAdmin.person_checker_args)
async def start_edit_past_trip_date(callback: types.CallbackQuery, db, person_id):
    field_id = int(callback.data.split(' ~')[2])

    await start_editing(callback, PastTripDate, field_id, db, person_id,
                        FSMEditAdmin.past_trip_date, f'{date} Введите новую дату')


# @dp.message_handler(state=FSMEditAdmin.past_trip_date)
async def edit_past_trip_date(message: types.Message, state: FSMContext):
    await update_person_data_field(
        message=message, model=PastTripDate, field_key='trip_date',
        updates={'trip_date': 'target_field'}, id_to_compare=FSMEditAdmin.field_id,
        state=state, current_time_deviation_sign=None)


# @dp.callback_query_handler(Text(startswith='abort_deletion_past_trip_date'))
@objects_in_database_checker(*FSMEditAdmin.person_checker_args)
async def abort_past_trip_date_deletion(callback: types.CallbackQuery, person_id):
    await handle_field_deletion_undo(callback, 'past_trip_date', person_id)


# @dp.callback_query_handler(Text(startswith='delete_past_trip_date'))
@objects_in_database_checker(*FSMEditAdmin.person_checker_args)
async def delete_past_trip_date(callback: types.CallbackQuery, db):
    await handle_field_deletion(callback, PastTripDate, db)


# @dp.callback_query_handler(Text(startswith='notes'))
@objects_in_database_checker(*FSMEditAdmin.person_checker_args)
async def start_edit_notes(callback: types.CallbackQuery, db, person_id):
    await start_editing(
        callback, Person, person_id,
        db, person_id, FSMEditAdmin.notes, f'{memo} Напишите заметки')


# @dp.message_handler(state=FSMEditAdmin.notes)
async def edit_notes(message: types.Message, state: FSMContext):
    await update_person_data(
        message, Person, {'notes': message.text}, FSMEditAdmin.person_id, state)


# @dp.callback_query_handler(Text(startswith='add_field'))
@objects_in_database_checker(*FSMEditAdmin.person_checker_args)
async def start_ading_field(callback: types.CallbackQuery, person_id):
    field_type = callback.data.split()[2]
    adding_state = getattr(FSMEditAdmin, f'adding_{field_type}')

    if field_type == 'phone_number':
        emoji = telephone
        prompt = 'номер телефона'
    else:
        emoji = date
        prompt = 'дату прошлой поездки'

    set_fsm_edit_admin_attrs(callback.message, person_id)
    await prepare_data_editing(adding_state, callback, person_id, f'{emoji} Введите {prompt}')


# @dp.message_handler(state=FSMEditAdmin.adding_phone_number)
async def add_phone_number(message: types.Message, state: FSMContext):
    await add_person_data_field(
        message, PhoneNumber, 'phone_number',
        {'phone_number': 'target_field', 'person_id': FSMEditAdmin.person_id}, state)


# @dp.message_handler(state=FSMEditAdmin.adding_past_trip_date)
async def add_past_trip_date(message: types.Message, state: FSMContext):
    await add_person_data_field(
        message, PastTripDate, 'trip_date',
        {'trip_date': 'target_field', 'person_id': FSMEditAdmin.person_id},
        state, current_time_deviation_sign='<=')


# @dp.callback_query_handler(Text(startswith='go_back'))
@objects_in_database_checker(*FSMEditAdmin.person_checker_args)
async def handle_back_button(callback: types.CallbackQuery, person_id):
    kb_type = callback.data.split()[2]

    kb_creators = {
        'edit_delete': (create_edit_delete_person_kb, (person_id, )),
        'fields': (create_edit_kb, (person_id, )),
        'phone_number': (
            create_field_values_keyboard,
            (callback, PhoneNumber, ['phone_number', 'id'], kb_type)
        ),
        'past_trip_date': (
            create_field_values_keyboard,
            (callback, PastTripDate, ['trip_date', 'id'], kb_type)
        )
    }

    keyboard = kb_creators[kb_type][0](*kb_creators[kb_type][1])

    await bot.edit_message_reply_markup(
        chat_id=OWNER_ID, message_id=callback.message.message_id,
        reply_markup=keyboard)


def register_edit_person_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(start_edit_passport_photo, Text(startswith='passport_photo'))
    dp.register_callback_query_handler(cancel_changes, Text(startswith='cancel'), state="*")
    dp.register_message_handler(edit_passport_photo, content_types=['photo'], state=FSMEditAdmin.passport_photo)
    dp.register_callback_query_handler(start_edit_full_name, Text(startswith='full_name'))
    dp.register_message_handler(edit_full_name, state=FSMEditAdmin.full_name)
    dp.register_callback_query_handler(send_phone_numbers_keyboard, Text(startswith='phone_numbers'))
    dp.register_callback_query_handler(choose_phone_number, Text(startswith='phone_number'))
    dp.register_callback_query_handler(start_edit_phone_number, Text(startswith='edit_phone_number'))
    dp.register_message_handler(edit_phone_number, state=FSMEditAdmin.phone_number)
    dp.register_callback_query_handler(handle_delete_field_button, Text(startswith='try_remove_field'))
    dp.register_callback_query_handler(abort_phone_number_deletion, Text(startswith='abort_deletion_phone_number'))
    dp.register_callback_query_handler(delete_phone_number, Text(startswith='delete_phone_number'))
    dp.register_callback_query_handler(start_edit_region, Text(startswith='region'))
    dp.register_message_handler(edit_region, state=FSMEditAdmin.region)
    dp.register_callback_query_handler(start_edit_departure_date, Text(startswith='departure_date'))
    dp.register_message_handler(edit_departure_date, state=FSMEditAdmin.departure_date)
    dp.register_callback_query_handler(start_edit_call_date, Text(startswith='call_date'))
    dp.register_message_handler(edit_call_date, state=FSMEditAdmin.call_date)
    dp.register_callback_query_handler(send_past_trip_dates_keyboard, Text(startswith='past_trip_dates'))
    dp.register_callback_query_handler(choose_past_trip_date, Text(startswith='past_trip_date'))
    dp.register_callback_query_handler(start_edit_past_trip_date, Text(startswith='edit_past_trip_date'))
    dp.register_message_handler(edit_past_trip_date, state=FSMEditAdmin.past_trip_date)
    dp.register_callback_query_handler(abort_past_trip_date_deletion, Text(startswith='abort_deletion_past_trip_date'))
    dp.register_callback_query_handler(delete_past_trip_date, Text(startswith='delete_past_trip_date'))
    dp.register_callback_query_handler(start_edit_notes, Text(startswith='notes'))
    dp.register_message_handler(edit_notes, state=FSMEditAdmin.notes)
    dp.register_callback_query_handler(start_ading_field, Text(startswith='add_field'))
    dp.register_message_handler(add_phone_number, state=FSMEditAdmin.adding_phone_number)
    dp.register_message_handler(add_past_trip_date, state=FSMEditAdmin.adding_past_trip_date)
    dp.register_callback_query_handler(handle_back_button, Text(startswith='go_back'))


def main():
    pass


if __name__ == '__main__':
    main()
