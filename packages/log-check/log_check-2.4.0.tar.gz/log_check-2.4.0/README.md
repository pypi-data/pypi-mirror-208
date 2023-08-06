# log_check

检查LOGI等日志函数的占位符`{}`数量和参数数量是否一致

### 安装

~~~
pip install log_check
~~~

### 使用方式：

```shell
logc [Files|Paths] [-S|-show_ok|-H|-hide_ok|-h|-help]
```

例如
```
logc
```

将检查当前目录下的所有 `.cpp`  `.hpp`  `.h` 文件

或者

```shell
// 1个或者多个文件
logc main.cpp
logc main.cpp a.cpp a.h a.hpp
find -name '*.cpp'|xargs logc
find -name '*.cpp' -or -name '*.hpp' -or '*.h'|xargs logc

// 一个或者多个文件夹
logc ./crcp
logc ./crcp ./file_transfer ./code_verify_lib

// 混合
logc ./crcp ./VideoSource ./main.cpp ./a.cpp
```

如果文件超过**128**个，则会不显示检查通过（ok）的文件，改为显示进度条

你可以通过`-s`, `-show_ok`或者`-h`,`-hide`选项控制是否显示检查通过的文件

### 提示

如果格式字符串中包含成对的 `{}` 但不是占位符或者包含转义的引号，则程序会误判为错误
详见样例代码 `xxx.cpp`


### 实现细节：

##### 1. 使用正则表达式  `(LOG[T|D|I|W|E|C]\(.*?\n{0,}.*?\);)` 匹配到函数。

由于可能会提前匹配到 `);` 导致错误：

~~~c++
LOGI(kTag, "({});", a);
~~~

本程序会通过结合括号匹配做修正

##### 2. 计算`{}`的数量
通过匹配`({.*?})`实现，所以如果有类似于`{a string}`等 `fmt::formt()`认为不是占位符的成对大括号，

##### 3. 计算参数个数

从第一个 `,` 后开始通过数**同层级**下 `,` 的个数，且计算`""`和`''`内的会被无视，所以能正确检查：

~~~
LOGW(kTag, "{}", f(g(h({1,2,3}))));
~~~


转义的单、双引（`\"` `\'`）号会提前去除，以避免对引号内外误判：

~~~c++
LOGI(kTag, ", \", ,{}", '\'');  -> LOGI(kTag, ", , ,{}", '');
~~~
