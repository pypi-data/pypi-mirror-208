def fstr(template, **kwargs):
    """f-string模版解析，用了eval黑魔法"""
    def add_lines(lines, tab=0):
        if isinstance(lines, str):
            lines = lines.split('\n')
        elif isinstance(lines, (list, tuple, set)):
            return '\n'.join(add_lines(line, tab) for line in lines)
        else:
            raise TypeError(f"不支持的类型{type(lines)}")

        space = ' ' * (4 * tab)
        return f"\n".join(''if line.isspace() else (space + line) for line in lines)

    def add_connect(conn, *args):
        def flatten(lst):
            result = []
            for item in lst:
                if isinstance(item, (list, set, tuple)):
                    result.extend(flatten(item))
                else:
                    result.append(item)
            return result

        return conn.join(flatten(args))

    return eval(f'''f"""{template}"""''', kwargs, locals())


# 数组+二分查找确定函数的onDispatch实现
# 填充interface_name, function_names, dispatch_case_list
template_array_style_onDispatch_at_server = """\
int onDispatch(ksf::KsfCurrentPtr _current, std::vector<char> &_sResponseBuffer) override {{
    static std::string __{interface_name}_all[] = {{"{'", "'.join(function_names)}"}};
                                        
    std::pair<std::string *, std::string *> r = equal_range(__{interface_name}_all, __{interface_name}_all + {len(function_names)}, _current->getFuncName());
    
    if (r.first == r.second) {{
        return ksf::KSFSERVERNOFUNCERR;
    }}
    
    switch (r.first - __{interface_name}_all) {{
{dispatch_case_str}
    }} //end switch
    
    return ksf::KSFSERVERNOFUNCERR;
}} //end onDispatch
"""

template_array_style_onDispatch_at_client = """\
int onDispatch(ksf::ReqMessagePtr msg) override {{
    static std::string __{interface_name}_all[] = {{"{'", "'.join(function_names)}"}};
                                        
    std::pair<std::string *, std::string *> r = equal_range(__{interface_name}_all, __{interface_name}_all + {len(function_names)}, std::string(msg->request.sFuncName));
    
    if (r.first == r.second) {{
        return ksf::KSFSERVERNOFUNCERR;
    }}
    
    switch (r.first - __{interface_name}_all) {{
{add_lines(dispatch_case_str, 2)}
    }} //end switch
    
    return ksf::KSFSERVERNOFUNCERR;
}} //end onDispatch
"""

# 集合+二分查找确定函数的onDispatch实现
# 填充interface_name, function_names, dispatch_case_list
template_set_style_onDispatch_at_server = """\
int onDispatch(ksf::KsfCurrentPtr _current, std::vector<char> &_sResponseBuffer) override {{
    static std::set<std::string> __{interface_name}_all = {{"{'", "'.join(function_names)}"}};
    
    auto iter = __{interface_name}_all.find(_current->getFuncName());
    if (iter == __{interface_name}_all.end()) {{
        return ksf::KSFSERVERNOFUNCERR;
    }}
    
    switch (std::distance(__{interface_name}_all.begin(), iter)) {{
{dispatch_case_str}
    }} //end switch
    
    return ksf::KSFSERVERNOFUNCERR;
}} //end onDispatch
"""

# 集合+二分查找确定函数的onDispatch实现
# 填充interface_name, function_names, dispatch_case_list
template_hash_style_onDispatch_at_server = """\
int onDispatch(ksf::KsfCurrentPtr _current, std::vector<char> &_sResponseBuffer) override {{
    switch (HASH64(_current->getFuncName())) {
{dispatch_case_str}
    }} //end switch
    
    return ksf::KSFSERVERNOFUNCERR;
}} //end onDispatch
"""

# onDispatch的case语句
# 填充 case, variable_declare, request_version_kup, request_version_json, request_version_ksf, return_type, function_name, operator_params
# 填充response_version_kup, response_version_json, response_version_ksf, response_params
template_dispatch_case_at_server = """\
case {case}: {{
    ksf::KsfInputStream<ksf::BufferReader> _is;
    _is.setBuffer(_current->getRequestBuffer());
{add_lines(variable_declare, 1)}
    switch (_current->getRequestVersion()) {{
        case ksf::KUPVERSION: {{
            ksf::kup::UniAttribute<ksf::BufferWriterVector, ksf::BufferReader>  _ksfAttr_;
            _ksfAttr_.setVersion(_current->getRequestVersion());
            _ksfAttr_.decode(_current->getRequestBuffer());
{add_lines(request_version_kup, 3)}
            break;
        }} 
        case ksf::JSONVERSION: {{
            ksf::JsonValueObjPtr _jsonPtr = ksf::JsonValueObjPtr::dynamicCast(ksf::KS_Json::getValue(_current->getRequestBuffer()));
{add_lines(request_version_json, 3)}
            break;
        }}
        case ksf::KSFVERSION: {{
{add_lines(request_version_ksf, 3)}
            break;
        }}
        default: return ksf::KSFSERVERDECODEERR;
    }}
    
    {return_type}{function_name}({operator_params}_current);
    
    if(_current->isResponse()) {{
        switch (_current->getRequestVersion()) {{
            case ksf::KUPVERSION: {{
                ksf::kup::UniAttribute<ksf::BufferWriterVector, ksf::BufferReader>  _ksfAttr_;
                _ksfAttr_.setVersion(_current->getRequestVersion());
                
{add_lines(response_version_kup, 4)}
                _ksfAttr_.encode(_sResponseBuffer);
                break;
            }} 
            case ksf::JSONVERSION: {{
                ksf::JsonValueObjPtr _p = new ksf::JsonValueObj();
{add_lines(response_version_json, 4)}
                ksf::KS_Json::writeValue(_p, _sResponseBuffer);
                break;
            }} 
            case ksf::KSFVERSION: {{
                ksf::KsfOutputStream<ksf::BufferWriterVector> _os;
{add_lines(response_version_ksf, 4)}
                _os.swap(_sResponseBuffer);
                break;
            }}
            default: {{}}
        }}
    }}
    return ksf::KSFSERVERSUCCESS;

}}
"""

template_dispatch_case_at_client = """\
case {case}: {{
    if (msg->response->iRet != ksf::KSFSERVERSUCCESS) {{
        callback_{function_name}_exception(msg->response->iRet);
        return msg->response->iRet;
    }}
    
    ksf::KsfInputStream<ksf::BufferReader> _is;
    
    _is.setBuffer(msg->response->sBuffer);
    
{add_lines(output_arguments, 1)}
    
    ksf::CallbackThreadData *pCbtd = ksf::CallbackThreadData::getData();
    assert(pCbtd != NULL);
    
    pCbtd->setResponseContext(msg->response->context);
    
    callback_{function_name}({output_params});
    
    pCbtd->delResponseContext();
    
    return ksf::KSFSERVERSUCCESS;
}}
"""

# 普通回调参数解析
template_output_argument_parse = """\
{typename} {argument_name};
_is.read({argument_name}, {index}, true);
"""

# resetDefault
# 填充struct_name
template_resetDefault = '''\
///重新赋值为初始构造的结构
void resetDefault() {{
    *this = {struct_name}{{}}; 
}}'''

# writoTo variable(有检查default)
# 填充 variable_name, variable_tag
template_writeTo_variable = """_os.write({variable_name}, {variable_tag});"""

# writoTo variable(有检查default)
# 填充 check_default, variable_declare
template_writeTo_variable_with_check = """\
if ({check_default}) \
{variable_declare}\
"""


# 枚举转字符串
# 填充enum_name, etos_member
template_etos = """\
inline std::string etos(const {enum_name} &e) {{
    switch (e) {{
{add_lines(etos_member, 2)}
        default: return "";
    }}
}}
"""

# 字符串转枚举
# 填充enum_name, stoe_member
template_stoe = """\
inline int stoe(const std::string &s, {enum_name} &e) {{
{add_lines(stoe_member, 1)}
    return -1;
}}
"""

# 枚举
# 填充comment, enum_name, enum_members
template_enum = """\
{comment}\
enum {enum_name} 
{{
{add_lines(enum_members, 1)}
}};
"""

# writeTo
# 填充variables
template_writeTo = '''\
///序列化为二进制流
template<typename WriterT>
void writeTo(ksf::KsfOutputStream<WriterT>& _os) const {{
{add_lines(variables, 1)}
}}
'''

# writeToJson
# 填充variables
template_writeToJson = '''\
///序列化为Json
ksf::JsonValueObjPtr writeToJson() const {{
    ksf::JsonValueObjPtr p = new ksf::JsonValueObj();
{add_lines(variables, 1)}
    return p;
}}

///序列化为Json字符串
std::string writeToJsonString() const {{
    return ksf::KS_Json::writeValue(writeToJson());
}}
'''

# readFrom
# 填充variables, is_wrap
template_readFrom = '''\
///二进制反序列化为结构体
template<typename ReaderT>
void readFrom(ksf::KsfInputStream<ReaderT>& _is) {{
    {"obj." if is_wrap else ""}resetDefault();
    
{add_lines(variables, 1)}
}}
'''

# readFromJson
# 填充 variables, is_wrap
template_readFromJson = '''\
///Json反序列化为结构体
void readFromJson(const ksf::JsonValuePtr &p, bool isRequire = true) {{
    {"obj." if is_wrap else ""}resetDefault();
    if(!p || p->getType() != ksf::eJsonTypeObj) {{
        char s[128];
        snprintf(s, sizeof(s), "read 'struct' type mismatch, get type: %d.", (p ? p->getType() : 0));
        throw ksf::KS_Json_Exception(s);
    }}

    ksf::JsonValueObjPtr pObj=ksf::JsonValueObjPtr::dynamicCast(p);
{add_lines(variables, 1)}
}}

///Json字符串反序列化为结构体
void readFromJsonString(const std::string &str) {{
    readFromJson(ksf::KS_Json::getValue(str));
}}
'''

# display
# 填充 variables
template_display = '''\
///打印
std::ostream& display(std::ostream& _os, int _level = 0) const {{
    ksf::Displayer _ds(_os, _level);
{add_lines(variables, 1)}
    return _os;
}}
'''

# displaySimple
# 填充 variables
template_displaySimple = '''\
///简单打印
std::ostream& displaySimple(std::ostream& _os, int _level = 0) const {{
    ksf::Displayer _ds(_os, _level);
{add_lines(variables, 1)}
    return _os;
}}
'''

# operator== & operator!=
# 填充 struct_name, variables
template_operator_equal = '''\
inline bool operator==(const {struct_name} &l, const {struct_name} &r) {{
    return {add_connect(' && ', variables)};
}}

inline bool operator!=(const {struct_name} &l, const {struct_name} &r) {{
    return !(l == r);
}}
'''

# operator< & operator> & operator<= & operator>=
# 填充 struct_name, variables
template_operator_compare = """\
inline bool operator<(const {struct_name} &l, const {struct_name} &r) {{
{add_lines(variables, 1)}
    return false;
}}

inline bool operator<=(const {struct_name} &l, const {struct_name} &r) {{
    return !(r < l);
}}

inline bool operator>(const {struct_name} &l, const {struct_name} &r) {{
    return r < l;
}}

inline bool operator>=(const {struct_name} &l, const {struct_name} &r) {{
    return !(l < r);
}}
"""

# operator<< & operator>> (json模式)
# 填充 struct_name
template_operator_stream_with_json = """\
inline std::ostream &operator<<(std::ostream &os, const {struct_name} &r) {{
    os << {'ksf::MakeWrap(r)' if wrap_mode else 'r'}.writeToJsonString();
    return os;
}}

inline std::istream &operator>>(std::istream &is, {struct_name} &l) {{
    std::istreambuf_iterator<char> eos;
    std::string s(std::istreambuf_iterator<char>(is), eos);
    {'ksf::MakeWrap(l)' if wrap_mode else 'l'}.readFromJsonString(s);
    return is;
}}
"""

# function call in callback
# 填充 function_name, arguments
template_function_call = """\
virtual void callback_{function_name}({arguments}) {{ throw std::runtime_error("callback_{function_name} override incorrect."); }}
virtual void callback_{function_name}_exception(int32_t ret) {{ throw std::runtime_error("callback_{function_name}_exception override incorrect."); }}
"""

# 获取应答上下文
# 无填充
template_getResponseContext = f"""\
virtual const std::map<std::string, std::string> &getResponseContext() const {{
    ksf::CallbackThreadData *pCallbackThreadData = ksf::CallbackThreadData::getData();
    assert(pCallbackThreadData);
    
    if (!pCallbackThreadData->getContextValid()) {{
        throw ksf::KS_Exception("cannot get response context");
    }}
    
    return pCallbackThreadData->getResponseContext();
}}
"""

# 原始callback类
# 填充 interface_name, function_handles, get_response_context, dispatch_str
template_callback = """\
class {interface_name}PrxCallback : public ksf::AgentCallback
{{
public:
    ~{interface_name}PrxCallback() override = default;
    
public:
{add_lines(function_handles, 1)}
public:
{add_lines(get_response_context, 1)}
public:
{add_lines(dispatch_str, 1)}
}}; //end {interface_name}PrxCallback

using {interface_name}PrxCallbackPtr = ksf::KS_AutoPtr<{interface_name}PrxCallback>;

"""

# Promise模式callback类
# 填充 interface_name, interface_promises, dispatch_case_str, function_names
template_callback_promise = """\
class {interface_name}PrxCallbackPromise: public ksf::AgentCallback
{{
public:
    ~{interface_name}PrxCallbackPromise() override = default;

{add_lines(interface_promises, 1)}

public:
{add_lines(on_dispatch, 1)}
}}; //end {interface_name}PrxCallbackPromise

using {interface_name}PrxCallbackPromisePtr = ksf::KS_AutoPtr<{interface_name}PrxCallbackPromise>;

"""

# Promise模式onDispatch
# 填充 dispatch_case_str, interface_name, function_names
template_onDispatch_promise = """\
int onDispatch(ksf::ReqMessagePtr msg) override {{
    static std::string __{interface_name}_all[] = {{"{'", "'.join(function_names)}"}};

    std::pair<std::string *, std::string *> r = equal_range(__{interface_name}_all, __{interface_name}_all + {len(function_names)}, msg->request.sFuncName);

    if (r.first == r.second) {{
        return ksf::KSFSERVERNOFUNCERR;
    }}

    switch (r.first - __{interface_name}_all) {{
{add_lines(dispatch_case_str, 2)}
    }} //end switch
    
    return ksf::KSFSERVERNOFUNCERR;
}} //end onDispatch
"""

# Promise模式parse_func_dispatch
# 填充 case_index, output_arguments, function_name, interface_name
template_parse_func_dispatch_promise = """\
case {case}: {{
    if (msg->response->iRet != ksf::KSFSERVERSUCCESS) {{
        callback_{function_name}_exception(msg->response->iRet);
        return msg->response->iRet;
    }}

    ksf::KsfInputStream<ksf::BufferReader> _is;
    _is.setBuffer(msg->response->sBuffer);
    {interface_name}PrxCallbackPromise::Promise{function_name}Ptr ptr = new {interface_name}PrxCallbackPromise::Promise{function_name}();
    
    try {{
{add_lines(output_arguments, 2)}
    }} catch (std::exception &ex) {{
        callback_{function_name}_exception(ksf::KSFCLIENTDECODEERR);
        return ksf::KSFCLIENTDECODEERR;
    }} catch (...) {{
        callback_{function_name}_exception(ksf::KSFCLIENTDECODEERR);
        return ksf::KSFCLIENTDECODEERR;
    }}
    
    ptr->_mRspContext = msg->response->context;
    callback_{function_name}(ptr);
    return ksf::KSFSERVERSUCCESS;
}}
"""

# Coroutine模式parse_func_dispatch
template_parse_func_dispatch_coroutine = """\
case {case}: {{
    if (msg->response->iRet != ksf::KSFSERVERSUCCESS) {{
        callback_{function_name}_exception(msg->response->iRet);
        return msg->response->iRet;
    }}

    ksf::KsfInputStream<ksf::BufferReader> _is;
    _is.setBuffer(msg->response->sBuffer);

    try {{
{add_lines(func_case_list, 2)}

        callback_{function_name}({', '.join(output_arguments)});
    }} catch (std::exception &ex) {{
        callback_{function_name}_exception(ksf::KSFCLIENTDECODEERR);
        return ksf::KSFCLIENTDECODEERR;
    }} catch (...) {{
        callback_{function_name}_exception(ksf::KSFCLIENTDECODEERR);
        return ksf::KSFCLIENTDECODEERR;
    }}

    return ksf::KSFSERVERSUCCESS;
}}
"""

template_onDispatch_coroutine = """\
int onDispatch(ksf::ReqMessagePtr msg) override {{
    static std::string __{interface_name}_all[] = {{"{'", "'.join(function_names)}"}};

    std::pair<std::string *, std::string *> r = equal_range(__{interface_name}_all, __{interface_name}_all + {len(function_names)}, msg->request.sFuncName);

    if (r.first == r.second) {{
        return ksf::KSFSERVERNOFUNCERR;
    }}

    switch (r.first - __{interface_name}_all) {{
{add_lines(func_case_str, 2)}
    }} //end switch
    
    return ksf::KSFSERVERNOFUNCERR;
}} //end onDispatch
"""

# Promise模式CallBackPromise类
# 填充 interface_name, function_name, output_parsed_list
template_callback_promise_class = """\
public:
    struct Promise{function_name}: virtual public KS_HandleBase 
    {{
{add_lines(output_parsed_list, 2)}
        std::map<std::string, std::string> _mRspContext;
    }};
        
    using Promise{function_name}Ptr = ksf::KS_AutoPtr<{interface_name}PrxCallbackPromise::Promise{function_name}>;
    
    {interface_name}PrxCallbackPromise(const ksf::Promise<{interface_name}PrxCallbackPromise::Promise{function_name}Ptr> &promise): _promise_{function_name}(promise) {{}}
    
    virtual void callback_{function_name}(const {interface_name}PrxCallbackPromise::Promise{function_name}Ptr &ptr) {{
        _promise_{function_name}.setValue(ptr);
    }}
    
    virtual void callback_{function_name}_exception(ksf::Int32 ret) {{
        std::stringstream oss;
        oss << "Function:{function_name}_exception|Ret:";
        oss << ret;
        _promise_{function_name}.setException(ksf::copyException(oss.str(), ret));
    }}
    
protected:
    ksf::Promise<{interface_name}PrxCallbackPromise::Promise{function_name}Ptr > _promise_{function_name};
"""

# Coroutine模式CallBack类
# 填充 interface_name, on_dispatch
template_callback_coroutine_class = """\
class {interface_name}CoroPrxCallback : public {interface_name}PrxCallback
{{
public:
    ~{interface_name}CoroPrxCallback() override = default;

public:
    const std::map<std::string, std::string> &getResponseContext() const override {{ return _mRspContext; }}
    
    virtual void setResponseContext(const std::map<std::string, std::string> &mContext) {{ _mRspContext = mContext; }}

public:
{add_lines(on_dispatch, 1)}

protected:
    std::map<std::string, std::string> _mRspContext;
}}; //end {interface_name}CoroPrxCallback

typedef ksf::KS_AutoPtr<{interface_name}CoroPrxCallback> {interface_name}CoroPrxCallbackPtr;

"""

# Proxy类
# 填充 interface_name, functions
template_proxy_class = """\
class {interface_name}Proxy : public ksf::Agent
{{
public:
    using _Context_ = std::map<std::string, std::string>;
    using _Status_ = std::map<std::string, std::string>;
    
public:
/*
 * ksf关联函数
 */
    {interface_name}Proxy* ksf_hash(uint32_t key) {{
        return ({interface_name}Proxy*)Agent::ksf_hash(key);
    }}

    {interface_name}Proxy* ksf_consistent_hash(uint32_t key) {{
        return ({interface_name}Proxy*)Agent::ksf_consistent_hash(key);
    }}

    {interface_name}Proxy* ksf_open_trace(bool traceParam = false) {{
        return ({interface_name}Proxy*)Agent::ksf_open_trace(traceParam);
    }}

    {interface_name}Proxy* ksf_set_timeout(int msecond) {{
        return ({interface_name}Proxy*)Agent::ksf_set_timeout(msecond);
    }}

    static const char* ksf_prxname() {{ return "{interface_name}Proxy"; }}
    
public:
{add_lines(functions, 1)}
}}; //end {interface_name}Proxy

using {interface_name}Prx = ksf::KS_AutoPtr<{interface_name}Proxy>;

"""

# Proxy类函数
# 填充 function_name, interface_name,
# 填充 input_arguments, output_arguments, return_type, return_line, comment
# 填充 argument_request_context, argument_response_context
# 填充 argument_async_callback, argument_coroutine_callback
template_proxy_function = """\
{comment}\
{return_type} {function_name}({add_connect(', ', arguments, argument_request_context, argument_response_context)}) {{
    ksf::KsfOutputStream<ksf::BufferWriterVector> _os;
{add_lines(input_argument_declare, 1)}
    _Status_ _status_;
    std::shared_ptr<ksf::ResponsePacket> rsp = ksf_invoke(ksf::KSFNORMAL, "{function_name}", _os, _context_, _status_);
    
    if (_rsp_context_) {{
        _rsp_context_->swap(rsp->context);
    }}

    ksf::KsfInputStream<ksf::BufferReader> _is;
    _is.setBuffer(rsp->sBuffer);
{add_lines(output_argument_declare, 1)}
    {return_line}
}}

void async_{function_name}({add_connect(', ', argument_async_callback, input_arguments, argument_request_context)}) {{
    ksf::KsfOutputStream<ksf::BufferWriterVector> _os;
{add_lines(input_argument_declare, 1)}
    _Status_ _status_;
    ksf_invoke_async(ksf::KSFNORMAL, "{function_name}", _os, _context_, _status_, callback);
}}

ksf::Future<{interface_name}PrxCallbackPromise::Promise{function_name}Ptr> \
promise_async_{function_name}({add_connect(', ', input_arguments, argument_request_context)}) {{
    ksf::Promise<{interface_name}PrxCallbackPromise::Promise{function_name}Ptr> promise;
    {interface_name}PrxCallbackPromisePtr callback = new {interface_name}PrxCallbackPromise(promise);

    ksf::KsfOutputStream<ksf::BufferWriterVector> _os;
{add_lines(input_argument_declare, 1)}
    _Status_ _status_;
    
    ksf_invoke_async(ksf::KSFNORMAL, "{function_name}", _os, _context_, _status_, callback);

    return promise.getFuture();
}}

void coro_{function_name}({add_connect(', ', argument_async_callback, input_arguments, argument_request_context)}) {{
    ksf::KsfOutputStream<ksf::BufferWriterVector> _os;
{add_lines(input_argument_declare, 1)}
    _Status_ _status_;
    ksf_invoke_async(ksf::KSFNORMAL, "{function_name}", _os, _context_, _status_, callback, true);
}}
"""

############################################################################################################
# 服务端接口类同步方法纯虚函数
# 填充 function_name, arguments, argument_current, return_type, comment
template_server_pure_function = """\
{comment}\
virtual {return_type} {function_name}({add_connect(', ', arguments, argument_current)}) = 0;
"""

# 服务端接口类异步应答
# 填充 function_name, arguments, argument_current, return_type, comment
template_server_async_function = """\
static void async_response_{function_name}({add_connect(', ', argument_current, arguments)}) {{
    switch (_current_->getRequestVersion()) {{
{add_lines(async_response_case, 2)}
    default: std::runtime_error("unsupported ksf packet version" + std::to_string(_current_->getRequestVersion()));
    }} // end switch
}} // end async_response_{function_name}
"""

# 服务端接口类推送应答
# 填充 function_name, arguments, argument_current, return_type, comment
template_server_push_function = """\
static void async_response_push_{function_name}({add_connect(', ', argument_current, arguments, argument_request_context)}) {{
{add_lines(push_func_case, 1)}
}}
"""

# 服务端接口类推送应答单ksf版
# 填充 function_name, arguments
template_server_push_function_ksf = """\
ksf::KsfOutputStream<ksf::BufferWriterVector> _os;
{add_lines(arguments)}
_current_->sendPushResponse(ksf::KSFSERVERSUCCESS, "{function_name}", _os, _context_);\
"""

# 服务端接口类异步应答case-ksf
# 填充 function_name, arguments, argument_current, return_type, comment
template_server_async_response_case_ksf = """\
case ksf::KSFVERSION: {{
    ksf::KsfOutputStream<ksf::BufferWriterVector> _os;
{add_lines(arguments, 1)}
    _current_->sendResponse(ksf::KSFSERVERSUCCESS, _os);
    break;
}}"""

# 服务端接口类异步应答case-json
# 填充 function_name, arguments, argument_current, return_type, comment
template_server_async_response_case_json = """\
case ksf::JSONVERSION: {{
    ksf::JsonValueObjPtr _p = new ksf::JsonValueObj();
{add_lines(arguments, 1)}
    std::vector<char> sJsonResponseBuffer;
    ksf::KS_Json::writeValue(_p, sJsonResponseBuffer);
    _current_->sendResponse(ksf::KSFSERVERSUCCESS, sJsonResponseBuffer);
    break;
}}"""

# 服务端接口类异步应答case-kup
# 填充 function_name, arguments, argument_current, return_type, comment
template_server_async_response_case_kup = """\
case ksf::KUPVERSION: {{
    ksf::kup::UniAttribute<ksf::BufferWriterVector, ksf::BufferReader> _ksfAttr_;
    _ksfAttr_.setVersion(_current_->getRequestVersion());
{add_lines(arguments, 1)}
    std::vector<char> sKupResponseBuffer;
    _ksfAttr_.encode(sKupResponseBuffer);
    _current_->sendResponse(ksf::KSFSERVERSUCCESS, sKupResponseBuffer);
    break;
}}"""

# 服务端接口类异步应答链路追踪
# 填充 function_name, arguments, argument_current, return_type, comment
template_server_async_response_trace = """\
if (_current_->isTraced()) {{
    std::string _trace_param_;
    int _trace_param_flag_ = ksf::ServantProxyThreadData::needTraceParam(ksf::ServantProxyThreadData::TraceContext::EST_SS, _current_->getTraceKey(), _rsp_len_);
    if (ksf::ServantProxyThreadData::TraceContext::ENP_NORMAL == _trace_param_flag_) {{
        ksf::JsonValueObjPtr _p_ = new ksf::JsonValueObj();
        {return_type}
        _trace_param_ = ksf::KS_Json::writeValue(_p_);
    }} else if(ksf::ServantProxyThreadData::TraceContext::ENP_OVERMAXLEN == _trace_param_flag_) {{
        _trace_param_ = "{{\"trace_param_over_max_len\":true}}";
    }}
    
    KSF_TRACE(_current_->getTraceKey(), TRACE_ANNOTATION_SS, "", ksf::ServerConfig::Application + "." + ksf::ServerConfig::ServerName, "{function_name}", 0, _trace_param_, "");
}}
"""

############################################################################################################
# 服务端接口类
# 填充 interface_name, comment, functions, async_functions, push_functions
template_server_interface = """\
class {interface_name} : public ksf::Servant
{{
public:
    ~{interface_name}() override = default;
    
protected:
    using _Context_ = std::map<std::string, std::string>;
    using _Status_ = std::map<std::string, std::string>;
    
public:
    /*必须继承并实现的函数*/

{add_lines(functions, 1)}
public:
    /*异步应答的封装函数*/
    
{add_lines(async_functions, 1)}
public:
    /*推送应答的封装函数*/
    
{add_lines(push_functions, 1)}
public:
    /*分发函数*/
    
{add_lines(dispatch, 1)}

}}; // end {interface_name}

"""

# 命名空间
template_namespace = """\
{module_begin}
{add_lines(elements)}
{module_end}
"""

# 头文件描述
template_header_description = """\
/**
 * @brief {file_name} generated by ksfctl
 * @date {date}
 * @version {version}
 */
"""

# 头文件内容
template_header = """\
{header_description}
#pragma once
    
{add_lines(import_headers)}


{add_lines(namespaces)}
    
"""

############################################################################################################
# 结构体模版
# 填充 struct_name, comment, members
template_struct = """\
{comment}\
struct {struct_name} : public ksf::Struct
{{
{variables}

public:
    ///获取类名
    static std::string className() {{
        return "{module_name}::{struct_name}";
    }}
    
    ///获取类的md5
    static std::string MD5() {{
        return "{md5sum}";
    }}
    
public:
{add_lines(struct_functions, 1)}
}}; // end {struct_name}

{add_lines(struct_operators)}
"""

template_struct_export = """\
{comment}\
struct {struct_name}
{{
{add_lines(variables, 1)}

public:
    using __self__ = {struct_name}; //结构体自指标识
    
public:
{add_lines(struct_functions, 1)}
}}; // end {struct_name}
"""

template_struct_wrap = """\
template<> 
struct ksf::Wrap<{struct_name}> : public ksf::Struct
{{
public:
    {struct_name} sobj; //结构体对象
    {struct_name} &obj; //结构体对象引用

public:
    ///获取类名
    static std::string className() {{
        return "{struct_name}";
    }}
    
    ///获取类的md5
    static std::string MD5() {{
        return "{md5sum}";
    }}

public:
    ///构造函数&析构函数
    Wrap(): obj(sobj) {{obj.resetDefault();}}
    Wrap(Wrap&& wrap): sobj(std::move(wrap.sobj)), obj(sobj) {{}}
    Wrap({struct_name}& object): obj(object) {{}}
    Wrap(const {struct_name}& object): obj(*(const_cast<{struct_name}*>(&object))) {{}}
    virtual ~Wrap() = default;

public:
{add_lines(struct_functions, 1)}
}}; // end {struct_name}

{namespace_left} using {struct_name_without_namespace}Wrap = ksf::Wrap<{struct_name}>; {namespace_right}

{add_lines(struct_operators)}
"""