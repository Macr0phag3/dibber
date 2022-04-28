import pickle
import __main__

from jinja2 import Template


def run(string):
    # come on, be a hack! :)
    Template(
        "{{ setattr(__import__('__main__'), 'result', "+string+") }}"
    ).render(setattr=setattr, __import__=__import__)
    return __main__.result
