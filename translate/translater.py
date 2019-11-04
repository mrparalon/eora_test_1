from abc import ABC, abstractmethod
from translate.dicts import russian_dict


class Translater(ABC):
    def __init__(self, message):
        self.message = message

    @abstractmethod
    def translate(self, message):
        pass


class RussianTranslater(Translater):
    def translate(self):
        # Здесь можно добавить исправление опечаток
        translated_message = russian_dict.get(self.message)
        return translated_message


class PhotoTranslater(Translater):
    # Здесь можно добавить распознание по фото. Принимать по тому же интерфейсу
    # ссылку
    def translate(self):
        pass
