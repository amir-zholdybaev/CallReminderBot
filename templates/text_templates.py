from misc.emojis import (
    telephone, memo, date, handset, airplane,
    house_with_garden, necktie, red_circle, white_check_mark)


def get_person_partial_info_text(person):
    phone_numbers = ''

    for index, table_row in enumerate(person.phone_numbers):
        if index < len(person.phone_numbers) - 1:
            phone_numbers += f'{table_row.phone_number}\n'
        else:
            phone_numbers += table_row.phone_number

    person_partial_info_text = (
        f'{person.full_name}\n\n'
        f'{phone_numbers}'
    )

    return person_partial_info_text


def get_person_full_info_text(person):
    phone_numbers = ''
    departure_date = 'Пусто'
    notes = 'Пусто'
    past_trip_dates = 'Пусто\n'

    if person.departure_date:
        departure_date = person.departure_date

    if person.notes:
        notes = person.notes

    if person.past_trip_dates:
        past_trip_dates = ''

        for table_row in person.past_trip_dates:
            past_trip_dates += f'{table_row.trip_date}\n'

    if person.phone_numbers:
        for table_row in person.phone_numbers:
            phone_numbers += f'{table_row.phone_number}\n'

    person_full_info_text = (
        f'{necktie} ФИО:\n{person.full_name}\n\n'
        f'{telephone} Номера:\n{phone_numbers}\n'
        f'{house_with_garden} Регион:\n{person.region}\n\n'
        f'{airplane} Предстоящая дата отъезда:\n{departure_date}\n\n'
        f'{memo} Заметки:\n{notes}\n\n'
        f'{handset} Когда позвонить:\n{person.call_date}\n\n'
        f'{date} Даты прошлых поездок:\n{past_trip_dates}'
    )

    return person_full_info_text


class Notifier():
    delete_confirmation_question = f'\n\n{red_circle} ВЫ ДЕЙСТВИТЕЛЬНО ХОТИТЕ УДАЛИТЬ? {red_circle}'
    delete_cancelled_message = f'\n\n{white_check_mark} УДАЛЕНИЕ ОТМЕНЕНО {white_check_mark}'
    delete_success_message = f'\n\n{white_check_mark} УДАЛЕНО {white_check_mark}'


def main():
    pass


if __name__ == '__main__':
    main()
