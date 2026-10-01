"""Template codec for the bundled index.html (rebuilt from the documented encoder).

Split at '<script type="__bundler/template">' ... '</script>'.
Body = newline + JSON + newline + TWO spaces ('\n  ').
Encode with json.dumps(src, ensure_ascii=False).replace('</', '<\\u002F').
"""
import json, sys

OPEN = '<script type="__bundler/template">'
CLOSE = '</script>'
LEAD, TAIL = '\n', '\n  '


def decode(html):
    i = html.index(OPEN) + len(OPEN)
    j = html.index(CLOSE, i)
    body = html[i:j]
    assert body.startswith(LEAD) and body.endswith(TAIL), 'template framing changed'
    return html[:i], json.loads(body[len(LEAD):-len(TAIL)]), html[j:]


def encode(pre, src, post):
    return pre + LEAD + json.dumps(src, ensure_ascii=False).replace('</', '<\\u002F') + TAIL + post


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'decode':   # codec.py decode <html> <app.html>
        pre, src, post = decode(open(sys.argv[2], encoding='utf-8').read())
        open(sys.argv[3], 'w', encoding='utf-8').write(src)
    elif cmd == 'encode':  # codec.py encode <base html> <app.html> <out html>
        pre, _, post = decode(open(sys.argv[2], encoding='utf-8').read())
        src = open(sys.argv[3], encoding='utf-8').read()
        open(sys.argv[4], 'wb').write(encode(pre, src, post).encode('utf-8'))
