import json
import warnings

import ply.yacc as yacc

from ksfctl.parser.ksf import *
from ksfctl.parser.token import KsfLexer
from ksfctl.parser.tools import *


class KsfParser:
    def __init__(self):
        # 解析语法的准备
        self.lexer = KsfLexer()
        self.lexer.build()
        self.tokens = self.lexer.tokens
        self.parser = yacc.yacc(module=self)

    def parse(self, data):
        self.text = data
        return self.parser.parse(data)

    def p_file(self, p):
        """
        file : module_list
             | ksf_header module_list
        """
        if len(p) == 3:
            p[0] = {'include': p[1], 'module': p[2]}
        else:
            p[0] = {'include': [], 'module': p[1]}

    def p_ksf_header(self, p):
        '''ksf_header : comment_multi include_list
        '''
        p[0] = p[2]

    def p_include_list(self, p):
        '''include_list : include_list include_item
                        | include_item'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]

    def p_include_item(self, p):
        '''include_item : INCLUDE STRING_CONSTANT'''
        p[0] = p[2]

    def p_module_name(self, p):
        """
        module_name : IDENTIFIER
        """
        p[0] = p[1]

    def p_module(self, p):
        """
        module : comment_multi MODULE module_name LEFT_BRACE element_list RIGHT_BRACE SEMICOLON comment_line
        """
        p[0] = {'name': p[3], 'comment': p[1] if p[1] is not None else p[8], 'elements': p[5]}

    def p_module_list(self, p):
        """
        module_list : module
                    | module_list module
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[1].append(p[2])
            p[0] = p[1]

    def p_return_type(self, p):
        """
        return_type : type
        """
        p[0] = p[1]

    def p_operation(self, p):
        """
        operation : comment_multi return_type operation_name LEFT_PAREN operation_param_list RIGHT_PAREN SEMICOLON comment_line
                  | comment_multi return_type operation_name LEFT_PAREN empty RIGHT_PAREN SEMICOLON comment_line
        """
        p[0] = {
            'type': 'operation',
            'name': p[3],
            'return_type': p[2],
            'variable': [] if p[5] is None else p[5],
            'comment': p[1] if p[1] is not None else p[8]
        }

    def p_element_list(self, p):
        """
        element_list : element
                     | element_list element
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[1].append(p[2])
            p[0] = p[1]

    def p_comment_multi(self, p):
        """
        comment_multi : COMMENT_MULTILINE
                      | empty
        """
        if len(p) == 2 and isinstance(p[1], str):
            p[0] = p[1]
        else:
            p[0] = None

    def p_comment_line(self, p):
        """
        comment_line : COMMENT_LINE
                | empty
        """
        if len(p) == 2 and isinstance(p[1], str):
            p[0] = p[1]
        else:
            p[0] = None

    ####### 元素 ########
    def p_element(self, p):
        """
        element : interface
                | struct
                | enum
                | constant
                | struct_keyword
        """
        p[0] = p[1]

    ####### 接口 #######
    def p_interface(self, p):
        """
        interface : comment_multi INTERFACE interface_name LEFT_BRACE operation_list RIGHT_BRACE SEMICOLON
        """
        p[0] = {
            'element': 'interface',
            'name': p[3],
            'operator': p[5],
            'comment': p[1]
        }

    ####### 结构体 ########
    def p_struct(self, p):
        """
        struct : comment_multi STRUCT struct_name LEFT_BRACE variable_list RIGHT_BRACE SEMICOLON
        """
        p[0] = {
            'element': 'struct',
            'name': p[3],
            'variable': p[5],
            'comment': p[1]
        }

    ####### 常量 ########
    def p_constant(self, p):
        """
        constant : comment_multi CONST type IDENTIFIER EQUALS value SEMICOLON comment_line
        """
        p[0] = {
            'element': 'constant',
            'type': p[3],
            'name': p[4],
            'value': p[6],
            'comment': p[1] if p[1] is not None else p[8],
        }

    ####### 枚举 ########
    def p_enum(self, p):
        """
        enum : comment_multi ENUM enum_name LEFT_BRACE enum_items opt_comma RIGHT_BRACE SEMICOLON
        """
        p[0] = {
            'element': 'enum',
            'name': p[3],
            'type': 'int32',
            'member': p[5],
            'comment': p[1]
        }

    ####### 结构体进行比较时需要的字段关联 #######
    def p_struct_keyword(self, p):
        """
        struct_keyword : KEY LEFT_SQUARE IDENTIFIER COMMA key_params RIGHT_SQUARE SEMICOLON
        """
        p[0] = {
            'element': 'key',
            'name': f'key[{p[3]}]',
            'struct': p[3],
            'args': p[5]
        }

    ######### 各类list #########
    def p_opt_comma(self, p):
        """
        opt_comma : COMMA
                  | empty
        """

    #### 枚举值列表 ####
    def p_enum_items(self, p):
        """
        enum_items : enum_item
                   | enum_items COMMA enum_item
        """
        if len(p) == 2:
            if 'value' not in p[1]:
                p[1]['value'] = 0
            p[0] = [p[1]]
        else:
            if 'value' not in p[3]:
                p[3]['value'] = p[1][-1]['value'] + 1

            p[0] = p[1] + [p[3]]

    def p_operation_list(self, p):
        """
        operation_list : operation
                       | operation_list operation
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[1].append(p[2])
            p[0] = p[1]

    def p_operation_name(self, p):
        """
        operation_name : IDENTIFIER
        """
        p[0] = p[1]

    def p_operation_param_list(self, p):
        """
        operation_param_list : operation_param
                             | operation_param_list COMMA operation_param
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_operation_output(self, p):
        """
        operation_output : OUTPUT
                        | empty
        """
        if p[1] is None:
            p[0] = False
        else:
            p[0] = True

    def p_operation_param(self, p):
        """
        operation_param : operation_output type IDENTIFIER
        """
        p[0] = {'is_output': p[1],
                'value_type': p[2],
                'name': p[3]}

    def p_interface_name(self, p):
        """
        interface_name : IDENTIFIER
        """
        p[0] = p[1]

    def p_struct_name(self, p):
        """
        struct_name : IDENTIFIER
        """
        p[0] = p[1]

    def p_variable_list(self, p):
        """
        variable_list : variable
                       | variable_list variable
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[1].append(p[2])
            p[0] = p[1]

    def p_variable_name(self, p):
        """
        variable_name : IDENTIFIER
        """
        p[0] = p[1]

    def p_enum_name(self, p):
        """
        enum_name : IDENTIFIER
        """
        p[0] = p[1]

    def p_enum_item(self, p):
        """
        enum_item : IDENTIFIER EQUALS number_value comment_line
                  | IDENTIFIER comment_line
        """
        if len(p) == 4:
            p[0] = {
                'name': p[1],
                'value': int(p[3], 0),
                'comment': p[4]
            }
        else:
            p[0] = {
                'name': p[1],
                'comment': p[2]
            }

    ######## 类型定义 ########
    def p_unsigned_type(self, p):
        """
        unsigned_type : UNSIGNED INT
                        | UNSIGNED SHORT
                        | UNSIGNED LONG
                        | UNSIGNED CHAR
        """
        if p[2] == 'long':
            p[0] = {'element': 'type', 'type': 'native', 'name': 'int', 'bit': 64, 'unsigned': True}
        elif p[2] == 'short':
            p[0] = {'element': 'type', 'type': 'native', 'name': 'int', 'bit': 16, 'unsigned': True}
        elif p[2] == 'int':
            p[0] = {'element': 'type', 'type': 'native', 'name': 'int', 'bit': 32, 'unsigned': True}
        elif p[2] == 'byte':
            p[0] = {'element': 'type', 'type': 'native', 'name': 'int', 'bit': 8, 'unsigned': True}

    def p_primitive_type(self, p):
        """
        primitive_type : INT
                       | SHORT
                       | LONG
                       | FLOAT
                       | DOUBLE
                       | CHAR
                       | BOOL
                       | STRING
                       | unsigned_type
        """
        if isinstance(p[1], str):
            if p[1] == 'int':
                bit = 32
                p[0] = {'element': 'type', 'type': 'native', 'name': 'int', 'bit': bit, 'unsigned': False}
            elif p[1] == 'short':
                bit = 16
                p[0] = {'element': 'type', 'type': 'native', 'name': 'int', 'bit': bit, 'unsigned': False}
            elif p[1] == 'long':
                bit = 64
                p[0] = {'element': 'type', 'type': 'native', 'name': 'int', 'bit': bit, 'unsigned': False}
            elif p[1] == 'float':
                bit = 32
                p[0] = {'element': 'type', 'type': 'native', 'name': 'float', 'bit': bit, 'unsigned': False}
            elif p[1] == 'double':
                bit = 64
                p[0] = {'element': 'type', 'type': 'native', 'name': 'double', 'bit': bit, 'unsigned': False}
            elif p[1] == 'byte':
                bit = 8
                p[0] = {'element': 'type', 'type': 'native', 'name': 'int', 'bit': bit, 'unsigned': False}
            else:
                p[0] = {'element': 'type', 'type': 'native', 'name': p[1]}
        else:
            p[0] = p[1]

    def p_struct_type(self, p):
        """
        struct_type : struct_name
        """
        v = p[1].split('::')
        if len(v) == 1:
            module = None
            name = v[0]
        else:
            module = v[0]
            name = v[1]

        p[0] = {
            'element': 'type',
            'type': 'class',  # 可能为struct，也可能为enum，需后面进行判定
            'name': name,
            'module': module,
        }

    def p_map_type(self, p):
        """
        map_type : MAP LEFT_ANGLE_BRACKET type COMMA type RIGHT_ANGLE_BRACKET
             | MAP LEFT_SQUARE IDENTIFIER RIGHT_SQUARE LEFT_ANGLE_BRACKET type COMMA type RIGHT_ANGLE_BRACKET
        """
        if len(p) == 7:
            p[0] = {
                'element': 'type',
                'type': 'map',
                'is_ordered': True,
                'is_hashed': False,
                'is_unique_member': True,
                'name': 'map<' + p[3]['name'] + ', ' + p[5]['name'] + '>',
                'key_type': p[3],
                'value_type': p[5]
            }
        else:
            if p[3] == 'hashmap':
                p[0] = {
                    'element': 'type',
                    'type': 'map',
                    'is_ordered': False,
                    'is_hashed': True,
                    'is_unique_member': True,
                    'name': 'hashmap<' + p[6]['name'] + ', ' + p[8]['name'] + '>',
                    'key_type': p[6],
                    'value_type': p[8]
                }
            else:
                raise Exception(f"Syntax error at token {p[1]}")

    def p_vector_type(self, p):
        """
        vector_type : VECTOR LEFT_ANGLE_BRACKET type RIGHT_ANGLE_BRACKET
             | VECTOR LEFT_SQUARE IDENTIFIER RIGHT_SQUARE LEFT_ANGLE_BRACKET type RIGHT_ANGLE_BRACKET
        """
        if len(p) == 5:
            p[0] = {
                'element': 'type',
                'type': 'vector',
                'is_ordered': True,
                'is_hashed': False,
                'is_unique_member': False,
                'name': 'vector<' + p[3]['name'] + '>',
                'value_type': p[3]
            }
        else:
            if p[3] == 'set':
                p[0] = {
                    'element': 'type',
                    'type': 'vector',
                    'is_ordered': True,
                    'is_hashed': False,
                    'is_unique_member': True,
                    'name': 'set<' + p[6]['name'] + '>',
                    'value_type': p[6]
                }
            elif p[3] == 'hashset':
                p[0] = {
                    'element': 'type',
                    'type': 'vector',
                    'is_ordered': False,
                    'is_hashed': True,
                    'is_unique_member': True,
                    'name': 'hashset<' + p[6]['name'] + '>',
                    'value_type': p[6]
                }
            else:
                raise Exception(f"Syntax error at token {p[1]}")

    def p_array_type(self, p):
        """
        array_type : type LEFT_SQUARE RIGHT_SQUARE
        """
        p[0] = {
            'element': 'type',
            'type': 'array',
            'name': 'array<' + p[1]['name'] + '>',
            'value_type': p[1],
        }

    def p_void_typ(self, p):
        """
        void_type : VOID
        """
        p[0] = {
            'element': 'type',
            'type': 'void',
            'name': 'void',
        }

    def p_type(self, p):
        """
        type : primitive_type
             | vector_type
             | map_type
             | array_type
             | struct_type
             | void_type
        """
        p[0] = p[1]

    ######## 值定义 ########
    def p_number_value(self, p):
        """
        number_value : EXPR_CONSTANT
                     | RADIX_CONSTANT
        """
        p[0] = p[1]

    def p_string_value(self, p):
        """
        string_value : STRING_CONSTANT
        """
        p[0] = p[1]

    def p_bool_value(self, p):
        """
        bool_value : TRUE
                   | FALSE
        """
        p[0] = p[1]

    def p_value(self, p):
        """
        value : string_value
              | number_value
              | bool_value
              | IDENTIFIER
        """
        is_number = True if p.slice[1].type == 'number_value' else False
        is_bool = True if p.slice[1].type == 'bool_value' else False
        is_enum = True if p.slice[1].type == 'IDENTIFIER' else False
        p[0] = {'value': p[1],
                'is_number': is_number,
                'is_bool': is_bool,
                'is_enum': is_enum,
                }

    def p_ro(self, p):
        """
        ro : REQUIRED
           | OPTIONAL
        """
        if p[1] == 'require':
            p[0] = True
        elif p[1] == 'optional':
            p[0] = False
        else:
            raise Exception(f"Syntax error at token {KsfLexer.find_position(p.lexer.lexdata, p.lexer)}")

    def p_tag(self, p):
        """
        tag : number_value
        """

        def is_valid(s):
            if s.isdigit():
                num = int(s, 0)
                if 0 <= num <= 255:
                    return True
            return False

        if is_valid(p[1]):
            p[0] = p[1]
        else:
            raise Exception(
                f"Syntax error at token {p.type} ({p.value}), line {KsfLexer.find_position(p.lexer.lexdata, p.lexer)}")

    def p_variable(self, p):
        """
        variable : tag ro type variable_name SEMICOLON comment_line
        | tag ro type variable_name EQUALS value SEMICOLON comment_line
        """

        if len(p) == 7:
            variable = {'type': 'variable',
                        'tag': p[1],
                        'is_required': p[2],
                        'value_type': p[3],
                        'name': p[4],
                        'comment': p[6]}
        else:
            variable = {'type': 'variable',
                        'tag': p[1],
                        'is_required': p[2],
                        'value_type': p[3],
                        'name': p[4],
                        'default': p[6],
                        'comment': p[8]}

        # 特殊处理一下bool类型
        if 'default' in variable:
            if variable['value_type']['name'] == 'bool':
                variable['default']['is_number'] = False
                variable['default']['is_bool'] = True
                if variable['default']['value'] == '1':
                    variable['default']['value'] = True
                elif variable['default']['value'] == '0':
                    variable['default']['value'] = False
                elif variable['default']['value'] == 'true':
                    variable['default']['value'] = True
                elif variable['default']['value'] == 'false':
                    variable['default']['value'] = False
                else:
                    raise SyntaxError(f'不支持的布尔默认值[{p[6]}]，请检查')

        p[0] = variable

    def p_key_params(self, p):
        """
        key_params : IDENTIFIER
                   | key_params COMMA IDENTIFIER
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_empty(self, p):
        """
        empty :
        """
        pass

    def p_error(self, p):
        if p:
            if p.type in {'COMMENT_MULTILINE', 'COMMENT_LINE'}:
                self.parser.errok()
                return
            else:
                raise SyntaxError(
                    f"Syntax error at token {p.type} ({p.value}), line {KsfLexer.find_position(p.lexer.lexdata, p.lexer)}")
        else:
            SyntaxError("Syntax error at EOF")


def pretty_print(jvalue):
    print(json.dumps(jvalue, indent=2, ensure_ascii=False))


def generate_ksf_ast(grammar, export_symbols=None):
    """
    检查解析出的语法数据是否合法，并生成基础ast树
    :param grammar:
    :return:
    """
    g_files = Graph()  # 文件有向图
    g_files_reverse = Graph()  # 文件逆向有向图

    # 1. 生成头文件包含树
    for file in grammar:
        curr = file
        if len(grammar[file]['include']) != 0:
            for include in grammar[file]['include']:
                # 在search路径中添加当前文件所在路径

                inc_path = Path(include)
                if inc_path is None:
                    raise FileNotFoundError(f"依赖的头文件[{include}]未找到")

                # print(f'{item}->{inc_path.name}')
                if inc_path.name == curr:
                    raise SyntaxError(f"不允许#include自身，[{curr}]存在错误的依赖")

                if inc_path.name not in grammar:
                    raise SyntaxError(f"索引到的ksf协议文件列表中找不到对应的依赖，[{curr}]存在错误的依赖[{inc_path}]")

                if not g_files.add_edge(inc_path.name, curr):
                    warnings.warn(f"[{curr}]重复添加依赖[{inc_path.name}]", category=SyntaxWarning, stacklevel=4,
                                  source=None)

                g_files_reverse.add_edge(curr, inc_path.name)

    # 2. 解析一下包含头，看看有没有循环包含
    def check_if_cycled():
        cycle = g_files.find_cycle()
        if cycle:
            raise Exception(f"解析的头文件依赖出现回环:{' -> '.join(str(node) for node in cycle)}, 请检查协议文件！")

    check_if_cycled()

    # 判断名称重复了
    flag_dicts = defaultdict(dict)

    def is_name_collision(flag, name, filename=None):
        if name not in flag_dicts[flag]:
            flag_dicts[flag][name] = filename
            return False
        else:
            return True

    def has_name(flag, name, filename=None):
        if name not in flag_dicts[flag]:
            return False, f"该名称[{name}]不存在"

        if filename is None or flag_dicts[flag][name] is None:
            return True, ""

        # 如果filename不为None, 则需要递归的判断一下该名称所在的文件是否位于当前文件所能依赖的所有文件中
        if flag_dicts[flag][name] == filename or flag_dicts[flag][name] in g_files_reverse.get_all_prev(filename,
                                                                                                        with_self=True):
            return True, ""
        else:
            return False, f"该名称[{name}]不位于被[{filename}]依赖的文件中"

    def traverse_all_file(func):
        # 处理单点文件
        for cur_file in grammar:
            if not g_files.has_node(cur_file):
                func(cur_file)

        # 按照依赖顺序遍历文件
        g_files.bfs_dag(func)

    # traverse_all_file(lambda a:print(a))
    # exit(0)

    def check_module_depends(filename):
        for module_desc in grammar[filename]['module']:
            # print(f'检测文件[{filename}]的模块[{module_desc["name"]}]中...')
            module_name = module_desc["name"]

            for element in module_desc['elements']:
                curr_element_name = module_name + '.' + element['name']
                if 'name' in element and is_name_collision('element', curr_element_name, filename):
                    raise SyntaxError(f"不允许有重复的模块元素命名{curr_element_name}")

                # 判断类型是否合法
                def is_valid(etype, *callback):
                    # native 为原生类型，不用解析
                    if etype['type'] == 'native':
                        return True

                    # vector 需递归解析
                    if etype['type'] == 'vector':
                        return is_valid(etype['value_type'])

                    # map 则需要 key_type和value_type双解析
                    if etype['type'] == 'map':
                        return is_valid(etype['value_type']) and is_valid(etype['key_type'])

                    element_name = (module_name if etype['module'] is None else etype['module']) + '.' + etype['name']
                    valid, err_msg = has_name('element', element_name, filename)
                    if not valid:
                        raise SyntaxError(err_msg)

                    if len(callback) != 0:
                        for cb in callback:
                            cb(element_name)

                # pretty_print(element)
                # 判断是否成立的原则：
                # 1. 类(结构体or枚举)之前是否有其他类定义，包括在依赖的文件中定义的
                # 2. 接口中定义的类是否被定义
                if element['element'] == 'enum':
                    for member in element['member']:
                        if is_name_collision('enum_member', module_name + '.' + element['name'] + '.' + member['name']):
                            raise SyntaxError(f"枚举定义[{module_name + '.' + element['name']}]中有重复"
                                              f"[{module_name + '.' + element['name'] + '.' + member['name']}]")
                elif element['element'] == 'struct':
                    # 先确定自身的变量类型是否是已经存在的，不存在则退出
                    # pretty_print(element['variable'])
                    for var in element['variable']:
                        if is_name_collision('struct_variable',
                                             module_name + '.' + element['name'] + '.' + var['name']):
                            raise SyntaxError(
                                f"结构体[{module_name + '.' + element['name']}]不允许有重名的变量{var['name']}")

                        value_type = var['value_type']

                        def check_default(element_name):
                            default = var['default'] if 'default' in var else None
                            if default is not None:
                                if not default['is_enum']:
                                    module_enum = default['value'].split("::")
                                    if len(module_enum) == 1:
                                        valid, err_msg = has_name('enum_member', (
                                            module_name if value_type['module'] is None else value_type[
                                                'module']) + '.' + value_type[
                                                                      'name'] + '.' + module_enum[0], filename)
                                        if not valid:
                                            raise SyntaxError(err_msg)
                                    elif len(module_enum) == 2:
                                        if module_enum[0] != (
                                                module_name if value_type['module'] is None else value_type['module']):
                                            raise SyntaxError(
                                                f"默认的枚举值[{default['value']}]不属于该类型[{value_type['name']}]")

                                        valid, err_msg = has_name('enum_member', (
                                            module_name if value_type['module'] is None else value_type[
                                                'module']) + '.' + value_type[
                                                                      'name'] + '.' + module_enum[1], filename)
                                        if not valid:
                                            raise SyntaxError(err_msg)

                        is_valid(value_type, check_default)
                elif element['element'] == 'interface':
                    # 对于所有函数，判断 返回值类型、参数类型是否合法
                    # 对于所有函数，判断 参数名是否重复
                    for operator in element['operator']:
                        if is_name_collision('operator_name',
                                             curr_element_name + '.' + operator['name']):
                            raise SyntaxError(
                                f"不允许有重名的接口函数{module_name + '.' + element['name'] + '.' + operator['name']}")

                        def has_return():
                            return operator['return_type']['name'] != 'void'

                        has_return() and is_valid(operator['return_type'])
                        for var in operator['variable']:
                            is_valid(var['value_type'])
                            operator_name = module_name + '.' + element['name'] + '.' + operator['name'] + '.' + var[
                                'name']
                            if is_name_collision('operator_params', operator_name + '.' + var['name']):
                                raise SyntaxError(f"接口[{module_name + '.' + element['name']}]定义中有重复参数名"
                                                  f"[{operator_name + '.' + var['name']}]")

                elif element['element'] == 'key':
                    # 对于所有key值, 保证结构体类型合法，参数名存在于结构体定义中，且Key只能定义在对应的模块中，且每一个结构体只能定义一个key
                    valid, err_msg = has_name('element', module_name + '.' + element['struct'], filename)
                    if not valid:
                        raise SyntaxError(f"定义key时，结构体的{err_msg}")

                    if is_name_collision('key', module_name + '.' + element['struct'], filename):
                        raise SyntaxError(
                            f"一个结构体只能定义一个key，结构体[{module_name + '.' + element['struct']}]有重复的key定义")

                    for arg in element['args']:
                        valid, err_msg = has_name('struct_variable', module_name + '.' + element['struct'] + '.' + arg)
                        if not valid:
                            raise SyntaxError(f"定义key时，参数的{err_msg}")

                elif element['element'] == 'constant':
                    pass
                else:
                    raise SyntaxError(f"无法处理的元素[{element.__str__()}]")

    def parse_file_to_object(filename):
        # 因为已经经过检测了，所以全局只需要根据文件进行相应的组织
        for module_desc in grammar[filename]['module']:
            # print(f'解析文件[{filename}]的模块[{module_desc["name"]}]中...')
            module_name = module_desc["name"]

            Ksf.file2module[filename].append(module_name)
            Ksf.module2file[module_name].append(filename)

            for element in module_desc['elements']:
                if element['element'] == 'enum':
                    ksf_enum = KsfEnum(file=filename,
                                       module=module_name,
                                       name=element['name'],
                                       member=element['member'],
                                       comment=element['comment']
                                       )

                    Ksf.add_enum(ksf_enum)
                elif element['element'] == 'struct':
                    ksf_struct = KsfStruct(file=filename,
                                           module=module_name,
                                           name=element['name'],
                                           variable=element['variable'],
                                           comment=element['comment']
                                           )

                    Ksf.add_struct(ksf_struct)
                elif element['element'] == 'interface':
                    ksf_interface = KsfInterface(file=filename,
                                                 module=module_name,
                                                 name=element['name'],
                                                 operator=element['operator'],
                                                 comment=element['comment']
                                                 )

                    Ksf.add_interface(ksf_interface)
                elif element['element'] == 'key':
                    Ksf.add_struct_key(module=module_name,
                                       struct=element['struct'],
                                       arg=element['args']
                                       )
                elif element['element'] == 'constant':
                    ksf_const = KsfConst(file=filename,
                                         module=module_name,
                                         value_type=element['type'],
                                         name=element['name'],
                                         value=element['value'],
                                         comment=element['comment']
                                         )

                    Ksf.add_constant(ksf_const)
                else:
                    raise SyntaxError(f"无法处理的元素[{element.__str__()}]")

    # 检查模块依赖关系，确定合法
    traverse_all_file(check_module_depends)

    # 开始转换文件到结构体
    traverse_all_file(parse_file_to_object)

    # 遍历所有导出的元素
    # for element in Ksf.all_elements:
    #     if element.id in Ksf.element_graph:
    #         print(element.id)

    # Ksf.obj_graph.bfs_dag(lambda x: print(x))
    Ksf.update_export_symbol(export_symbols)


def find_file(file_path, search_dirs, with_curr_dir_first):
    file = Path(file_path)
    if with_curr_dir_first and file.exists():
        return file

    if file.is_absolute() and not file.exists():
        return None

    for search_dir in search_dirs:
        search_file = Path(search_dir) / file_path
        if search_file.exists():
            return search_file

    return None


def generate(files, search_dirs: set, with_curr_dir_first: bool, export_symbols):
    parser_grammar = {}

    def parse_depends(file, is_source=False):
        file = find_file(file, search_dirs, with_curr_dir_first)
        if file is None:
            raise FileNotFoundError(f"文件[{file}]没有找到")

        Ksf.add_file(file, is_source)

        # 创建语法分析器
        parser = KsfParser()
        if file not in parser_grammar:
            with file.open() as f:
                curr_file_grammar = parser.parse(f.read())
                parser_grammar[file.name] = curr_file_grammar

                if len(curr_file_grammar['include']) != 0:
                    for include in curr_file_grammar['include']:
                        # 在search路径中添加当前文件所在路径
                        curr_search_dirs = search_dirs
                        curr_search_dirs.add(str(file.parent.resolve()))

                        inc_path = find_file(include, curr_search_dirs, with_curr_dir_first)
                        if inc_path is None:
                            raise FileNotFoundError(f"{f.name}依赖的头文件[{include}]未找到")

                        Ksf.add_include(file, inc_path, include)

                        if str(Path(inc_path).name) not in parser_grammar:
                            parse_depends(inc_path)

    for file in files:
        parse_depends(file, is_source=True)

    # print(parser_grammar.keys())
    generate_ksf_ast(parser_grammar, export_symbols)
    return Ksf


# 测试用例
if __name__ == '__main__':

    # 读取文件
    parser_grammar = {}
    file_path = [
        'example/enum_simple.ksf',
        'example/const_definition.ksf',
        'example/struct_simple.ksf'
    ]

    # (默认)生成单文件模式ast，保证所有数据都完全合法解析
    generate(file_path)

    for enum in Ksf.enums:
        print(Ksf.enums[enum].id)

    for struct in Ksf.structs:
        print(Ksf.structs[struct].id)
        print(Ksf.structs[struct].key_fields)

    for interface in Ksf.interfaces:
        print(Ksf.interfaces[interface].id)

    for const in Ksf.consts:
        print(Ksf.consts[const].id)
