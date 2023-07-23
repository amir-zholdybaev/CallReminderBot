import re


def format_date(string):
    date_string = re.sub(r'\D', '', string)
    return date_string[:4] + '-' + date_string[4:6] + '-' + date_string[6:]


def printf(*args, sep: str = ' ', end: str = '\n', col: int = 197, bg: int = 0):
    str = ''

    for arg in args:
        str += f'{sep}{arg}'

    print(f"\033[38;5;{col}m\033[48;5;{bg}m{str}\033[0m", end=end)


def console_clear():
    print('\033[2J')


def edit_text(
    source_text, addition_text=None, insertion_offset=None,
    replacement_data: dict | str = None
):
    if addition_text:
        if insertion_offset is None:
            source_text = source_text + addition_text

        elif insertion_offset == 0:
            source_text = addition_text + source_text

        else:
            position = source_text.find(insertion_offset)

            if position != -1:
                source_text = source_text[:position] + addition_text + source_text[position:]
            else:
                raise ValueError(f"Fragment '{insertion_offset}' not found in the text.")

    if replacement_data:
        if isinstance(replacement_data, dict):
            for replaceable_text, replacement_text in replacement_data.items():
                source_text = source_text.replace(replaceable_text, replacement_text)

    return source_text


def conv_to_pref_format(seconds):
    days = seconds // (24 * 3600)

    seconds = seconds % (24 * 3600)
    hours = int(seconds // 3600)

    seconds %= 3600
    minutes = int(seconds // 60)

    seconds %= 60

    return (days, hours, minutes, seconds)


def get_hours_ending(hours):
    ending = ''

    number = hours % 20

    if number == 1:
        ending = 'час'

    elif number > 1 and number < 5:
        ending = 'часа'

    else:
        ending = 'часов'

    return ending


def convert_cyrillic_letters_to_latin(string):
    transcript_symbols = [
        'a', 'b', 'v', 'g', 'd', 'e', 'zh', 'z',
        'i', 'y', 'k', 'l', 'm', 'n', 'o', 'p', 'r',
        's', 't', 'u', 'f', 'h', 'c', 'ch', 'sh',
        'shch', '', 'y', '', 'e', 'yu', 'ya'
    ]

    start_index = ord('а')
    slug = ''

    for char in string.lower():
        if 'в' <= char <= 'я':
            slug += transcript_symbols[ord(char) - start_index]
        elif char == 'ё':
            slug += 'yo'
        # elif char in ' !?;:.,':
        #     slug += '-'
        else:
            slug += char

    while '--' in slug:
        slug = slug.replace('--', '-')

    return slug

    # Данный функционал реализовать используя регулярные выражения


def main():
    pass


if __name__ == '__main__':
    main()
