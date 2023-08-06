
# Table Symbols

horizontal_table_symbol = '║'
first_table_symbols = ['═', '╔', '╚', '╠']
between_table_symbol = ['═', '╦', '╩', '╬']
last_table_symbol = ['═', '╗', '╝', '╣']

# ─ ━ │ ┃ ┄ ┅ ┆ ┇ ┈ ┉ ┊ ┋ ┌ ┍ ┎ ┏
# ┐ ┑ ┒ ┓ └ ┕ ┖ ┗ ┘ ┙ ┚ ┛ ├ ┝ ┞ ┟
# ┠ ┡ ┢ ┣ ┤ ┥ ┦ ┧ ┨ ┩ ┪ ┫ ┬ ┭ ┮ ┯
# ┰ ┱ ┲ ┳ ┴ ┵ ┶ ┷ ┸ ┹ ┺ ┻ ┼ ┽ ┾ ┿
# ╀ ╁ ╂ ╃ ╄ ╅ ╆ ╇ ╈ ╉ ╊ ╋ ╌ ╍ ╎ ╏
# ═ ║ ╒ ╓ ╔ ╕ ╖ ╗ ╘ ╙ ╚ ╛ ╜ ╝ ╞ ╟
# ╠ ╡ ╢ ╣ ╤ ╥ ╦ ╧ ╨ ╩ ╪ ╫ ╬ ╭ ╮ ╯
# ╰ ╱ ╲ ╳ ╴ ╵ ╶ ╷ ╸ ╹ ╺ ╻ ╼ ╽ ╾ ╿


# Formatting

align_left = 'left'
align_center = 'center'
align_right = 'right'
align_space = 'space'


def split_line_breaker(s :str):
    return s.splitlines()


def join_line_list(l: list):
    return '\n'.join(l)


def too_long_world_split(word, max_length):
    min_length = int(max_length * 0.4)
    rest_length = len(word)

    if '.' in word:
        parts = word.split('.')
        s = parts.pop(0)
        for p in parts:
            new_length = len(s) + len(p)
            if new_length < max_length and (rest_length > min_length or new_length < min_length):
                s = s + '.' + p

                rest_length = rest_length - len(p) - 1
            else:
                yield s

                s = p
        yield s


def line_word_split(line: str, max_length):
    words = line.strip().split(' ')

    for w in words:
        if len(w) < max_length:
            yield w
        else:
            yield from too_long_world_split(w, max_length)


def word_text_splitter(s: str, max_length):
    s = s.strip()
    lines = split_line_breaker(s)
    # lines = [l.strip().split(' ') for l in lines]
    for l in lines:
        yield list(line_word_split(l, max_length))


def format_line(line: str, width: int, align=align_left, fill_up=' '):
    if align == align_left:
        r = line.ljust(width, fill_up)
    elif align == align_center:
        r = line.center(width, fill_up)
    elif align == align_right:
        r = line.rjust(width, fill_up)
    elif align == align_space:
        l = line.split('[SPACE]')
        l = [i.strip() for i in l]
        width_line = sum([len(i) for i in l])
        quote_width = (width - width_line)  # todo handling multiple space in 1 line
        space = ' ' * quote_width
        line = space.join(l)
        f_str = '{0:%s^%d}' % (fill_up, width)
        r = f_str.format(line)
    else:
        raise "Format Align not exist"

    return r


def parse_margin(top=1, bottom=1, left=2, right=2):
    return top, bottom, left, right


def text_formatter(s: str, max_lenght: int, text_align=align_left, margin=None):
    out_lines = []
    if margin is None:
        margin = {}
    top, bottom, left, right = parse_margin(**margin)

    text_max_width = max_lenght - left - right

    for words_line in word_text_splitter(s, text_max_width):
        line = []
        line_width = 0
        for word in words_line:
            len_word = len(word) + 1
            if line_width + len_word <= text_max_width:
                line.append(word)
                line_width = line_width + len_word
            else:
                out_lines.append(line)
                line = [word]
                line_width = len_word
        out_lines.append(line)

    # do margin
    top, bottom, left, right = parse_margin(**margin)
    for i in range(0, top):
        out_lines.insert(0, [' '])
    for i in range(0, bottom):
        out_lines.append([' '])

    l_marg = ' ' * left
    r_marg = ' ' * right

    text = [' '.join(l) for l in out_lines]
    text = [l_marg + format_line(l, text_max_width, text_align) + r_marg for l in text]
    text = join_line_list(text)
    return text


def format_sperator(raw):
    """
    # raw_seperator
    # [ 1 0 0 0 1 0 0 1 ]  ╔ ═ ═ ═ ╦ ═ ═ ╗
    # [ 3 0 0 0 3 0 0 3 ]  ╠ ═ ═ ═ ╬ ═ ═ ╣
    # [ 2 0 0 0 2 0 0 2 ]  ╚ ═ ═ ═ ╩ ═ ═ ╝

    # 1 -> ╔ ╦ ╗
    # 2 -> ╚ ╩ ╝
    # summe ---- 1 + 2 = 3
    # 3 -> ╠ ╬ ╣
    """
    start, middle_list, end = raw[0], raw[1:-1], raw[-1]
    t = first_table_symbols[start]
    for m in middle_list:
        t = t + between_table_symbol[m]
    t = t + last_table_symbol[end]
    return t


def format_column(text, width, align=align_left, margin=None):
    t = text_formatter(text, width, align, margin)
    return t


def format_row(columns):
    t = ""

    _width_cols = []
    _cols = []
    for col in columns:
        col_text = format_column(**col)
        _cols.append(col_text)
        col_width = col['width']
        _width_cols.append(col_width)

    # gen seperator line
    raw_seperator = [1]
    for c in _width_cols:
        raw_seperator.extend([0] * c)
        raw_seperator.append(1)

    _cols = [split_line_breaker(t) for t in _cols]
    _col_text_lines = []

    # gen row-text
    while True:
        _running = False
        _col_line = []
        for index, col in enumerate(_cols):
            if col:  # len min 1
                _col_line.append(col.pop())
                _running = True
            else:
                c = ' ' * _width_cols[index]
                _col_line.append(c)
        if _running:
            t = f"{horizontal_table_symbol}{horizontal_table_symbol.join(_col_line)}║"
            _col_text_lines.insert(0, t)
        else:
            break
    t = join_line_list(_col_text_lines)
    return raw_seperator, t


# table list
# [ { text , len , align, margin } | .... ]
# [ {text , len} | {text , len} ]
# [ {text , len} | { text , len , align, margin } ]
# [ {text , len} ]
# ....

def set_in_last_line_text(line_conf, line):
    text = line_conf['text']
    align = line_conf['align']
    len_text = len(text)

    formatted = format_line(text, len(line) - 2, align)
    for index, value in enumerate(formatted, start=1):
        if value != ' ':
            line = f"{line[:index]}{text}{line[index + len_text:]}"
            break
    return line


def format_table(table):
    next_bottom_line = None
    text_raws = []
    for row in table['table']:
        top_bottom_line, row = format_row(row)
        top_line = top_bottom_line
        bottom_line = [i * 2 for i in top_bottom_line]
        if next_bottom_line is None:  # first line
            _top_line_text = format_sperator(top_line)
            text_raws.append(_top_line_text)
        else:  # middle lines
            longer, shorter = (next_bottom_line, top_line) if len(next_bottom_line) > len(top_line) else \
                (top_line, next_bottom_line)
            for index, v in enumerate(shorter):
                longer[index] = longer[index] + v
            _middle_line_text = format_sperator(longer)
            text_raws.append(_middle_line_text)
        next_bottom_line = bottom_line
        text_raws.append(row)
    # last Line                                              # last Line
    _last_line_text = format_sperator(next_bottom_line)
    if 'bottom_line' in table:
        _last_line_text = set_in_last_line_text(table['bottom_line'], _last_line_text)

    text_raws.append(_last_line_text)
    return join_line_list(text_raws)


if __name__ == '__main__':
    title = "Test Title"

    description = '''
    Man sagt: „Immer wenn Menschen Vögel durch die Lüfte fliegen sehen, bekommen sie das Bedürfnis auf eine Reise zu gehen.“

    Kino no Tabi handelt von den Erlebnissen der Reisenden Kino und ihres sprechenden Motorrads Hermes. Auf ihren Wegen durch die Länder ihrer Welt treffen die beiden auf unzählige Personen, welche allesamt mit den unterschiedlichsten Problemen in ihrem jeweiligem Land zu kämpfen haben. Das Treffen mit den Reisenden, die die Rolle zweier kommentierender Beobachter übernehmen, ist für diese Menschen meist ein einschneidendes Ereignis in ihren Leben. Trotz seines Daseins als ein sprechendes Motorrad, fungiert Hermes hierbei als ein überraschend intelligenter und tiefsinniger Gesprächspartner Kinos, die wiederum ein nahezu geschlechtsneutrales und damit übertragbares und allgemeingültiges Auftreten an den Tag legt.

    Drei Tage lang bleiben sie jeweils in jedem der mittelalterlich anmutenden Länder. Sehend, lernend, philosophierend, aber niemals wertend, bevor sie sich ein weiteres Mal auf die Reise machen, denn das nächste Land in dieser tragisch-schönen Welt wartet schon auf sie.
    '''
    table_list = {
        'table': [
            [{"text": title, "width": 76, "align": "center"}],
            [{"text": description, "width": 76, "align": "left",
              "margin": {"top": 1, "bottom": 2, "left": 3, "right": 2}}],
            [{"text": title, "width": 30, "align": "left"}, {"text": title, "width": 30, "align": "right"}],
            [{"text": title, "width": 80, "align": "center"}],
            [{"text": title, "width": 60, "align": "center"}],
        ],
        'bottom_line': {"text": 'TEST', "align": "center"}
    }

    t = format_table(table_list)
    print(t)
