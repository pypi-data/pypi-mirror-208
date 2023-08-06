# Copyright (c) 2022 Jaakko Keränen <jaakko.keranen@iki.fi>
# License: BSD-2-Clause

"""Static files"""

import fnmatch
import os.path
import string

from gmcapsule import Capsule, get_mime_type
from pathlib import Path

META = '.meta'


def check_meta_rules(path, hostname):
    cfg = Capsule.config()
    root = cfg.root_dir() / hostname
    dir = Path(path).parent
    while True:
        if not str(dir).startswith(str(cfg.root_dir())):
            break
        if (dir / META).exists():
            for rule in open(dir / META, 'rt').readlines():
                rule = rule.strip()
                if len(rule) == 0: continue
                pos = rule.find(':')
                if pos < 0: continue
                rule_path = dir / rule[:pos].strip()
                rule_meta = rule[pos + 1:].strip()
                if fnmatch.fnmatch(root / path, rule_path):
                    if len(rule_meta) >= 4 and rule_meta[2] in string.whitespace:
                        return int(rule_meta[:2]), rule_meta[3:]
                    return 20, rule_meta
        dir = dir.parent

    return 20, get_mime_type(path)


def serve_file(req):
    if req.scheme != 'gemini':
        return 59, "Only Gemini requests allowed"

    cfg = Capsule.config()
    if req.path == '':
        return 31, '/'

    for seg in req.path.split('/'):
        if seg != '.' and seg != '..' and seg.startswith('.'):
            return 51, "Not found"

    host_root = cfg.root_dir() / req.hostname
    path = os.path.normpath(host_root / req.path[1:])
    if not path.startswith(str(host_root)):
        return 51, "Not found"

    if os.path.isdir(path):
        if not req.path.endswith('/'):
            return 31, req.path + '/'
        path = str(Path(path) / 'index.gmi')

    status, meta = check_meta_rules(path, req.hostname)
    if status and status != 20:
        return status, meta

    if not os.path.exists(path):
        return 51, "Not found"

    # Note: We return the file object so the sender doesn't have to buffer
    # the entire file in memory first.
    return status, meta, (open(path, 'rb') if status == 20 else None)


def init(capsule):
    cfg = capsule.config()
    if 'static' in cfg.ini and 'root' in cfg.section('static'):
        print('  Content directory:', cfg.root_dir() / '{hostname}')
        capsule.add('/*', serve_file)
