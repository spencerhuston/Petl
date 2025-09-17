from enum import Enum, EnumMeta


class PetlMetaEnum(EnumMeta):
    def __contains__(cls, item):
        try:
            cls(item)
        except ValueError:
            return False
        return True


class PetlBaseEnum(Enum, metaclass=PetlMetaEnum):
    pass
