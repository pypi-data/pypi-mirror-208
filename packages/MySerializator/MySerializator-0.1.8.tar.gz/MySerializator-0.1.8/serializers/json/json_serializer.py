from source.meta_serializer import MetaSerializer
from source.serializer import Serializer


class JsonSerializer(MetaSerializer):
    serializer_ = Serializer()

    def dump(self, obj, file):
        file.write(self.dumps(obj))

    def dumps(self, obj):
        packed = self.serializer_.serialize(obj)

        if isinstance(packed, (list, tuple)):
            return self.list_n_tuple_to_string_util(packed)

        if isinstance(packed, dict):
            return self.dict_to_string_util(packed)

        return self.ser_primitive(obj)

    def ser_primitive(self, obj):
        if isinstance(obj, str):
            obj = f"'{obj}'"
        return f'"{str(obj)}"'

    def dict_to_string_util(self, dictionary):
        if not dictionary:
            return '{}'

        result = '{'

        for key, value in dictionary.items():
            if isinstance(value, dict):
                result += f'"{key}": {self.dict_to_string_util(value)},'
            elif isinstance(value, (list, tuple)):
                result += f'"{key}": {self.list_n_tuple_to_string_util(value)},'
            else:

                result += f'"{key}": {self.ser_primitive(value)},'

        return result[:-1] + '}'

    def list_n_tuple_to_string_util(self, collection):
        if not collection:
            return '[]'

        result = '['

        for item in collection:
            if isinstance(item, dict):
                result += f'{self.dict_to_string_util(item)},'
            elif isinstance(item, (list, tuple)):
                result += f'{self.list_n_tuple_to_string_util(item)},'
            else:
                result += f'{self.ser_primitive(item)},'

        return result[:-1] + ']'

    def load(self, file):
        data = file.read()
        return self.loads(data)

    def loads(self, string):
        result, ind = self.loads_with_index(string, 0)
        return self.serializer_.deserialize(result)

    def loads_with_index(self, string, index):
        match string[index]:
            case '"':
                if string[index + 1] == "'":
                    return self.deser_string(string, index + 2)
                else:
                    return self.deser_primitive(string, index)
            case '[':
                return self.deser_list(string, index)
            case '{':
                return self.deser_dict(string, index)

    def deser_dict(self, string, index):
        # on start string fragment {......}
        end_index = index
        bracket_count = 1

        # related element
        while bracket_count > 0 and end_index + 1 < len(string):
            end_index += 1
            if string[end_index] == '{':
                bracket_count += 1
            if string[end_index] == '}':
                bracket_count -= 1
        index += 1
        # from here string fragment ......}
        result = {}
        while index < end_index:
            if string[index] in (',', ' '):
                index += 1
                continue
            key, index = self.loads_with_index(string, index)
            while string[index] in (':', ' '):
                index += 1
            value, index = self.loads_with_index(string, index)
            result[key] = value

        return result, end_index + 1

    def deser_list(self, string, index):
        # on start string fragment [.....]
        end_index = index + 1
        bracket_count = 1

        # related element
        while bracket_count > 0 and end_index < len(string):
            if string[end_index] == '[':
                bracket_count += 1
            if string[end_index] == ']':
                bracket_count -= 1
            end_index += 1
        index += 1
        # from here string fragment is .....]

        # extracted data
        result = []
        while index < end_index:
            if string[index] in (',', ' '):
                index += 1
                continue
            if end_index - index < 2:
                break
            element, index = self.loads_with_index(string, index)
            result.append(element)

        return result, end_index + 1

    def deser_string(self, string, index):
        # on start string fragment: '.....'"
        end_index = index

        # related element
        while string[end_index] != "'" and end_index < len(string):
            end_index += 1
        data_slice = string[index:end_index]

        return data_slice, end_index + 3

    def string_catcher(self, string, index):
        # on start string fragment: '.....'"
        end_index = index

        # related element
        while string[end_index] != '"' and end_index < len(string):
            end_index += 1
        data_slice = string[index:end_index]

        return data_slice, end_index + 3

    def deser_number(self, string, index):
        # on start string fragment: ....."
        end_index = index

        # related element
        while string[end_index] != '"' and end_index < len(string):
            end_index += 1
        data_slice = string[index:end_index]

        try:
            if '.' in data_slice:
                return float(data_slice), end_index + 1
            else:
                return int(data_slice), end_index + 1
        except:
            return self.string_catcher(string, index)

    def deser_primitive(self, string, index):
        # on start string fragment: "....."
        # cases: bool,None,number
        index += 1
        if string[index] == 'N':
            return None, index + 5
        elif string[index] == 'T':
            return True, index + 5
        elif string[index] == 'F':
            return False, index + 6
        else:
            return self.deser_number(string, index)