from ksfctl.parser.ksf import *
from ksfctl.parser.parser import generate


class KsfParser:
    def __init__(self, ast, destination, export_symbols, **kwargs):
        self.__dict__.update(kwargs)
        self.ast = ast

        Path(destination).mkdir(parents=True, exist_ok=True)
        self.dest_path = Path(destination)
        self.export_symbols = export_symbols  # 导出符号列表

    def __getattr__(self, name):
        if name.startswith('with_') and not hasattr(self, 'name'):
            return False
        return super().__getattr__(name)

    @staticmethod
    def endl():
        return '\n'

    @staticmethod
    def get_column_widths(lst):
        # 创建一个空列表来保存每列的最大宽度
        column_widths = [0] * len(lst[0])

        # 遍历列表中的所有元素，找到每列的最大宽度
        for item in lst:
            for i, value in enumerate(item):
                column_widths[i] = max(column_widths[i], len(value))

        return column_widths

    def add_include(self, header):
        """添加头文件"""
        if header in self.inc_native:
            self.inc_native[header] = True
        elif header in self.inc_depends:
            self.inc_native[header] = True

    def enable_push(self, operator_name):
        """启用推送函数"""
        if not self.push_functions or operator_name in self.push_functions:
            return True
        return False

    def enable_async_rsp(self, operator_name):
        """启用异步响应"""
        if not self.push_functions or operator_name not in self.push_functions:
            return True
        return False

    def get_repl_headfile(self, header):
        return header

    def get_module(self, module):
        return module

    def get_full_name(self, module, name):
        return f"{self.get_module(module)}::{name}"

    def get_ns_begin(self, module, with_endl=True):
        return f"module {module} {{\n"

    def get_ns_end(self, module, with_endl=True):
        """获取命名空间结束，有多少::就有多少}"""
        return f"}};\n"

    def parse_header(self, with_ksf):
        output = ""
        for header in self.inc_ordered[0]:
            if self.inc_native[header]:
                output += "#include " + header + "\n"

        output += "\n"

        if with_ksf:
            for header in self.inc_ordered[1]:
                if self.inc_native[header]:
                    output += "#include " + header + "\n"
        return output

    @staticmethod
    def get_type_id(curr_module, value_type):
        return f"{curr_module if value_type['module'] is None else value_type['module']}.{value_type['name']}"

    def is_movable_type(self, module, value_type):
        """判断是否是可以进行std::move的类型"""
        if value_type['type'] == 'native':
            return value_type['name'] == 'string'
        elif isinstance(value_type, KsfStructType):

            if hasattr(value_type, 'module'):
                class_full_name = value_type['module'] + "." + value_type['name']
            else:
                class_full_name = module + "." + value_type['name']

            return class_full_name not in self.ast.enums
        elif isinstance(value_type, KsfVectorType):
            return True
        elif isinstance(value_type, KsfMapType):
            return True
        else:
            return False

    def parse_type(self, module, value_type: KsfType):
        if isinstance(value_type, KsfBuildInType):
            if value_type.name == 'string':
                return 'string'
            elif value_type.name == 'int':
                if value_type.bit == 8:
                    return f'{"unsigned byte" if value_type.unsigned else "byte"}'
                elif value_type.bit == 16:
                    return f'{"unsigned short" if value_type.unsigned else "short"}'
                elif value_type.bit == 32:
                    return f'{"unsigned int" if value_type.unsigned else "int"}'
                elif value_type.bit == 64:
                    return f'{"unsigned long" if value_type.unsigned else "long"}'
                raise SyntaxError(f"不支持解析的字段类型[{value_type}]")
            elif value_type.name == 'float':
                return value_type.name
            elif value_type.name == 'double':
                return value_type.name
            elif value_type.name == 'bool':
                return value_type.name
            else:
                raise SyntaxError(f"不支持解析的字段类型[{value_type}]")
        elif isinstance(value_type, KsfStructType):
            if value_type.module is not None and module != value_type.module:
                return self.get_module(value_type['module']) + "::" + value_type.name
            else:
                return value_type.name
        elif isinstance(value_type, KsfVectorType):
            if not self.with_special_container:
                true_type = 'vector'
            elif value_type.is_ordered and not value_type.is_hashed and not value_type.is_unique_member:
                true_type = 'vector'
            elif value_type.is_ordered and not value_type.is_hashed and value_type.is_unique_member:
                true_type = 'vector[set]'
            elif not value_type.is_ordered and value_type.is_hashed and value_type.is_unique_member:
                true_type = 'vector[hashset]'
            else:
                raise SyntaxError(f"不支持解析的字段类型[{value_type}]")

            return f"{true_type}<{self.parse_type(module, value_type.value_type)}>"
        elif isinstance(value_type, KsfMapType):
            if not self.with_special_container:
                true_type = 'map'
            elif not value_type.is_ordered and value_type.is_hashed and value_type.is_unique_member:
                true_type = 'map[hashmap]'
            elif value_type.is_ordered and not value_type.is_hashed and value_type.is_unique_member:
                true_type = 'map'
            else:
                raise SyntaxError(f"不支持解析的字段类型[{value_type}]")
            return f"{true_type}<{self.parse_type(module, value_type.key_type)}, {self.parse_type(module, value_type.value_type)}>"

        raise SyntaxError(f"不支持解析的字段类型[{value_type}]")

    def parse_comment_above(self, comment, tab=None):
        if comment is None or comment == '':
            return ''

        comment_lines = comment.split('\n')
        if len(comment_lines) == 1:
            return f"{tab}//{comment}\n"
        else:
            import re
            matches = re.findall(r"\s+\*\s+(.*)\n", f"/*{comment}*/")
            comment_str = f'{tab}/**\n'

            # 将每行注释内容拼接为Python风格的注释
            for match in matches:
                comment_str += f"{tab} * {match}\n"
            comment_str += f'{tab} */\n'
            return comment_str

    def parse_comment_line(self, comment):
        if comment is None or comment == '':
            return ''

        comment_lines = comment.split('\n')
        if len(comment_lines) == 1:
            return f"//{comment}"
        else:
            raise SyntaxError("不支持的注释方式")

    def parse_value(self, value):
        return value['value'] if value['is_number'] else f'"{value["value"]}"'

    def parse_const(self, curr_module, ksf_const: KsfConst):
        if ksf_const.value_type['name'] == 'string':
            return f"{self.parse_comment_above(ksf_const.comment)}{self.curr_tab}constexpr const char *{ksf_const.name} = {self.parse_value(ksf_const.value)};\n\n"
        return f"{self.parse_comment_above(ksf_const.comment)}{self.curr_tab}constexpr {self.parse_type(curr_module, ksf_const.value_type)} {ksf_const.name} = {self.parse_value(ksf_const.value)};\n\n"

    def parse_enum_member(self, ksf_enum_member: KsfEnumMember):
        return f"    {ksf_enum_member.name} = {ksf_enum_member.value}"

    def parse_enum_to_str(self, curr_module, ksf_enum_member: KsfEnumMember, with_module=False):
        if with_module:
            return f"case {curr_module}::{ksf_enum_member.name}: return \"{ksf_enum_member.name}\";"
        else:
            return f"case {ksf_enum_member.name}: return \"{ksf_enum_member.name}\";"

    def parse_str_to_enum(self, curr_module, ksf_enum_member: KsfEnumMember, with_module=False):
        if with_module:
            return f"if (s == \"{ksf_enum_member.name}\") {{ e = {curr_module}::{ksf_enum_member.name}; return 0; }}"
        else:
            return f"if (s == \"{ksf_enum_member.name}\") {{ e = {ksf_enum_member.name}; return 0; }}"

    def parse_default_var(self, name, value_type, default):
        if default is None:
            if value_type['name'] == 'int':
                return f'''if ({name} == 0) '''
            elif value_type['name'] == 'float':
                return f'if (ksf::KS_Common::equal(0.0f, {name})) '
            elif value_type['name'] == 'double':
                return f'if (ksf::KS_Common::equal(0.0, {name})) '
            elif value_type['name'] == 'bool':
                return f'if ({name})'
            elif value_type['name'] == 'string':
                return f'if ({name}.empty())'
            else:
                return ''

        # 特殊处理一下bool型
        if default['is_bool']:
            return f'if ({"" if default["value"] else "!"}{name})'
        elif default['is_number']:
            if value_type['name'] == 'float':
                return f'if (ksf::KS_Common::equal({name}, {default["value"]}f)) '
            elif value_type['name'] == 'double':
                return f'if (ksf::KS_Common::equal({name}, {default["value"]})) '
            return f'if ({name} == {default["value"]}) '
        elif default['is_enum']:
            return f'if ({name} == {default["value"]}) '
        else:
            return f'if ({name} == "{default["value"]}") '

    def parse_variable(self, curr_module, ksf_var: KsfField):
        def parse_default_var(value_type, default):
            if default is None:
                return None

            # 特殊处理一下bool型
            if default['is_bool']:
                return f'{"true" if default["value"] else "false"}'
            elif default['is_number'] or default['is_enum']:
                return f'{default["value"]}'
            else:
                return f'"{default["value"]}"'

        default_var = parse_default_var(ksf_var.value_type, ksf_var.default)

        return ksf_var.tag, 'require' if ksf_var.is_required else 'optional', self.parse_type(curr_module,
                                                                                              ksf_var.value_type), ksf_var.name, f' = {default_var};' if default_var is not None else ';'

    def add_lines(self, lines, tab=0):
        space = ' ' * (4 * tab)

        return f"\n".join(space + line for line in lines.split("\n")) + self.endl()


def create_parser(files, repl_ns_dict, repl_inc_dir, include_dirs, destination_dir, push_functions, export_symbols,
                  flags=None):
    if flags is None:
        flags = defaultdict(bool)

    file_path = files

    real_inc_dirs = set()
    for inc in include_dirs:
        real_inc_dirs.add(str(Path(inc).resolve()))
    ast = generate(file_path, real_inc_dirs, flags['with_current_priority'], export_symbols)
    return KsfParser(ast, repl_ns_dict, repl_inc_dir, destination_dir, push_functions, export_symbols, **flags)
