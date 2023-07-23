from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def create_simple_keyboard(buttons_dict: dict, resize_keyboard=True, one_time_keyboard=True):
    KEYBOARD = ReplyKeyboardMarkup(resize_keyboard=resize_keyboard, one_time_keyboard=one_time_keyboard)
    ROW_BUTTONS = []

    for button, type_of_addition in buttons_dict.items():
        if type_of_addition == "row":
            ROW_BUTTONS.append(KeyboardButton(button))
        else:
            if ROW_BUTTONS:
                KEYBOARD.row(*ROW_BUTTONS)
                ROW_BUTTONS.clear()

            KEYBOARD.add(KeyboardButton(button))

    if ROW_BUTTONS:
        KEYBOARD.row(*ROW_BUTTONS)

    return KEYBOARD


def main():
    pass


if __name__ == '__main__':
    main()
