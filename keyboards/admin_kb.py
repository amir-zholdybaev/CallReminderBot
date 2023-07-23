from .create_keyboard import create_simple_keyboard
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def create_booking_kb():
    BUTTONS = {
        '/Записать': 'row',
        '/Посмотреть': 'row',
    }
    return create_simple_keyboard(BUTTONS, one_time_keyboard=False)


def create_cancel_kb():
    CANCEL_BTN = KeyboardButton('/Отмена')
    EMPTY_BTN = KeyboardButton(' ')

    CANCEL_KEYBOARD = ReplyKeyboardMarkup(resize_keyboard=True)
    CANCEL_KEYBOARD.row(EMPTY_BTN, CANCEL_BTN, EMPTY_BTN)

    return CANCEL_KEYBOARD


def create_skip_kb():
    SKIP_BTN = KeyboardButton('/Пропустить')
    CANCEL_BTN = KeyboardButton('/Отмена')
    EMPTY_BTN = KeyboardButton(' ')

    SKIP_KEYBOARD = ReplyKeyboardMarkup(resize_keyboard=True)
    SKIP_KEYBOARD.add(SKIP_BTN)
    SKIP_KEYBOARD.row(EMPTY_BTN, CANCEL_BTN, EMPTY_BTN)

    return SKIP_KEYBOARD


def create_trip_status_kb():
    BUTTONS = {
        '/Готовые_к_поездке': 'row',
        '/Уже_выехали/съездили': 'row',
        '/Назад': 'column',
    }
    return create_simple_keyboard(BUTTONS, one_time_keyboard=False)


def create_details_kb(person_id):
    DETAILS_BTN = InlineKeyboardButton(
        text='Подробнее',
        callback_data=f'details {person_id}'
    )
    DETAILS_KEYBOARD = InlineKeyboardMarkup()
    DETAILS_KEYBOARD.add(DETAILS_BTN)

    return DETAILS_KEYBOARD


def create_edit_delete_person_kb(person_id):
    EDIT_BTN = InlineKeyboardButton(
        text='Изменить',
        callback_data=f'edit_person {person_id}'
    )
    DELETE_BTN = InlineKeyboardButton(
        text='Удалить',
        callback_data=f'try_delete {person_id}'
    )

    EDIT_DELETE_KEYBOARD = InlineKeyboardMarkup()
    EDIT_DELETE_KEYBOARD.add(EDIT_BTN, DELETE_BTN)

    return EDIT_DELETE_KEYBOARD


def create_delete_confirmation_keyboard(person_id, target, field_value=None, field_id=None):
    CONFIRM_BTN = InlineKeyboardButton(
        text='Да',
        callback_data=f'delete_{target} {person_id} ~{field_value} ~{field_id}'
    )
    CANCEL_BTN = InlineKeyboardButton(
        text='Нет',
        callback_data=f'abort_deletion_{target} {person_id} {target} ~{field_value} ~{field_id}'
    )

    DELETE_CONFIRMATION_KEYBOARD = InlineKeyboardMarkup()
    DELETE_CONFIRMATION_KEYBOARD.add(CONFIRM_BTN, CANCEL_BTN)

    return DELETE_CONFIRMATION_KEYBOARD


def create_edit_delete_field_kb(filed_type, person_id, field_id, field_value):
    VALUE_BTN = InlineKeyboardButton(text=field_value, callback_data=field_value)

    EDIT_BTN = InlineKeyboardButton(
        text='Изменить',
        callback_data=f'edit_{filed_type} {person_id} ~{field_value} ~{field_id}'
    )
    DELETE_BTN = InlineKeyboardButton(
        text='Удалить',
        callback_data=f'try_remove_field {person_id} {filed_type} ~{field_value} ~{field_id}'
    )
    GO_BACK_BTN = InlineKeyboardButton(
        text='Назад', callback_data=f'go_back {person_id} {filed_type}'
    )

    EDIT_DELETE_KEYBOARD = InlineKeyboardMarkup()
    EDIT_DELETE_KEYBOARD.add(VALUE_BTN)
    EDIT_DELETE_KEYBOARD.add(EDIT_BTN, DELETE_BTN)
    EDIT_DELETE_KEYBOARD.add(GO_BACK_BTN)

    return EDIT_DELETE_KEYBOARD


def create_edit_kb(person_id):
    PASSPORT_PHOTO = InlineKeyboardButton(
        text='Фото паспорта', callback_data=f'passport_photo {person_id}'
    )
    FULL_NAME = InlineKeyboardButton(
        text='ФИО', callback_data=f'full_name {person_id}'
    )
    PHONE_NUMBERS = InlineKeyboardButton(
        text='Номера', callback_data=f'phone_numbers {person_id}'
    )
    REGION = InlineKeyboardButton(
        text='Регион', callback_data=f'region {person_id}'
    )
    DEPARTURE_DATE = InlineKeyboardButton(
        text='Дата отъезда', callback_data=f'departure_date {person_id}'
    )
    NOTES = InlineKeyboardButton(
        text='Заметки', callback_data=f'notes {person_id}'
    )
    CALL_DATE = InlineKeyboardButton(
        text='Дата звонка', callback_data=f'call_date {person_id}'
    )
    PAST_TRIP_DATES = InlineKeyboardButton(
        text='Прошлые поездки', callback_data=f'past_trip_dates {person_id}'
    )
    GO_BACK_BTN = InlineKeyboardButton(
        text='Назад', callback_data=f'go_back {person_id} edit_delete'
    )

    EDIT_KEYBOARD = InlineKeyboardMarkup()
    EDIT_KEYBOARD.add(PASSPORT_PHOTO, FULL_NAME, PHONE_NUMBERS)
    EDIT_KEYBOARD.add(DEPARTURE_DATE, CALL_DATE, REGION)
    EDIT_KEYBOARD.add(PAST_TRIP_DATES, NOTES, GO_BACK_BTN)

    return EDIT_KEYBOARD


def create_cancel_changes_kb(person_id):
    CANCEL_BTN = InlineKeyboardButton(
        text='Отменить',
        callback_data=f'cancel {person_id}'
    )

    CANCEL_CHANGES_KEYBOARD = InlineKeyboardMarkup()
    CANCEL_CHANGES_KEYBOARD.add(CANCEL_BTN)

    return CANCEL_CHANGES_KEYBOARD


def create_person_data_fields_kb(person_id, field_list, filed_type):
    FIELDS_KEYBOARD = InlineKeyboardMarkup()
    buttons = []

    for index, field in enumerate(field_list):
        field_value = field[0]
        field_id = field[1]

        FIELD_BTN = InlineKeyboardButton(
            text=field_value,
            callback_data=f'{filed_type} {person_id} ~{field_value} ~{field_id}'
        )

        if (index + 1) % 3 != 0:
            buttons.append(FIELD_BTN)

            if len(buttons) == 2 or len(field_list) < 2:
                FIELDS_KEYBOARD.add(*buttons)
                buttons.clear()
        else:
            FIELDS_KEYBOARD.add(FIELD_BTN)

    ADD_FIELD_BTN = InlineKeyboardButton(
        text='Добавить', callback_data=f'add_field {person_id} {filed_type}'
    )
    GO_BACK_BTN = InlineKeyboardButton(
        text='Назад', callback_data=f'go_back {person_id} fields'
    )

    FIELDS_KEYBOARD.add(ADD_FIELD_BTN, GO_BACK_BTN)

    return FIELDS_KEYBOARD


def create_empty_kb():
    EMPTY_KEYBOARD = InlineKeyboardMarkup()
    return EMPTY_KEYBOARD


def main():
    pass


if __name__ == '__main__':
    main()
