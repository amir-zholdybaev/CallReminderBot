def edit_text(
    source_text, addition_text=None, insertion_offset=None,
    replaceable_text=None, replacement_text=''
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

    if replaceable_text:
        source_text = source_text.replace(replaceable_text, replacement_text)

    elif replaceable_text is None and addition_text is None:
        source_text = replacement_text

    return source_text


# try:
#     final_text = edit_text(
#         "Это пример текста, в котором нужно найти позицию определенного текста.",
#         addition_text='1-ую ', insertion_offset='позицию', replaceable_text='определенного ',
#         replacement_text='данного ')

#     print(final_text)

# except ValueError as e:
#     print("Ошибка при редактировании текста:", str(e))


def edit_text_2(
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
        elif isinstance(replacement_data, str):
            source_text = replacement_data

    return source_text


try:
    final_text = edit_text_2(
        "Это пример текста, в котором нужно найти позицию определенного текста.",
        addition_text='1-ую ', insertion_offset='позицию',
        replacement_data={'определенного ': ''})

    print(final_text)

except ValueError as e:
    print("Ошибка при редактировании текста:", str(e))
