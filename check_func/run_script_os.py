import sys


def run(raw, live):
    if getattr(live, '__name__') == 'os':
        with open(".temp-result.py", "w") as fw:
            fw.write(raw)

        return not sys.modules['os'].system(
            sys.executable + ' .temp-result.py 2>/dev/null'
        )
