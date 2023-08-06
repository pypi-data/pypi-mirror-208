# 统一解析所有由click传过来的option字段
import os
import pathlib

import click
import yaml


# include, destination_dir, replace_ns, replace_namespace, replace_include_path,
#               push_function, sdk_mode, verbose, sdk_export, sdk_invoke, export_symbols, config_file,
#               config,

def flag_verbose(kwargs):
    """verbose flag"""
    print_verbose_func = lambda msg: None
    if "verbose" in kwargs:
        if kwargs["verbose"]:
            print_verbose_func = click.echo
        del kwargs["verbose"]

    return print_verbose_func


def list_replace_namespace(kwargs, parsed_args: dict):
    print_text = []
    parsed_args["replace_namespace"] = {}

    if "replace_namespace" in kwargs and kwargs["replace_namespace"] is not None:
        for origin, alias in kwargs['replace_namespace']:
            parsed_args["replace_namespace"][origin] = alias
            print_text.append(f'将命名空间 {origin} 替换为 {alias}。')

    if "replace_ns" in kwargs and kwargs["replace_ns"] is not None:
        for replace_namespace_str in kwargs['replace_ns'].split(";"):
            origin, alias = replace_namespace_str.split("/")
            parsed_args["replace_namespace"][origin] = alias
            print_text.append(f'将命名空间 {origin} 替换为 {alias}。')

    if print_text == "":
        print_text = ["未指定替换命名空间。"]

    del kwargs["replace_namespace"]
    del kwargs["replace_ns"]

    return '\n'.join(print_text)


def list_replace_include_path(kwargs, parsed_args: dict):
    print_text = []
    parsed_args["replace_include_path"] = {}

    if "replace_include_path" in kwargs and kwargs["replace_include_path"] is not None:
        for origin, alias in kwargs['replace_include_path']:
            parsed_args["replace_include_path"][origin] = alias
            print_text.append('将包含路径 {origin} 替换为 {alias}。')

    if len(print_text) == 0:
        print_text = ["未指定替换包含路径."]

    del kwargs["replace_include_path"]

    return '\n'.join(print_text)


def var_match_mode(kwargs, parsed_args: dict):
    parsed_args["match_mode"] = "glob"
    default_text = "(默认glob)"

    if "match_mode" in kwargs and kwargs["match_mode"] is not None:
        parsed_args["match_mode"] = kwargs["match_mode"]
        default_text = ""
        del kwargs["match_mode"]

    return f"""匹配模式: {parsed_args["match_mode"]}{default_text}"""


def var_work_directory(kwargs, parsed_args: dict):
    parsed_args["work_directory"] = os.getcwd()
    default_text = "(默认当前目录[@pwd], 可用其他目录索引格式(用户根目录@home,...))"

    if "work_directory" in kwargs and kwargs["work_directory"] is not None:
        if kwargs["work_directory"] == "@pwd":
            parsed_args["work_directory"] = os.getcwd()
        elif kwargs["work_directory"] == "@home":
            parsed_args["work_directory"] = os.path.expanduser("~")
        else:
            path = pathlib.Path(kwargs["work_directory"])

            if pathlib.Path.is_dir(path):
                if pathlib.Path.is_absolute(path):
                    parsed_args["work_directory"] = path
                else:
                    parsed_args["work_directory"] = os.path.join(os.getcwd(), path)
            else:
                raise click.BadParameter(f"指定的路径 {path} 不存在或不是一个目录。")

        default_text = ""
        del kwargs["work_directory"]

    return f"""当前执行路径: {parsed_args["work_directory"]}{default_text}"""


def var_destination_path(kwargs, parsed_args: dict):
    parsed_args["destination_path"] = os.getcwd()
    default_text = "(默认当前路径@pwd)"

    if "destination_path" in kwargs and kwargs["destination_path"] is not None:
        parsed_args["destination_path"] = kwargs["destination_path"]
        default_text = ""
        del kwargs["destination_path"]

    return f"""输出目录: {parsed_args["destination_path"]}{default_text}"""


def list_include_path(kwargs, parsed_args: dict):
    parsed_args["include_path"] = set()
    print_text = []

    if "include_path" in kwargs and kwargs["include_path"] is not None:
        parsed_args["include_path"].update(kwargs["include_path"])
        print_text.append(f"""包含路径: {parsed_args["include_path"]}""")
        del kwargs["include_path"]

    # if len(parsed_args["include_path"]) == 0:
    parsed_args["include_path"].update([parsed_args['work_directory']])
    print_text.append(f"""包含路径: {parsed_args["include_path"]}(当前执行目录@pwd)""")

    return '\n'.join(print_text)


def list_push_function(kwargs, parsed_args: dict):
    parsed_args["push_function"] = []
    print_text = ""

    if "push_function" in kwargs and kwargs["push_function"] is not None:
        parsed_args["push_function"] = kwargs["push_function"]
        print_text = f"""推送函数: {parsed_args["push_function"]}"""
        del kwargs["push_function"]

    return print_text


def list_export_symbol(kwargs, parsed_args: dict):
    if "visibility" in kwargs and kwargs["visibility"] is not None:
        if kwargs["visibility"] == "public":
            kwargs["export_symbols"] = ["*"]

    parsed_args["export_symbol"] = []
    print_text = ""

    if "export_symbols" in kwargs and kwargs["export_symbols"] is not None:
        parsed_args["export_symbol"] = kwargs["export_symbols"]
        print_text = f"""导出符号: {parsed_args["export_symbol"]}"""
        del kwargs["export_symbols"]

    return print_text


def var_invoke_file(kwargs, parsed_args: dict):
    parsed_args["invoke_file"] = ""
    print_text = ""

    if "invoke_file" in kwargs and kwargs["invoke_file"] is not None:
        parsed_args["invoke_file"] = kwargs["invoke_file"]
        print_text = f"""调用文件: {parsed_args["invoke_file"]}"""
        del kwargs["invoke_file"]

    return print_text


def var_export_file(kwargs, parsed_args: dict):
    parsed_args["export_file"] = ""
    print_text = ""

    if "export_file" in kwargs and kwargs["export_file"] is not None:
        parsed_args["export_file"] = kwargs["export_file"]
        print_text = f"""导出文件: {parsed_args["export_file"]}"""
        del kwargs["export_file"]

    return print_text


def var_output_file(kwargs, parsed_args: dict):
    parsed_args["output_file"] = ""
    print_text = ""

    if "output_file" in kwargs and kwargs["output_file"] is not None:
        parsed_args["output_file"] = kwargs["output_file"]
        print_text = f"""聚合文件: {parsed_args["output_file"]}"""
        del kwargs["output_file"]

    return print_text


def parse_config_file_to_parsed_args(kwargs, parsed_args: dict):
    if kwargs['config_file'] is not None:
        config_yaml = kwargs['config_file']
        with open(config_yaml, 'r') as f:
            export_symbols = set()
            configs = yaml.safe_load(f.read())
            # print(configs)
            parsed_args['replace_namespace'] = {}
            parsed_args['export_symbols'] = export_symbols

            for config in configs:
                module = config['module']
                if 'namespace' in config:
                    parsed_args['replace_namespace'][module] = config['namespace']

                for element_type, elements in config['export'].items():
                    if element_type == 'interface':
                        for element in elements:
                            if isinstance(element, dict):
                                for interface, functions in element.items():
                                    if functions is None or len(functions) == 0:
                                        export_symbols.add(f'{module}.{interface}')
                                    else:
                                        for function in functions:
                                            export_symbols.add(f'{module}.{interface}.{function}')
                            else:
                                export_symbols.add(f'{module}.{element}')
                    else:
                        for element in elements:
                            export_symbols.add(f'{module}.{element}')
    del kwargs['config_file']


def var_dispatch_mode(kwargs, parsed_args: dict):
    parsed_args["dispatch_mode"] = "default"
    print_text = ""

    if "dispatch_mode" in kwargs and kwargs["dispatch_mode"] is not None:
        parsed_args["dispatch_mode"] = kwargs["dispatch_mode"]
        print_text = f"""分发模式: {parsed_args["dispatch_mode"]}"""
        del kwargs["dispatch_mode"]

    return print_text