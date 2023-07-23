from datetime import datetime
from create_bot import bot
from misc.utils import format_date
import phonenumbers
from misc.emojis import warning


class Error:
    def __init__(self, message, invalid_value):
        self.message = message
        self.invalid_value = invalid_value


class StringValidator:
    def __init__(self, func):
        self.func = func

    def __call__(self, string_arg, *args, **kwargs):
        if not isinstance(string_arg, str):
            raise TypeError(
                f"Invalid argument type: the <{self.func.__name__}> method expects the str type, "
                f"but the {type(string_arg)} is passed."
            )
        return self.func(string_arg, *args, **kwargs)


class Validator():
    validators = {
        'dates': 'validate_date',
        'phone_numbers': 'validate_phone_number'
    }

    def __init__(self):
        self.errors = []
        self.valid_values = []
        self.is_checked = False
        self.is_valid = False

    @staticmethod
    @StringValidator
    def validate_date(value, current_time_deviation_sign=None):
        error_message = 'Неправильная дата: '

        try:
            correct_date = datetime.strptime(format_date(value), '%Y-%m-%d').date()

            if current_time_deviation_sign:
                current_date = datetime.now().date()

                date_comparison_dict = {
                    '<': correct_date < current_date, '<=': correct_date <= current_date,
                    '==': correct_date == current_date, '>': correct_date > current_date,
                    '>=': correct_date >= current_date, '!=': correct_date != current_date
                }

                if date_comparison_dict[current_time_deviation_sign]:
                    return correct_date
                else:
                    raise Exception()

            return correct_date

        except Exception:
            return Error(error_message, value)

    @staticmethod
    @StringValidator
    def validate_phone_number(value):
        error_message = 'Неправильный номер: '

        try:
            phone_number = phonenumbers.parse(value, None)

            if not phonenumbers.is_valid_number(phone_number):
                return Error(error_message, value)

            return phonenumbers.format_number(
                phone_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL
            )

        except Exception:
            return Error(error_message, value)

    def check(self, dates=None, phone_numbers=None, *args, **kwargs):
        self.errors = []
        self.valid_values = []
        values_to_check = {'dates': dates, 'phone_numbers': phone_numbers}

        for key, value_list in values_to_check.items():
            if value_list:
                if not isinstance(value_list, list):
                    value_list = [value_list]

                for value in value_list:
                    result = getattr(self, self.validators[key])(value, *args, **kwargs)

                    if isinstance(result, Error):
                        self.errors.append(result)
                    else:
                        self.valid_values.append(result)

        self.is_checked = True

        if self.errors:
            self.is_valid = False
            return None

        self.is_valid = True
        return self.valid_values


class BotValidator(Validator):
    async def send_validation_result_message(self, chat_id, success_message, keyboard=None):
        if self.is_checked:
            msg = ''

            if self.is_valid:
                msg = await bot.send_message(chat_id, success_message, reply_markup=keyboard)
            else:
                error_message = ''

                for error in self.errors:
                    error_message += f'{warning} {error.message}{error.invalid_value} {warning}\n'

                error_message += '\nПопробуйте снова'

                msg = await bot.send_message(chat_id, error_message, reply_markup=keyboard)

            return msg
        else:
            raise Exception('The value is not checked, you need to check the value first')


class FSMValidator(BotValidator):
    async def switch_state_if_valid(self, state, state_name):
        if self.is_checked:
            if self.is_valid:
                if state_name == 'next':
                    await state.next()
                elif state_name == 'finish':
                    current_state = await state.get_state()

                    if current_state is None:
                        return

                    await state.finish()
                else:
                    await state.set_state(state_name)
        else:
            raise Exception('The value is not checked, you need to check the value first')


def main():
    pass


if __name__ == '__main__':
    main()
