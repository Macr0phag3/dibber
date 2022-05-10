import __main__

from flask import Flask, render_template_string, request


app = Flask(__name__)
app.debug = True


@app.route('/')
def hello():
    user = request.args.get("payload")
    return render_template_string(
        user,
        setattr=setattr,
        __import__=__import__,
    )


def run(string):
    app.test_client().get(
        '/', query_string={
            "payload":
            "{{ setattr(__import__('__main__'), 'result', "+string+") }}"
        }
    ).get_data(as_text=True)

    return __main__.result
