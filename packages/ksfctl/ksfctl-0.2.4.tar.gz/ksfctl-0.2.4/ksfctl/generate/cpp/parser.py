from ksfctl.parser.ksf import *
from ksfctl.parser.parser import generate


class CppParser:
    def __init__(self,
                 ast,
                 repl_ns_dict,
                 repl_inc_dir,
                 destination,
                 push_functions,
                 export_symbols,
                 dispatch_mode,
                 **kwargs
                 ):
        self.__dict__.update(kwargs)
        self.ast = ast
        self.curr_module = None

        Path(destination).mkdir(parents=True,
                                exist_ok=True)
        self.dest_path = Path(destination)
        self.repl_ns_dict = repl_ns_dict  # 命名空间替换字典
        self.repl_inc_dir = repl_inc_dir  # 头文件替换字典
        self.push_functions = push_functions  # 推送函数列表
        self.export_symbols = export_symbols  # 导出符号列表
        self.dispatch_mode = dispatch_mode  # 分发模式[支持array, set, hash]

        self.inc_ordered = [[
            "ostream",
            "string",
            "vector",
            "set",
            "unordered_set",
            "map",
            "unordered_map",
        ], [
            "ksf/proto/proto.h",
            "ksf/proto/json.h"
        ], [
            "servant/Agent.h",
            "servant/Servant.h",
            "promise/promise.h", ]]

        self.inc_native = {
            "ostream": False,
            "string": True,
            "vector": False,
            "set": False,
            "unordered_set": False,
            "map": False,
            "unordered_map": False,
            "ksf/proto/proto.h": False,
            "ksf/proto/json.h": False,
            "servant/Agent.h": False,
            "servant/Servant.h": False,
            "promise/promise.h": False,
        }
        self.inc_depends = set()

    def __getattr__(self,
                    name):
        if name.startswith('with_') and not hasattr(self,
                                                    'name'):
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
                column_widths[i] = max(column_widths[i],
                                       len(value))

        return column_widths

    def add_include(self,
                    header):
        """添加头文件"""
        if header in self.inc_native:
            self.inc_native[header] = True
        else:
            self.inc_depends.add(header)

    def enable_push(self,
                    operator_name):
        """启用推送函数"""
        if operator_name in self.push_functions:
            return True
        return False

    def enable_async_rsp(self,
                         operator_name):
        """启用异步响应"""
        if not self.push_functions or operator_name not in self.push_functions:
            return True
        return False

    def has_return(self,
                   operator):
        return not isinstance(operator.return_type,
                              KsfVoidType)

    def get_repl_headfile(self,
                          header):
        if header in self.repl_inc_dir:
            return self.repl_inc_dir[header]
        return header

    def get_module(self,
                   module):
        if module in self.repl_ns_dict:
            return self.repl_ns_dict[module]
        return module

    def get_full_name(self,
                      module,
                      name):
        return f"{self.get_module(module)}::{name}"

    def get_ns_begin(self,
                     module,
                     with_endl=True):
        if self.with_cxx17:
            return f"""namespace {self.get_module(module)} {{"""
        """获取命名空间开始，将::替换为{"""
        ns = self.get_module(module)
        braces = ""
        for ns_simple in ns.split('::'):
            braces += f'namespace {ns_simple} {{{self.endl() if with_endl else " "}'
        return f"{braces}"

    def get_ns_end(self,
                   module,
                   with_endl=True):
        if self.with_cxx17:
            return f"""}} // namespace {self.get_module(module)}"""

        """获取命名空间结束，有多少::就有多少}"""
        ns = self.get_module(module)
        braces = ""
        for ns_simple in ns.split('::'):
            braces = f'}} {f"// namespace {ns_simple}{self.endl()}" if with_endl else ""}{braces}'
        return f"{braces}"

    def parse_header(self,
                     with_ksf=True,
                     with_servant=True):
        output = []
        for header in self.inc_ordered[0]:
            if self.inc_native[header]:
                output.append(f'''#include <{header}>''')

        output.append('')
        if with_ksf:
            for header in self.inc_ordered[1]:
                if self.inc_native[header]:
                    output.append(f'''#include <{header}>''')

        if with_servant:
            for header in self.inc_ordered[2]:
                if self.inc_native[header]:
                    output.append(f'''#include <{header}>''')

        output.append('')
        for header in self.inc_depends:
            output.append(f'''#include "{self.get_repl_headfile(header)}"''')
        return output

    def is_movable_type(self,
                        value_type):
        """判断是否是可以进行std::move的类型"""
        if isinstance(value_type,
                      KsfStringType):
            return True
        elif isinstance(value_type,
                        (KsfStructType, KsfEnumType)):
            if hasattr(value_type,
                       'module'):
                class_full_name = value_type['module'] + "." + value_type['name']
            else:
                class_full_name = self.curr_module + "." + value_type['name']

            return class_full_name not in self.ast.enums
        elif isinstance(value_type,
                        KsfVectorType):
            return True
        elif isinstance(value_type,
                        KsfMapType):
            return True
        else:
            return False

    def parse_type(self,
                   value_type: KsfType,
                   is_wrap=False):
        if isinstance(value_type,
                      KsfBuildInType):
            if isinstance(value_type,
                          KsfIntType):
                if value_type.bit == 8:
                    return f'{"unsigned char" if value_type.is_unsigned else "char"}'
                return f'{"u" if value_type.is_unsigned else ""}int{value_type.bit}_t'
            elif isinstance(value_type,
                            KsfFloatType):
                return value_type.name
            elif isinstance(value_type,
                            KsfStringType):
                self.add_include(f"string")
                return 'std::string'
            elif isinstance(value_type,
                            KsfBoolType):
                return 'bool'
            else:
                raise SyntaxError(f"不支持解析的字段类型[{value_type}]")
        elif isinstance(value_type,
                        (KsfStructType, KsfEnumType)):
            if value_type.module is not None and self.curr_module != value_type.module:
                return self.get_module(value_type['module']) + "::" + value_type.name + ("Wrap" if is_wrap else "")
            else:
                return value_type.name + ("Wrap" if is_wrap else "")
        elif isinstance(value_type,
                        KsfVectorType):
            if value_type.is_ordered and not value_type.is_hashed and not value_type.is_unique_member:
                true_type = 'std::vector'
                self.add_include("vector")
            elif value_type.is_ordered and not value_type.is_hashed and value_type.is_unique_member:
                true_type = 'std::set'
                self.add_include("set")
            elif not value_type.is_ordered and value_type.is_hashed and value_type.is_unique_member:
                true_type = 'std::unordered_set'
                self.add_include("unordered_set")
            else:
                raise SyntaxError(f"不支持解析的字段类型[{value_type}]")

            return f"{true_type}<{self.parse_type(value_type.value_type, is_wrap=is_wrap)}>"
        elif isinstance(value_type,
                        KsfMapType):
            if not value_type.is_ordered and value_type.is_hashed and value_type.is_unique_member:
                true_type = 'std::unordered_map'
                self.add_include("unordered_map")
            elif value_type.is_ordered and not value_type.is_hashed and value_type.is_unique_member:
                true_type = 'std::map'
                self.add_include('map')
            else:
                raise SyntaxError(f"不支持解析的字段类型[{value_type}]")
            return f"{true_type}<{self.parse_type(value_type.key_type, is_wrap=is_wrap)}, {self.parse_type(value_type.value_type, is_wrap=is_wrap)}>"

        raise SyntaxError(f"不支持解析的字段类型[{value_type}]")

    def parse_comment_above(self,
                            comment):
        if comment is None or comment == '':
            return ''

        comment_lines = comment.split('\n')
        if len(comment_lines) == 1:
            return f"//{comment}\n"
        else:
            return self.add_lines(f"/*{comment}*/") + '\n'

    def parse_comment_line(self,
                           comment):
        if comment is None or comment == '':
            return ''

        comment_lines = comment.split('\n')
        if len(comment_lines) == 1:
            return f"//{comment}"
        else:
            raise SyntaxError("不支持的注释方式")

    def parse_value(self,
                    value):
        return value['value'] if value['is_number'] else f'"{value["value"]}"'

    def parse_const(self,
                    ksf_const: KsfConst):
        if isinstance(ksf_const.value_type,
                      KsfStringType):
            return f"{self.parse_comment_above(ksf_const.comment)}constexpr const char *{ksf_const.name} = {self.parse_value(ksf_const.value)};"
        return f"{self.parse_comment_above(ksf_const.comment)}constexpr {self.parse_type(ksf_const.value_type)} {ksf_const.name} = {self.parse_value(ksf_const.value)};"

    def parse_enum_member(self,
                          ksf_enum_member: KsfEnumMember):
        return f"{ksf_enum_member.name} = {ksf_enum_member.value},"

    def parse_enum_to_str(self,
                          ksf_enum_member: KsfEnumMember,
                          with_module=False):
        if with_module:
            return f"case {self.curr_module}::{ksf_enum_member.name}: return \"{ksf_enum_member.name}\";"
        else:
            return f"case {ksf_enum_member.name}: return \"{ksf_enum_member.name}\";"

    def parse_str_to_enum(self,
                          ksf_enum_member: KsfEnumMember,
                          with_module=False):
        if with_module:
            return f"if (s == \"{ksf_enum_member.name}\") {{ e = {self.curr_module}::{ksf_enum_member.name}; return 0; }}"
        else:
            return f"if (s == \"{ksf_enum_member.name}\") {{ e = {ksf_enum_member.name}; return 0; }}"

    def parse_default_var(self,
                          name,
                          value_type,
                          default,
                          is_equal=True):
        if default is None:
            if isinstance(value_type,
                          KsfIntType):
                return f'''{name} {"=" if is_equal else "!"}= 0'''
            elif isinstance(value_type,
                            KsfFloatType):
                if value_type.bit == 32:
                    return f'{"" if is_equal else "!"}ksf::KS_Common::equal(0.0f, {name})'
                else:
                    return f'{"" if is_equal else "!"}ksf::KS_Common::equal(0.0, {name})'
            elif isinstance(value_type,
                            KsfBoolType):
                return f'{"" if is_equal else "!"}{name}'
            elif isinstance(value_type,
                            KsfStringType):
                return f'{"" if is_equal else "!"}{name}.empty()'

            return ''

        # 特殊处理一下bool型
        if default['is_bool']:
            return f'{"" if default["value"] == is_equal else "!"}{name}'
        elif default['is_number']:
            if isinstance(value_type,
                          KsfFloatType):
                if value_type.bit == 32:
                    return f'{"" if default["value"] == is_equal else "!"}ksf::KS_Common::equal({name}, {default["value"]}f)'
                else:
                    return f'{"" if default["value"] == is_equal else "!"}ksf::KS_Common::equal({name}, {default["value"]})'
            return f'{name} {"=" if default["value"] == is_equal else "!"}= {default["value"]}'
        elif default['is_enum']:
            return f'{name} {"=" if default["value"] == is_equal else "!"}= {default["value"]}'
        else:
            return f'{name} {"=" if default["value"] == is_equal else "!"}= "{default["value"]}"'

    def parse_variable(self,
                       ksf_var: KsfField):
        def parse_default_var(value_type,
                              default):
            if default is None:
                if isinstance(value_type,
                              KsfIntType):
                    return '0'
                elif isinstance(value_type,
                                KsfFloatType):
                    if value_type.bit == 32:
                        return '0.0f'
                    else:
                        return '0.0'
                elif isinstance(value_type,
                                KsfBoolType):
                    return 'true'
                elif isinstance(value_type,
                                KsfStringType):
                    return '""'
                else:
                    return None

            # 特殊处理一下bool型
            if default['is_bool']:
                return f'{"true" if default["value"] else "false"}'
            elif default['is_number'] or default['is_enum']:
                return f'{default["value"]}'
            else:
                return f'"{default["value"]}"'

        default_var = parse_default_var(ksf_var.value_type,
                                        ksf_var.default)
        comment = self.parse_comment_line(ksf_var.comment)

        return comment, self.parse_type(ksf_var.value_type
                                        ), ksf_var.name, f' = {default_var};' if default_var is not None else ';'

    def add_lines(self,
                  lines,
                  tab=0):
        if isinstance(lines,
                      str):
            lines = lines.split('\n')
        elif isinstance(lines,
                        (list, tuple, set)):
            return '\n'.join(self.add_lines(line,
                                            tab) for line in lines)
        else:
            raise TypeError(f"不支持的类型{type(lines)}")

        space = ' ' * (4 * tab)
        return f"\n".join(space + line for line in lines)


def create_parser(files,
                  repl_ns_dict,
                  repl_inc_dir,
                  include_dirs,
                  destination_dir,
                  push_functions,
                  export_symbols,
                  flags=None
                  ):
    if flags is None:
        flags = defaultdict(bool)

    file_path = files

    real_inc_dirs = set()
    for inc in include_dirs:
        real_inc_dirs.add(str(Path(inc).resolve()))
    ast = generate(file_path,
                   real_inc_dirs,
                   flags['with_current_priority'],
                   export_symbols)
    return CppParser(ast,
                     repl_ns_dict,
                     repl_inc_dir,
                     destination_dir,
                     push_functions,
                     export_symbols,
                     **flags)


# 测试用例
if __name__ == '__main__':
    file_path = [
        'example/enum_simple.ksf',
        'example/const_definition.ksf',
        'example/struct_simple.ksf'
    ]

    include_dirs = ['../../']

    destination_dir = '../../../gen'

    push_functions = {}

    export_symbols = {}

    sdk_invoke = {}

    sdk_export = {}

    parser = create_parser(file_path,
                           {},
                           {},
                           include_dirs,
                           destination_dir,
                           push_functions,
                           export_symbols,
                           flags={'with_current_priority': True}
                           )

    parser.parse_variable(parser.ast.modules[0],
                          parser.ast.modules[0].fields[0])
