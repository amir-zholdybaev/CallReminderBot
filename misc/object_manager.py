class ObjectManager:
    def __init__(self):
        self.objects = dict()

    def add(self, key, value):
        if value is None:
            raise ValueError("Object cannot be None")

        self.objects[key] = value

    def get(self, key):
        if key not in self.objects:
            return None

        return self.objects[key]

    def delete(self, key):
        if key not in self.objects:
            return None

        value = self.objects.get(key)
        del self.objects[key]

        return value

    # length() - возвращает количество элементов в словаре items.

    # contains(item_id) - возвращает True, если элемент с данным item_id присутствует в словаре items, и False в противном случае.

    # update(item_id, item) - обновляет элемент в словаре items с item_id на новый элемент item.

    # clear() - удаляет все элементы из словаря items.

    # keys() - возвращает список всех ключей в словаре items.

    # values() - возвращает список всех значений в словаре items.


def main():
    pass


if __name__ == '__main__':
    main()
