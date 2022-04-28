# dibber

用于搜索 Python 特定的对象/函数/模块，产出的 payload 的可用于 Python 沙箱逃逸、SSTI 等等。

## help

<img src="/pics/help.png" width="600">


```bash
usage: dibber.py [-h] --check CHECK [--depth DEPTH] [--disable-cache] [--verbose VERBOSE] [--dir DIR] [--eval EVAL] [--debug] [--mini] input

Version: 1.0; Supported all python versions

positional arguments:
  input              input the initial searching instance

optional arguments:
  -h, --help         show this help message and exit
  --check CHECK      how to check the payload?
  --depth DEPTH      max searching depth
  --disable-cache    disable cache
  --verbose VERBOSE  verbose level
  --dir DIR          how to get the attributes?
  --eval EVAL        how to turn the payload from string-format to instance?
  --debug            run in debug mode
  --mini             find the shortest payload

```

## cookbook
理论上支持所有版本的 Python

### 示例
1. 搜索 python code `"".__class__.__mro__[-1].__subclasses__()` 的利用链：`python dibber.py --check run_script_os --depth 6 '"".__class__.__mro__[-1].__subclasses__()'`

<img src="/img/exp1.png" width="600">

1. 搜索 jinja2 `self` 的利用链：`python dibber.py --check keyword_check --eval jinja2_template 'self' --depth 4`

<img src="/img/exp2.png" width="600">

1. 搜索 mako `self` 的利用链：`python dibber.py --check keyword_check --eval mako_template 'context' --depth 4`

<img src="/img/exp3.png" width="600">

### 编写插件

有两个文件夹：
1. `check_func`: 这里面的函数用于检查是否成功找到一条利用链
1. `eval_func`: 这里面的函数执行字符串形式的代码，返回执行的结果

如果有特殊的需要（例如需要特殊的检查逻辑或者遇到特殊的模板无法直接 eval 等），直接按照已有插件，新增即可。

## supported
- [x] raw python code
- [x] flask
- [x] mako

## Others
<img src="https://clean-1252075454.cos.ap-nanjing.myqcloud.com/20200528120800990.png" width="500">

[![Stargazers over time](https://starchart.cc/Macr0phag3/dibber.svg)](https://starchart.cc/Macr0phag3/dibber)
