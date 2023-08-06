from Serializators.functions_for_deserialize import Deserialize
from functions_for_serializer import Serialize


class XMLSerializer:
    data_serializer = Serialize()
    data_deserializer = Deserialize()

    def dumps(self, obj):
        packed = self.data_serializer.serialize(obj)
        if isinstance(packed, (list, tuple)):
            return self.__list_n_tuple_to_string_util(packed)
        if isinstance(packed, dict):
            return self.__dict_to_string_util(packed)
        if isinstance(packed, str):
            packed = f'"{packed}"'
        return self.__ser_primitive(packed)

    def dump(self, obj, file):
        file.write(self.dumps(obj))

    def loads(self, string):
        result, ind = self.__loads_with_index(string, 0)
        return self.data_deserializer.deserialize(result)

    def load(self, file):
        return self.loads(file.read())

    def __loads_with_index(self, string, index):
        index += 1
        end_index = index
        while string[end_index] != '>':
            end_index += 1

        tag = string[index:end_index]

        match tag:
            case 'int' | 'float':
                return self.__deserialize_digit(string, end_index + 1)
            case 'bool':
                return self.__deserialize_bool(string, end_index + 1)
            case 'NoneType':
                return None, index + 24
            case 'str':
                return self.__deserialize_str(string, end_index + 1)
            case 'list':
                return self.__deserialize_list(string, end_index + 1)
            case 'dict':
                return self.__deserialize_dict(string, end_index + 1)

    def __deserialize_digit(self, string, index):
        end_index = index

        while string[end_index] != '<':
            end_index += 1

        data_slice = string[index:end_index]
        if '.' in data_slice:
            return float(data_slice), end_index + 8
        return int(data_slice), end_index + 6

    def __deserialize_bool(self, string, index):
        if string[index] == 'T':
            return True, index+11
        else:
            return False, index+12

    def __deserialize_str(self, string, index):
        end_index = index
        while string[end_index:end_index + 6] != '</str>':
            end_index += 1

        data_slice = string[index + 1:end_index - 1]
        return f'{data_slice}', end_index + 6

    def __deserialize_list(self, string, index):
        end_index = index

        result = []

        bracket_count = 1
        while bracket_count > 0:
            if string[end_index:end_index + 6] == '<list>':
                bracket_count += 1
            elif string[end_index:end_index + 7] == '</list>':
                bracket_count -= 1
            end_index += 1
        end_index -= 1

        while index < end_index:
            item, index = self.__loads_with_index(string, index)
            result.append(item)

        return result, end_index + 7

    def __deserialize_dict(self, string, index):
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
            item, index = self.__deserialize_dict_item(string, index)
            result[item[0]] = item[1]

        return result, end_index + 7

    def __deserialize_dict_item(self, string, index):
        end_index = index + 11
        key, end_index = self.__loads_with_index(string, end_index)
        end_index += 13
        value, end_index = self.__loads_with_index(string, end_index)
        return (key, value), end_index + 15

    def __list_n_tuple_to_string_util(self, packed):
        return f'<{packed.__class__.__name__}>{"".join([self.dumps(item) for item in packed])}</{packed.__class__.__name__}>'

    def __dict_to_string_util(self, packed):
        return f'<{packed.__class__.__name__}>{"".join([self.__ser_dict_element(key, value) for key, value in packed.items()])}</{packed.__class__.__name__}>'

    def __ser_dict_element(self, key, value):
        return f'<item><key>{self.dumps(key)}</key><value>{self.dumps(value)}</value></item>'

    def __ser_primitive(self, packed):
        return f'<{packed.__class__.__name__}>{packed}</{packed.__class__.__name__}>'
