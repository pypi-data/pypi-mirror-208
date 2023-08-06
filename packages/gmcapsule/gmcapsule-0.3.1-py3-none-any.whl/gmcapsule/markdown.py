# Copyright (c) 2021 Jaakko Keränen <jaakko.keranen@iki.fi>
# License: BSD-2-Clause

import re, string


def sub_cb(pattern, repl, text, match_callback):
    """Substitute all matches of `pattern` with `repl` in `text`,
    calling `match_callback` for each matched region."""
    for m in pattern.finditer(text):
        match_callback(m)
    return pattern.subn(repl, text)[0]


def to_gemtext(src):
    src = src.replace('&nbsp;', '\u00a0')
    src = src.replace('```', '\n```\n')

    ptn_standalone_link = re.compile("^[\\s*_]*\\[(.+?)\\]\\(([^)]+)\\)[\\s*_]*$")
    ptn_image_link = re.compile("\n?!\\[(.+)\\]\\(([^)]+)\\)\n?")
    ptn_named_link = re.compile("\\[(.+?)\\]\\[(.+?)\\]")
    ptn_link = re.compile("\\[(.+?)\\]\\(([^)]+)\\)")
    ptn_name = re.compile("\\s*\\[(.+?)\\]\\s*:\\s*([^\n]+)")
    ptn_paragraph_break = re.compile("(\\s*\n){2,}")

    result = ''
    is_pre = False  # four-space indent
    is_block = False
    is_last_empty = False
    pending_links = []

    def add_pending_link(m):
        pending_links.append((m.group(2), m.group(1)))

    def add_pending_named_link(m):
        pending_links.append(('[]' + m.group(2), m.group(1)))

    def flush_pending_links(result):
        ptn_dest = re.compile("\n\\s*\\[(.+?)\\]\\s*:\\s*([^\n]+)")
        if len(result) and not result.endswith('\n'):
            result += "\n"
        for url, title in pending_links:
            if url.startswith('[]'):
                # Find the matching named link.
                dest = ptn_dest.search(src)
                if dest:
                    url = dest.group(2)
            result += f"=> {url} {title}\n"
        pending_links.clear()
        return result

    for line in src.split('\n'):
        if not (is_pre or is_block):
            if line == '```':
                is_block = True
                result += "\n```\n"
                continue
            if len(line) == 0:
                is_last_empty = True
                continue
            if is_last_empty:
                result += "\n\n"
            if line[:1] == '#':
                result = flush_pending_links(result)
                line += "\n"
            elif line[:1] == '>':
                result += "\n"
                line += "\n"
            elif line[:1] == '*':
                line += "\n"
            elif len(line) >= 2 and line[:1] in string.digits and \
                 (line[1] == '.' or
                  (line[1] in string.digits and line[2] == '.')):
                result += "\n\n"
                line += "\n"
            elif line[:1] == '|' and line[-1:] == '|':
                line += "\n"
            elif len(result) > 0 and not result[-1] in string.whitespace:
                result += " "
            is_last_empty = False
        elif is_block:
            if not result.endswith('\n'):
                result += '\n'
            if line == '```':
                is_block = False
                result += "```\n"
            else:
                result += line
            continue
        if line[:4] == '    ':
            line = line[4:]
            if not is_pre:
                result += "```\n"
                is_pre = True
        elif is_pre:
            # The space-indentation has ended.
            if not result.endswith('\n'):
                result += '\n'
            result += "```\n"
            if line == "```":
                line = ''
            is_pre = False
        if is_pre:
            result += line + "\n"
        else:
            ln = line
            ln = ptn_name.subn("", ln)[0]
            ln = ptn_standalone_link.subn("\n=> \\2 \\1", ln)[0]
            ln = ptn_image_link.subn("\n=> \\2 \\1\n", ln)[0]
            ln = sub_cb(ptn_named_link, "\\1", ln, add_pending_named_link)
            ln = sub_cb(ptn_link, "\\1", ln, add_pending_link)
            ln = ln.replace("\\_", "_")  # escaped underscores
            result += ln

    result = flush_pending_links(result)
    result = ptn_paragraph_break.subn("\n\n", result)[0]

    return result
