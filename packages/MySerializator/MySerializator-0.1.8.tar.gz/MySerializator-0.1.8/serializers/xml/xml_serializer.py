from source.meta_serializer import MetaSerializer
from source.serializer import Serializer


class XmlSerializer(MetaSerializer):
    serialized = Serializer()

    def dump(self, obj, file):
        file.write(self.dumps(obj))

    def dumps(self, obj):
        serialized_ = self.serialized.serialize(obj)
        if isinstance(serialized_, (list, tuple)):
            return self.list_n_tuple_to_string_util(serialized_)
        if isinstance(serialized_, dict):
            return self.dict_to_string_util(serialized_)
        if isinstance(serialized_, str):
            serialized_ = f'"{serialized_}"'
        return self.ser_primitive(serialized_)

    def load(self, file):
        data = file.read()
        return self.loads(data)

    def loads(self, string):
        result, ind = self.loads_with_index(string, 0)
        return self.serialized.deserialize(result)

    def list_n_tuple_to_string_util(self, serialized):
        return f'<{serialized.__class__.__name__}>{"".join([self.dumps(item) for item in serialized])}</{serialized.__class__.__name__}>'

    def dict_to_string_util(self, serialized):
        return f'<{serialized.__class__.__name__}>{"".join([self.ser_dict_element(key, value) for key, value in serialized.items()])}</{serialized.__class__.__name__}>'

    def ser_dict_element(self, key, value):
        return f'<item><key>{self.dumps(key)}</key><value>{self.dumps(value)}</value></item>'

    def ser_primitive(self, serialized):
        return f'<{serialized.__class__.__name__}>{serialized}</{serialized.__class__.__name__}>'



    def loads_with_index(self, string, index):
        # string[index]=='<'
        index += 1
        end_index = index
        while string[end_index] != '>':
            end_index += 1

        tag = string[index:end_index]
        # end_index+1 ->value start

        match tag:
            case 'int' | 'float':
                return self.deser_digit(string, end_index + 1)
            case 'bool':
                return self.deser_bool(string, end_index + 1)
            case 'NoneType':
                return None, index + 24
            case 'str':
                return self.deser_str(string, end_index + 1)
            case 'list':
                return self.deser_list(string, end_index + 1)
            case 'dict':
                return self.deser_dict(string, end_index + 1)

    def deser_digit(self, string, index):
        end_index = index

        while string[end_index] != '<':
            end_index += 1

        data_slice = string[index:end_index]
        if '.' in data_slice:
            return float(data_slice), end_index + 8
        return int(data_slice), end_index + 6

    def deser_bool(self, string, index):
        if string[index] == 'T':
            return True, index + 11
        else:
            return False, index + 12

    def deser_str(self, string, index):
        end_index = index
        while string[end_index:end_index + 6] != '</str>':
            end_index += 1

        data_slice = string[index + 1:end_index - 1]
        return f'{data_slice}', end_index + 6

    def deser_list(self, string, index):
        end_index = index

        result = []

        # data fragment
        bracket_count = 1
        while bracket_count > 0:
            if string[end_index:end_index + 6] == '<list>':
                bracket_count += 1
            elif string[end_index:end_index + 7] == '</list>':
                bracket_count -= 1
            end_index += 1
        end_index -= 1

        # extract
        while index < end_index:
            item, index = self.loads_with_index(string, index)
            result.append(item)

        return result, end_index + 7

    def deser_dict(self, string, index):
        end_index = index

        result = {}
        # data fragment
        bracket_count = 1
        while bracket_count > 0:
            if string[end_index:end_index + 6] == '<dict>':
                bracket_count += 1
            elif string[end_index:end_index + 7] == '</dict>':
                bracket_count -= 1
            end_index += 1
        end_index -= 1

        # extract
        while index < end_index:
            item, index = self.deser_dict_item(string, index)
            result[item[0]] = item[1]

        return result, end_index + 7

    def deser_dict_item(self, string, index):
        # returns key,value tuple w' index
        # input string <item><key><...
        end_index = index + 11
        # now <...
        # key extraction
        key, end_index = self.loads_with_index(string, end_index)
        # print(f'extracted key {key}')
        # now </key><value><...
        end_index += 13
        # now<...
        value, end_index = self.loads_with_index(string, end_index)
        # print(f'extracted value {value}')
        # now</value></item>...
        return (key, value), end_index + 15