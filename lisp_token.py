def log(*args, **kwargs):
    print(*args, **kwargs)


from enum import Enum


class Type(Enum):
    error = -1          # error
    auto = 0            # +-*/
    bracketLeft = 1     # [
    bracketRight = 2    # ]
    number = 3          # 169
    string = 4          # "name"
    add = 5
    sub = 6
    mul = 7
    div = 8
    percent = 9         # %
    keyword = 10        # 关键字
    gt = 11
    lt = 12
    eq = 13
    ne = 14
    vars = 15           # 变量


class Token(object):
    def __init__(self, token_type, token_value):
        super(Token, self).__init__()
        # 用表驱动法处理 if
        d = {
            '+': Type.add,
            '-': Type.sub,
            '*': Type.mul,
            '/': Type.div,
            '[': Type.bracketLeft,
            ']': Type.bracketRight,
            '%': Type.percent,
            '>': Type.gt,
            '<': Type.lt,
            '=': Type.eq,
            '!': Type.ne,
        }
        if token_type == Type.auto:
            self.type = d[token_value]
        else:
            self.type = token_type
        self.value = token_value

    def __repr__(self):
        return '{}'.format(self.value)

    def __eq__(self, other):
        return self.value == other


def string_end(code, index):
    """
    code = "abc"
    index = 1
    """
    s = ''
    offset = index
    while offset < len(code):
        c = code[offset]
        if c == '"':
            # 找到了字符串的结尾
            # s = code[index:offset]
            return s, offset
        elif c == '\\':
            # 处理转义符, 现在只支持 \"
            if code[offset+1] == '"':
                s += '"'
                offset += 2
            else:
                # 这是一个错误, 非法转义符
                pass
        else:
            s += c
            offset += 1
    # 程序出错, 没有找到反引号 "
    pass


def vars_end(code, offset):
    """
    接收 code, 直到空格跳出
    """
    code = code[offset:].strip()
    c = ''
    index = 0
    for i, e in enumerate(code):
        if e == ']' or e == ' ':
            break
        else:
            c += e
            index += 1
    return c, index


def keyword_end(code, index):
    c = code[index:]
    keyword_list = ['function', 'if', 'log', 'yes', 'no', 'set', 'default']
    max_ele = sorted(keyword_list, key=len)
    for i in range(len(max_ele[-1])):
        if c[:i+1] in keyword_list:
            return c[:i+1], i


def _keyword(code, index):
    """
    code 是完整的字符串
    判断一个字符是不是关键字
    之前的方法(检查首字母), 会导致变量首位不能和关键字首位相
    elif c in ['i', 'l', 'y', 'n', 's']:
    """
    keyword_list = ['function', 'if', 'log', 'yes', 'no', 'set', 'default']
    max_ele = sorted(keyword_list, key=len)
    for i in range(len(max_ele[-1])):
        if code[index-1: index+i] in keyword_list:
            return True
        else:
            continue
    return False


def _vars(code, i):
    """
    如果前四位是 set, 就说明是变量
    """
    if code[i-5:i-2] == 'set':
        return True
    return False


def json_tokens(code):
    length = len(code)
    tokens = []
    spaces = '\n\t\r '
    digits = '1234567890'
    # 当前下标
    i = 0
    while i < length:
        # 先看看当前应该处理啥
        c = code[i]
        i += 1
        if c in spaces:
            # 空白符号要跳过, space tab return
            continue
        elif c in '+-*/%[]><=!':
            # 处理 6 种单个符号
            t = Token(Type.auto, c)
            tokens.append(t)
        elif c == '"':
            # 处理字符串
            s, offset = string_end(code, i)
            i = offset + 1

            t = Token(Type.string, s)
            tokens.append(t)
        elif c in digits:
            # 处理数字, 现在不支持小数和负数
            end = 0
            for offset, char in enumerate(code[i:]):
                if char not in digits:
                    end = offset
                    break
            n = code[i-1:i+end]
            i += end
            t = Token(Type.number, n)
            tokens.append(t)
        elif c == ';':
            # 处理注释
            if '\n' not in code[i:]:
                # 说明是单表达式时的注释
                break
            index = code[i:].index('\n')
            i += index
        # 这一步应该直接判断
        elif _keyword(code, i):
            # 处理关键字
            k, offset = keyword_end(code, i-1)
            i += offset
            t = Token(Type.keyword, k)
            tokens.append(t)
        elif _vars(code, i) or c.isalpha():
            # 说明是变量, 目前对变量名做首字母要求
            var, index = vars_end(code, i-1)
            t = Token(Type.vars, var)
            tokens.append(t)
            i += index - 1
        else:
            pass
    return tokens


def parsed_array(tokens):
    token_array = []
    counter = 0
    break_index = 0
    for i, p in enumerate(tokens):
        e = p.value
        if counter > 0:
            counter -= 1
            continue
        elif e == '[':
            v, break_index = parsed_array(tokens[i+1:])
            counter = break_index
            token_array.append(v)
        if e not in ',[]':
            token_array.append(p)
        elif e == ']':
            break_index = i + 1
            break
    return token_array, break_index


def main():
    code = """
        [set v1 [* 3 4]]
        [function [add x y] [+ x y]]
        [set v2 5]
        [+ v1 v2]
        [log v1]
        [add -1 5]
    """
    print('code', code.lstrip())
    ts = json_tokens(code)
    print('tokens', ts)
    tree, c = parsed_array(ts)
    print('tree', tree)


if __name__ == '__main__':
    main()
