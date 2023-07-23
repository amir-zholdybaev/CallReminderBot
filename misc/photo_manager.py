from .object_manager import ObjectManager
from datetime import datetime


class PhotoManager:
    photos = ObjectManager()

    def __init__(self, photo, photo_id, path=None):
        self.photo = photo
        self.photo_id = photo_id
        self._path = path
        self.photos.add(self.photo_id, self)

    @property
    def path(self):
        if not self._path:
            current_date = datetime.now()

            self._path = (
                f'photos/{current_date.year}/{current_date.month}/'
                f'{current_date.day}/{int(current_date.timestamp())}.jpg'
            )

        return self._path

    async def download(self):
        return await self.photo.download(destination_file=self.path)

    def delete(self):
        self.photos.delete(self.photo_id)


def main():
    pass


if __name__ == '__main__':
    main()
