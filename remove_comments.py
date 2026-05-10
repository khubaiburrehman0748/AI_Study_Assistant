import io
import os
import re
import tokenize
from pathlib import Path

root = Path(__file__).parent

py_files = list(root.glob('backend/**/*.py')) + list(root.glob('frontend/**/*.py'))
js_files = list(root.glob('frontend/static/js/**/*.js'))
css_files = list(root.glob('frontend/static/css/**/*.css'))
html_files = list(root.glob('frontend/templates/**/*.html'))
env_files = [root / 'backend' / '.env', root / 'backend' / '.env.example']


def strip_python(path):
    data = path.read_bytes()
    try:
        tokens = tokenize.tokenize(io.BytesIO(data).readline)
    except tokenize.TokenError:
        return
    out = []
    prev_end = (1, 0)
    for tok in tokens:
        tok_type = tok.type
        tok_string = tok.string
        start, end = tok.start, tok.end
        if tok_type == tokenize.ENCODING or tok_type == tokenize.ENDMARKER:
            continue
        if tok_type == tokenize.COMMENT:
            continue
        if prev_end[0] < start[0]:
            out.append('\n' * (start[0] - prev_end[0]))
            out.append(' ' * start[1])
        elif prev_end[1] < start[1]:
            out.append(' ' * (start[1] - prev_end[1]))
        out.append(tok_string)
        prev_end = end
    path.write_text(''.join(out), encoding='utf-8')


def strip_c_like_comments(text, line_comments=True):
    res = []
    i = 0
    n = len(text)
    state = 'NORMAL'
    while i < n:
        ch = text[i]
        nxt = text[i+1] if i+1 < n else ''
        if state == 'NORMAL':
            if line_comments and ch == '/' and nxt == '/':
                i += 2
                while i < n and text[i] != '\n':
                    i += 1
                continue
            if ch == '/' and nxt == '*':
                i += 2
                while i < n and not (text[i] == '*' and i+1 < n and text[i+1] == '/'):
                    i += 1
                i += 2
                continue
            if ch == '"':
                res.append(ch); state = 'DQUOTE'; i += 1; continue
            if ch == "'":
                res.append(ch); state = 'SQUOTE'; i += 1; continue
            if ch == '`':
                res.append(ch); state = 'TEMPLATE'; i += 1; continue
            res.append(ch); i += 1
        elif state in ('DQUOTE', 'SQUOTE', 'TEMPLATE'):
            res.append(ch)
            if ch == '\\' and i + 1 < n:
                res.append(text[i+1]); i += 2; continue
            if state == 'DQUOTE' and ch == '"':
                state = 'NORMAL'
            elif state == 'SQUOTE' and ch == "'":
                state = 'NORMAL'
            elif state == 'TEMPLATE' and ch == '`':
                state = 'NORMAL'
            i += 1
        else:
            res.append(ch); i += 1
    return ''.join(res)


def strip_html_comments(text):
    return re.sub(r'<!--.*?-->', '', text, flags=re.S)


def strip_env(path):
    lines = path.read_text(encoding='utf-8').splitlines()
    new = []
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith('#'):
            continue
        if '#' in line:
            idx = line.find('#')
            before = line[:idx].rstrip()
            if before:
                new.append(before)
            else:
                continue
        else:
            new.append(line)
    if new:
        path.write_text('\n'.join(new) + '\n', encoding='utf-8')
    else:
        path.write_text('', encoding='utf-8')


for path in py_files:
    strip_python(path)
for path in js_files:
    content = path.read_text(encoding='utf-8')
    path.write_text(strip_c_like_comments(content, line_comments=True), encoding='utf-8')
for path in css_files:
    content = path.read_text(encoding='utf-8')
    path.write_text(strip_c_like_comments(content, line_comments=False), encoding='utf-8')
for path in html_files:
    content = path.read_text(encoding='utf-8')
    path.write_text(strip_html_comments(content), encoding='utf-8')
for path in env_files:
    if path.exists():
        strip_env(path)
print('done')
