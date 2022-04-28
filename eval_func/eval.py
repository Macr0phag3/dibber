def run(string):
    result = eval(string)
    if isinstance(result, (int, float, bool, str, bytes)):
        return None

    return result
