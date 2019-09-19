def head(elems):
    out = []
    for elem in elems:
        out.append(f'<th>{elem}</th>')

    out = ''.join(out)

    return f'<tr>{out}</tr>'


def row(elems):
    out = []
    for elem in elems:
        out.append(f'<td>{elem}</td>')

    out = ''.join(out)

    return f'<tr>{out}</tr>'


def to_html(h, d):
    table = []
    table.append(head(h))
    table.extend(row(r) for r in d)

    table = ''.join(table)

    return f'<table>{table}</table>'
