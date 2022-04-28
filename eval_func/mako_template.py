import pickle
import __main__

from mako.template import Template


def run(string):
    # come on, be a hack! :)
    Template(
        "${ setattr(__import__('__main__'), 'result', "+string+") }"
    ).render()
    return __main__.result
