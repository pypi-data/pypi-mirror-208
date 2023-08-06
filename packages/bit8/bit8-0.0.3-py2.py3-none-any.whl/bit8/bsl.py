def parse_file(f):
    if type(f) is str: f = open(f)
    r = {}
    cur = None
    w = 0
    for line in f:
        if line[0] == ':':
            cur = line[1:].strip('\n')
            r[cur] = []
        elif line[0] == '|':
            if line[1] == '=':
                w = line.count('=')
            else:
                r[cur].append(list(line.strip()[1:w+1].ljust(w, ' ')))
    return r
