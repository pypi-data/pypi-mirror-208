import ply.lex as lex


# 定义 KSF IDL 文件中的词法符号
class KsfLexer:
    states = (
        ('comment', 'exclusive'),
    )

    tokens = (
        'INCLUDE',
        'INTERFACE',
        'MODULE',
        'STRUCT',
        'ENUM',
        'CONST',
        'KEY',
        'USING',
        'IMPORT',
        'EXPORT',

        # 符号
        'LEFT_PAREN',
        'RIGHT_PAREN',
        'LEFT_BRACE',
        'RIGHT_BRACE',
        "LEFT_SQUARE",
        "RIGHT_SQUARE",
        "LEFT_ANGLE_BRACKET",
        "RIGHT_ANGLE_BRACKET",
        'SEMICOLON',
        'COMMA',
        # 'COLON',
        'EQUALS',
        # 'DOT',
        # 输出参数前缀
        'OUTPUT',

        'IDENTIFIER',
        'STRING_CONSTANT',
        # 'INT_CONSTANT',
        'RADIX_CONSTANT',
        'EXPR_CONSTANT',

        # 限定
        'UNSIGNED',

        # 字段模式
        "REQUIRED",
        "OPTIONAL",

        # 基本类型
        'VOID',
        'INT',
        'LONG',
        'FLOAT',
        'DOUBLE',
        'SHORT',
        'BOOL',
        'CHAR',
        'STRING',
        'VECTOR',
        'MAP',

        'FALSE',
        'TRUE',

        'COMMENT_MULTILINE',
        'COMMENT_LINE',
    )

    # 定义词法规则优先级
    precedence = (
        ('left', 'EXPR_CONSTANT'),
    )

    # 定义 KSF IDL 文件中的词法规则
    t_LEFT_PAREN = r'\('
    t_RIGHT_PAREN = r'\)'
    t_LEFT_BRACE = r'\{'
    t_RIGHT_BRACE = r'\}'
    t_LEFT_SQUARE = r'\['
    t_RIGHT_SQUARE = r'\]'
    t_LEFT_ANGLE_BRACKET = r'\<'
    t_RIGHT_ANGLE_BRACKET = r'\>'
    t_SEMICOLON = r';'
    t_COMMA = r','
    # t_COLON = r':'
    t_EQUALS = r'='

    # t_DOT = r'\.'
    t_comment_ignore = ''

    # 定义多行注释的规则，进入 comment 状态
    def __init__(self):
        self.lexer = None

    def t_comment(self, t):
        r'\/\*'
        t.lexer.begin('comment')

    def t_comment_COMMENT_MULTILINE(self, t):
        r"[\s\S]*?\*/"
        t.value = t.value[:-2]

        t.lexer.begin('INITIAL')
        return t

    def t_comment_error(self, t):
        t.lineno, t.lexpos = self._find_position(t.lexer.lexdata, t.lexpos)
        print("Illegal character '%s' in MULTI_LINE_COMMENT" % t.value[0])
        t.lexer.skip(1)

    def t_IDENTIFIER(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_]*(::[a-zA-Z_][a-zA-Z0-9_]*)?'
        t.type = {
            "bool": "BOOL",
            "require": "REQUIRED",
            "optional": "OPTIONAL",
            "enum": "ENUM",
            "struct": "STRUCT",
            "interface": "INTERFACE",
            "module": "MODULE",
            "map": "MAP",
            "vector": "VECTOR",
            "string": "STRING",
            "byte": "CHAR",
            "short": "SHORT",
            "long": "LONG",
            "double": "DOUBLE",
            "float": "FLOAT",
            "int": "INT",
            "unsigned": "UNSIGNED",
            "key": "KEY",
            "out": "OUTPUT",
            "const": "CONST",
            "false": "FALSE",
            "true": "TRUE",
            "using": "USING",
            "import": "IMPORT",
            "export": "EXPORT",
            "void": "VOID",
        }.get(t.value, "IDENTIFIER")
        return t

    # 定义字符串
    def t_STRING_CONSTANT(self, t):
        r""""[^"]*\""""
        t.value = t.value[1:-1]
        return t

    # 定义多进制的正则表达式
    def t_RADIX_CONSTANT(self, t):
        r'(-?(0[bB][01]+|0[oO][0-7]+|0[xX][0-9a-fA-F]+|\d+(\.\d+)?([eE][-+]?\d+)?))'
        return t

    # 定义科学计数的正则表达式
    def t_EXPR_CONSTANT(self, t):
        r'(-?\d+(\.\d+)?([eE][-+]?\d+)?)'
        return t

    def t_COMMENT_LINE(self, t):
        r"""//.*"""
        t.value = t.value[2:]
        return t

    # 定义包含关键字的规则
    def t_INCLUDE(self, t):
        r'\#include'
        return t

    # 定义忽略的字符，包括空格、制表符和换行符·
    t_ignore = ' \t\r\n'

    def t_newline(self, t):
        r"\n+"
        t.lexer.lineno += len(t.value)

    # 定义错误处理函数，打印错误信息
    def t_error(self, t):
        t.lineno, t.lexpos = self.find_position(t.lexer.lexdata, t)
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    # 编译lexer
    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    def test(self, data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            tok.lineno, tok.lexpos = self.find_position(data, tok)
            print(tok)

    @staticmethod
    def find_position(text, token):
        """
        获取当前token所在位置
        :param text:
        :param token:
        :return:
        """
        index = token.lexpos
        lines = text.splitlines(keepends=True)
        line_number = 0
        for line in lines:
            line_length = len(line)
            if index < line_length:
                column_number = index
                break
            index -= line_length
            index -= 1  # 减去回车符
            line_number += 1
        else:
            return -1, -1
        return line_number + 1, column_number + 2


if __name__ == '__main__':
    from pathlib import Path
    lexer = KsfLexer()
    lexer.build()
    # 定义 KSF IDL 文件
    ksf_idl = '''
#include "123.ksf"
module MyModule {
    /*my interface*/
    interface MyInterface {
        int add(int a, int b);
        void print(string message);
    }
}
    '''

    # file = Path('../../example/const_definition.ksf')
    file = Path('/Users/xiongjuli/kingstar/ksf-cpp/event/proto/event/EventBase.ksf')
    with file.open() as f:
        # 将 KSF IDL 文件传递给词法分析器
        lexer.test(f.read())
