from abc import ABCMeta


class BaseSerializer(metaclass=ABCMeta):
    def dumps(self, obj_to_serialize):
        pass

    def dump(self, obj_to_serialize, file):
        pass

    def load(self, file) -> str:
        pass

    def loads(self, str_to_load_from: str) -> str:
        pass
