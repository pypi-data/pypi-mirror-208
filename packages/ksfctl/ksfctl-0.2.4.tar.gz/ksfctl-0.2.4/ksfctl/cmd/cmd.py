import enum
from pathlib import Path

from ksfctl.cmd.options import *
from ksfctl.generate.cpp.generator import cpp_gen


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.pass_context
def cli(ctx):
    pass


help_str = f'''\
ksf文件解析器\n
解析ksf文件到其他语言，目前支持[ksf(自转译), c++(cpp), python(py), java, node.js(node), go]\n
关键字: \n
module, struct, enum, interface, const, bool, int, long, short, byte, double, float, string, map, vector, using, import, export, require, optional, key, out, false, true\n
基础元素: 以模块(module)为核心，文件包含关系为树状结构，模块包含接口interface，结构struct，枚举enum，常量const等元素\n
适合场景: 用于定义协议，生成对应的代码，用于服务端和客户端的通信\n
'''


@cli.group(name='trans', help=help_str,
           context_settings={'help_option_names': ['-h', '--help']}
           )
@click.pass_context
def ksf_trans(ctx):
    pass


class ModeType(enum.Enum):
    FILE = 'file'
    ALL_IN_ONE = 'all_in_one'
    EXPORT_IMPORT = 'export_import'
    INVOKE_SEPARATE = 'invoke_separate'


class VisibilityType(enum.Enum):
    PUBLIC = 'public'
    PRIVATE = 'private'


@ksf_trans.command(name='cxx', context_settings={'help_option_names': ['-h', '--help']})
@click.pass_context
@click.argument('patterns',
                nargs=-1,
                required=True,
                type=str,
                metavar='...<glob> or ...<regex>'
                )
@click.option('--match-mode',
              'match_mode',
              default='glob',
              metavar='<mode>',
              type=click.Choice(('file', 'glob', 'glob-recursive')),
              help='匹配模式'
              )
@click.option('--mode', 'mode', default=ModeType.FILE.value, type=click.Choice([mode.value for mode in ModeType]),
              help=f'''\
生成器模式选择.

file=单文件(每一个.ksf对应生成一个文件)
all_in_one=合并文件(只生成一个聚合文件)
invoke_separate=调用分离模式
export_import=导出导入模式(sdk模式), 默认为file)
'''
              )
@click.option('--dispatch-mode', 'dispatch_mode', default='array', type=click.Choice(('array', 'set', 'hash')),
              metavar='<dispatch-mode>', help='分发模式, 支持(array, set, hash)'
              )
@click.option('--visibility', 'visibility', default=VisibilityType.PUBLIC.value,
              type=click.Choice([visibility.value for visibility in VisibilityType]), help='生成的符号的可见性'
              )
@click.option('-f', '--config-file', 'config_file', multiple=False, type=str, metavar='<config-file>',
              help='注入的脚本文件yaml(优先级低于其他选项，即其他命令行参数可以覆盖文件定义的内容)'
              )
@click.option('-i', '--include', '--include-path', 'include_path', multiple=True, type=str, help='ksf协议文件搜索路径',
              metavar='[<include-path> or @pwd]'
              )
@click.option('-d', '--dir', '--dest', 'destination_path', multiple=False, help='生成的头文件存放的路径',
              metavar='<destination-path>'
              )
@click.option('-o', '--output-file', 'output_file', multiple=False, default="ksf_out.h",
              help='[聚合模式]生成的聚合头文件名', metavar='<output-file>'
              )
@click.option('--export-file', 'export_file', multiple=False, default="ksf_export.h",
              help='[导入导出模式/调用分离模式生效]生成的导出符号头文件名(默认为ksf_export.h)', metavar='<export-file>'
              )
@click.option('--invoke-file', 'invoke_file', multiple=False, default="ksf_invoke.h",
              help='[导入导出模式/调用分离模式生效]生成的调用头文件名(默认为ksf_invoke.h)', metavar='<invoke-file>'
              )
@click.option('--export', 'export_symbols', multiple=True, help='需要导出的结构体或者函数体')
@click.option('--hidden', 'hidden_symbols', multiple=True, help='需要隐藏的结构体或者函数体(TODO)')
@click.option('--replace_ns', '--replace-ns', multiple=False, help='(将被废弃)替换namespace')
@click.option('--replace-namespace', nargs=2, multiple=True, type=str, help='(推荐)将指定命名空间替换为另一个命名空间')
@click.option('--replace-include-path', nargs=2, multiple=True, type=str, help='(推荐)替换头文件路径')
@click.option('--push-function', multiple=True,
              help='携带push模式的函数名, 用于生成push函数，参数形式为module.interface.operator'
              )
@click.option('--ignore-relative-path', 'ignore_relative_path', is_flag=True, flag_value=True, default=False,
              help='忽略依赖目录'
              )
@click.option('-w',
              '--work-directory',
              'work_directory',
              multiple=False,
              default="@pwd",
              metavar='<work-directory>',
              help='工作目录'
              )
@click.option('--verbose', 'verbose', is_flag=True, flag_value=True, default=False, help='是否打印详细信息')
# 可选优化选项
@click.option('--enable-check-default/--disable-check-default',
              'check_default',
              default=True,
              help='是否打包默认值'
              )
@click.option('--enable-json/--disable-json', 'json', is_flag=True, default=True, help='是否生成Json格式')
@click.option('--enable-rpc/--disable-rpc', 'rpc', is_flag=True, default=True, help='是否生成RPC接口')
@click.option('--enable-current-priority/--disable-current-priority',
              'current_priority',
              is_flag=True,
              default=True,
              help='是否优先使用当前目录'
              )
@click.option('--enable-trace/--disable-trace',
              'trace',
              is_flag=True,
              default=False,
              help='是否需要调用链追踪逻辑'
              )
@click.option('--enable-push/--disable-push', 'push', is_flag=True, default=True, help='是否需要推送接口')
@click.option('--enable-invoke-client/--disable-invoke-client',
              'invoke_client',
              is_flag=True,
              default=True,
              help='是否有客户端调用实现'
              )
@click.option('--enable-promise/--disable-promise',
              'promise',
              is_flag=True,
              default=True,
              help='是否使用客户端Promise调用实现'
              )
@click.option('--enable-coroutine/--disable-coroutine',
              'coroutine',
              is_flag=True,
              default=True,
              help='是否使用客户端Coroutine调用实现'
              )
@click.option('--enable-invoke-server/--disable-invoke-server',
              'invoke_server',
              is_flag=True,
              default=True,
              help='是否有客户端调用实现'
              )
@click.option('--enable-rvalue-ref/--disable-rvalue-ref', 'rvalue_ref', is_flag=True, default=False,
              help='是否参数使用右值引用'
              )
@click.option('--enable-cxx17/--disable-cxx17',
              'cxx17',
              is_flag=True,
              flag_value=True,
              default=False,
              help='使用C++17'
              )
def cxx(ctx, patterns, mode, **kwargs):
    """c++(cpp)语言解析器"""
    ctx.help_option_names += ['-h']

    parsed_kwargs = {}

    print_verbose = flag_verbose(kwargs)

    """解析配置文件"""
    if "config_file" in kwargs:
        """解析配置文件"""
        parse_config_file_to_parsed_args(kwargs, parsed_kwargs)

    """文件匹配模式"""
    print_verbose(var_match_mode(kwargs, parsed_kwargs))

    """文件匹配模式"""
    print_verbose(var_work_directory(kwargs, parsed_kwargs))

    files = set()
    work_dir = parsed_kwargs["work_directory"]
    if parsed_kwargs['match_mode'] == 'glob-recursive':
        for pattern in patterns:
            p = Path(pattern)
            if p.is_absolute():
                files.update(Path(work_dir).rglob(str(p.relative_to(work_dir))))
            else:
                files.update(Path(work_dir).rglob(pattern))
    elif parsed_kwargs['match_mode'] == 'glob':
        for pattern in patterns:
            p = Path(pattern)
            if p.is_absolute():
                files.update(Path(work_dir).glob(str(p.relative_to(work_dir))))
            else:
                files.update(Path(work_dir).glob(pattern))
    elif parsed_kwargs['match_mode'] == 'file':
        files.update(patterns)

    if len(files) == 0:
        raise click.BadParameter('未指定任何文件。')

    """模式"""
    print_verbose(f"""模式: {mode}""")

    """将指定命名空间替换为另一个命名空间"""
    print_verbose(list_replace_namespace(kwargs, parsed_kwargs))

    """替换头文件路径"""
    print_verbose(list_replace_include_path(kwargs, parsed_kwargs))

    """生成文件位置"""
    print_verbose(var_destination_path(kwargs, parsed_kwargs))

    """头文件包含路径"""
    print_verbose(list_include_path(kwargs, parsed_kwargs))

    """忽略依赖目录"""
    print_verbose(f"忽略依赖目录：{kwargs['ignore_relative_path']}")

    """是否优先搜索当前目录"""
    print_verbose(f"是否优先搜索当前目录：{kwargs['current_priority']}")

    """携带push模式的函数名, 用于生成push函数，参数形式为module.interface.operator"""
    print_verbose(list_push_function(kwargs, parsed_kwargs))

    """是否只导出部分符号"""
    print_verbose(list_export_symbol(kwargs, parsed_kwargs))

    """分发模式"""
    print_verbose(var_dispatch_mode(kwargs, parsed_kwargs))

    """是否启动c++17风格"""
    print_verbose(f"是否启动c++17风格：{kwargs['cxx17']}")

    """是否检测默认值"""
    print_verbose(f"是否检测默认值：{kwargs['check_default']}")

    """是否生成Json序列化接口"""
    print_verbose(f"是否生成Json序列化接口：{kwargs['json']}")

    """是否生成RPC接口"""
    print_verbose(f"是否生成RPC接口：{kwargs['rpc']}")

    """是否需要调用链追踪逻辑"""
    print_verbose(f"是否需要调用链追踪逻辑：{kwargs['trace']}")

    """是否参数使用右值引用"""
    print_verbose(f"是否参数使用右值引用：{kwargs['rvalue_ref']}")

    """解析所有的flags，携带with_头"""
    parsed_kwargs['flags'] = {}
    for k, v in kwargs.items():
        if isinstance(v, bool):
            parsed_kwargs['flags'].update({f'with_{k}': v})

    print_verbose(var_invoke_file(kwargs, parsed_kwargs))
    if mode == ModeType.EXPORT_IMPORT.value:
        """启动sdk模式，会生成一个export的头文件和一个内部invoke的头文件"""
        print_verbose(var_export_file(kwargs, parsed_kwargs))
    elif mode == ModeType.FILE.value:
        pass
    else:
        """启动all_one模式，会生成一个聚合的头文件"""
        print_verbose(var_output_file(kwargs, parsed_kwargs))
    cpp_gen(mode, files=files, **parsed_kwargs)


# @ksf_trans.command(name='ksf', help="抽取元素并合并成新的ksf文件",
#                    context_settings={'help_option_names': ['-h', '--help']}
#                    )
# @click.pass_context
# @click.argument('ksf_files', nargs=-1, required=True, type=str)
# @click.option('-d', '--destination', type=str, help='输出文件夹')
# @click.option('-o', '--output', type=str, help='输出文件名')
# @click.option('-i', '--include', type=str, multiple=True, help='头文件包含路径')
# @click.option('--export', 'export_symbols', type=str, multiple=True, help='导出的接口')
# @click.option('--verbose', 'verbose', is_flag=True, flag_value=True, default=False, help='是否打印详细信息')
# @click.option('--special-container', 'special_container', is_flag=True, flag_value=True, default=False,
#               help='是否启用特殊容器(默认不启用)，特殊容器为(vector[set], vector[hashset], map[hashmap])，不启用时退化为vector和map'
#               )
# def merge_ksf(ctx, **kwargs):
#     verbose = False
#
#     def print_verbose(msg):
#         if verbose:
#             click.echo(msg)
#
#     if 'verbose' in kwargs:
#         verbose = kwargs['verbose']
#         del kwargs['verbose']
#
#     if 'ksf_files' in kwargs:
#         ksf_files = kwargs['ksf_files']
#         del kwargs['ksf_files']
#     else:
#         print_verbose('未指定ksf文件')
#         exit(1)
#
#     if 'destination' in kwargs:
#         destination_dir = kwargs['destination']
#         del kwargs['destination']
#     else:
#         destination_dir = '.'
#
#     if 'output' in kwargs:
#         output = kwargs['output']
#         del kwargs['output']
#     else:
#         print_verbose('未指定输出文件名')
#         exit(1)
#
#     if 'include' in kwargs:
#         include = kwargs['include']
#         del kwargs['include']
#     else:
#         include = []
#
#     if 'export_symbols' in kwargs:
#         export_symbols = kwargs['export_symbols']
#         del kwargs['export_symbols']
#     else:
#         print_verbose('未指定导出的接口')
#         exit(1)
#
#     """解析所有的flags，携带with_头"""
#     kwargs_with_prefix = {}
#     for k, v in kwargs.items():
#         kwargs_with_prefix.update({f'with_{k}': v})

# case_gen(files=ksf_files,
#          include_dirs=include,
#          destination_dir=destination_dir,
#          out_file=output,
#          export_symbols=export_symbols,
#          **kwargs_with_prefix
#          )


if __name__ == '__main__':
    cli()
    exit(0)

    runner = CliRunner()
    result1 = runner.invoke(cli, ['-h'])
    assert result1.exit_code == 0

    result2 = runner.invoke(cli, ['--help'])
    assert result2.exit_code == 0
