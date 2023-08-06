from .constants import UNKNOWN_TYPE_ERROR
from .converter import Converter


class XmlSerializer:
    _converter = Converter()

    @classmethod
    def dumps(cls, obj):
        return cls._convert_to_xml_string(cls._converter.convert(obj))

    @classmethod
    def dump(cls, obj, file):
        file.write(cls.dumps(obj))

    @classmethod
    def loads(cls, obj):
        result, _ = cls._deconvert_from_xml_string(obj)
        return cls._converter.deconvert(result)

    @classmethod
    def load(cls, file):
        return cls.loads(file.read())

    @classmethod
    def _convert_to_xml_string(cls, obj):
        if isinstance(obj, bool):
            return f'<bool>{str(obj)}</bool>'
        if isinstance(obj, int):
            return f'<int>{str(obj)}</int>'
        if isinstance(obj, float):
            return f'<float>{str(obj)}</float>'
        if isinstance(obj, str):
            return f'<str>{obj}</str>'
        if isinstance(obj, type(None)):
            return f'<none>None</none>'
        if isinstance(obj, (list, tuple)):
            return f"<list>{''.join(list(map(cls.dumps, obj)))}</list>"
        if isinstance(obj, dict):
            data = ''.join(
                [f'<{key}>{cls.dumps(value)}</{key}>' for (key, value) in obj.items()]
            )
            return f'<dict>{data}</dict>'
        raise Exception(UNKNOWN_TYPE_ERROR)

    @classmethod
    def _deconvert_from_xml_string(cls, obj, start_position=0):
        index = start_position
        if obj[index] != '<':
            raise Exception(f'Invalid symbol at position {index}')

        type_start_index = index + 1
        type_end_index = index

        while obj[type_end_index] != '>':
            type_end_index += 1

        obj_type = obj[type_start_index:type_end_index]
        method_name = f'_loads_{obj_type}'

        if not hasattr(cls, method_name):
            raise Exception(UNKNOWN_TYPE_ERROR)
        index = type_end_index + 1

        return getattr(cls, method_name)(obj, index)

    @classmethod
    def _loads_str(cls, obj, start_position):
        end_position = start_position
        while obj[end_position:end_position + 6] != '</str>':
            end_position += 1

        return obj[start_position:end_position], end_position + 6

    @classmethod
    def _loads_bool(cls, obj, start_position):
        end_position = start_position
        while obj[end_position:end_position + 7] != '</bool>':
            end_position += 1

        bool_obj = obj[start_position:end_position]

        if bool_obj == 'True':
            return True, end_position + 7
        else:
            return False, end_position + 7

    @classmethod
    def _loads_int(cls, obj, start_position):
        end_position = start_position
        while obj[end_position:end_position + 6] != '</int>':
            end_position += 1

        int_obj = obj[start_position:end_position]
        return int(int_obj), end_position + 6

    @classmethod
    def _loads_float(cls, obj, start_position):
        end_position = start_position
        while obj[end_position:end_position + 8] != '</float>':
            end_position += 1

        float_obj = obj[start_position:end_position]
        return float(float_obj), end_position + 8

    @classmethod
    def _loads_none(cls, obj, start_position):
        end_position = start_position
        while obj[end_position:end_position + 7] != '</none>':
            end_position += 1

        return None, end_position + 7

    @classmethod
    def _loads_list(cls, obj, start_position):
        end_position = start_position
        deep = 1
        while deep:
            if obj[end_position:end_position + 6] == '<list>':
                deep += 1
            if obj[end_position:end_position + 7] == '</list>':
                deep -= 1

            end_position += 1

        end_position -= 1
        arr = []
        position = start_position
        while position < end_position:
            result, position = cls._deconvert_from_xml_string(obj, position)
            arr.append(result)

        return arr, end_position + 7

    @classmethod
    def _loads_dict(cls, obj, start_position):
        end_position = start_position
        deep = 1
        while deep:
            if obj[end_position:end_position + 6] == '<dict>':
                deep += 1
            if obj[end_position:end_position + 7] == '</dict>':
                deep -= 1
            end_position += 1

        end_position -= 1

        position = start_position
        result = {}

        while position < end_position:
            key_start_position = position + 1
            key_end_position = position + 1

            while obj[key_end_position] != '>':
                key_end_position += 1

            key = obj[key_start_position:key_end_position]

            value, position = cls._deconvert_from_xml_string(obj, key_end_position + 1)
            position += 3 + len(key)

            result[key] = value

        return result, end_position + 7
