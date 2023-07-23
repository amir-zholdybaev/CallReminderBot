from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.filters import Text
from create_bot import OWNER_ID
from keyboards.admin_kb import create_cancel_kb, create_booking_kb, create_skip_kb
from database.models import engine, Person, PhoneNumber
from database.db_manager import DBManager
from misc.photo_manager import PhotoManager
from misc.task_manager import TaskManager
from misc.validators import FSMValidator
from misc.emojis import (
    telephone, memo, handset, airplane, house_with_garden,
    necktie, x_sign, camera_with_flash, white_check_mark)


class FSMAdmin(StatesGroup):
    admin_ids = [OWNER_ID]

    full_name = State()    # ФИО человека
    phone_numbers = State()    # номер телефона
    region = State()    # регион проживания
    passport_photo = State()    # фото паспорта
    departure_date = State()    # дата вылета в умру
    notes = State()    # заметки
    call_date = State()    # дата звонка человеку

    validator = FSMValidator()

    @staticmethod
    async def save_person_data(data, user_id):
        with DBManager(engine) as db:
            phone_numbers = data['phone_numbers']
            del data['phone_numbers']

            new_person = db.insert(Person, [data])[0]
            db.session.commit()

            rows = [{'phone_number': number,
                     'person_id': new_person.id} for number in phone_numbers]

            db.insert(PhoneNumber, rows)

            photo = PhotoManager.photos.get(key=user_id)

            if photo:
                await photo.download()
                photo.delete()


# @dp.message_handler(commands=['Записать'], state=None)
async def start_loading_person_info(message: types.Message):
    if message.from_user.id in FSMAdmin.admin_ids:
        await FSMAdmin.full_name.set()
        await message.answer(
            f'{necktie} Введите ФИО человека',
            reply_markup=create_cancel_kb())


# @dp.message_handler(state="*", commands='отмена')
# @dp.message_handler(Text(equals='отмена', ignore_case=True), state="*")
async def cancel_loading_person_info(message: types.Message, state: FSMContext):
    if message.from_user.id in FSMAdmin.admin_ids:
        current_state = await state.get_state()

        if current_state is None:
            return

        await state.finish()
        await message.answer(
            f'{x_sign} Запись отменена {x_sign}', reply_markup=create_booking_kb())


# @dp.message_handler(state=FSMAdmin.full_name)
async def load_full_name(message: types.Message, state: FSMContext):
    if message.from_user.id in FSMAdmin.admin_ids:
        async with state.proxy() as data:
            data['full_name'] = message.text

        await FSMAdmin.next()
        await message.answer(
            f"{telephone} Введите номера телефонов через запятую",
            reply_markup=create_cancel_kb())


# @dp.message_handler(state=FSMAdmin.phone_numbers)
async def load_phone_numbers(message: types.Message, state: FSMContext):
    if message.from_user.id in FSMAdmin.admin_ids:
        async with state.proxy() as data:
            data['phone_numbers'] = FSMAdmin.validator.check(
                phone_numbers=[number.strip() for number in message.text.split(',')])

        await FSMAdmin.validator.switch_state_if_valid(state, FSMAdmin.region)
        await FSMAdmin.validator.send_validation_result_message(
            message.chat.id, f"{house_with_garden} Введите регион проживания",
            keyboard=create_cancel_kb())


# @dp.message_handler(state=FSMAdmin.region)
async def load_region(message: types.Message, state: FSMContext):
    if message.from_user.id in FSMAdmin.admin_ids:
        async with state.proxy() as data:
            data['region'] = message.text

        await FSMAdmin.next()
        await message.answer(
            f"{camera_with_flash} Загрузите фото паспорта", reply_markup=create_skip_kb())


# @dp.message_handler(content_types=['photo'], state=FSMAdmin.passport_photo)
async def load_passport_photo(message: types.Message, state: FSMContext):
    if message.from_user.id in FSMAdmin.admin_ids:
        async with state.proxy() as data:
            passport_photo = PhotoManager(
                photo=message.photo[-1],
                photo_id=message.from_user.id
            )
            data['passport_photo'] = passport_photo.path

        await FSMAdmin.next()
        await message.reply(
            f"{airplane} Введите дату вылета в умру в формате гггг-мм-дд",
            reply_markup=create_cancel_kb())


# @dp.message_handler(commands=['Пропустить'], state=FSMAdmin.passport_photo)
async def skip_upload_passport_photo(message: types.Message, state: FSMContext):
    if message.from_user.id in FSMAdmin.admin_ids:
        async with state.proxy() as data:
            data['passport_photo'] = None

        await FSMAdmin.next()
        await message.reply(
            f"{airplane} Введите дату вылета в умру в формате гггг-мм-дд",
            reply_markup=create_cancel_kb())


# @dp.message_handler(state=FSMAdmin.departure_date)
async def load_departure_date(message: types.Message, state: FSMContext):
    if message.from_user.id in FSMAdmin.admin_ids:
        async with state.proxy() as data:
            departure_date = FSMAdmin.validator.check(dates=message.text, current_time_deviation_sign='>=')

            if departure_date:
                data['departure_date'] = departure_date[0]

        await FSMAdmin.validator.switch_state_if_valid(state, FSMAdmin.notes)
        await FSMAdmin.validator.send_validation_result_message(
            message.chat.id, f"{memo} Напишите заметки", keyboard=create_cancel_kb())


# @dp.message_handler(state=FSMAdmin.notes)
async def load_notes(message: types.Message, state: FSMContext):
    if message.from_user.id in FSMAdmin.admin_ids:
        async with state.proxy() as data:
            data['notes'] = message.text

        await FSMAdmin.next()
        await message.answer(
            f"{handset} Введите дату звонка клиенту в формате гггг-мм-дд",
            reply_markup=create_cancel_kb())


# @dp.message_handler(state=FSMAdmin.call_date)
async def load_call_date(message: types.Message, state: FSMContext):
    if message.from_user.id in FSMAdmin.admin_ids:
        async with state.proxy() as data:
            call_date = FSMAdmin.validator.check(dates=message.text, current_time_deviation_sign='>=')

            if call_date:
                data['call_date'] = call_date[0]

            if FSMAdmin.validator.is_valid:
                await FSMAdmin.save_person_data(data, message.from_user.id)

        await FSMAdmin.validator.switch_state_if_valid(state, 'finish')
        await FSMAdmin.validator.send_validation_result_message(
            message.chat.id, f"{white_check_mark} Клиент записан {white_check_mark}",
            keyboard=create_booking_kb())

        TaskManager.reset_all_tasks_execution_status()


def register_states_handlers(dp: Dispatcher):
    dp.register_message_handler(start_loading_person_info, commands=['Записать'], state=None)
    dp.register_message_handler(cancel_loading_person_info, state="*", commands='отмена')
    dp.register_message_handler(cancel_loading_person_info, Text(equals='отмена', ignore_case=True), state="*")
    dp.register_message_handler(load_full_name, state=FSMAdmin.full_name)
    dp.register_message_handler(load_phone_numbers, state=FSMAdmin.phone_numbers)
    dp.register_message_handler(load_region, state=FSMAdmin.region)
    dp.register_message_handler(load_passport_photo, content_types=['photo'], state=FSMAdmin.passport_photo)
    dp.register_message_handler(skip_upload_passport_photo, commands=['Пропустить'], state=FSMAdmin.passport_photo)
    dp.register_message_handler(load_departure_date, state=FSMAdmin.departure_date)
    dp.register_message_handler(load_notes, state=FSMAdmin.notes)
    dp.register_message_handler(load_call_date, state=FSMAdmin.call_date)


def main():
    pass


if __name__ == '__main__':
    main()
