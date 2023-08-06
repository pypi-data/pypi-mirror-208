from types import NoneType

from .base import BaseSerializer


class JSONSerializer(BaseSerializer):
    """
    The responsibility of serializer is to a middleware between
    'pre-serializer' tool and raw data in file or in the string.
    This means that all the data passed to serializer factory must be
    'encoded' or 'unified' before it will get the serializer
    """

    _primitive_dump_mapping = {
        bool: lambda obj: str(obj).lower(),  # booleans are stored in like a set of characters in lowercase
        (int, float): lambda obj: str(obj),  # in the string or file will look like common digit
        str: lambda obj: '"%s"' % obj,  # strings are signed by double quotes that helps to distinguish strings
        NoneType: lambda obj: "null",  # another keyword fot displaying NoneType object
    }

    def dumps(self, obj) -> str:
        for _type in self._primitive_dump_mapping:
            if isinstance(obj, _type):
                return self._primitive_dump_mapping.get(_type)(obj)

        if isinstance(obj, (list, tuple)):  # calling dumps method to every item in the list. Collections like
            return f"[{','.join(list(map(self.dumps, obj)))}]"  # list or tuple wrapped in square braces

        if isinstance(obj, dict):
            data = ",".join(  # Note that both key and value are already unified values
                [f'"{key}": {self.dumps(value)}' for (key, value) in obj.items()]  # key would always be string
            )
            return "{%s}" % data

    def dump(self, obj, file) -> None:
        file.write(self.dumps(obj))

    def loads(self, str_to_load_from: str):
        """
        starts recursively loading datatypes
        :param str_to_load_from: string containing serialized data
        :return: object of one of the primitives or collection like dict of list
        """
        res, _ = self._loads(str_to_load_from, 0)  # second returned value is end_index
        return res

    def load(self, file):
        return self.loads(file.read())

    def _loads(self, s: str, start_index: int) -> tuple[bool | str | int | float | list | dict | None, int]:
        if s[start_index] == '"':
            return self._loads_str(s, start_index)
        if s[start_index] == "[":
            return self._loads_list(s, start_index)

        if s[start_index].isdigit():
            return self._loads_num(s, start_index)

        if s[start_index] == "t":  # means false
            return True, start_index + 4

        if s[start_index] == "f":  # means true
            return False, start_index + 5

        if s[start_index] == "n":  # means null
            return None, start_index + 4

        if s[start_index] == "{":
            return self._loads_dict(s, start_index)

    def _loads_list(self, s: str, start_index: int) -> tuple[list, int]:
        end_index = start_index + 1
        braces = 1
        while braces:  # the same logic as in '_load_dict'
            if s[end_index] == "[":
                braces += 1
            if s[end_index] == "]":
                braces -= 1

            end_index += 1

        lst = []  # creating the result list
        index = start_index + 1
        while index < end_index - 2:  # fulfilling lst
            while s[index] in (" ", ",", "\n"):
                index += 1
            res, index = self._loads(s, index)  # uploading each item separately
            lst.append(res)

        return lst, end_index

    def _loads_dict(self, s: str, start_index: int) -> tuple[dict, int]:
        end_index = start_index + 1  # points at the first symbol after {
        braces = 1

        while braces:
            """
            This guarantees that all the inner dictionaries won't be missed
            """
            if s[end_index] == "{":
                braces += 1
            if s[end_index] == "}":
                braces -= 1

            end_index += 1
        # end index at first symbol after the last }

        index = start_index + 1
        result = {}
        while index < end_index - 2:  # end_index - 2 points at the last character before }
            while s[index] in (" ", ",", "\n"):  # missing all separators
                index += 1
            key, index = self._loads_str(s, index)  # uploading key

            while s[index] in (" ", ",", "\n", ":"):  # missing all separators
                index += 1

            value, index = self._loads(s, index)  # uploading value

            result[key] = value  # assigning new attribute

        return result, end_index + 1

    def _loads_str(self, s: str, start_index: int) -> tuple[str, int]:
        end_index = start_index + 1  # pointing the first character
        while s[end_index] != '"':
            end_index += 1

        # end index is pointing at the second quote now
        return s[start_index + 1 : end_index], end_index + 1

    def _loads_num(self, s: str, start_index: int) -> tuple[int | float, int]:
        end_index = start_index + 1
        while len(s) > end_index and (  # checking if the index is in range
            s[end_index].isdigit() or s[end_index] == "."
        ):  # measuring the len of slice
            end_index += 1

        num = s[start_index:end_index]  # string representation of number

        if num.count("."):
            return float(num), end_index

        return int(num), end_index  # end_index points on not-digit value
