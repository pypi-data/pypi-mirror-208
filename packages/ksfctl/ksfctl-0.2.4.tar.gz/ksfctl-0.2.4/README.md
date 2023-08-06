# ksf-client

ksf命令行工具

## parse功能
```ksfctl parse```

### c++
```ksfctl parse cpp test.ksf```

文件类型为ksf，名称为test.ksf，生成的文件为test.h
```ksf
#include "const_definition.ksf"

module MyModule
{
    const string ABC = "123"; //测试一下啊

    /**
     * 测试一下我的用例
     */
    enum MyEnum2
    {
        ENM1 = 0x0,
        ENM2 = 0x1,
        ENM3 = 0b101,
        ENM4 = 0o101
    };

    /**
     * 定义第二个结构体
     */
    struct MySecond
    {
        0  require  bool                         BOOL1 = true;
        1  require  int                          ENM1;
        2  require  double                       ENM2;
        3  require  float                        ENM3;
        4  optional byte                         ENM4 = 1;
        5  optional string                       ENM5 = "'2'"; //测试
        6  require  MyModule::MyFirst            ENM51;
        7  require  MyEnum2                      ENM52;
        8  require  vector<string>               ENM61;
        9  require  vector<vector<MyFirst>>      ENM611;
        10 require  vector[set]<string>          ENM612;
        11 require  vector[hashset]<string>      ENM62;
        12 require  map<string, string>          ENM6;
        13 require  map<string, MyFirst>         ENM623;
        14 require  map[hashmap]<string, string> ENM7;
    };

    key[MySecond, ENM1, ENM4];

    interface TestObj
    {
        /**
         * 测试一下描述
         */
        MyFirst func(MyFirst first, out vector<MySecond> seconds);
        MyFirst func2(MyFirst first, out vector<MySecond> seconds);
        void func3(MyFirst first, out vector<MySecond> seconds);
    };
};
```

目前支持几种特殊机制：
1. 可以使用可选参数替换module名称为多级命名空间，如：--replace-namespace MyModule MyModule1::MyModule2::MyModule3
2. 可以使用可选参数替换包含的其他头文件的路径，如：--replace-include-path Test.h subdir/Test.h
3. 可以使用可选参数忽略所有的依赖目录层级，输出只包含头文件的include路径，--ignore-relative-path
4. 可以使用--current-priority/--no-current-priority，指定是否需要优先在当前目录查找头文件，如果不指定，则默认为true
5. 可以选择是否检测默认值  --check-default / --no-check-default，默认为true
6. 可以选择完全使用右值引用传递参数--param-rvalue-ref / --no-param-rvalue-ref，默认为false
7. 可以选择不生成推送接口--no-push / --push，默认为true