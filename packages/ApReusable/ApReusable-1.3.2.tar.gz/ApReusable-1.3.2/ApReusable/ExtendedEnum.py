from enum import Enum


class ExtendedEnum(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

    @classmethod
    def tuple(cls):
        return list(map(lambda c: (c.name, c.value), cls))

    @classmethod
    def dict(cls):
        dictionary = {}
        for v in list(map(lambda c: (c.name, c.value), cls)):
            dictionary[v[0]] = v[1]
        return dictionary
