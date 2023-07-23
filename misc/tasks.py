import asyncio
from datetime import datetime
from create_bot import OWNER_ID
from database.db_manager import DBManager
from database.models import engine, Person, PastTripDate
from templates.text_templates import get_person_full_info_text
from keyboards.admin_kb import create_edit_delete_person_kb
from misc.bot_utils import send_message_or_photo
from sqlalchemy import and_
from misc.emojis import bang_bang


async def remind_to_call():
    current_date = datetime.now().date()
    remind_text = f'{bang_bang} Сегодня нужно позвонить этому человеку: {bang_bang}\n\n'

    with DBManager(engine) as db:
        conditions = and_(Person.call_date == current_date, Person.was_dialed == False)
        persons_to_call = db.get(Person, conditions=conditions)

        for person in persons_to_call:
            remind_text += f'{get_person_full_info_text(person)}'

            await send_message_or_photo(
                OWNER_ID, text=remind_text,
                keyboard=create_edit_delete_person_kb(person.id),
                photo=person.passport_photo
            )

            await asyncio.sleep(2)

        if persons_to_call:
            db.update(Person, {'was_dialed': True}, conditions=conditions)


async def update_persons_departure_status():
    current_date = datetime.now().date()

    with DBManager(engine) as db:
        conditions = and_(Person.departure_date <= current_date, Person.is_departed == False)
        not_departed_persons = db.get(Person, conditions=conditions)

        if not_departed_persons:
            rows = [{'trip_date': person.departure_date,
                     'person_id': person.id} for person in not_departed_persons]

            db.insert(PastTripDate, rows)
            db.update(Person, {'departure_date': None, 'is_departed': True}, conditions=conditions)


def main():
    pass


if __name__ == '__main__':
    main()
