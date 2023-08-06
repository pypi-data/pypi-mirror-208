from datetime import datetime
from hashlib import md5

from ksfctl.generate.cpp.parser import CppParser
from ksfctl.generate.cpp.template import *
from ksfctl.parser.ksf import *
from ksfctl.parser.parser import generate


class CppGenerator(CppParser):
    def __init__(self,
                 ast,
                 repl_ns_dict,
                 repl_inc_dir,
                 destination,
                 push_functions,
                 input_file,
                 output_file,
                 invoke_file,
                 dispatch_mode,
                 **kwargs
                 ):
        super().__init__(ast,
                         repl_ns_dict,
                         repl_inc_dir,
                         destination,
                         push_functions,
                         [],
                         dispatch_mode,
                         **kwargs)
        self.input_file = input_file
        self.output_file = Path(destination) / output_file  # 生成的头文件
        self.invoke_file = Path(destination) / invoke_file  # 生成的调用文件

    def parse_enum(self,
                   ksf_enum: KsfEnum):
        enum_members = []
        function_etos = []
        function_stoe = []
        for m in ksf_enum.member:
            enum_members.append(self.parse_enum_member(m))
            function_etos.append(self.parse_enum_to_str(m))
            function_stoe.append(self.parse_str_to_enum(m))

        return [fstr(template_enum,
                     comment=self.parse_comment_above(ksf_enum.comment),
                     enum_name=ksf_enum.name,
                     enum_members=enum_members,
                     ),
                fstr(template_etos,
                     enum_name=ksf_enum.name,
                     etos_member=function_etos),
                fstr(template_stoe,
                     enum_name=ksf_enum.name,
                     stoe_member=function_stoe)]

    def parse_resetDefault(self,
                           ksf_struct: KsfStruct):
        return fstr(template_resetDefault,
                    struct_name=ksf_struct.name)

    def parse_variable_writeTo(self,
                               ksf_field: KsfField):
        value_type = ksf_field.value_type
        if self.with_check_default and not ksf_field.is_required:
            if isinstance(value_type,
                          KsfBuildInType):
                if isinstance(value_type,
                              KsfBoolType):
                    check_default = f"""{'!' if not ksf_field.has_default() or ksf_field.default['value'] else ''}{ksf_field.name}"""
                else:
                    check_default = self.parse_default_var(f'{ksf_field.name}',
                                                           value_type,
                                                           ksf_field.default,
                                                           is_equal=False
                                                           )
            elif isinstance(value_type,
                            KsfStructType):
                return fstr(template_writeTo_variable,
                            variable_name=ksf_field.name,
                            variable_tag=ksf_field.tag, )
            elif isinstance(value_type,
                            KsfEnumType):
                module_name = f"{value_type.module}::" if self.curr_module != value_type.module else ""

                # 如果是枚举类型
                if ksf_field.has_default():
                    # 有枚举默认值的，使用默认值
                    check_default = f"""{ksf_field.name} != {module_name}{value_type.name}::{ksf_field.default['value']}"""
                else:
                    # 没有默认值的，使用第一个枚举值
                    check_default = f"""{ksf_field.name} != {module_name}{value_type.name}::{ksf_field.value_type.obj_type.member[0].name}"""
            elif isinstance(value_type,
                            KsfVectorType):
                check_default = f"""!{ksf_field.name}.empty()"""
            elif isinstance(value_type,
                            KsfMapType):
                check_default = f"""!{ksf_field.name}.empty()"""
            else:
                raise SyntaxError(f"不能被解析的字段类型[{value_type}]")

            return fstr(template_writeTo_variable_with_check,
                        check_default=check_default,
                        variable_declare=fstr(template_writeTo_variable,
                                              variable_name=ksf_field.name,
                                              variable_tag=ksf_field.tag, ),
                        )
        else:
            return fstr(template_writeTo_variable,
                        variable_name=ksf_field.name,
                        variable_tag=ksf_field.tag, )

    def parse_writeTo(self,
                      ksf_struct: KsfStruct):
        var_list = []
        for var in ksf_struct.variable:
            var_list.append(self.parse_variable_writeTo(ksf_struct.variable[var]))

        return fstr(template_writeTo,
                    variables=var_list)

    def parse_variable_writeToJson(self,
                                   ksf_field: KsfField):
        return f"""p->value["{ksf_field.name}"] = ksf::json::Output::writeJson({ksf_field.name});"""

    def parse_writeToJson(self,
                          ksf_struct: KsfStruct):
        var_list = []
        for var in ksf_struct.variable:
            var_list.append(self.parse_variable_writeToJson(ksf_struct.variable[var]))

        return fstr(template_writeToJson,
                    variables=var_list)

    def parse_variable_readFrom(self,
                                ksf_field: KsfField):
        return f"""_is.read({ksf_field.name}, {ksf_field.tag}, {"true" if ksf_field.is_required else "false"});"""

    def parse_readFrom(self,
                       ksf_struct: KsfStruct):
        var_list = []
        for var in ksf_struct.variable:
            var_list.append(self.parse_variable_readFrom(ksf_struct.variable[var]))

        return fstr(template_readFrom,
                    variables=var_list,
                    is_wrap=False)

    def parse_variable_readFromJson(self,
                                    ksf_field: KsfField):
        return f"""ksf::json::Input::readJson({ksf_field.name}, pObj->value["{ksf_field.name}"], {"true" if ksf_field.is_required else "false"});"""

    def parse_readFromJson(self,
                           ksf_struct: KsfStruct):
        var_list = []
        for var in ksf_struct.variable:
            var_list.append(self.parse_variable_readFromJson(ksf_struct.variable[var]))

        return fstr(template_readFromJson,
                    variables=var_list,
                    is_wrap=False)

    def parse_display(self,
                      ksf_struct: KsfStruct):
        var_list = ""
        for var in ksf_struct.variable:
            field = ksf_struct.variable[var]
            if isinstance(field.value_type,
                          KsfEnumType):
                var_list += f'_ds.display(static_cast<int32_t>({ksf_struct.variable[var].name}),"{ksf_struct.variable[var].name}");\n'
            else:
                var_list += f'_ds.display({ksf_struct.variable[var].name},"{ksf_struct.variable[var].name}");\n'

        return fstr(template_display,
                    variables=var_list)

    def parse_displaySimple(self,
                            ksf_struct: KsfStruct):
        var_list = []
        index = 0
        for field in ksf_struct.variable.values():
            index += 1
            if isinstance(field.value_type,
                          KsfEnumType):
                var_list.append(
                    f'_ds.displaySimple(static_cast<int32_t>({field.name}), {"false" if index == len(ksf_struct.variable) else "true"});\n')
            else:
                var_list.append(
                    f'_ds.displaySimple({field.name}, {"false" if index == len(ksf_struct.variable) else "true"});')

        return fstr(template_displaySimple,
                    variables=var_list)

    def parse_equal(self,
                    ksf_struct: KsfStruct):
        var_list = []
        for var in ksf_struct.variable:
            field = ksf_struct.variable[var]
            if isinstance(field.value_type,
                          KsfFloatType):
                var_list.append(f'ksf::KS_Common::equal(l.{field.name}, r.{field.name})')
            else:
                var_list.append(f'(l.{field.name} == r.{field.name})')

        return fstr(template_operator_equal,
                    struct_name=ksf_struct.name,
                    variables=' && '.join(var_list)
                    )

    def parse_struct_variables(self,
                               ksf_struct: KsfStruct):
        text_lines = []
        # 解析字段
        var_list = []
        for var in ksf_struct.variable:
            var_list.append(self.parse_variable(ksf_struct.variable[var]))

        var_widths = self.get_column_widths(var_list)
        for comment, var_type, var_name, var_value in var_list:
            if comment:
                text_lines.append(self.add_lines(f"{comment:<{var_widths[0]}}",
                                                 1))
            text_lines.append(self.add_lines(f"{var_type:<{var_widths[1]}} {var_name:<{var_widths[2]}}{var_value}",
                                             1
                                             )
                              )

        return self.endl().join(text_lines)

    def parse_struct(self,
                     ksf_struct: KsfStruct):
        self.add_include("ksf/proto/proto.h")

        comment = self.parse_comment_above(ksf_struct.comment)
        variables = self.parse_struct_variables(ksf_struct)
        struct_functions = [
            self.parse_resetDefault(ksf_struct),
            self.parse_writeTo(ksf_struct),
            self.parse_readFrom(ksf_struct)
        ]

        struct_operators = []

        if self.with_json:
            self.add_include("ksf/proto/json.h")
            struct_functions.append(self.parse_writeToJson(ksf_struct))
            struct_functions.append(self.parse_readFromJson(ksf_struct))

        struct_functions.append(self.parse_display(ksf_struct))
        struct_functions.append(self.parse_displaySimple(ksf_struct))
        struct_operators.append(self.parse_equal(ksf_struct))

        if len(ksf_struct.key_fields) != 0:
            key_vars = []
            for key_field in ksf_struct.key_fields:
                key_vars.append(f"""if(l.{key_field} != r.{key_field})  return (l.{key_field} < r.{key_field});""")
            struct_operators.append(fstr(template_operator_compare,
                                         struct_name=ksf_struct.name,
                                         variables=key_vars))

        if self.with_json:
            struct_operators.append(fstr(template_operator_stream_with_json,
                                         wrap_mode=False,
                                         struct_name=ksf_struct.name
                                         )
                                    )

        return fstr(template_struct,
                    comment=comment,
                    module_name=self.curr_module,
                    struct_name=ksf_struct.name,
                    md5sum=md5(ksf_struct.id.encode('utf8')).hexdigest(),
                    variables=variables,
                    struct_functions=struct_functions,
                    struct_operators=struct_operators
                    )

    def parse_output_var(self,
                         value_type,
                         name,
                         with_type):
        if not isinstance(value_type,
                          KsfVoidType):
            if not self.is_movable_type(value_type):
                return f"{self.parse_type(value_type)} {name}" if with_type else name
            elif self.with_rvalue_ref:
                return f"{self.parse_type(value_type)} &&{name}" if with_type else f"std::move({name})"
            else:
                return f"const {self.parse_type(value_type)} &{name}" if with_type else name

    def parse_output_vars(self,
                          ksf_operator,
                          with_type=True):
        vars_list = []
        if ksf_operator.has_return():
            vars_list.append(self.parse_output_var(ksf_operator.return_type,
                                                   '_ret',
                                                   with_type))

        for arg in ksf_operator.output.values():
            vars_list.append(self.parse_output_var(arg.value_type,
                                                   arg.name,
                                                   with_type
                                                   )
                             )

        return ', '.join(vars_list)

    def parse_InterfacePrxCallBack(self,
                                   ksf_interface: KsfInterface):
        func_case_list = []
        function_handles = []
        dispatch_str = []

        def parse_func_dispatch(index,
                                operator):
            """处理函数的分发"""
            output_args = []

            if operator.has_return():
                output_args.append(fstr(template_output_argument_parse,
                                        typename=self.parse_type(operator.return_type),
                                        argument_name='_ret',
                                        index=0
                                        )
                                   )

            for var in operator.output.values():
                output_args.append(fstr(template_output_argument_parse,
                                        typename=self.parse_type(var.value_type),
                                        argument_name=var.name,
                                        index=var.index
                                        )
                                   )

            func_case_list.append(fstr(template_dispatch_case_at_client,
                                       case=index,
                                       function_name=operator.name,
                                       output_params=self.parse_output_vars(operator,
                                                                            False),
                                       output_arguments=output_args
                                       )
                                  )

            function_handles.append(fstr(template_function_call,
                                         function_name=operator.name,
                                         arguments=self.parse_output_vars(operator,
                                                                          True)
                                         )
                                    )

        get_response_context = template_getResponseContext

        def dispatch(function_names):
            dispatch_str.append(fstr(template_array_style_onDispatch_at_client,
                                     dispatch_case_str=func_case_list,
                                     interface_name=ksf_interface.name,
                                     function_names=function_names
                                     )
                                )

        self.parse_DispatchOperatorCallBack(ksf_interface,
                                            dispatch,
                                            parse_func_dispatch)

        return fstr(template_callback,
                    interface_name=ksf_interface.name,
                    function_handles=function_handles,
                    get_response_context=get_response_context,
                    dispatch_str=dispatch_str
                    )

    def parse_InterfacePrxCallbackPromise(self,
                                          ksf_interface: KsfInterface):
        dispatch_case_str = []
        interface_promises = []
        on_dispatch = []

        def parse_func_dispatch(index,
                                operator):
            output_parsed_list = []
            if operator.has_return():
                output_parsed_list.append(f"{self.parse_type(operator.return_type)} _ret;")

            for var in operator.output.values():
                output_parsed_list.append(f"{self.parse_type(var.value_type)} {var.name};")

            interface_promises.append(fstr(template_callback_promise_class,
                                           interface_name=ksf_interface.name,
                                           function_name=operator.name,
                                           output_parsed_list=output_parsed_list
                                           )
                                      )

            func_case_list = []
            if operator.has_return():
                func_case_list.append(f"""_is.read(ptr->_ret, 0, true);""")

            for var2 in operator.output.values():
                func_case_list.append(f"""_is.read(ptr->{var2.name}, {var2.index}, true);""")

            dispatch_case_str.append(fstr(template_parse_func_dispatch_promise,
                                          case=index,
                                          interface_name=ksf_interface.name,
                                          function_name=operator.name,
                                          output_arguments=func_case_list
                                          )
                                     )

        def dispatch(function_names):
            on_dispatch.append(fstr(template_onDispatch_promise,
                                    dispatch_case_str=dispatch_case_str,
                                    interface_name=ksf_interface.name,
                                    function_names=function_names
                                    )
                               )

        self.parse_DispatchOperatorCallBack(ksf_interface,
                                            dispatch,
                                            parse_func_dispatch)

        return fstr(template_callback_promise,
                    interface_name=ksf_interface.name,
                    function_names=ksf_interface.operator.keys(),
                    interface_promises=interface_promises,
                    on_dispatch=on_dispatch
                    )

    def parse_InterfaceCoroPrxCallback(self,
                                       ksf_interface: KsfInterface):
        func_case_str = []
        on_dispatch = []

        def parse_case_dispatch(index,
                                operator):
            func_case_list = []
            if operator.has_return():
                func_case_list.append(
                    f"""{self.parse_type(operator.return_type)} _ret;\n_is.read(_ret, 0, true);"""
                )

            for var2 in operator.output.values():
                func_case_list.append(
                    f"""{self.parse_type(var2.value_type)} {var2.name};\n_is.read({var2.name}, {var2.index}, true);"""
                )

            def parse_output_vars(with_type=True):
                def parse_output_var(value_type,
                                     name,
                                     with_type):
                    if value_type.name != 'void':
                        if not self.is_movable_type(value_type):
                            return f"{self.parse_type(value_type)} {name}" if with_type else name
                        elif self.with_rvalue_ref:
                            return f"{self.parse_type(value_type)} &&{name}" if with_type else f"std::move({name})"
                        else:
                            return f"const {self.parse_type(value_type)} &{name}" if with_type else name

                vars_list = []
                if operator.has_return():
                    vars_list.append(parse_output_var(operator.return_type,
                                                      '_ret',
                                                      with_type))

                for argument in operator.output.values():
                    vars_list.append(parse_output_var(argument.value_type,
                                                      argument.name,
                                                      with_type))

                return vars_list

            func_case_str.append(fstr(template_parse_func_dispatch_coroutine,
                                      case=index,
                                      output_arguments=parse_output_vars(with_type=False),
                                      function_name=operator.name,
                                      func_case_list=func_case_list
                                      )
                                 )

        def dispatch(function_names):
            on_dispatch.append(fstr(template_onDispatch_coroutine,
                                    interface_name=ksf_interface.name,
                                    function_names=function_names,
                                    func_case_str=func_case_str
                                    )
                               )

        self.parse_DispatchOperatorCallBack(ksf_interface,
                                            dispatch,
                                            parse_case_dispatch)
        return fstr(template_callback_coroutine_class,
                    interface_name=ksf_interface.name,
                    on_dispatch=on_dispatch
                    )

    def parse_InterfaceProxyOperator(self,
                                     ksf_interface: KsfInterface):
        functions = []
        for operator in ksf_interface.operator.values():
            input_argument_declare = []
            output_argument_declare = []
            for var in operator.input.values():
                input_argument_declare.append(f"""_os.write({var.name}, {var.index});""")

            if operator.has_return():
                output_argument_declare.append(
                    f"""{self.parse_type(operator.return_type)} _ret;\n_is.read(_ret, 0, true);"""
                )

            for name in operator.output:
                var = operator.output[name]
                output_argument_declare.append(f"""_is.read({name}, {var.index}, true);""")

            def parse_all_vars(with_output=False):
                parsed_list = []
                for var_name, is_output in operator.ordered_var:
                    if is_output:
                        if with_output:
                            parsed_list.append(
                                f"{self.parse_type(operator.output[var_name].value_type)} &{var_name}"
                            )
                    else:
                        parsed_list.append(
                            f"const {self.parse_type(operator.input[var_name].value_type)} &{var_name}"
                        )

                return parsed_list

            arguments = parse_all_vars(with_output=True)
            input_arguments = parse_all_vars(with_output=False)
            comment = self.parse_comment_above(operator.comment)
            return_type = self.parse_type(operator.return_type) if operator.has_return() else 'void'

            return_line = self.add_lines(f"\nreturn _ret;",
                                         1) if operator.has_return() else ""

            functions.append(fstr(template_proxy_function,
                                  interface_name=ksf_interface.name,
                                  function_name=operator.name,
                                  arguments=arguments,
                                  input_arguments=input_arguments,
                                  argument_async_callback=f'{ksf_interface.name}PrxCallbackPtr callback',
                                  argument_coroutine_callback=f'{ksf_interface.name}CoroPrxCallbackPtr callback',
                                  argument_request_context=f'const _Context_ &_context_ = _Context_()',
                                  argument_response_context=f'_Context_ *_rsp_context_ = nullptr',
                                  input_argument_declare=input_argument_declare,
                                  output_argument_declare=output_argument_declare,
                                  return_type=return_type,
                                  return_line=return_line,
                                  comment=comment
                                  )
                             )
        return functions

    def parse_InterfaceProxy(self,
                             ksf_interface: KsfInterface):
        return fstr(template_proxy_class,
                    interface_name=ksf_interface.name,
                    functions=self.parse_InterfaceProxyOperator(ksf_interface)
                    )

    def parse_OperatorParamsList(self,
                                 operator: KsfOperator,
                                 mode: str):
        """mode: json, ksf, kup"""
        parsed_list = []
        for index, (name, is_output) in enumerate(operator.ordered_var):
            if mode == 'json':
                parsed_list.append(
                    f"""ksf::json::Input::readJson({name}, _jsonPtr->value["{name}"], {"false" if is_output else "true"});"""
                )
            elif mode == 'kup':
                if is_output:
                    parsed_list.append(f"""_ksfAttr_.getByDefault("{name}", {name}, {name});""")
                else:
                    parsed_list.append(f"""_ksfAttr_.get("{name}", {name});""")
            elif mode == 'ksf':
                parsed_list.append(f"""_is.read({name}, {index + 1}, {"false" if is_output else "true"});""")

        return parsed_list

    def parse_DispatchOperatorCallBack(self,
                                       ksf_interface: KsfInterface,
                                       interface_callback,
                                       *operator_callbacks
                                       ):
        if self.dispatch_mode in ['array', 'set']:
            operators = dict(sorted(ksf_interface.operator.items()))
        else:
            operators = ksf_interface.operator

        for index, operator in enumerate(operators.values()):
            for cb in operator_callbacks:
                cb(index,
                   operator)

        interface_callback(operators.keys())

    def parse_OperatorInvokeVars(self,
                                 index,
                                 operator: KsfOperator):
        parsed_list = []
        for name, is_output in operator.ordered_var:
            if not is_output:
                var = operator.input[name]
                if self.with_rvalue_ref and self.is_movable_type(var.value_type):
                    parsed_list.append(f"""std::move({var.name}), """)
                else:
                    parsed_list.append(f"""{var.name}, """)
            else:
                var = operator.output[name]
                parsed_list.append(f"""{var.name}, """)

        return ''.join(parsed_list)

    def parse_OperatorVarlist(self,
                              index,
                              operator: KsfOperator):
        parsed_list = []
        for name, is_output in operator.ordered_var:
            if not is_output:
                var = operator.input[name]
            else:
                var = operator.output[name]
            parsed_list.append(f"""{self.parse_type(var.value_type)} {var.name};""")

        return parsed_list

    def parse_OperatorOutputVar(self,
                                index,
                                operator: KsfOperator,
                                mode):
        parsed_list = []
        if operator.return_type['name'] != 'void':
            if mode == 'ksf':
                parsed_list.append(f"""_os.write(_ret, 0);""")
            elif mode == 'kup':
                parsed_list.append(f"""_ksfAttr_.put("", _ret);""")
                parsed_list.append(f"""_ksfAttr_.put("ksf_ret", _ret);""")
            elif mode == 'json':
                parsed_list.append(f"""_p->value["ksf_ret"] = ksf::json::Output::writeJson(_ret);""")

        for name in operator.output:
            var = operator.output[name]
            if mode == 'ksf':
                parsed_list.append(f"""_os.write({name}, {var.index});""")
            elif mode == 'kup':
                parsed_list.append(f"""_ksfAttr_.put("{name}", {name});""")
            elif mode == 'json':
                parsed_list.append(f"""_p->value["{name}"] = ksf::json::Output::writeJson({name});""")

        return parsed_list

    def parse_OperatorAllVars(self,
                              index,
                              operator: KsfOperator,
                              with_input=False):
        parsed_list = []
        if not with_input and operator.has_return():
            parsed_list.append(f"const {self.parse_type(operator.return_type)} &_ret")

        for var_name, is_output in operator.ordered_var:
            if is_output:
                if with_input:
                    parsed_list.append(
                        f"{self.parse_type(operator.output[var_name].value_type)} &{var_name}"
                    )
                else:
                    parsed_list.append(
                        f"const {self.parse_type(operator.output[var_name].value_type)} &{var_name}"
                    )
            elif with_input:
                if self.is_movable_type(operator.input[var_name].value_type):
                    if self.with_rvalue_ref:
                        parsed_list.append(
                            f"{self.parse_type(operator.input[var_name].value_type)} &&{var_name}"
                        )
                    else:
                        parsed_list.append(
                            f"const {self.parse_type(operator.input[var_name].value_type)} &{var_name}"
                        )
                else:
                    parsed_list.append(
                        f"{self.parse_type(operator.input[var_name].value_type)} {var_name}"
                    )

        return parsed_list

    def parse_InterfaceObjModule(self,
                                 ksf_interface: KsfInterface):
        dispatch_list = []

        virtual_func_list = []
        async_func_list = []
        push_func_list = []
        dispatch_case_list = []

        def parse_Operator(index,
                           operator):
            async_case = []
            push_func_case = []
            # 当这个方法是异步方法时，需要生成一个同步方法纯虚函数和一个异步方法回调
            if self.enable_async_rsp(f"{self.curr_module}.{ksf_interface.name}.{operator.name}"):
                # 生成同步方法纯虚函数
                comment = self.parse_comment_above(operator.comment)
                return_type = self.parse_type(operator.return_type) if operator.has_return() else 'void'
                arguments = self.parse_OperatorAllVars(index,
                                                       operator,
                                                       True)
                virtual_func_list.append(fstr(template_server_pure_function,
                                              comment=comment,
                                              return_type=return_type,
                                              function_name=operator.name,
                                              arguments=arguments,
                                              argument_current='ksf::KsfCurrentPtr _current_'
                                              )
                                         )
                # 增加kup支持
                async_case.append(fstr(template_server_async_response_case_kup,
                                       arguments=self.parse_OperatorOutputVar(index,
                                                                              operator,
                                                                              mode='kup'
                                                                              )
                                       )
                                  )

                # 增加json支持，当有json解析方法时
                if self.with_json:
                    async_case.append(fstr(template_server_async_response_case_json,
                                           arguments=self.parse_OperatorOutputVar(index,
                                                                                  operator,
                                                                                  mode='json'
                                                                                  )
                                           )
                                      )

                async_case.append(fstr(template_server_async_response_case_ksf,
                                       arguments=self.parse_OperatorOutputVar(index,
                                                                              operator,
                                                                              mode='ksf'
                                                                              )
                                       )
                                  )

                # 链路追踪
                if self.with_trace:
                    if not self.with_json:
                        raise SyntaxError("如果需要链路追踪，需要打开生成Json序列化支持(--json)")

                    return_type = '_p_->value[""] = ksf::json::Output::writeJson(_ret);' if operator.has_return() else ''
                    async_func_list.append(fstr(template_server_async_response_trace,
                                                return_type=return_type,
                                                function_name=operator.name
                                                )
                                           )
                # 生成异步方法回调
                async_func_list.append(fstr(template_server_async_function,
                                            function_name=operator.name,
                                            arguments=self.parse_OperatorAllVars(index,
                                                                                 operator),
                                            argument_current='ksf::KsfCurrentPtr _current_',
                                            async_response_case=async_case,
                                            )
                                       )

            # 如果方法为推送方法，需要生成一个推送方法的推送应答
            if self.enable_push(f"{self.curr_module}.{ksf_interface.name}.{operator.name}"):
                dispatch_case_list.append(f"""    case {index}: return ksf::KSFSERVERNOFUNCERR;""")
            else:
                # 填充
                # case, variable_declare,
                # request_version_kup, request_version_json, request_version_ksf,
                # return_type, operator_name, operator_params
                # response_version_kup, response_version_json, response_version_ksf
                dispatch_case_list.append(self.add_lines(
                    fstr(template_dispatch_case_at_server,
                         case=index,
                         variable_declare=self.parse_OperatorVarlist(
                             index,
                             operator
                         ),
                         request_version_kup=self.parse_OperatorParamsList(
                             operator,
                             mode='kup'
                         ),
                         request_version_json=self.parse_OperatorParamsList(
                             operator,
                             mode='json'
                         ),
                         request_version_ksf=self.parse_OperatorParamsList(
                             operator,
                             mode='ksf'
                         ),
                         return_type=f'{self.parse_type(operator.return_type)} _ret = ' if operator.has_return() else '',
                         function_name=operator.name,
                         operator_params=self.parse_OperatorInvokeVars(
                             index,
                             operator
                         ),
                         response_version_kup=self.parse_OperatorOutputVar(
                             index,
                             operator,
                             mode='kup'
                         ),
                         response_version_json=self.parse_OperatorOutputVar(
                             index,
                             operator,
                             mode='json'
                         ),
                         response_version_ksf=self.parse_OperatorOutputVar(
                             index,
                             operator,
                             mode='ksf'
                         )
                         ),
                    1
                )
                )

            if self.with_push and self.enable_push(f"{self.curr_module}.{ksf_interface.name}.{operator.name}"):
                push_func_case.append(fstr(template_server_push_function_ksf,
                                           function_name=operator.name,
                                           arguments=self.parse_OperatorOutputVar(index,
                                                                                  operator,
                                                                                  mode='ksf'
                                                                                  ), )
                                      )

                arguments = self.parse_OperatorAllVars(index,
                                                       operator)
                push_func_list.append(fstr(template_server_push_function,
                                           function_name=operator.name,
                                           arguments=arguments,
                                           argument_request_context=f'const _Context_ &_context_ = _Context_()',
                                           argument_current='ksf::KsfCurrentPtr _current_',
                                           push_func_case=push_func_case, )
                                      )

        def dispatch(function_names):
            if self.dispatch_mode == 'array':
                dispatch_list.append(
                    fstr(template_array_style_onDispatch_at_server,
                         interface_name=ksf_interface.name,
                         function_names=function_names,
                         dispatch_case_str=self.add_lines(dispatch_case_list,
                                                          1)
                         )
                )
            elif self.dispatch_mode == 'set':
                dispatch_list.append(
                    fstr(template_set_style_onDispatch_at_server,
                         interface_name=ksf_interface.name,
                         function_names=function_names,
                         dispatch_case_str=self.add_lines(dispatch_case_list,
                                                          1)
                         )
                )
            elif self.dispatch_mode == 'hash':
                dispatch_list.append(
                    fstr(template_hash_style_onDispatch_at_server,
                         interface_name=ksf_interface.name,
                         function_names=function_names,
                         dispatch_case_str=self.add_lines(dispatch_case_list,
                                                          1)
                         )
                )

        self.parse_DispatchOperatorCallBack(ksf_interface,
                                            dispatch,
                                            parse_Operator)

        return dispatch_list, virtual_func_list, async_func_list, push_func_list

    def parse_InterfaceObj(self,
                           ksf_interface: KsfInterface):
        dispatch, virtual_func, parsed_async_list, parsed_push_list = self.parse_InterfaceObjModule(ksf_interface)
        return fstr(template_server_interface,
                    interface_name=ksf_interface.name,
                    functions=virtual_func,
                    async_functions=parsed_async_list,
                    push_functions=parsed_push_list,
                    dispatch=dispatch,
                    )

    def parse_interface(self,
                        ksf_interface: KsfInterface):
        interface_declare = []

        if self.with_invoke_client:
            self.add_include("servant/Agent.h")
            interface_declare.append(self.add_lines(self.parse_InterfacePrxCallBack(ksf_interface)))
            if self.with_promise:
                self.add_include("promise/promise.h")
                interface_declare.append(self.parse_InterfacePrxCallbackPromise(ksf_interface))

            if self.with_coroutine:
                interface_declare.append(self.parse_InterfaceCoroPrxCallback(ksf_interface))

            interface_declare.append(self.parse_InterfaceProxy(ksf_interface))

        if self.with_invoke_server:
            self.add_include("servant/Servant.h")
            interface_declare.append(self.parse_InterfaceObj(ksf_interface))

        return interface_declare

    def generate(self):
        self.curr_module = None
        module_declares = []
        # 生成头文件（需要判断是否忽略路径)
        for input_file in self.input_file:
            for inc, inc_file_name in input_file.includes:
                if self.with_ignore_relative_path:
                    self.add_include(f'"{inc.name[:-4]}.h"')
                else:
                    self.add_include(self.get_repl_headfile(f'"{inc_file_name[:-4]}.h"'))

            element_declares = []  # 用于存放每个模块的元素内容

            for ele in input_file.elements:
                # 生成命名空间
                if self.curr_module is None:
                    self.curr_module = ele.module
                elif self.curr_module != ele.module:
                    module_declares.append(fstr(template_namespace,
                                                module_begin=self.get_ns_begin(),
                                                module_end=self.get_ns_end(),
                                                elements=element_declares
                                                )
                                           )
                    self.curr_module = ele.module

                if isinstance(ele,
                              KsfConst):
                    element_declares.append(self.parse_const(ele))
                    pass
                elif isinstance(ele,
                                KsfEnum):
                    element_declares.append(self.parse_enum(ele))
                    pass
                elif isinstance(ele,
                                KsfStruct):
                    element_declares.append(self.parse_struct(ele))
                    pass
                elif isinstance(ele,
                                KsfInterface) and self.with_rpc:
                    element_declares.append(self.parse_interface(ele))

            if self.curr_module is not None:
                module_declares.append(fstr(template_namespace,
                                            module_begin=self.get_ns_begin(self.curr_module),
                                            module_end=self.get_ns_end(self.curr_module),
                                            elements=element_declares
                                            )
                                       )
                self.curr_module = None

        header_content = fstr(template_header,
                              header_description=fstr(template_header_description,
                                                      file_name=self.output_file.name,
                                                      date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                      version="1.0.0",
                                                      ),
                              import_headers=self.parse_header(with_ksf=True),
                              namespaces=module_declares
                              )

        with self.output_file.open("w") as f:
            f.write(header_content)

    def generate_text(self, modules, with_ksf=False, with_servant=False, includes=[]):
        module_declares = []
        self.curr_module = None
        element_declares = []

        for include in includes:
            self.add_include(include)

        for module, element_declare in modules:
            if self.curr_module is not None and self.curr_module != module:
                module_declares.append(fstr(template_namespace,
                                            module_begin=self.get_ns_begin(self.curr_module),
                                            module_end=self.get_ns_end(self.curr_module),
                                            elements=element_declares
                                            )
                                       )
                element_declares = []

            self.curr_module = module

            element_declares.append(element_declare)

        if self.curr_module is not None:
            module_declares.append(fstr(template_namespace,
                                        module_begin=self.get_ns_begin(self.curr_module),
                                        module_end=self.get_ns_end(self.curr_module),
                                        elements=element_declares
                                        )
                                   )
            self.curr_module = None

        return fstr(template_header,
                    header_description=fstr(template_header_description,
                                            file_name=self.output_file.name,
                                            date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                            version="1.0.0",
                                            ),
                    import_headers=self.parse_header(with_ksf=with_ksf, with_servant=with_servant),
                    namespaces=module_declares
                    )

    def generate_all(self,
                     is_seperate=False):
        # TODO 调用分离模式，将调用和结构体分离
        self.curr_module = None
        const_list = []
        enum_list = []
        struct_list = []
        interface_list = []
        module_declares = []

        for sym in self.ast.get_all_export_symbol():
            ele = self.ast.all_element.obj[sym]
            self.curr_module = ele.module

            if isinstance(ele,
                          KsfConst):
                const_list.append((ele.module, self.parse_const(ele)))
            elif isinstance(ele,
                            KsfEnum):
                enum_list.append((ele.module, self.parse_enum(ele)))
            elif isinstance(ele,
                            KsfStruct):
                struct_list.append((ele.module, self.parse_struct(ele)))
            elif isinstance(ele,
                            KsfInterface) and self.with_rpc:
                interface_list.append((ele.module, self.parse_interface(ele)))

        # 生成头文件（需要判断是否忽略路径)
        if is_seperate:
            data_list = const_list + enum_list + struct_list
            if data_list:
                header_content = self.generate_text(data_list, with_ksf=True, with_servant=False)
                with self.output_file.open("w") as f:
                    f.write(header_content)

            if interface_list:
                header_content = self.generate_text(interface_list,
                                                    with_ksf=True,
                                                    with_servant=True,
                                                    includes=[self.output_file.name])
                with self.invoke_file.open("w") as f:
                    f.write(header_content)
        else:
            header_content = self.generate_text(const_list + enum_list + struct_list + interface_list,
                                                with_ksf=True,
                                                with_servant=True)

            with self.output_file.open("w") as f:
                f.write(header_content)


#############################################################################################################


class CppSdkGenerator(CppParser):
    def __init__(self,
                 ast,
                 repl_ns_dict,
                 repl_inc_dir,
                 destination,
                 push_functions,
                 export_symbols,
                 invoke,
                 export,
                 **kwargs
                 ):
        super().__init__(ast,
                         repl_ns_dict,
                         repl_inc_dir,
                         destination,
                         push_functions,
                         export_symbols,
                         **kwargs)
        self.sdk_invoke = Path(destination) / invoke  # 生成的纯rpc头文件
        self.sdk_export = Path(destination) / export  # 生成的纯结构体头文件

    def parse_enum_pure(self,
                        ksf_enum: KsfEnum):
        enum_members = []
        for m in ksf_enum.member:
            enum_members.append(self.parse_enum_member(m))

        return fstr(template_enum,
                    comment=self.parse_comment_above(ksf_enum.comment),
                    enum_name=ksf_enum.name,
                    enum_members=enum_members,
                    )

    def parse_enum_func(self,
                        ksf_enum: KsfEnum):
        function_etos = []
        function_stoe = []
        for m in ksf_enum.member:
            function_etos.append(self.parse_enum_to_str(m,
                                                        True))
            function_stoe.append(self.parse_str_to_enum(m,
                                                        True))

        return [fstr(template_etos,
                     enum_name=ksf_enum.name,
                     etos_member=function_etos),
                fstr(template_stoe,
                     enum_name=ksf_enum.name,
                     stoe_member=function_stoe)]

    def parse_resetDefault(self,
                           ksf_struct: KsfStruct):
        return fstr(template_resetDefault,
                    struct_name=ksf_struct.name, )

    def parse_variable_writeTo(self,
                               ksf_field: KsfField):
        value_type = ksf_field.value_type
        if self.with_check_default and not ksf_field.is_required:
            if isinstance(value_type,
                          KsfBuildInType):
                if isinstance(value_type,
                              KsfBoolType):
                    check_default = f"""{'!' if not ksf_field.has_default() or ksf_field.default['value'] else ''}obj.{ksf_field.name}"""
                else:
                    check_default = self.parse_default_var(f'obj.{ksf_field.name}',
                                                           value_type,
                                                           ksf_field.default,
                                                           is_equal=False
                                                           )
            elif isinstance(value_type,
                            KsfStructType):
                return fstr(template_writeTo_variable,
                            variable_name=f'obj.{ksf_field.name}',
                            variable_tag=ksf_field.tag, )
            elif isinstance(value_type,
                            KsfEnumType):
                module_name = f"{value_type.module}::" if self.curr_module != value_type.module else ""

                # 如果是枚举类型
                if ksf_field.has_default():
                    # 有枚举默认值的，使用默认值
                    check_default = f"""obj.{ksf_field.name} != {module_name}{value_type.name}::{ksf_field.default['value']}"""
                else:
                    # 没有默认值的，使用第一个枚举值
                    check_default = f"""obj.{ksf_field.name} != {module_name}{value_type.name}::{ksf_field.value_type.obj_type.member[0].name}"""
            elif isinstance(value_type,
                            KsfVectorType):
                check_default = f"""!obj.{ksf_field.name}.empty()"""
            elif isinstance(value_type,
                            KsfMapType):
                check_default = f"""!obj.{ksf_field.name}.empty()"""
            else:
                raise SyntaxError(f"不能被解析的字段类型[{value_type}]")

            return fstr(template_writeTo_variable_with_check,
                        check_default=check_default,
                        variable_declare=fstr(template_writeTo_variable,
                                              variable_name=f'obj.{ksf_field.name}',
                                              variable_tag=ksf_field.tag, ),
                        )
        else:
            return fstr(template_writeTo_variable,
                        variable_name=f'obj.{ksf_field.name}',
                        variable_tag=ksf_field.tag, )

    def parse_writeTo(self,
                      ksf_struct: KsfStruct):
        var_list = []
        for var in ksf_struct.variable:
            var_list.append(self.parse_variable_writeTo(ksf_struct.variable[var]))
        return fstr(template_writeTo,
                    variables=var_list)

    def parse_variable_writeToJson(self,
                                   ksf_field: KsfField):
        return f"""p->value["{ksf_field.name}"] = ksf::json::Output::writeJson(obj.{ksf_field.name});"""

    def parse_writeToJson(self,
                          ksf_struct: KsfStruct):
        var_list = []
        for var in ksf_struct.variable.values():
            var_list.append(self.parse_variable_writeToJson(var))

        return fstr(template_writeToJson,
                    variables=var_list)

    def parse_variable_readFrom(self,
                                ksf_field: KsfField):
        return f"""_is.read(obj.{ksf_field.name}, {ksf_field.tag}, false);"""

    def parse_readFrom(self,
                       ksf_struct: KsfStruct):
        var_list = []
        for var in ksf_struct.variable:
            var_list.append(self.parse_variable_readFrom(ksf_struct.variable[var]))

        return fstr(template_readFrom,
                    variables=var_list,
                    is_wrap=True)

    def parse_variable_readFromJson(self,
                                    ksf_field: KsfField):
        return f"""ksf::json::Input::readJson(obj.{ksf_field.name}, pObj->value["{ksf_field.name}"], false);"""

    def parse_readFromJson(self,
                           ksf_struct: KsfStruct):
        var_list = []
        for var in ksf_struct.variable:
            var_list.append(self.parse_variable_readFromJson(ksf_struct.variable[var]))

        return fstr(template_readFromJson,
                    variables=var_list,
                    is_wrap=True)

    def parse_display(self,
                      ksf_struct: KsfStruct):
        var_list = []
        for field in ksf_struct.variable.values():
            if isinstance(field.value_type,
                          KsfEnumType):
                var_list.append(f'_ds.display(static_cast<int32_t>(obj.{field.name}), "{field.name}");')
            else:
                var_list.append(f'_ds.display(obj.{field.name}, "{field.name}");')

        return fstr(template_display,
                    variables=var_list)

    def parse_displaySimple(self,
                            ksf_struct: KsfStruct):
        var_list = []
        for field in ksf_struct.variable.values():
            if isinstance(field.value_type,
                          KsfEnumType):
                var_list.append(f'_ds.displaySimple(static_cast<int32_t>(obj.{field.name}), true);')
            else:
                var_list.append(f'_ds.displaySimple(obj.{field.name}, true);')

        return fstr(template_displaySimple,
                    variables=var_list)

    def parse_equal(self,
                    ksf_struct: KsfStruct):
        var_list = []
        for var in ksf_struct.variable:
            field = ksf_struct.variable[var]
            if isinstance(field.value_type,
                          KsfFloatType):
                var_list.append(f'ksf::KS_Common::equal(l.{field.name}, r.{field.name})')
            else:
                var_list.append(f'l.{field.name} == r.{field.name}')

        return fstr(template_operator_equal,
                    variables=var_list,
                    struct_name=self.get_full_name(self.curr_module,
                                                   ksf_struct.name)
                    )

    def parse_struct_pure(self,
                          ksf_struct: KsfStruct):
        variables = []
        # 解析字段
        var_list = []
        for var in ksf_struct.variable:
            var_list.append(self.parse_variable(ksf_struct.variable[var]))

        var_widths = self.get_column_widths(var_list)
        for comment, var_type, var_name, var_value in var_list:
            if comment:
                variables.append(f"{comment:<{var_widths[0]}}")
            variables.append(f"{var_type:<{var_widths[1]}} {var_name:<{var_widths[2]}}{var_value}")
        return fstr(template_struct_export,
                    comment=self.parse_comment_above(ksf_struct.comment),
                    struct_name=ksf_struct.name,
                    variables=variables,
                    struct_functions=[self.parse_resetDefault(ksf_struct)]
                    )

    def parse_struct_wrap(self,
                          ksf_struct: KsfStruct):
        full_struct_name = self.get_full_name(ksf_struct.module,
                                              ksf_struct.name)
        struct_functions = [
            self.parse_writeTo(ksf_struct),
            self.parse_readFrom(ksf_struct),
        ]
        struct_operators = [
            self.parse_equal(ksf_struct),

        ]

        if self.with_json:
            self.add_include("ksf/proto/json.h")
            struct_functions.append(self.parse_writeToJson(ksf_struct))  # writeToJson
            struct_functions.append(self.parse_readFromJson(ksf_struct))  # readFromJson

        self.add_include("ostream")
        struct_functions.append(self.parse_display(ksf_struct))  # display
        struct_functions.append(self.parse_displaySimple(ksf_struct))  # displaySimple

        if len(ksf_struct.key_fields) != 0:
            key_variables = []
            for key_field in ksf_struct.key_fields:
                key_variables.append(f'if(l.{key_field} != r.{key_field})  return (l.{key_field} < r.{key_field});')
            struct_operators.append(fstr(template_operator_compare,
                                         struct_name=full_struct_name,
                                         variables=key_variables
                                         )
                                    )

        if self.with_json:
            self.add_include("ksf/proto/json.h")
            # export
            struct_operators.append(fstr(template_operator_stream_with_json,
                                         wrap_mode=True,
                                         struct_name=full_struct_name
                                         )
                                    )

            # wrap
            struct_operators.append(fstr(template_operator_stream_with_json,
                                         wrap_mode=False,
                                         struct_name=f'{full_struct_name}Wrap'
                                         )
                                    )

        return fstr(template_struct_wrap,
                    module_name=self.curr_module,
                    struct_name_without_namespace=ksf_struct.name,
                    struct_name=full_struct_name,
                    md5sum=md5(ksf_struct.id.encode('utf8')).hexdigest(),
                    struct_functions=struct_functions,
                    struct_operators=struct_operators,
                    namespace_left=self.get_ns_begin(self.curr_module),
                    namespace_right=self.get_ns_end(self.curr_module),
                    )

    def parse_InterfacePrxCallBack(self,
                                   ksf_interface: KsfInterface):
        func_case_list = []
        function_handles = []
        dispatch_str = []

        def parse_func_dispatch(index,
                                operator):
            """处理函数的分发"""
            output_args = []

            if operator.has_return():
                output_args.append(fstr(template_output_argument_parse,
                                        typename=self.parse_type(operator.return_type,
                                                                 is_wrap=True),
                                        argument_name='_ret',
                                        index=0
                                        )
                                   )

            for var in operator.output.values():
                output_args.append(fstr(template_output_argument_parse,
                                        typename=self.parse_type(var.value_type,
                                                                 is_wrap=True),
                                        argument_name=var.name,
                                        index=var.index
                                        )
                                   )

            func_case_list.append(fstr(template_dispatch_case_at_client,
                                       case=index,
                                       function_name=f'{operator.name}Wrap',
                                       output_params=self.parse_output_vars(operator,
                                                                            False),
                                       output_arguments=output_args
                                       )
                                  )

            function_handles.append(fstr(template_function_call,
                                         function_name=f'{operator.name}Wrap',
                                         arguments=self.parse_output_vars(operator,
                                                                          True)
                                         )
                                    )

        get_response_context = template_getResponseContext

        def dispatch(function_names):
            dispatch_str.append(fstr(template_array_style_onDispatch_at_client,
                                     dispatch_case_str=func_case_list,
                                     interface_name=f'{ksf_interface.name}Wrap',
                                     function_names=function_names
                                     )
                                )

        self.parse_DispatchOperatorCallBack(ksf_interface,
                                            dispatch,
                                            parse_func_dispatch)

        return fstr(template_callback,
                    interface_name=f'{ksf_interface.name}Wrap',
                    function_handles=function_handles,
                    get_response_context=get_response_context,
                    dispatch_str=dispatch_str
                    )

    def parse_InterfacePrxCallbackPromise(self,
                                          ksf_interface: KsfInterface):
        parsed_str = f"""\
class {ksf_interface.name}WrapPrxCallbackPromise: public ksf::AgentCallback
{{
public:
    virtual ~{ksf_interface.name}WrapPrxCallbackPromise() = default;
\n"""

        dispatch_case_str = ""
        case_index = 0
        for item in ksf_interface.operator:
            operator = ksf_interface.operator[item]
            if not operator.export:
                continue

            parsed_str += f"""\
public:
    struct Promise{operator.name}: virtual public KS_HandleBase 
    {{
    public:
        std::map<std::string, std::string> _mRspContext;\n"""

            if operator.return_type['name'] != 'void':
                parsed_str += f"\
        {self.parse_type(operator.return_type, is_wrap=True)} _ret;\n"

            for item in operator.output:
                var = operator.output[item]
                parsed_str += f"\
        {self.parse_type(var.value_type, is_wrap=True)} {var.name};\n"

            parsed_str += f"""\
    }};

    using Promise{operator.name}Ptr = ksf::KS_AutoPtr<{ksf_interface.name}WrapPrxCallbackPromise::Promise{operator.name}>;

    {ksf_interface.name}WrapPrxCallbackPromise(const ksf::Promise<{ksf_interface.name}WrapPrxCallbackPromise::Promise{operator.name}Ptr> &promise): _promise_{operator.name}(promise) {{}}

    virtual void callback_{operator.name}Wrap(const {ksf_interface.name}WrapPrxCallbackPromise::Promise{operator.name}Ptr &ptr) {{
        _promise_{operator.name}.setValue(ptr);
    }}

    virtual void callback_{operator.name}Wrap_exception(ksf::Int32 ret) {{
        std::stringstream oss;
        oss << "Function:{operator.name}Wrap_exception|Ret:";
        oss << ret;
        _promise_{operator.name}.setException(ksf::copyException(oss.str(), ret));
    }}

protected:
    ksf::Promise<{ksf_interface.name}WrapPrxCallbackPromise::Promise{operator.name}Ptr > _promise_{operator.name};\n\n"""

            def parse_var_dispatch(var,
                                   name,
                                   index):
                if var['name'] == 'void':
                    return ""

                return f"""\
                    _is.read(ptr->{name}, {index}, true);\n"""

            def parse_func_dispatch():
                """处理函数的分发"""
                func_case_str = f"""\
            case {case_index}: {{
                if (msg->response->iRet != ksf::KSFSERVERSUCCESS) {{
                    callback_{operator.name}Wrap_exception(msg->response->iRet);
                    return msg->response->iRet;
                }}

                ksf::KsfInputStream<ksf::BufferReader> _is;
                _is.setBuffer(msg->response->sBuffer);
                {ksf_interface.name}WrapPrxCallbackPromise::Promise{operator.name}Ptr ptr = new {ksf_interface.name}WrapPrxCallbackPromise::Promise{operator.name}();

                try {{\n"""

                func_case_list = []
                ret = parse_var_dispatch(operator.return_type,
                                         '_ret',
                                         0)
                if ret != "":
                    func_case_list.append(ret)

                for item2 in operator.output:
                    var2 = operator.output[item2]
                    func_case_list.append(parse_var_dispatch(var2.value_type,
                                                             var2.name,
                                                             var2.index))

                func_case_str += ''.join(func_case_list)
                return func_case_str

            case_index += 1
            dispatch_case_str += parse_func_dispatch()
            dispatch_case_str += f"""\
                }} catch (std::exception &ex) {{
                    callback_{operator.name}Wrap_exception(ksf::KSFCLIENTDECODEERR);
                    return ksf::KSFCLIENTDECODEERR;
                }} catch (...) {{
                    callback_{operator.name}Wrap_exception(ksf::KSFCLIENTDECODEERR);
                    return ksf::KSFCLIENTDECODEERR;
                }}

                ptr->_mRspContext = msg->response->context;
                callback_{operator.name}Wrap(ptr);
                return ksf::KSFSERVERSUCCESS;
            }}\n"""

        parsed_str += f"""\
public:
    int onDispatch(ksf::ReqMessagePtr msg) override
    {{
        static std::string __{ksf_interface.name}_all[] = {{"{'", "'.join(ksf_interface.operator.keys())}"}};

        std::pair<std::string *, std::string *> r = equal_range(__{ksf_interface.name}_all, __{ksf_interface.name}_all + {len(ksf_interface.operator.keys())}, std::string(msg->request.sFuncName));

        if (r.first == r.second) {{
            return ksf::KSFSERVERNOFUNCERR;
        }}

        switch (r.first - __{ksf_interface.name}_all) {{\n"""
        parsed_str += dispatch_case_str
        parsed_str += f"""\
        }} //end switch

        return ksf::KSFSERVERNOFUNCERR;
    }} //end onDispatch\n"""

        parsed_str += f"\n}}; //end {ksf_interface.name}WrapPrxCallbackPromise\n\n" \
                      f"using {ksf_interface.name}WrapPrxCallbackPromisePtr = ksf::KS_AutoPtr<{ksf_interface.name}WrapPrxCallbackPromise>;\n" \
                      f"\n"
        return parsed_str

    def parse_InterfaceCoroPrxCallback(self,
                                       ksf_interface: KsfInterface):
        def parse_var_dispatch(var,
                               name,
                               index):
            if var['name'] == 'void':
                return ""

            return f"""\
                    {self.parse_type(var)} {name};
                    _is.read({name}, {index}, true);\n\n"""

        def parse_func_dispatch():
            """处理函数的分发"""
            func_case_str = ""
            index = 0
            for item in ksf_interface.operator:
                operator = ksf_interface.operator[item]
                if not operator.export:
                    index += 1
                    continue

                def parse_output_vars(with_type=True):
                    def parse_output_var(value_type,
                                         name,
                                         with_type):
                        if value_type.name != 'void':
                            if not self.is_movable_type(value_type):
                                return f"{self.parse_type(value_type)} {name}" if with_type else name
                            elif self.with_rvalue_ref:
                                return f"{self.parse_type(value_type)} &&{name}" if with_type else f"std::move({name})"
                            else:
                                return f"const {self.parse_type(value_type)} &{name}" if with_type else name

                    vars_list = []
                    if operator.return_type.name != 'void':
                        vars_list.append(parse_output_var(operator.return_type,
                                                          '_ret',
                                                          with_type))

                    for item in operator.output:
                        vars_list.append(
                            parse_output_var(operator.output[item].value_type,
                                             operator.output[item].name,
                                             with_type)
                        )

                    return ', '.join(vars_list)

                func_case_str += f"""
            case {index}: {{
                if (msg->response->iRet != ksf::KSFSERVERSUCCESS) {{
                    callback_{operator.name}Wrap_exception(msg->response->iRet);
                    return msg->response->iRet;
                }}

                ksf::KsfInputStream<ksf::BufferReader> _is;
                _is.setBuffer(msg->response->sBuffer);

                try {{\n"""
                func_case_list = []
                ret = parse_var_dispatch(operator.return_type,
                                         '_ret',
                                         0)
                if ret != "":
                    func_case_list.append(ret)

                for item2 in operator.output:
                    var2 = operator.output[item2]
                    func_case_list.append(parse_var_dispatch(var2.value_type,
                                                             var2.name,
                                                             var2.index))

                func_case_str += ''.join(func_case_list)

                func_case_str += f"""\
                    callback_{operator.name}Wrap({parse_output_vars(with_type=False)});
                }} catch (std::exception &ex) {{
                    callback_{operator.name}Wrap_exception(ksf::KSFCLIENTDECODEERR);
                    return ksf::KSFCLIENTDECODEERR;
                }} catch (...) {{
                    callback_{operator.name}Wrap_exception(ksf::KSFCLIENTDECODEERR);
                    return ksf::KSFCLIENTDECODEERR;
                }}

                return ksf::KSFSERVERSUCCESS;
            }}\n"""

                index += 1

            return func_case_str

        parsed_str = f"""\
class {ksf_interface.name}WrapCoroPrxCallback : public {ksf_interface.name}WrapPrxCallback
{{
public:
    virtual ~{ksf_interface.name}WrapCoroPrxCallback() = default;

public:
    const std::map<std::string, std::string> &getResponseContext() const override {{ return _mRspContext; }}

    virtual void setResponseContext(const std::map<std::string, std::string> &mContext) {{ _mRspContext = mContext; }}
"""
        parsed_str += f"""\
public:
    int onDispatch(ksf::ReqMessagePtr msg) override
    {{
        static std::string __{ksf_interface.name}_all[] = {{"{'", "'.join(ksf_interface.operator.keys())}"}};

        std::pair<std::string *, std::string *> r = equal_range(__{ksf_interface.name}_all, __{ksf_interface.name}_all + {len(ksf_interface.operator.keys())}, std::string(msg->request.sFuncName));

        if (r.first == r.second) {{
            return ksf::KSFSERVERNOFUNCERR;
        }}

        switch (r.first - __{ksf_interface.name}_all) {{
{parse_func_dispatch()}
        }} //end switch

        return ksf::KSFSERVERNOFUNCERR;
    }} //end onDispatch

protected:
    std::map<std::string, std::string> _mRspContext;
}}; //end {ksf_interface.name}WrapCoroPrxCallback

using {ksf_interface.name}WrapCoroPrxCallbackPtr = ksf::KS_AutoPtr<{ksf_interface.name}WrapCoroPrxCallback>;\n\n"""
        return parsed_str

    def parse_InterfaceProxy(self,
                             ksf_interface: KsfInterface):
        def parse_operators():
            parsed_oper_str = ""
            for item in ksf_interface.operator:
                operator = ksf_interface.operator[item]
                if not operator.export:
                    continue

                def parse_input_vars():
                    parsed_list = []
                    for name in operator.input:
                        var = operator.input[name]
                        parsed_list.append(f"""\
        _os.write({name}, {var.index});\n"""
                                           )
                    return parsed_list

                def parse_output_vars():
                    parsed_list = []
                    if operator.return_type['name'] != 'void':
                        parsed_list.append(f"""\
        {self.parse_type(operator.return_type, is_wrap=True)} _ret;
        _is.read(_ret, 0, true);\n"""
                                           )

                    for name in operator.output:
                        var = operator.output[name]
                        parsed_list.append(f"""\
        _is.read({name}, {var.index}, true);\n"""
                                           )
                    return parsed_list

                def parse_all_vars(with_output=False):
                    parsed_list = []
                    for var_name, is_output in operator.ordered_var:
                        if is_output:
                            if with_output:
                                parsed_list.append(
                                    f"{self.parse_type(operator.output[var_name].value_type, is_wrap=True)} &{var_name}, "
                                )
                        else:
                            parsed_list.append(
                                f"const {self.parse_type(operator.input[var_name].value_type, is_wrap=True)} &{var_name}, "
                            )

                    return parsed_list

                parsed_oper_str += f"""\
public:
{self.parse_comment_above(operator.comment, tab='    ')}\
    {self.parse_type(operator.return_type, is_wrap=True) if operator.has_return() else 'void'} {operator.name}({''.join(parse_all_vars(True))}const std::map<std::string, std::string> &mapReqContext = {{}}, std::map<std::string, std::string> *pResponseContext = NULL) {{
        ksf::KsfOutputStream<ksf::BufferWriterVector> _os;
{''.join(parse_input_vars())}
        std::map<std::string, std::string>   _mStatus;
        std::shared_ptr<ksf::ResponsePacket> rep = ksf_invoke(ksf::KSFNORMAL, "{operator.name}", _os, mapReqContext, _mStatus);
        if (pResponseContext) {{
            pResponseContext->swap(rep->context);
        }}

        ksf::KsfInputStream<ksf::BufferReader> _is;
        _is.setBuffer(rep->sBuffer);
{''.join(parse_output_vars())}
{f'''        return _ret;
    }}''' if operator.has_return() else '    }'}

    void async_{operator.name}({ksf_interface.name}WrapPrxCallbackPtr callback, {''.join(parse_all_vars())}const std::map<std::string, std::string> &context = {{}}) {{
        ksf::KsfOutputStream<ksf::BufferWriterVector> _os;
{''.join(parse_input_vars())}
        std::map<std::string, std::string> _mStatus;
        ksf_invoke_async(ksf::KSFNORMAL, "{operator.name}", _os, context, _mStatus, callback);
    }}

    ksf::Future<{ksf_interface.name}WrapPrxCallbackPromise::Promise{operator.name}Ptr> promise_async_{operator.name}({''.join(parse_all_vars())}const std::map<std::string, std::string> &context) {{
        ksf::Promise<{ksf_interface.name}WrapPrxCallbackPromise::Promise{operator.name}Ptr> promise;
        {ksf_interface.name}WrapPrxCallbackPromisePtr callback = new {ksf_interface.name}WrapPrxCallbackPromise(promise);

        ksf::KsfOutputStream<ksf::BufferWriterVector> _os;
{''.join(parse_input_vars())}
        std::map<std::string, std::string> _mStatus;
        ksf_invoke_async(ksf::KSFNORMAL, "{operator.name}", _os, context, _mStatus, callback);

        return promise.getFuture();
    }}

    void coro_{operator.name}({ksf_interface.name}WrapCoroPrxCallbackPtr callback, {''.join(parse_all_vars())}const std::map<std::string, std::string> &context = {{}}) {{
        ksf::KsfOutputStream<ksf::BufferWriterVector> _os;
{''.join(parse_input_vars())}
        std::map<std::string, std::string>            _mStatus;
        ksf_invoke_async(ksf::KSFNORMAL, "{operator.name}", _os, context, _mStatus, callback, true);
    }}\n\n"""
            return parsed_oper_str

        parsed_str = f"""\
class {ksf_interface.name}WrapProxy : public ksf::Agent
{{
public:
    {ksf_interface.name}WrapProxy* ksf_hash(uint32_t key) {{
        return ({ksf_interface.name}WrapProxy*)Agent::ksf_hash(key);
    }}

    {ksf_interface.name}WrapProxy* ksf_consistent_hash(uint32_t key) {{
        return ({ksf_interface.name}WrapProxy*)Agent::ksf_consistent_hash(key);
    }}

    {ksf_interface.name}WrapProxy* ksf_open_trace(bool traceParam = false) {{
        return ({ksf_interface.name}WrapProxy*)Agent::ksf_open_trace(traceParam);
    }}

    {ksf_interface.name}WrapProxy* ksf_set_timeout(int32_t ms) {{
        return ({ksf_interface.name}WrapProxy*)Agent::ksf_set_timeout(ms);
    }}

    static const char* ksf_prxname() {{ return "{ksf_interface.name}WrapProxy"; }}

{parse_operators()}
}}; //end {ksf_interface.name}WrapProxy

using {ksf_interface.name}WrapPrx = ksf::KS_AutoPtr<{ksf_interface.name}WrapProxy>;\n\n"""

        return parsed_str

    def parse_interface(self,
                        ksf_interface: KsfInterface):
        interface_declare = []

        self.add_include("servant/Agent.h")
        self.add_include("servant/Servant.h")

        interface_declare.append(self.parse_InterfacePrxCallBack(ksf_interface))
        self.add_include("promise/promise.h")
        interface_declare.append(self.parse_InterfacePrxCallbackPromise(ksf_interface))
        interface_declare.append(self.parse_InterfaceCoroPrxCallback(ksf_interface))
        interface_declare.append(self.parse_InterfaceProxy(ksf_interface))

        return fstr(template_namespace,
                    module_begin=self.get_ns_begin(self.curr_module),
                    module_end=self.get_ns_end(self.curr_module),
                    elements=interface_declare
                    )

    def generate(self):
        if len(self.ast.get_all_export_symbol()) == 0:
            raise RuntimeError("no export symbol")

        self.curr_module = None
        export_module_declares = []
        invoke_module_declares = []
        const_list = []
        enum_list = []
        struct_list = []
        hidden_str = []
        export_str = ''

        for sym in self.ast.get_all_export_symbol():
            ele = self.ast.all_element.obj[sym]
            self.curr_module = ele.module

            if isinstance(ele,
                          KsfConst):
                const_list.append((ele.module, self.parse_const(ele)))
                pass
            elif isinstance(ele,
                            KsfEnum):
                enum_list.append((ele.module, self.parse_enum_pure(ele)))
                invoke_module_declares.append(self.parse_enum_func(ele))
                pass
            elif isinstance(ele,
                            KsfStruct):
                struct_list.append((ele.module, self.parse_struct_pure(ele)))
                invoke_module_declares.append(self.parse_struct_wrap(ele))
                pass
            elif isinstance(ele,
                            KsfInterface) and self.with_rpc:
                invoke_module_declares.append(self.parse_interface(ele))

        self.curr_module = None
        element_declares = []
        for module, element_declare in const_list + enum_list + struct_list:
            if self.curr_module is not None and self.curr_module != module:
                export_module_declares.append(fstr(template_namespace,
                                                   module_begin=self.get_ns_begin(self.curr_module),
                                                   module_end=self.get_ns_end(self.curr_module),
                                                   elements=element_declares
                                                   )
                                              )
                element_declares = []
            self.curr_module = module

            element_declares.append(element_declare)

        self.add_include("ksf/proto/proto.h")

        if self.curr_module is not None:
            export_module_declares.append(fstr(template_namespace,
                                               module_begin=self.get_ns_begin(self.curr_module),
                                               module_end=self.get_ns_end(self.curr_module),
                                               elements=element_declares
                                               )
                                          )
            self.curr_module = None

        export_file_declare = fstr(template_header,
                                   header_description=fstr(template_header_description,
                                                           file_name=self.sdk_export.name,
                                                           date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                           version="1.0.0",
                                                           ),
                                   import_headers=self.parse_header(with_ksf=False),
                                   namespaces=export_module_declares
                                   )

        self.add_include(self.sdk_export.name)
        invoke_file_declare = fstr(template_header,
                                   header_description=fstr(template_header_description,
                                                           file_name=self.sdk_invoke.name,
                                                           date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                           version="1.0.0",
                                                           ),
                                   import_headers=self.parse_header(with_ksf=True),
                                   namespaces=invoke_module_declares
                                   )

        with self.sdk_export.open("w") as f:
            f.write(export_file_declare)

        with self.sdk_invoke.open("w") as f:
            f.write(invoke_file_declare)


def cpp_gen(mode,
            files,
            replace_namespace,
            replace_include_path,
            include_path,
            destination_path,
            push_function,
            export_symbol,
            dispatch_mode,
            flags: dict,
            **kwargs
            ):
    """生成cpp文件"""
    if flags is None:
        flags = defaultdict(bool)

    file_path = files

    real_inc_dirs = set()
    for inc in include_path:
        real_inc_dirs.add(str(Path(inc).resolve()))

    if mode == 'file':
        ast = generate(file_path,
                       real_inc_dirs,
                       flags['with_current_priority'],
                       [])
        for file in ast.files.values():
            if file.is_source:
                output_file = f"{file.path.name[:-4]}.h"
                CppGenerator(ast,
                             replace_namespace,
                             replace_include_path,
                             destination_path,
                             push_function,
                             input_file=[file],
                             output_file=output_file,
                             invoke_file=kwargs['invoke_file'],
                             dispatch_mode=dispatch_mode,
                             **flags
                             ).generate()
    elif mode in ('export_import', 'all_in_one', 'invoke_separate'):
        ast = generate(file_path,
                       real_inc_dirs,
                       flags['with_current_priority'],
                       export_symbol)
        if mode == 'export_import':
            CppSdkGenerator(ast,
                            replace_namespace,
                            replace_include_path,
                            destination_path,
                            push_function,
                            export_symbol,
                            invoke=kwargs['invoke_file'],
                            export=kwargs['export_file'],
                            dispatch_mode=dispatch_mode,
                            **flags
                            ).generate()
        elif mode == 'all_in_one':
            CppGenerator(ast,
                         replace_namespace,
                         replace_include_path,
                         destination_path,
                         push_function,
                         input_file=ast.files.values(),
                         output_file=kwargs['output_file'],
                         invoke_file=kwargs['invoke_file'],
                         dispatch_mode=dispatch_mode,
                         **flags
                         ).generate_all()
        else:
            CppGenerator(ast,
                         replace_namespace,
                         replace_include_path,
                         destination_path,
                         push_function,
                         input_file=ast.files.values(),
                         output_file=kwargs['output_file'],
                         invoke_file=kwargs['invoke_file'],
                         dispatch_mode=dispatch_mode,
                         **flags
                         ).generate_all(is_seperate=True)
    else:
        raise RuntimeError(f"未知的模式 {mode}")


# 测试用例
if __name__ == '__main__':
    file_path = [
        'example/enum_simple.ksf',
        'example/const_definition.ksf',
        'example/struct_simple.ksf'
    ]

    include_path = ['../../']

    destination_path = '../../../gen'

    cpp_gen('file',
            file_path,
            {},
            {},
            include_path,
            destination_path)
    cpp_gen('export_import',
            file_path,
            {},
            {},
            include_path,
            destination_path)
