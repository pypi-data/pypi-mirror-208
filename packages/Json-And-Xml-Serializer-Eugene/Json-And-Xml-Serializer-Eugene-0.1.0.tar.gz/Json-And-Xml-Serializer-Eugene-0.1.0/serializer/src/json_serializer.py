from .constants import UNKNOWN_TYPE_ERROR

from .converter import Converter


class JsonSerializer:
    _converter = Converter()

    @classmethod
    def load(cls, file):
        return cls.loads(file.read())

    @classmethod
    def loads(cls, obj):
        result, _ = cls._deconvert_from_string(obj)
        return cls._converter.deconvert(result)

    @classmethod
    def dump(cls, obj, file):
        file.write(cls.dumps(obj))

    @classmethod
    def dumps(cls, obj):
        return cls._convert_to_json_str(cls._converter.convert(obj))

    @classmethod
    def _convert_to_json_str(cls, obj):
        if isinstance(obj, bool):
            return str(obj).lower()
        if isinstance(obj, (int, float)):
            return str(obj)
        if isinstance(obj, str):
            return f'"{obj}"'
        if isinstance(obj, type(None)):
            return "null"
        if isinstance(obj, (list, set, tuple)):
            return f"[{','.join(list(map(cls.dumps, obj)))}]"
        if isinstance(obj, dict):
            data = ",".join(
                [f'"{key}": {cls.dumps(value)}' for (key, value) in obj.items()]
            )
            return f"""{{{data}}}"""
        raise Exception(UNKNOWN_TYPE_ERROR)

    @classmethod
    def _deconvert_from_string(cls, string_obj, start_index=0):
        if string_obj[start_index] == '"':
            return cls._loads_string(string_obj, start_index)
        elif string_obj[start_index] == '[':
            return cls._loads_list(string_obj, start_index)
        elif string_obj[start_index].isdigit() or string_obj[start_index] == '-':
            return cls._loads_nums(string_obj, start_index)
        elif string_obj[start_index] == 't':
            return True, start_index + 4
        elif string_obj[start_index] == 'f':
            return False, start_index + 5
        elif string_obj[start_index] == 'n':
            return None, start_index + 4
        elif string_obj[start_index] == '{':
            return cls._loads_dict(string_obj, start_index)
        raise Exception(UNKNOWN_TYPE_ERROR)

    @classmethod
    def _loads_nums(cls, obj, start_index):
        end_index = start_index + 1
        while len(obj) > end_index and (obj[end_index].isdigit() or obj[end_index] == '.'):
            end_index += 1

        num = obj[start_index:end_index]

        if num.count('.'):
            return float(num), end_index

        return int(num), end_index

    @classmethod
    def _loads_string(cls, obj, start_index):
        end_index = start_index + 1
        while obj[end_index] != '"':
            end_index += 1

        return obj[start_index + 1:end_index], end_index + 1

    @classmethod
    def _loads_list(cls, obj, start_index):
        end_index = start_index + 1
        braces = 1
        while braces:
            if obj[end_index] == '[':
                braces += 1
            if obj[end_index] == ']':
                braces -= 1

            end_index += 1

        output_list = []
        index = start_index + 1
        while index < end_index - 2:
            while obj[index] in (' ', ',', '\n'):
                index += 1
            res, index = cls._deconvert_from_string(obj, index)
            output_list.append(res)

        return output_list, end_index

    @classmethod
    def _loads_dict(cls, obj, start_index):
        end_index = start_index + 1
        braces = 1
        while braces:
            if obj[end_index] == '{':
                braces += 1
            if obj[end_index] == '}':
                braces -= 1

            end_index += 1

        index = start_index + 1
        output_dict = {}
        while index < end_index - 2:
            while obj[index] in (' ', ',', '\n'):
                index += 1
            key, index = cls._loads_string(obj, index)
            while obj[index] in (' ', ',', '\n', ':'):
                index += 1

            value, index = cls._deconvert_from_string(obj, index)
            output_dict[key] = value

        return output_dict, end_index + 1
