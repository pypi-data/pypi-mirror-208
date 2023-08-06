from base64 import b64decode, b64encode
from bson import ObjectId
from struct import pack, unpack
from decimal import Decimal
from simpleeval import SimpleEval, DEFAULT_FUNCTIONS

g_s = SimpleEval()
g_s.functions = DEFAULT_FUNCTIONS.copy()


def base64_encode(datas: bytes) -> str:
    return b64encode(datas).decode()


def base64_decode(datas: str) -> bytes:
    return b64decode(datas)


def chunk_list(values: list, num: int):
    for i in range(0, len(values), num):
        yield values[i: i+num]


# 转换类为字典
def convert_class_to_dict(obeject_class):
    object_value = {}
    for key in dir(obeject_class):
        value = getattr(obeject_class, key)
        if not key.startswith('__') and not key.startswith('_') and not callable(value):
            object_value[key] = value
    return object_value


def generate_object_id():
    return ObjectId().__str__()


def remove_exponent(value: Decimal):
    return value.to_integral() if value == value.to_integral() else value.normalize()


def remove_exponent_str(value: str) -> str:
    dec_value = Decimal(value)
    if dec_value == dec_value.to_integral():    # int
        return str(int(float(value)))
    else:
        return value.rstrip('0')


def is_number(value: str):
    try:
        return True, float(value)
    except ValueError:
        pass
    return False, value


def find_all_pos(scale: str, exp: str):
    return [i for i, c in enumerate(scale) if c == exp]


def revert_exp(scale: str) -> str:
    exps = {'+': ['-', []], '-': ['+', []], '*': ['/', []], '/': ['*', []]}
    for exp in exps.keys():
        exps[exp][1] = find_all_pos(scale, exp)

    _scale = list(scale)
    for exp, [_exp, pos] in exps.items():
        for _pos in pos:
            _scale[_pos:_pos+1] = _exp
    return ''.join(_scale)


'''
"v+20"  #基础方法 + - * / %  == < > <= >= >> <<
"int(v)" #基础函数 randint rand int float str
"com(v)"   #自定义函数 bit signed inverse_long inverse_float inverse_double
"1 if v == 20.1234 else 0" #表达式
'''


def format_value(value_old: str, scale: str = '1', decimal: int = 2, revert: bool = False) -> str:
    value = str(value_old)
    scale = '1' if scale == '' else scale
    is_scale_num, scale = is_number(str(scale))
    if len(value) > 0:
        try:
            if value.lower() in ['true', 'active']:
                value = '1'
            elif value.lower() in ['false', 'inactive']:
                value = '0'

            is_value_num, value = is_number(str(value))
            if is_value_num is True:
                if is_scale_num:
                    if scale != float('1'):
                        value = value * scale
                else:
                    if len(scale) > 0:  # 表达式
                        scale = revert_exp(scale) if revert is True else scale
                        g_s.names = {'v': value}
                        value = g_s.eval(scale)

                is_value_num, value = is_number(str(value))
                if is_value_num is True:
                    d = Decimal(str(value))
                    if -d.as_tuple().exponent > decimal:
                        _format = f"%.{decimal}f"
                        value = _format % value  # 格式化小数点
                    value = remove_exponent_str(str(value))
            return str(value)
        except Exception:
            pass
    return str(value_old)


# 自定义
# 取位函数
def bit(value, index: int):
    try:
        value = int(value)
        return value & (1 << index) and 1 or 0
    except Exception:
        pass
    return value


def signed(value):
    try:
        value = int(value)
        return unpack('h', pack('H', value))[0]
    except Exception:
        pass
    return value


def inverse_long(value):
    try:
        value = int(float(value))
        vev_value = unpack('HH', pack('L', value))
        return unpack('L', pack('HH', vev_value[1], vev_value[0]))[0]
    except Exception:
        pass
    return value


def inverse_float(value):
    try:
        value = float(value)
        vev_value = unpack('HH', pack('f', value))
        return unpack('f', pack('HH', vev_value[1], vev_value[0]))[0]
    except Exception:
        pass
    return value


def inverse_double(value):
    try:
        value = float(value)
        vev_value = unpack('HHHH', pack('d', value))
        return unpack('d', pack('HHHH', vev_value[3], vev_value[2], vev_value[1], vev_value[0]))[0]
    except Exception:
        pass
    return value


def _and(*args):
    start = 1
    for a in args:
        start = start & a
    return start


def _or(*args):
    start = 0
    for a in args:
        start = start | a
    return start


# 添加自定义函数
g_s.functions.update(max=max, min=min, bit=bit, signed=signed, inverse_long=inverse_long, inverse_float=inverse_float, inverse_double=inverse_double, _and=_and, _or=_or)
