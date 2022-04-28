# encoding: utf-8
from __future__ import print_function

import re
import sys
import time
import argparse
from functools import partial

from colorama import Fore, Style, init as Init


def put_color(string, color, bold=True):
    '''
    give me some color to see :P
    '''

    if color == 'gray':
        COLOR = Style.DIM+Fore.WHITE
    else:
        COLOR = getattr(Fore, color.upper(), "WHITE")

    return '{}{}{}{}'.format(
        Style.BRIGHT if bold else "",
        COLOR,
        string,
        Style.RESET_ALL
    )


def hashable(obj):
    try:
        hash(obj)
    except TypeError:
        return False

    return True


def _clear(string):
    try:
        str_result = str(string)
    except KeyboardInterrupt:
        raise
    except Exception:
        str_result = ""

    return re.sub(" at 0x[0-9a-f]*", '', str_result)


def _eval_func(raw):
    try:
        result = eval_func(raw)
    except KeyboardInterrupt:
        raise
    except Exception as e:
        result = None

    return result


def _safe_dir(raw, live, debug=False):
    sub_attr = []

    try:
        live.keys()
    except KeyboardInterrupt:
        raise
    except Exception:
        pass
    else:
        for d in live.keys():
            sub_attr.append('[{}]'.format(repr(d)))

    if isinstance(live, (list, tuple)):
        for i in range(len(live)):
            sub_attr.append('[{}]'.format(i))

    if callable(live):
        sub_attr.append('()')

    dir_raw = dir(live)
    for i, v in enumerate(dir_raw):
        sub_attr.append('.'+v)

    return sub_attr


def _safe_getattr(ins, key):
    try:
        result = getattr(ins, key, None)
    except KeyboardInterrupt:
        raise
    except Exception:
        result = None

    return result


class Dibber:
    def __init__(self):
        self.matched = {}
        self.chain = {}

        self.output_max_length = 100
        self._t = time.time()
        self._c = 0

        # fix dir() bug
        self.makeup_attr = [
            '.__base__',
            '.__globals__',
            '.__subclasses__',
        ]

        # do NOT search attr in this list
        self.black_attr = [
            'stdout',
            '__len__', '__format__', '__delattr__',
            '__ge__', '__eq__', '__doc__',
            '__str__', '__setattr__', '__sizeof__',
            '__le__', '__lt__', '__gt__', '__reduce__',
            '__hash__', '__reduce_ex__', '__rmul__',
            '__dir__', '__setitem__', '__reversed__',
            '__iter__', '__imul__', '__iadd__', '__repr__',
            '__ne__', '__ifloordiv__', '__iand__', '__getitem__',
            '__abs__', '__class_getitem__', '__get__', '__invert__',
            '__dict__', '__getattribute__', '__ipow__', '__irshift__',
            '__isub__', '__itruediv__', '__ixor__', '__lshift__',
            '__matmul__', '__mod__', '__mul__', '__neg__', '__next__',
            '__or__', '__and__', '__pos__', '__pow__', '__radd__',
            '__rand__', '__rand__', '__rdivmod__', '__rfloordiv__',
            '__rlshift__', '__rmatmul__', '__rmod__', '__rsub__',
            '__rshift__', '__rtruediv__', '__rxor__', '__xor__',
            '__truediv__', '__bool__', '__contains__', '__delitem__',
            '__ior__', '__ror__', '__sub__', '__xor__', '__length_hint__',
            '__add__', '__isabstractmethod__', '__divmod__', '__float__',
            '__floordiv__', '__int__', '__rpow__', '__truediv__',
            '__ceil__', '__floor__', '__getformat__', '__round__',
            '__set_format__', '__delete__', '__set__', '__ilshift__',
            '__imatmul__', '__imod__', '__index__', '__rrshift__', '__bytes__',
        ]

        # do NOT call these class func
        self.black_callable_class = [
            "site._Helper", "site.Quitter",
            "site.license", "site._Printer",
        ]

        # do NOT call these func
        self.black_callable = [
            '__main__.', '_weakrefset.', 're.',
            '_ctypes.CField',
            'Barrier', 'ModuleSpec',
            '_shutdown', '_signal.pause',
            '_sitebuiltins.', '_start_new_thread',
            '_stop', '_thread.interrupt_main', '_weakrefset._commit_removals',
            'base64.test', 'configparser.SafeConfigParser',
            'contextlib.aclose', 'exit', 'exit_thread',
            'locale._print_locale', 'os.tempnam', 'poll.poll',
            'posix.abort', 'posix.abort', 'posix.fork', 'posix.forkpty',
            'posix.tempnam', 'posix.tmpnam', 'posix.wait',
            'pprint.PrettyPrinter', 'pprint._perfcheck',
            'signal.default_int_handler', 'signal.pause',
            'site._Helper', 'site._script', 'socket',
            'start_new', 'start_new_thread',
            'sys._debugmallocstats', 'sys.exc_clear', 'sysconfig._main',
            'threading.Event', 'threading.Thread',
            'traceback.print_exc', 'traceback.print_stack',
            'uu.test', 'zlib.Compress', 'zlib.Decompress', 'zlib.decompressobj',
            'breakpoint', 'breakpointhook',
            'help', "print", "input", "raw_input", "copyright"
        ] + [
            # common
            "_test", "_shutdown", "main", "writelines",

            # int
            '.bit_length', '.conjugate',

            # float
            '.as_integer_ratio', '.conjugate', '.fromhex', '.hex', '.is_integer',

            # str
            '.capitalize', '.center', '.count', '.decode', '.encode', '.endswith',
            '.expandtabs', '.find', '.format', '.index', '.isalnum', '.isalpha',
            '.isdigit', '.islower', '.isspace', '.istitle', '.isupper', '.join',
            '.ljust', '.lower', '.lstrip', '.partition', '.replace', '.rfind',
            '.rindex', '.rjust', '.rpartition', '.rsplit', '.rstrip', '.split',
            '.splitlines', '.startswith', '.strip', '.swapcase', '.title',
            '.translate', '.upper', '.zfill',

            # set
            '.add', '.clear', '.copy', '.difference', '.difference_update', '.discard',
            '.intersection', '.intersection_update', '.isdisjoint', '.issubset',
            '.issuperset', '.pop', '.remove', '.symmetric_difference',
            '.symmetric_difference_update', '.union', '.update',

            # dict
            '.clear', '.copy', '.fromkeys', '.get', '.has_key', '.items', '.iteritems',
            '.iterkeys', '.itervalues', '.keys', '.pop', '.popitem', '.setdefault',
            '.update', '.values', '.viewitems', '.viewkeys', '.viewvalues',

            # list & tuple
            '.append', '.count', '.extend', '.index', '.insert', '.pop', '.remove',
            '.reverse', '.sort',
        ]

    def _dir(self, raw):
        live = _eval_func(raw)
        if live is None:
            return []

        dir_result = _safe_dir(raw, live)
        for i in self.makeup_attr:
            if i not in dir_result:
                dir_result.append(i)

        return dir_result

    def _check_func(self, raw, live, attr_path=[]):
        try:
            result = check_func(raw, live)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            result = None

        if result and shortest:
            if len(raw) > args.max_length:
                return False
            else:
                args.max_length = len(raw)

        if result:
            for i in attr_path:
                live_cache = _eval_func(i)
                if hashable(live_cache) and live_cache:
                    self.chain[live_cache] = raw[len(i):]

        return result

    def _clear_line(self):
        print(' '*self.output_max_length, end="\r")

    def _truncate(self, string):
        if len(string) > self.output_max_length-5:
            string = string[:self.output_max_length]+' ...'

        self._clear_line()
        print(string, end="\r")

    def _visit(self, node, depth=0, attr_path=[]):
        tip = "running in depth"

        # 避免进度指示循环过快
        t = time.time()
        if t - self._t > 0.1:
            self._t = t
            self._c = (self._c+1) % len(tip)

        if depth == max_depth:
            return

        if depth:
            self._truncate(
                '{} {}: ... {}'.format(
                    tip[:self._c]+tip[self._c].upper()+tip[self._c+1:],
                    depth+1,
                    node[self.init_length:]
                ),
            )

        depth += 1
        sub_attrs = self._dir(node)
        for index, sub_attr in enumerate(sub_attrs):
            if depth == 1 and verbose:
                self._clear_line()
                print('[+] {} of {}'.format(index+1, len(sub_attrs)))

            if sub_attr[1:] in self.black_attr:
                continue

            raw = node + sub_attr
            live = _eval_func(raw)
            if live is None:
                continue

            _module = _safe_getattr(live, '__module__') or ''
            if callable(live):
                _name = _safe_getattr(live, '__name__') or ''
                _qname = _safe_getattr(live, '__qualname__')
                if any([i in self.black_callable for i in [
                    _module+'.'+_name, _qname, _module+'.', _name
                ]]) or (_safe_getattr(live, '__class__') and any([
                    i in str(live.__class__) for i in
                    self.black_callable_class
                ])):
                    continue

            if self._check_func(raw, live, attr_path=attr_path):
                self._clear_line()
                if not verbose:
                    print(
                        '[+] {} of {}'.format(index+1, len(sub_attrs))
                    )

                print("  [-] find: {}".format(put_color(raw, "green")))

                continue

            if not disable_cache and hashable(live) and live in self.chain:
                new_raw = raw + self.chain[live]
                live_cache = _eval_func(new_raw)
                if live_cache and self._check_func(new_raw, live_cache):
                    self._clear_line()
                    print(
                        "  [-] find in cache: {}".format(
                            put_color(new_raw, "cyan"))
                    )
                    continue

            self._visit(raw, attr_path=attr_path+[raw], depth=depth)

    def run(self, strings):
        if verbose:
            print('[+] check init payload')

        try:
            live = eval_func(strings)
        except Exception as e:
            print('[x] init payload is invalid: {}'.format(put_color(e, "red")))
            return

        self.init_length = len(strings)
        if self._check_func(strings, live, attr_path=[]):
            if not verbose:
                print('[+] check init payload')

            print("  [-] find: " + strings)

        self._visit(strings, depth=0)


VERSION = "1.0"
Init()

print("""
┌┬┐{}┌┐ ┌┐ ┌─┐┬─┐
 ││{}├┴┐├┴┐├┤ ├┬┘
─┴┘{}└─┘└─┘└─┘┴└─ v{}{}{}
""".format(*([
    put_color(i, 'yellow')
    for i in ['┬', '│', '┴']
] + [Fore.GREEN, VERSION, Style.RESET_ALL]
)))

parser = argparse.ArgumentParser(
    description='Version: {}; Supported all python versions'.format(VERSION))
parser.add_argument(
    "input",
    help="input the initial searching instance"
)

parser.add_argument(
    "--check", required=True,
    help="how to check the payload?"
)

parser.add_argument(
    "--depth", default=3, type=int,
    help="max searching depth"
)
parser.add_argument(
    "--disable-cache", action="store_true", default=False,
    help="disable cache"
)
parser.add_argument(
    "--verbose", default=1, type=int,
    help="verbose level"
)

parser.add_argument(
    "--dir", default="dir",
    help="how to get the attributes?"
)

parser.add_argument(
    "--eval", default="eval",
    help="how to turn the payload from string-format to instance?"
)

parser.add_argument(
    "--debug", action="store_true", default=False,
    help="run in debug mode"
)
parser.add_argument(
    "--mini", action="store_true",
    help="find the shortest payload"
)

args = parser.parse_args()
dir_func_name = args.dir
check_func_name = args.check
eval_func_name = args.eval
init_input = args.input
shortest = args.mini
max_depth = args.depth
debug = args.debug
verbose = args.verbose
disable_cache = args.disable_cache

try:
    check_func = __import__(
        "check_func.{}".format(check_func_name), fromlist=[""]
    ).run
except Exception as e:
    sys.exit(
        '[!] load check_func `{}` failed: {}'.format(
            check_func_name, put_color(e, "red")
        )
    )

try:
    eval_func = __import__(
        "eval_func.{}".format(eval_func_name), fromlist=[""]
    ).run
except Exception as e:
    sys.exit(
        '[!] load eval_func `{}` failed: {}'.format(
            eval_func_name, put_color(e, "red")
        )
    )

if shortest:
    args.max_length = 1000

mro_finder = Dibber()
mro_finder.run(init_input)
