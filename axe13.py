from lisp_token import log, parsed_array, Type, Token
from lisp_token import json_tokens as lisp_tokens


def reduce(fn, array, basic, vars):
    array = [basic] + array
    if len(array) == 2:
        x, y = array
        if isinstance(y, list):
            y = apply_op(y, vars)
        return fn(int(x), int(y))
    else:
        x, y, *ls = array
        t = fn(int(x), int(y))
        return reduce(fn, ls, t, vars)


def format_expression(ls, vars):
    expression = []
    for i, e in enumerate(ls):
        if e.type == Type.number:
            expression.append(e.value)
        elif e.type == Type.vars:
            v = vars.get(e.value, Type.error)
            if v == Type.error:
                raise ValueError
            expression.append(v)
        else:
            pass
    return expression


def apply_op(tokens, vars):
    from operator import add, sub, mul, truediv, mod
    op_dic = {
        '+': add,
        '-': sub,
        '*': mul,
        '/': truediv,
        '%': mod,
    }
    op, *expression = tokens
    expression = format_expression(expression, vars)
    basic = expression[0]
    expression = expression[1:]
    return reduce(op_dic[op.value], expression, basic, vars)


def apply_compare(tokens, vars):
    # 本来应该用 tokens.type == Type.keyword 的方式统一
    if isinstance(tokens, Token):
        # 说明是关键字
        return tokens
    elif isinstance(tokens, list):
        from operator import eq, ne, gt, lt
        op_dic = {
            '>': gt,
            '<': lt,
            '!': ne,
            '=': eq,
        }
        op, *expression = tokens
        v1, v2 = format_expression(expression, vars)
        ans = op_dic[op.value](v1, v2)
        if ans:
            return Token(Type.keyword, 'yes')
        return Token(Type.keyword, 'no')
    else:
        pass


def apply_if(tokens, vars):
    boolean = apply_compare(tokens[1], vars)
    index = 2
    # 新增魔法方法 __eq__
    if boolean == 'no':
        index = 3
    t = tokens[index]
    token = interpreter([t], vars)
    return token


def apply_log(tokens, vars):
    value = tokens[1]
    console = value
    if isinstance(value, list):
        console, _ = interpreter([value], vars)
    elif isinstance(value, Token):
        if value.type == Type.string:
            console = value.value
        elif value.type == Type.vars:
            error = Type.error
            # vars 中存的数组
            console, *_ = vars.get(value.value, error)
        else:
            pass
    else:
        pass
    print('>>> {}'.format(console))


def apply_set(tokens, vars):
    _, k, v = tokens
    if isinstance(v, list):
        v, _ = interpreter([v], vars)
    elif isinstance(v, Token):
        if v.type == Type.vars:
            v = vars.get(v.value)
        elif v.type == Type.number:
            v = int(v.value)
        else:
            print('set error')
    vars[k.value] = v


def apply_function(tokens, vars):
    # _, define, *(body, *a) = tokens
    _, define, body = tokens
    function_name, *arg = define
    # log('--------function body---------', body)
    vars[function_name.value] = body


def apply_call(tokens, vars):
    define, *args = tokens
    function_name, *body = vars[define.value]
    body = args
    token = [function_name, *body]
    (value, *_), *_ = interpreter([token], vars)
    return value


def interpreter(tree, vars):
    """
    tree 是一个形如 [表达式 1, [表达式 2, ... 表达式 n]]
    返回运行后, 表达式的值
    """
    output = []
    apply_dic = {
        'op': apply_op,
        'compare': apply_compare,
        'if': apply_if,
        'log': apply_log,
        'set': apply_set,
        'function': apply_function,
        'call': apply_call,
    }

    for i in tree:
        key = key_from_token(i, vars)
        fn = apply_dic[key]
        output.append(fn(i, vars))
    return output, vars


def key_from_token(array, vars):
    t = array[0].value
    keyword_list = ['function', 'if', 'log', 'yes', 'no', 'set', 'default']
    if t in '+-*/%':
        return 'op'
    elif t in '><=!':
        return 'compare'
    elif t in keyword_list:
        return t
    elif t in vars:
        if isinstance(vars[t], list):
            return 'call'
    else:
        return 'function'


def apply(code):
    vars = {}
    tokens = lisp_tokens(code)
    tree, _ = parsed_array(tokens)
    console = interpreter(tree, vars)
    return console


def test():
    print('run main')
    c = """
    [set a 1]
    [set b 2]
    [set v1 [+ a b]]
    
    [log v1]
    
    [function [plus x y] [+ x y]]
    
    [set v2 [plus 4 5]]
    [log v2]
    
    [if yes
        [log "是 yes"]
        [log "是 no"]
    ]
    """
    # log('输入\n', c)
    console = apply(c)
    # log('返回值', console)


def main():
    test()


if __name__ == '__main__':
    main()
