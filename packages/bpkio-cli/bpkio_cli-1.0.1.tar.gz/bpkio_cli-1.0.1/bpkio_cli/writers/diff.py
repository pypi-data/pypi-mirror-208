import difflib

import click

red = lambda text: click.style(text, fg="red", strikethrough=True)
green = lambda text: click.style(text, fg="green", underline=True)
blue = lambda text: click.style(text, fg="blue")
white = lambda text: click.style(text, fg="white")


def generate_diff(old, new):
    result = ""
    codes = difflib.SequenceMatcher(a=old, b=new).get_opcodes()
    for code in codes:
        if code[0] == "equal":
            result += white(old[code[1] : code[2]])
        elif code[0] == "delete":
            result += red(old[code[1] : code[2]])
        elif code[0] == "insert":
            result += green(new[code[3] : code[4]])
        elif code[0] == "replace":
            # result += red(old[code[1] : code[2]]) + green(new[code[3] : code[4]])
            result += green(new[code[3] : code[4]])
    return result
