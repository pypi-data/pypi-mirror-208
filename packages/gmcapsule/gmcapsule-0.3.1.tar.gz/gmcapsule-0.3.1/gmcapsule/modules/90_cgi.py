# Copyright (c) 2022 Jaakko Keränen <jaakko.keranen@iki.fi>
# License: BSD-2-Clause

"""CGI programs"""

import os
import pathlib
import shlex
import subprocess
import urllib.parse

import gmcapsule
from gmcapsule import Capsule


class CgiContext:
    def __init__(self, url_path, args, work_dir=None):
        self.args = args
        self.base_path = url_path
        if self.base_path.endswith('/*'):
            self.base_path = self.base_path[:-2]
        self.work_dir = work_dir

    def __call__(self, req):
        try:
            env_vars = dict(os.environ)

            # Standard CGI variables.
            env_vars['GATEWAY_INTERFACE'] = 'CGI/1.1'
            env_vars['REMOTE_ADDR'] = '%s:%d' % req.remote_address
            if req.query != None:
                env_vars['QUERY_STRING'] = req.query
            env_vars['PATH_INFO'] = req.path
            env_vars['SCRIPT_NAME'] = self.base_path
            env_vars['SERVER_SOFTWARE'] = 'GmCapsule/' + gmcapsule.__version__
            env_vars['SERVER_PROTOCOL'] = req.scheme.upper()
            env_vars['SERVER_NAME'] = req.hostname
            env_vars['SERVER_PORT'] = str(Capsule.config().port())
            env_vars[req.scheme.upper() + '_URL'] = f"{req.scheme}://{req.hostname}{req.path}" + (
                '?' + req.query if req.query != None else '')
            env_vars[req.scheme.upper() + '_URL_PATH'] = req.path

            # TLS client certificate.
            if req.identity:
                env_vars['AUTH_TYPE'] = 'Certificate'
                id_sub = req.identity.subject()
                env_vars['REMOTE_USER'] = id_sub['CN'] if 'CN' in id_sub else ''
                env_vars['TLS_CLIENT_HASH'] = req.identity.fp_cert
                env_vars['TLS_CLIENT_SUBJECT'] = ''.join([f'/{k}={v}' for k, v in id_sub.items()])  # "/CN=name"
                env_vars['TLS_CLIENT_ISSUER'] = ''.join([f'/{k}={v}' for k, v in req.identity.issuer().items()])  # "/CN=name"
                env_vars['REMOTE_IDENT'] = str(req.identity)      # cert fingerprints
            else:
                env_vars['AUTH_TYPE'] = ''
                env_vars['REMOTE_USER'] = ''

            # Titan metadata.
            if req.content:
                env_vars['CONTENT_LENGTH'] = str(len(req.content))
                env_vars['CONTENT_TYPE'] = req.content_mime if req.content_mime is not None else ''
                env_vars['TITAN_TOKEN'] = req.content_token if req.content_token is not None else ''
            else:
                env_vars['CONTENT_LENGTH'] = '0'

            result = subprocess.run(self.args,
                                    cwd=self.work_dir,
                                    check=True,
                                    input=req.content,
                                    stdout=subprocess.PIPE,
                                    env=env_vars).stdout
            try:
                # Parse response header.
                crlf_pos = result.find(b'\r\n')
                if crlf_pos >= 1024:
                    return 42, "CGI command returned invalid response header"
                header = result[:crlf_pos].decode('utf-8')
                body = result[crlf_pos + 2:]
                status = int(header[:2])
                meta = header[2:].strip()
                if status < 10:
                    return 42, "CGI command returned invalid status code"
                return status, meta, body
            except:
                try:
                    return 20, 'text/plain; charset=utf-8', result.decode('utf-8')
                except:
                    return 20, 'application/octet-stream', result
        except Exception as er:
            return 42, "CGI error: " + str(er)


class CgiTreeMapper:
    def __init__(self, protocol, host, root_dir):
        self.protocol = protocol
        self.host = host
        self.root_dir = pathlib.Path(root_dir)

    def __call__(self, url_path):
        # Check if url_path is a valid CGI entrypoint and return
        # a CgiContext for it.
        fn = str(self.root_dir) + url_path
        if self.protocol == 'titan':
            fn += ',titan'
        if os.path.isdir(fn):
            return None
        if os.access(fn, os.X_OK):
            return CgiContext(url_path, [fn], work_dir=os.path.dirname(fn))
        return None


# # NOTE: This require restarting the server when binaries are added/removed.
# def add_cgibin_entrypoints_recursively(capsule, host, base, cur_dir=None):
#     if cur_dir is None:
#         cur_dir = base
#     for name in os.listdir(cur_dir):
#         fn = cur_dir / name
#         if os.path.isdir(fn):
#             add_cgibin_entrypoints_recursively(capsule, host, base, fn)
#         elif os.access(fn, os.X_OK):
#             protocol = 'gemini'
#             if name.endswith(',titan'):
#                 protocol = 'titan'
#             # Remove the base directory from the entry path.
#             path = str(fn)[len(str(base)):]
#             args = [str(fn)]
#             if protocol == 'titan':
#                 path = path[:-6]
#             print(f'  {protocol}://{host}{path} ->', args)
#             capsule.add(path, CgiContext(path, args, work_dir=cur_dir), host, protocol)


def init(capsule):
    cfg = Capsule.config()
    default_host = cfg.hostnames()[0]

    # Custom entrypoints for specific URLs.
    for section in Capsule.config().prefixed_sections('cgi.').values():
        protocol = section.get('protocol', fallback='gemini')
        host = section.get('host', fallback=default_host)
        work_dir = section.get('cwd', fallback=None)
        args = shlex.split(section.get('command'))
        for path in shlex.split(section.get('path', fallback='/*')):
            print(f'  {protocol}://{host}{path} ->', args)
            capsule.add(path, CgiContext(path, args, work_dir),
                        host, protocol)

    # Automatic entrypoints for all executables.
    bin_root = Capsule.config().ini.get('cgi', 'bin_root', fallback=None)
    if bin_root != None:
        bin_root = pathlib.Path(bin_root).resolve()
        for host in Capsule.config().hostnames():
            host_bin_root = bin_root / host
            for protocol in ['gemini', 'titan']:
                capsule.add(
                    CgiTreeMapper(protocol, host, host_bin_root), None,
                    host, protocol)
