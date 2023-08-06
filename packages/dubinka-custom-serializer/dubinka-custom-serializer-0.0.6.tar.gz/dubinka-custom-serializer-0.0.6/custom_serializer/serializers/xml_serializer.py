from ..encoder.encoder import Encoder, Decoder


def dump(obj, file):
    file.write(dumps(obj))


def dumps(obj):
    data = Encoder.encode(obj)
    return _dumps(data)


def _dumps(obj):
    if isinstance(obj, (int, float)):
        return f'<{obj.__class__.__name__}>{obj}</{obj.__class__.__name__}>'
    if isinstance(obj, bool):
        return f'<bool>{str(obj).lower()}</bool>'
    if isinstance(obj, str):
        return f'<str>{str(obj)}</str>'
    if isinstance(obj, type(None)):
        return f'<none>None</none>'
    if isinstance(obj, (list, tuple)):
        return f"<list>{''.join(list(map(_dumps, obj)))}</list>"
    if isinstance(obj, dict):
        data = "".join([f'<{key}>{_dumps(value)}</{key}>' for key, value in obj.items()])
        return f"<dict>{data}</dict>"


def loads(obj):
    res, _ = _loads(obj, 0)
    return Decoder.decode(res)


def load(file):
    return loads(file.read())


def _loads(obj: str, start_index):
    end = start_index + 1
    while end < len(obj) and obj[end] != '>':
        end += 1
    if obj[start_index + 1:end] == 'dict':
        return _loads_dict(obj, end + 1)
    if obj[start_index + 1:end] == 'str':
        return _loads_str(obj, end + 1)
    if obj[start_index + 1:end] == 'list':
        return _loads_list(obj, end + 1)
    if obj[start_index + 1:end] in ['float', 'int']:
        return _loads_num(obj, end + 1)
    if obj[start_index + 1:end] == 'none':
        return None, end + 12
    if obj[start_index + 1:end] == 'bool':
        if obj[end + 1] == 'T':
            return True, end + 12
        else:
            return False, end + 13


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
        return num, end + len(num.__class__.__name__) + 3


def _loads_str(obj, start_index):
    end = start_index

    while obj[end] != '<':
        end += 1

    return obj[start_index:end], end + 6


def _loads_dict(obj, start_index):
    end = start_index
    brackets = 1

    while brackets:
        if obj[end: end + 6] == '<dict>':
            brackets += 1
            end += 5
        elif obj[end: end + 7] == '</dict>':
            brackets -= 1
            end += 6
        end += 1

    dct = {}
    i = start_index
    while i < end - 7:
        start = i + 1
        while obj[i] != '>':
            i += 1
        key = obj[start:i]

        value, i = _loads(obj, i + 1)
        i += 3 + len(key)
        dct[key] = value

    return dct, end


def _loads_list(obj, start_index):
    end = start_index
    brackets = 1
    while brackets:
        if obj[end:end + 6] == '<list>':
            brackets += 1
            end += 5
        elif obj[end:end + 7] == '</list>':
            brackets -= 1
            end += 6
        end += 1

    lst = []
    i = start_index
    while i < end - 7:
        res, i = _loads(obj, i)
        lst.append(res)
    return lst, end
