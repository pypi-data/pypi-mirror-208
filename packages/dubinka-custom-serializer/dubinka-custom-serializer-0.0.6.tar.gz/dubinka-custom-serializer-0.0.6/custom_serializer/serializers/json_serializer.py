from ..encoder.encoder import Encoder, Decoder


def dump(obj, file):
    file.write(dumps(obj))


def dumps(obj):
    data = Encoder.encode(obj)
    return _dumps(data)


def _dumps(obj):
    if isinstance(obj, (int, float)):
        return str(obj)
    if isinstance(obj, bool):
        return str(obj).lower()
    if isinstance(obj, str):
        return f'"{str(obj)}"'
    if isinstance(obj, type(None)):
        return "null"
    if isinstance(obj, (list, tuple)):
        return f"[{', '.join(list(map(_dumps, obj)))}]"
    if isinstance(obj, dict):
        data = ", ".join([f'{_dumps(key)}: {_dumps(value)}' for key, value in obj.items()])
        return f"""{{{data}}}"""


def loads(obj):
    res, _ = _loads(obj, 0)
    return Decoder.decode(res)


def load(file):
    return loads(file.read())


def _loads(obj: str, start_index):
    if obj[start_index] == '{':
        return _loads_dict(obj, start_index)
    if obj[start_index] == '"':
        return _loads_str(obj, start_index)
    if obj[start_index] == '[':
        return _loads_list(obj, start_index)
    if obj[start_index].isdigit() or obj[start_index] == '-':
        return _loads_num(obj, start_index)
    if obj[start_index] == 'n':
        return None, start_index + 4
    if obj[start_index] == 't':
        return True, start_index + 4
    if obj[start_index] == 'f':
        return False, start_index + 5
    if obj[start_index].isalpha():
        return _loads_str_type(obj, start_index)


def _loads_str_type(obj, start_index):
    end = start_index + 1
    while end < len(obj) and obj[end] not in [',', ']', '}']:
        end += 1
    return obj[start_index:end], end + 1


def _loads_num(obj, start_index):
    end = start_index + 1

    while end < len(obj) and (obj[end].isdigit() or obj[end] == '.'):
        end += 1

    str_num = obj[start_index:end]
    num = 0
    try:
        num = int(str_num)
    except ValueError:
        num = float(str_num)
    finally:
        return num, end + 1


def _loads_str(obj, start_index):
    end = start_index + 1

    while obj[end] != '"':
        end += 1

    return obj[start_index + 1:end], end + 1


def _loads_dict(obj, start_index):
    end = start_index + 1
    brackets = 1

    while brackets:
        if obj[end] == '{':
            brackets += 1
        elif obj[end] == '}':
            brackets -= 1
        end += 1

    dct = {}
    i = start_index + 1
    while i < end - 1:
        while obj[i] in [' ', ',', '\n']:
            i += 1
        key, i = _loads(obj, i)
        while obj[i] in [' ', '\n', ',', ':']:
            i += 1
        value, i = _loads(obj, i)
        dct[key] = value

    return dct, end + 1


def _loads_list(obj, start_index):
    end = start_index + 1
    brackets = 1
    while brackets:
        if obj[end] == '[':
            brackets += 1
        elif obj[end] == ']':
            brackets -= 1
        end += 1

    lst = []
    i = start_index + 1
    while i < end - 1:
        while obj[i] in [' ', ',', '\n']:
            i += 1
        res, i = _loads(obj, i)
        lst.append(res)

    return lst, end + 1
