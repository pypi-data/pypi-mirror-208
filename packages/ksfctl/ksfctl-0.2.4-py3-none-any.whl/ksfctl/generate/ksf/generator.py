from datetime import datetime
from hashlib import md5

from ksfctl.generate.ksf.parser import KsfParser
from ksfctl.parser.ksf import *
from ksfctl.parser.parser import generate


################### 用例合并模式 ####################
class CaseGenerator(KsfParser):
    def __init__(self, ast, destination, export_symbols, out_file, **kwargs):
        super().__init__(ast, destination, export_symbols, **kwargs)
        self.out_file = Path(destination) / out_file  # 生成的纯rpc头文件

        self.to_file()

    def parse_enum(self, curr_module, ksf_enum: KsfEnum):
        enum_str = f"""\
    enum {ksf_enum.name}
    {{
"""
        enum_member_str_list = []
        for m in ksf_enum.member:
            enum_member_str_list.append(self.parse_enum_member(m))

        enum_str += self.add_lines(',\n'.join(enum_member_str_list), 1)

        enum_str += f"""\
    }};
"""

        return enum_str

    def parse_struct(self, curr_module, ksf_struct: KsfStruct):
        struct_str = f"""\
    struct {ksf_struct.name} 
    {{
"""
        # 解析字段
        var_list = []
        for var in ksf_struct.variable:
            var_list.append(self.parse_variable(curr_module, ksf_struct.variable[var]))

        var_widths = self.get_column_widths(var_list)
        for tag, ro, var_type, var_name, var_value in var_list:
            struct_str += self.add_lines(f"{tag} {ro} {var_type} {var_name} {var_value}", 2)

        struct_str += f"""\
    }};

"""
        return struct_str

    def parse_operator_param(self, curr_module, ksf_operator: KsfOperator):
        param_list = []
        for var_name, is_output in ksf_operator.ordered_var:
            param = ksf_operator.output[var_name] if is_output else ksf_operator.input[var_name]
            param_list.append(
                f"""{'out' if is_output else ''} {self.parse_type(curr_module, param.value_type)} {var_name}""")

        return ', '.join(param_list)

    def parse_interface(self, curr_module, ksf_interface: KsfInterface):
        interface_str = f'''\
    interface {ksf_interface.name}
    {{
'''

        for operator in ksf_interface.operator.values():
            if not operator.export:
                continue
            interface_str += f"""\
        {self.parse_type(curr_module, operator.return_type)} {operator.name}({self.parse_operator_param(curr_module, operator)});
"""
        interface_str += f'''\
    }};
'''

        return interface_str

    def to_file(self):
        if len(self.ast.get_all_export_symbol()) == 0:
            raise RuntimeError("no export symbol")

        curr_module = None
        const_list = []
        enum_list = []
        struct_list = []
        interface_list = []
        export_str = ''

        for sym in self.ast.get_all_export_symbol():
            ele = self.ast.all_element.obj[sym]
            module = ele.module

            if isinstance(ele, KsfConst):
                const_list.append((ele.module, self.parse_const(module, ele)))
                pass
            elif isinstance(ele, KsfEnum):
                enum_list.append((ele.module, self.parse_enum(module, ele)))
                pass
            elif isinstance(ele, KsfStruct):
                struct_list.append((ele.module, self.parse_struct(module, ele)))
                pass
            elif isinstance(ele, KsfInterface):
                interface_list.append((ele.module, self.parse_interface(module, ele)))

        for module, text in const_list + enum_list + struct_list + interface_list:
            if curr_module is None:
                curr_module = module
                export_str += f"""\
{self.get_ns_begin(module)}
"""
            elif curr_module != module:
                export_str += f"""\
{self.get_ns_end(curr_module)}

{self.get_ns_begin(module)}
"""
                curr_module = module
            export_str += text

        export_str = f"{export_str}{self.get_ns_end(curr_module)}\n\n"

        with self.out_file.open("w") as f:
            f.write(export_str)


def case_gen(files, include_dirs, destination_dir, export_symbols, out_file, with_special_container=False):
    file_path = files

    real_inc_dirs = set()
    for inc in include_dirs:
        real_inc_dirs.add(str(Path(inc).resolve()))
    ast = generate(files=file_path,
                   search_dirs=real_inc_dirs,
                   with_curr_dir_first=True,
                   export_symbols=export_symbols
                   )
    CaseGenerator(ast, destination_dir, export_symbols, out_file, with_special_container=with_special_container)


# 测试用例
if __name__ == '__main__':
    # case_gen(files=['example/struct_simple.ksf'],
    #          include_dirs=['.'], destination_dir='gen',
    #          export_symbols=['MyModule.TestObj.func', 'MyModule.TestObj.func2'],
    #          out_file='case.ksf')

    case_gen(files=['/Users/alexxiong/kingstar/TaurusTradeProxy/proto/Taurus/TaurusCounterObj.ksf'],
             include_dirs=['/Users/alexxiong/kingstar/TaurusTradeProxy/proto/Taurus'],
             destination_dir='gen',
             export_symbols=['Taurus.CounterObj.AccountLogin', 'Taurus.CounterObj.InsertOrder'],
             out_file='case.ksf',
             with_special_container=False)
