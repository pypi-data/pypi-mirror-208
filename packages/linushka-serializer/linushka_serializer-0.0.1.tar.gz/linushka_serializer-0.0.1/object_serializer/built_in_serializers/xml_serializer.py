from .base import BaseSerializer


def tag_factory(_type, lower: bool = False):
    return (
        f"<{_type.lower() if lower else _type}>",
        f"</{_type.lower() if lower else _type}>",
    )


class XMLSerializer(BaseSerializer):
    def dumps(self, obj) -> str:
        if isinstance(obj, bool):
            return f"<bool>{str(obj)}</bool>"

        if isinstance(obj, int):
            return f"<int>{str(obj)}</int>"

        if isinstance(obj, float):
            return f"<float>{str(obj)}</float>"

        if isinstance(obj, str):
            return f"<str>{obj}</str>"

        if isinstance(obj, type(None)):
            return "<none>None</none>"

        if isinstance(obj, (list, tuple)):
            return f"<list>{''.join(list(map(self.dumps, obj)))}</list>"

        if isinstance(obj, dict):
            data = "".join([f"<{key}>{self.dumps(value)}</{key}>" for (key, value) in obj.items()])
            return f"<dict>{data}</dict>"

    def dump(self, obj, file):
        file.write(self.dumps(obj))

    def loads(self, s: str):
        res, _ = self._loads(s, 0)
        return res

    def load(self, file):
        return self.loads(file.read())

    def _loads(self, s: str, start_index: int):
        index = start_index

        if s[index] != "<":
            raise Exception(f"Invalid symbol at position {index}")

        type_start_index = index + 1
        type_end_index = index

        while s[type_end_index] != ">":
            type_end_index += 1

        object_type = s[type_start_index:type_end_index]
        method_name = f"_loads_{object_type}"

        if not hasattr(self, method_name):
            raise Exception(f"Unknown type {method_name}")

        index = type_end_index + 1
        return getattr(self, method_name)(s, index)

    def _loads_str(self, s: str, start_index: int):
        f, second = tag_factory("str")
        end_index = start_index
        while s[end_index : end_index + 6] != second:
            end_index += 1

        return s[start_index:end_index], end_index + 6

    def _loads_bool(self, s: str, start_index: int):
        f, second = tag_factory("bool")
        end_index = start_index
        while s[end_index : end_index + 7] != second:
            end_index += 1

        bool_obj = s[start_index:end_index]
        if bool_obj == "True":
            return True, end_index + 7
        else:
            return False, end_index + 7

    def _loads_int(self, s: str, start_index: int):
        f, second = tag_factory("int")
        end_index = start_index
        while s[end_index : end_index + 6] != second:
            end_index += 1

        int_obj = s[start_index:end_index]
        return int(int_obj), end_index + 6

    def _loads_float(self, s: str, start_index: int):
        f, second = tag_factory("float")
        end_index = start_index
        while s[end_index : end_index + 8] != second:
            end_index += 1

        int_obj = s[start_index:end_index]
        return float(int_obj), end_index + 8

    def _loads_none(self, s: str, start_index: int):
        first, second = tag_factory("none")
        end_index = start_index
        while s[end_index : end_index + 7] != second:
            end_index += 1

        return None, end_index + 7

    def _loads_list(self, s: str, start_index: int):
        first, second = tag_factory("list")
        end_index = start_index
        deep = 1
        while deep:
            if s[end_index : end_index + 6] == first:
                deep += 1
            if s[end_index : end_index + 7] == second:
                deep -= 1

            end_index += 1

        end_index -= 1
        arr = []
        index = start_index
        while index < end_index:
            res, index = self._loads(s, index)
            arr.append(res)

        return arr, end_index + 7

    def _loads_dict(self, s: str, start_index: int):
        first, second = tag_factory("dict")
        end_index = start_index
        deep = 1
        while deep:
            if s[end_index : end_index + 6] == first:
                deep += 1
            if s[end_index : end_index + 7] == second:
                deep -= 1

            end_index += 1

        end_index -= 1

        index = start_index
        result = {}

        while index < end_index:
            ket_start_index = index + 1
            key_end_index = index + 1

            while s[key_end_index] != ">":
                key_end_index += 1

            key = s[ket_start_index:key_end_index]

            value, index = self._loads(s, key_end_index + 1)
            index += 3 + len(key)

            result[key] = value

        return result, end_index + 7
