# Copyright (c) 2021-2022 Jaakko Keränen <jaakko.keranen@iki.fi>
# License: BSD-2-Clause

"""Git Repository Viewer"""

import hashlib
import json
import os
import os.path
import pickle
import re
import subprocess
import time
import urllib
from pathlib import Path

from gmcapsule import Cache, Capsule, markdown_to_gemtext

pjoin = os.path.join


class GitViewCache(Cache):
    """
    File-based cache that stores content using ``pickle``.

    File paths inside the cache directory are based on a SHA-256 hash of
    the original URL path.

    Args:
        hostname (str): Hostname that this cache belongs to.
        file_root (str): Directory where the cached content is stored.
            A large number of hash-prefix subdirectories are created here.
    """
    def __init__(self, hostname, file_root):
        super().__init__()
        self.hostname = hostname
        self.file_root = file_root
        os.makedirs(file_root, exist_ok=True)
        self.ptn_static_path = re.compile('.*/(tags|commits|patch|cdiff|pcdiff)/[0-9a-f]+')

    def storage_path(self, path):
        digest = hashlib.sha256(path.encode('utf-8')).hexdigest()
        return digest[0:2] + '/' + digest[2:]

    def max_age(self, path):
        if self.ptn_static_path.match(path):
            return 60 * 24 * 3600  # two months
        return 3600 # one hour for dynamic content

    def try_load(self, path):
        if not path.startswith(self.hostname + '/'):
            return None, None
        storage_path = pjoin(self.file_root, self.storage_path(path))
        if not os.path.exists(storage_path):
            return None, None
        now_time = time.time()
        storage_time = os.path.getmtime(storage_path)
        # print('cache {%s} age %d seconds' % (path, int(now_time - storage_time)))
        if now_time - storage_time > self.max_age(path):
            return None, None
        return pickle.load(open(storage_path, 'rb'))

    def save(self, path, media_type, content):
        if not path.startswith(self.hostname + '/'):
            return False
        storage_path = pjoin(self.file_root, self.storage_path(path))
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)
        pickle.dump((media_type, content), open(storage_path, 'wb'))
        return True


GIT = '/usr/bin/git'
HOSTNAME = 'localhost'
NUM_COMMITS_FRONT = 8
NUM_COMMITS_PER_PAGE = 25
NUM_COMMITS_PER_TAG = 10

# Link Icons
LI_TAG  = '\U0001f516'
LI_FILE = '\U0001f5ce'


def ujoin(a, b):
    if b.startswith('/'):
        return b
    if not a.endswith('/'):
        return a + '/' + b
    return a + b


def preformat(raw, alt_text=''):
    raw = raw.replace('\n```', '\n ```')
    return f'```{alt_text}\n' + raw + '\n```\n'


def repositories():
    roots = []
    for name, cfg in Capsule.config().prefixed_sections('gitview.').items():
        url = cfg['url_root']
        if not url.startswith('/'): url = '/' + url
        if not url.endswith('/'): url += '/'
        roots.append((name, url, cfg))
    return roots


class Request:
    def __init__(self, gemini_request):
        self.req = gemini_request
        self.cfg = None
        # Extract the repository root from the path.
        for sectname, url_root, repo_cfg in repositories():
            if self.req.path == url_root or self.req.path == url_root[:-1] or \
                    self.req.path.startswith(url_root):
                self.cfg = repo_cfg
                self.url_root = url_root
                break
        # Parse the path.
        self.path = self.req.path
        self.branch = self.cfg['default_branch']
        if self.path.startswith(self.url_root):
            self.path = self.path[len(self.url_root):]
            if '/' in self.path[1:]:
                parts = self.path.split('/')
                if len(parts) > 0 and len(parts[0]) > 0:
                    self.branch = parts[0].replace('%2F', '/')
                    self.path = '/'.join(parts[1:])
        self.ubranch = self.branch.replace('/', '%2F') + '/'

        # print('cfg:', self.cfg)
        # print('url_root:', self.url_root)
        # print('path:', self.path)
        # print('branch:', self.branch)
        # print('ubranch:', self.ubranch)

    def git(self, args, as_bytes=False):
        result = subprocess.check_output(
            [GIT, '-C', self.cfg['path']] + args
        )
        if as_bytes: return result
        return result.decode('utf-8').rstrip()

    def git_commits(self, count, skip=0, commit_hash=None):
        try:
            out = self.git([
                'log',
                f'-n{count}',
                f'--skip={skip}',
                "--pretty=format:{^@^hash^@^:^@^%h^@^,^@^fullHash^@^:^@^%H^@^,^@^parent^@^:^@^%p^@^,^@^refs^@^:^@^%D^@^,^@^author^@^:^@^%an^@^,^@^date^@^:^@^%ad^@^,^@^email^@^:^@^%aE^@^,^@^message^@^:^@^%s^@^,^@^body^@^:^@^%b^@^,^@^commitDate^@^:^@^%ai^@^,^@^age^@^:^@^%cr^@^},^@&@^",
                commit_hash if commit_hash else self.branch])
            out = out.replace('^@&@^\n', '').replace(',^@&@^', '') \
                    .replace('\n', '\\n').replace('\t', '    ').replace('"', '\\"').replace('^@^', '"') \
                    .replace('\\n#', '\\n') \
                    .replace('"body":"#', '"body":"')
            out = '[' + out + ']'
            #print(out)
            return json.loads(out)
        except:
            return []

    def git_tags(self):
        tags = []
        try:
            for info in self.git(['for-each-ref', '--sort=creatordate',
                    '--format', '%(refname), %(creatordate:short)', 'refs/tags']).split('\n'):
                ref, date = info.split(',')
                date = date.strip()
                tags.append((date, ref[10:]))
        except:
            pass
        return tags

    def git_diff(self, commit_hash, raw=False):
        out = self.git(['log', '--color', '-n1', '-p', '--format=format:', commit_hash])
        size = len(out.encode('utf-8'))
        MAX_DIFF = 100 * 1024
        is_trunc = len(out) > MAX_DIFF
        if is_trunc: out = out[:MAX_DIFF]
        if raw:
            return out
        out = out.replace('\n```', '\n ```')
        return preformat(out, alt_text=f'Diff of changes in commit {commit_hash}') + \
            ("(truncated output; full size was %.2f KB)\n" % (size / 1024) if is_trunc else '')

    def git_summary(self, commit_hash):
        out = self.git(['log', '--stat', '-n1', '--format=format:', commit_hash])
        return preformat(out, alt_text='Summary of changes')

    def git_patch(self, commit_hash):
        out = self.git(['format-patch', '-N', '-n1', '--stdout', commit_hash])
        return out

    def git_raw(self, path):
        try:
            raw = self.git(['show', '--format=raw', self.branch + ':' + path], as_bytes=True)
            try:
                lc = path.lower()
                if lc.endswith('.png'):
                    media = 'image/png'
                elif lc.endswith('.jpg') or lc.endswith('.jpeg'):
                    media = 'image/jpeg'
                elif lc.endswith('.md') or lc.endswith('.mdown') or lc.endswith('.markdown'):
                    raw = markdown_to_gemtext(raw.decode('utf-8')).encode('utf-8')
                    media = 'text/gemini;charset=utf-8'
                elif lc.endswith('.gmi'):
                    media = 'text/gemini;charset=utf-8'
                else:
                    raw.decode('utf-8', 'strict')
                    media = 'text/plain;charset=utf-8'
            except UnicodeDecodeError:
                media = 'application/octet-stream'
            return media, raw
        except Exception as x:
            print(x)
        return None

    def git_tree(self, path):
        if path == '':
            path = '.'  # it's the root
        elif not path.endswith('/'):
            path += '/'
        files = []
        ptn_tree = re.compile(r"([0-9]+)\s+(\w+)\s+([0-9a-f]+)\s+([-0-9]+)\s+(.*)")
        for line in self.git(['ls-tree', '-l', self.branch, path]).split('\n'):
            m = ptn_tree.match(line.strip())
            if m:
                objname = m.group(5)
                objsize = int(m.group(4)) if m.group(4) != '-' else None
                objtype = m.group(2)
                files.append((objname, objsize, objtype))
        return files

    def git_readme(self):
        try:
            md = self.git(['show', self.branch + ':README.md'])
            text = markdown_to_gemtext(md)
            title = self.page_title(omit_default_branch=True).rstrip()
            if text.startswith(title):
                # Avoid the redundant level 1 heading.
                text = '# README.md\n\n' + text[len(title):].lstrip()
            return text
        except Exception as x:
            print(x)
        return ''

    def url(self, path):
        return ujoin(self.url_root, path)

    def commit_link(self, info):
        url = self.url(ujoin(self.ubranch, f"commits/{info['fullHash']}"))
        date = info['commitDate'][:10]
        msg = info['message']
        tags = []
        for ref in info['refs'].split(','):
            ref = ref.strip()
            if ref.startswith('tag:'):
                tags.append(LI_TAG + ' ' + ref[5:])
        tag_str = '' if len(tags) == 0 else ' \u2014 ' + ', '.join(tags)
        return f"=> {url} {date} {msg}{tag_str}\n"

    def page_title(self, subtitle=None, omit_default_branch=False):
        show_branch = not omit_default_branch or self.branch != self.cfg['default_branch']
        sub = f': {subtitle}' if subtitle != None else ''
        return f"# {self.cfg['title']}{sub} {'[' + self.branch + ']' if show_branch else ''}\n\n"


def handle_request(gemini_request):
    req = Request(gemini_request)
    DEFAULT_BRANCH = req.cfg['default_branch']

    page = req.page_title()

    if gemini_request.query == 'branches':
        # Branch selection menu.
        page = f"# {req.cfg['title']}: Branches\n\n"
        page += "Select the active branch.\n"
        for b in sorted(req.git(['branch']).split('\n')):
            b = b.strip()
            if b.startswith('*'):
                b = b[1:]
            b = b.strip()
            page += f"=> {req.url(b.replace('/', '%2F') + '/')} {b}\n"
        page += f"\n=> {req.url(DEFAULT_BRANCH + '/')} Use default ({DEFAULT_BRANCH})\n"

    elif req.path == 'tags' or req.path == 'tags/':
        tags = req.git_tags()
        if len(tags) == 0:
            page += 'No tagged commits.\n'
        else:
            page += '## Latest Tags\n\n'
            for date, tag in list(reversed(tags))[:8]:
                page += f"=> {req.url(req.ubranch + 'tags/' + tag)} {date} {tag}\n"
            page += '\n## All Tags\n\n'
            for tag in sorted([ref for _, ref in tags]):
                page += f"=> {req.url(req.ubranch + 'tags/' + tag)} {LI_TAG} {tag}\n"
        page += f"\n=> {req.url(req.ubranch)} Repository\n"

    elif req.path.startswith('tags/'):
        tag = req.path[5:]
        page += f'## {tag}\n\n'
        if 'tag_url' in req.cfg:
            page += f"=> {req.cfg['tag_url'].replace('{tag}', tag)} Open {tag} in Web Browser\n\n"
        page += "### History\n"
        commits = req.git_commits(NUM_COMMITS_PER_TAG, commit_hash=req.path[5:])
        first = True
        for commit in commits:
            page += req.commit_link(commit)
            if first:
                first = False
                if len(commit['body']) > 0:
                    page += commit['body'] + "\n"
        page += f"\n=> {req.url(req.ubranch + 'tags')} {LI_TAG} Tags\n"
        page += f"=> {req.url(req.ubranch)} Repository\n"

    elif req.path == 'commits' or req.path == 'commits/':
        page += '## Commits\n\n'
        try:
            skip = int(gemini_request.query)
        except:
            skip = 0
        count = NUM_COMMITS_PER_PAGE
        commits = req.git_commits(count + 1, skip)
        if skip > 0:
            prev_skip = max(0, skip - count)
            page += f"=> {req.url(ujoin(req.ubranch, f'commits?{prev_skip}'))} Previous {count} commits\n\n"
        for commit in commits[:count]:
            page += req.commit_link(commit)
        if len(commits) > count:
            page += f"\n=> {req.url(ujoin(req.ubranch, f'commits?{skip + count}'))} Next {count} commits\n"
        page += f"\n=> {req.url(req.ubranch)} Repository\n"

    elif req.path.startswith('commits/'):
        info = req.git_commits(1, commit_hash=req.path[8:])
        if len(info) == 0:
            return 51, "Not Found"
        info = info[0]
        hash = info['hash']
        full_hash = info['fullHash']
        email_subject = urllib.parse.quote(f"{req.cfg['title']} commit {hash}")
        email_body = urllib.parse.quote("=> gemini://%s:%d%scommits/%s" %
            (HOSTNAME,
            Capsule.config().port(),
            req.url_root + req.ubranch,
            full_hash)
        )
        tags = []
        for ref in info['refs'].split(','):
            ref = ref.strip()
            if ref.startswith('tag:'):
                tags.append(ref[5:])
        body = info['body'].strip()
        page += f"## {info['message']}\n\n"
        page += f"=> mailto:{info['email']}?subject={email_subject}&body={email_body} {info['author']}\n"
        page += f"{info['date']}\n"
        if len(body):
            page += "\n" + body + "\n"
        page += req.git_summary(full_hash)
        page += f"=> {req.url(req.ubranch + 'cdiff/' + full_hash)} Diff (Colored)\n"
        page += f"=> {req.url(req.ubranch + 'pcdiff/' + full_hash)} Diff (Colored, Plain Text)\n"
        page += f"=> {req.url(ujoin(req.ubranch, 'patch/' + full_hash + '.patch'))} \U0001f528 Patch\n"
        page += "\n"
        for tag in tags:
            page += f"=> {req.url(req.ubranch + 'tags/' + tag)} {LI_TAG} {tag}\n"
        for parent in info['parent'].split():
            page += f"=> {req.url(ujoin(req.ubranch, 'commits/' + parent))} Parent {parent}\n"
        page += f"=> {req.url(req.ubranch)} Repository\n"

    elif req.path.startswith('cdiff/'):
        hash = req.path[6:]
        info = req.git_commits(1, commit_hash=hash)
        if len(info) == 0:
            return 51, "Not Found"
        info = info[0]
        page += f"## {info['message']}\n\n"
        page += f"=> {req.url(req.ubranch + 'commits/' + hash)} {hash}\n"
        page += req.git_diff(hash)
        return page

    elif req.path.startswith('pcdiff/'):
        hash = req.path[7:]
        info = req.git_commits(1, commit_hash=hash)
        if len(info) == 0:
            return 51, "Not Found"
        return 20, "text/plain", req.git_diff(hash, raw=True)

    elif req.path.startswith('patch/'):
        hash = req.path[6:-6]   # .patch file extension
        info = req.git_commits(1, commit_hash=hash)
        if len(info) == 0:
            return 51, "Not Found"
        info = info[0]
        return 20, "text/plain", req.git_patch(hash)

    elif req.path.startswith('-/'):
        page = req.page_title(subtitle='File Tree')
        path = req.path[2:]
        tree = req.git_tree(path)
        # Links to parent directories.
        if path != '':
            page += f"=> {req.url(req.ubranch + '-/')} /\n"
        pdir = os.path.dirname(os.path.dirname(path))
        while pdir != '':
            page += f"=> {req.url(req.ubranch + '-/' + pdir + '/')} {pdir}/\n"
            pdir = os.path.dirname(pdir)
        for fpath, fsize, ftype in tree:
            if ftype == 'tree':
                page += f"=> {req.url(req.ubranch + '-/' + fpath + '/')} {fpath}/\n"
            elif ftype == 'blob':
                if fsize < 1.0e4:
                    size = '{:.2f} KB'.format(fsize / 1.0e3)
                elif fsize < 1.0e5:
                    size = '{:.1f} KB'.format(fsize / 1.0e3)
                elif fsize < 1.0e6:
                    size = '{:.0f} KB'.format(fsize / 1.0e3)
                else:
                    size = '{:.1f} MB'.format(fsize / 1.0e6)
                page += f"=> {req.url(req.ubranch + fpath)} {LI_FILE} {fpath}\u00a0\u00a0\u00a0\u00a0[{size}]\n"
            else:
                page += f"{fpath}\u00a0\u00a0\u00a0\u00a0[{ftype}]\n"
        page += f"\n=> {req.url(req.ubranch)} Repository\n"

    else:
        # Check for a raw file at this path.
        if len(req.path) > 0:
            raw = req.git_raw(req.path)
            if raw is not None:
                return 20, raw[0], raw[1]

        page = req.page_title(omit_default_branch=True)

        if 'brief' in req.cfg:
            page += req.cfg['brief'] + '\n'

        page += f"=> {req.url(req.ubranch + 'tags')} {LI_TAG} Tags\n"
        page += f"=> {req.url(req.ubranch + '-/')} {LI_FILE} File Tree\n"
        page += f"=> {req.url('?branches')} \u2325 Branches [{req.branch}]\n"
        page += f"=> {req.cfg['clone_url']} Clone URL\n"
        page += "\n## Latest Commits\n\n"
        for commit in req.git_commits(NUM_COMMITS_FRONT):
            page += req.commit_link(commit)
        page += f"=> {req.url(ujoin(req.ubranch, 'commits'))} More...\n"
        readme = req.git_readme()
        if readme:
            page += readme

    return page


def redirect_to_default(gemini_request):
    req = Request(gemini_request)
    if gemini_request.query:
        return handle_request(gemini_request)
    return 30, req.url(req.cfg['default_branch'] + '/')


def main_page(req):
    page = "# Git Repositories\n"
    for name, url_root, repo_cfg in sorted(repositories()):
        page += f"\n=> {url_root + repo_cfg['default_branch'].replace('/', '%2F') + '/'} {repo_cfg['title']}\n"
        if 'brief' in repo_cfg:
            page += repo_cfg['brief'] + '\n'
    return page


def init(capsule):
    cfg = capsule.config()
    try:
        mod_cfg = cfg.section('gitview')

        global GIT
        GIT = mod_cfg.get('git', fallback=GIT)

        global HOSTNAME
        HOSTNAME = mod_cfg.get('host', fallback=None)
        if HOSTNAME is None:
            HOSTNAME = cfg.hostnames()[0]

        if 'cache_path' in mod_cfg:
            capsule.add_cache(GitViewCache(HOSTNAME, mod_cfg['cache_path']))

        for name, url_root, _ in repositories():
            print(f'  Adding repository "{name}"...')
            capsule.add('/', main_page, hostname=HOSTNAME)
            capsule.add(url_root[:-1], redirect_to_default, hostname=HOSTNAME)
            capsule.add(url_root + '*', handle_request, hostname=HOSTNAME)

    except KeyError:
        # GitView not configured.
        pass
