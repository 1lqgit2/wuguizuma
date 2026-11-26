import sys

def check(path):
    s = open(path, encoding="utf-8").read()
    i = 0
    n = len(s)
    depth = 0
    par = 0
    while i < n:
        c = s[i]
        if c == '/' and i + 1 < n and s[i+1] == '/':
            while i < n and s[i] != '\n':
                i += 1
        elif c == '/' and i + 1 < n and s[i+1] == '*':
            i += 2
            while i + 1 < n and not (s[i] == '*' and s[i+1] == '/'):
                i += 1
            i += 2
        elif c == '@' and i + 1 < n and s[i+1] == '"':
            i += 2
            while i < n:
                if s[i] == '"':
                    if i + 1 < n and s[i+1] == '"':
                        i += 2
                        continue
                    i += 1
                    break
                i += 1
        elif c == '"':
            i += 1
            while i < n:
                if s[i] == '\\':
                    i += 2
                    continue
                if s[i] == '"':
                    i += 1
                    break
                i += 1
        elif c == "'":
            i += 1
            while i < n:
                if s[i] == '\\':
                    i += 2
                    continue
                if s[i] == "'":
                    i += 1
                    break
                i += 1
        else:
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
            elif c == '(':
                par += 1
            elif c == ')':
                par -= 1
            i += 1
    print(path, "brace", depth, "paren", par)

for p in sys.argv[1:]:
    check(p)
