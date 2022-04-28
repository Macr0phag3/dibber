import sys


def run(raw, live):
    if raw.split('.')[-1] == '__globals__':
        with open(".temp-result.py", "w") as fw:
            fw.write(raw)

        return not sys.modules['os'].system(
            sys.executable + ' .temp-result.py 2>/dev/null'
        )
