# Copyright (c) 2022 Jaakko Keränen <jaakko.keranen@iki.fi>
# License: BSD-2-Clause

"""

User manual
===========

GmCapsule is an extensible Gemini/Titan server.

Extensibility is achieved with Python modules that get loaded at launch
from the configured directories. A set of built-in extension modules is
provided for common functionality like CGI and for serving static files.

The supported protocols are `Gemini <https://gemini.circumlunar.space>`_ and
`Titan <https://transjovian.org/titan>`_. Both are accepted via the same
TCP port.

GmCapsule can be used in a few different ways:

- You can run it as-is for serving static files.
- You can use CGI programs to generate dynamic content and/or process
  queries and uploads. As an extreme example, you could attach a CGI
  program to the path ``/*`` and generate the entire capsule procedurally
  with it.
- You can use the included extension module `gitview` to make local Git
  repositories viewable via Gemini.
- You can write new extension modules that run as part of the server
  process for advanced use cases. For example, this enables the use
  of additional worker threads and caching state in memory.

``gmcapsuled`` is a simple command line utility for loading a configuration
and running the server. Use the ``--help`` option to see usage instructions.

One can also run the server manually in Python::

    from gmcapsule import *
    cfg = Config("myconfig.ini")
    capsule = Capsule(cfg)
    capsule.run()


Getting started
***************

1. Acquire or generate a server certificate.
2. Prepare a configuration file. A configuration file is required for
   running GmCapsule. For more details, see :ref:`Configuration` and
   :ref:`example.ini`.
3. Run ``gmcapsuled``.


Configuration
*************

The GmCapsule configuration file is in `INI format
<https://en.wikipedia.org/wiki/INI_file>`_. The following sections are
defined:

- :ref:`server` — server settings
- :ref:`static` — serving static files
- :ref:`titan` — Titan upload settings
- :ref:`cgi` — General CGI settings
- :ref:`cgi.*` — CGI programs
- :ref:`gitview` — Git repository viewer settings
- :ref:`gitview.*` — Git repository settings

Example of a minimal configuration file for serving static files from
`/var/gemini/example.com/`:

.. code-block:: ini

    [server]
    host  = example.com
    certs = /home/username/.certs

    [static]
    root = /var/gemini


server
------

host : string [string...]
    One or more hostnames for the server. Defaults to ``localhost``.

address : string
    IP address of the network interface where the server is listening.
    Defaults to ``0.0.0.0`` (all interfaces).

port : int
    IP port on which the server is listening.

certs : path
    Directory where the server certificate is stored. The directory must
    contain the PEM-formatted files `cert.pem` and `key.pem`. Defaults
    to `.certs`.

modules : path [path...]
    One or more directories to load extension modules from.

threads : int
    Number of worker threads. At least 1 is required. Defaults to 5.


titan
-----

Settings for Titan requests.

upload_limit : int
    Maximum size of content accepted in an upload, in bytes. Defaults to
    ``10485760`` (i.e., 10 MiB). Requests that attempt to upload larger
    content will be rejected with an error status.


static
------

Settings for the `static` module that serves files from a directory. Omitting
this section from the configuration disables the module.

root : path [path...]
    Content directory. Defaults to `.` (current directory). The hostname
    is appended as a subdirectory, so for example if this is set to:

    .. code-block:: ini

        [static]
        root = /home/user/gemini

    files will be served from `/home/user/gemini/example.com/`.


cgi
---

General settings for CGI programs.

bin_root : path
    CGI root directory. If set, all executables under the root are made
    available at corresponding URL entry points. The entire directory tree is
    checked for executables. This mapping of executables to entry points is
    dynamic, so you can add, modify, and remove executables inside the
    directory tree without restarting the server.

    The hostname is appended as a subdirectory, like with the static root
    content directory. For example:

    .. code-block:: ini

        [cgi]
        bin_root = /home/user/gemini/cgi-bin

    An executable at `/home/user/gemini/cgi-bin/example.com/action` would then
    be visible at gemini://example.com/action. If the executable name ends
    with ``,titan`` (note: a comma), the entrypoint will use the Titan
    protocol instead of Gemini. The ``,titan`` suffix is omitted from the URL.


cgi.*
-----

Each section whose name begins with ``cgi.`` is used for setting up CGI entry
points for the `cgi` module. For example, this registers
``gemini://example.com/listing`` to show the output of ``/bin/ls -l``:

.. code-block:: ini

    [cgi.listfiles]
    path    = /listing
    cwd     = /home/username/testdir
    command = /bin/ls -l

protocol : string
    Protocol for the CGI entry point. Defaults to ``gemini``.

host : string
    Hostname for the CGI entry point. If omitted, defaults to the first
    hostname defined in the :ref:`server` section.

path : string [string...]
    URL path for CGI entry point. An asterisk ``*`` in the end is considered
    a wildcard, matching any path that begins with the specified path.
    Multiple paths can be specified.

cwd : path
    Working directory for executing the CGI command. If omitted, the CGI
    command is executed in the directory where the server was started from.

command : string [string...]
    Command to execute when a request is received matching the CGI entry
    point. The specified strings are interpreted like a shell command, i.e.,
    values that contain spaces need to be quoted.

    See :ref:`CGI Programs` for details about executing CGI programs.


gitview
-------

Settings for the `gitview` module that enables viewing local Git
repositories via Gemini. If this section is missing, `gitview` is disabled.

host : string
    Hostname where is `gitview` running. If omitted, defaults to the first
    hostname defined in the :ref:`server` section. `gitview` is limited to a
    single hostname.

    This version of `gitview` assumes that the host is reserved just
    for viewing Git repositories. Therefore, using a dedicated virtual host
    is recommended, for example `git.example.com`. The hostname must be
    one of the hostnames in the :ref:`server` section.

git : path
    Path of the Git executable to use. Defaults to `/usr/bin/git`.

cache_path : path
    Directory where cached pages are stored. If omitted, caching is disabled.


gitview.*
---------

Configuration of a Git repository that is visible via `gitview`. For example:

.. code-block:: ini

    [gitview.lagrange]
    title          = Lagrange
    brief          = A Beautiful Gemini Client
    clone_url      = https://git.skyjake.fi/gemini/lagrange.git
    tag_url        = https://git.skyjake.fi/gemini/lagrange/releases/tag/{tag}
    path           = /Users/jaakko/src/lagrange
    url_root       = lagrange
    default_branch = release

title : string
    Name of the repository.

brief : string
    Short description of the repository. Shown on the root page.

clone_url : url
    Git clone URL.

tag_url : url
    Git tag URL for viewing tags in a web browser. This is useful for showing
    release notes and downloads attached to the tag. The placeholder ``{tag}``
    is replaced with the tag to view.

path : path
    Local file path of the Git repository. Git will be run in this directory.

url_root : string
    URL root path where the Git repository can be viewed via Gemini.

default_branch : string
    The default branch of the repository. This is used if no branch is
    specified in the URL.


Static files
************

Static files are served from the configured content directory. There must be
a separate subdirectory for each configured hostname inside the content
directory. For example, if the content directory is `/var/gemini`::

    var
    └── gemini
        ├── example.com
        └── sub.example.com

If the requested path is a directory that contains an `index.gmi` file, that
file is automatically sent as a response.

If the requested path is a directory but the URL path does not end with
a slash, a redirect is sent as a response with the slash added.

The MIME types of files are autodetected using Python's ``mimetypes`` and the
system ``file`` utility, if that is available. A few common file extensions
like ``.txt`` are directly mapped to the corresponding MIME types.


.meta files
-----------

A `.meta` file can be placed in any directory inside the content directory
tree, containing additional directives for handling static files.

Each `.meta` file affects the directory it's in and also all its
subdirectories. For example, placing a `.meta` in `/var/gemini` would affect
all directories inside all virtual hosts.

The `.meta` file has a simple format. Each line has the following structure:

.. code-block:: rst

    pattern: directive

``pattern``
    Shell globbing expression. For example: ``*.zip``
``directive``
    MIME type, or the full Gemini header that will be sent when serving
    the file.

If only a MIME type is specified, that will be used instead of the
autodetected type. If the full header is specified with a non-20 status code,
the response body will be empty and only the header is sent.


CGI programs
************

CGI programs inherit the environment of the server process. Additionally, the
following CGI-specific environment variables are set, providing input and
contextual information:

- ``REMOTE_ADDR``
- ``QUERY_STRING``
- ``PATH_INFO``
- ``SCRIPT_NAME``
- ``SERVER_PROTOCOL``
- ``SERVER_NAME``
- ``SERVER_PORT``
- ``AUTH_TYPE``
- ``REMOTE_IDENT`` (when client certificate provided)
- ``REMOTE_USER`` (when client certificate provided)
- ``CONTENT_LENGTH`` (Titan only)
- ``CONTENT_TYPE`` (Titan only)
- ``TITAN_TOKEN`` (Titan only)

The CGI programs's stdout is used as the response to the request. The response
is expected to begin with a valid meta line (status code and meta text), but
this is not required. If the meta line is missing, the following header is
prepended to UTF-8 text output:

.. code-block:: rst

    20 text/plain; charset=utf-8

Or, if the output is binary, the prepended header will be:

.. code-block:: rst

    20 application/octet-stream

The response is sent to the client after the program finishes running.

With Titan requests, the uploaded content is passed in via stdin. Note that
the CGI program is only executed after the full contents have already been
successfully received, so the program does not need to worry about interrupted
uploads.


Extensions
**********

All Python modules in the configured extension module directories (see
:ref:`server` configuration) are loaded at launch in alphabetical order, as
long as they use the following naming convention:

    `NN_extmod.py`

That is, the name of the extension ("extmod") is prefixed with two numbers
`NN` and an underscore. This naming gives more control over the order in
which modules are loaded. The ones loaded first have precedence over
registered URL entry points.


Initialization
--------------

Each extension module is required to have an initialization function:

.. py:function:: extmod.init(capsule)

    Initialize the extension module.

    This is called once immediately after the extension has been loaded.

    :param capsule: Server instance. The extension can use this to access
        configuration parameters, install caches, and register entry
        points.
    :type capsule: gmcapsule.Capsule


Requests
--------

An extension module is responsible for handling requests arriving at its
registered entry points. A :class:`~gmcapsule.gemini.Request` object is
given as an argument when the registered entry point callback or handler
object gets called.

The return value from the handler determines what gets sent as a response
to the client:

- Returning ``bytes`` or ``str`` means that the response is UTF-8 encoded
  "text/gemini", and the status code is 20.
- Returning a two-element tuple is interpreted as (status code, meta).
  The response body will be empty. This is useful for error messages and
  redirects.
- Returning a three-element tuple is interpreted as (status code, meta,
  body). If the body type is ``str``, it will be UTF-8 encoded before sending.
  Otherwise, the body is sent as-is. If the body type isn't ``bytes`` or
  ``bytearray``, it is assumed to be a buffered file-like object. In this
  case, the entire body is not read in memory first, and ``close()`` will be
  called on the object afterwards to release its resources.


Future improvements
*******************

The following limitations could/should be lifted in the future:

- Enable value interpolation in the `configparser`, allowing access to
  defined values and environment variables.
- Add Titan configuration option to not require a client certificate.
- Extension modules should be reloadable. Add a ``deinit()`` method.
- `gitview` should have a URL path prefix.
- Caches should be informed of identities and queries; content might still
  be cacheable.

"""

import configparser
import importlib
import importlib.machinery
import importlib.util
import mimetypes
import os
import re
import shlex
import subprocess
from pathlib import Path

from .gemini import Server, Cache
from .markdown import to_gemtext as markdown_to_gemtext


__version__ = '0.3.1'
__all__ = [
    'Config', 'Capsule', 'Cache',
    'get_mime_type', 'markdown_to_gemtext'
]


class Config:
    """
    Server configuration.

    Args:
        config_path (str): Path of a config INI file to load.

    Attributes:
        ini(configparser.ConfigParser): Contents of the config INI file.
            Extension modules can use this to access additional custom
            config parameters. See `configparser
            <https://docs.python.org/3/library/configparser.html>`_
            for details.
    """

    def __init__(self, config_path):
        self.debug_memtrace = False
        self.ini = configparser.ConfigParser()
        if os.path.exists(config_path):
            self.ini.read(config_path)
        else:
            print(config_path, 'not found -- using defaults')

    def hostnames(self):
        """
        Returns:
            list(str): All the configured hostnames. The first listed hostname
            is considered the default to be used when a hostname is not
            otherwise specified.
        """
        return self.ini.get('server', 'host', fallback='localhost').split()

    def address(self):
        return self.ini.get('server', 'address', fallback='0.0.0.0')

    def port(self):
        """
        Returns:
            int: Listening IP port of the server.
        """
        return self.ini.getint('server', 'port', fallback=1965)

    def certs_dir(self):
        return Path(self.ini.get('server', 'certs', fallback='.certs'))

    def root_dir(self):
        """
        Returns:
            pathlib.Path: Content root directory for serving static files.
            The hostname is always automatically appended to this as a
            subdirectory.
        """
        return Path(self.ini.get('static', 'root')).resolve()

    def mod_dirs(self):
        return [Path(p).resolve() for p in shlex.split(
            self.ini.get('server', 'modules', fallback='.'))]

    def num_threads(self):
        return self.ini.getint('server', 'threads', fallback=5)

    def max_upload_size(self):
        return self.ini.getint('titan', 'upload_limit', fallback=10 * 1024 * 1024)

    def section(self, name):
        """
        Find a section in the config INI file.

        Args:
            name (str): Name of the section.

        Returns:
            configparser.SectionProxy: INI section.

        Raises:
            KeyError: The section was not found.
        """
        return self.ini[name]

    def prefixed_sections(self, prefix):
        """
        Find all sections in the config INI file whose name begins with
        the given prefix.

        Args:
            prefix (str): Name prefix, e.g., ``cgi.``.

        Returns:
            dict: Mapping of section names (with the prefix removed) to the
            corresponding INI sections (configparser.SectionProxy). An
            empty dictionary is returned if there are no sections matching
            the prefix.
        """
        sects = {}
        for name in self.ini.sections():
            if not name.startswith(prefix): continue
            sects[name[len(prefix):]] = self.ini[name]
        return sects


class Capsule:
    """
    Server instance.

    The server is initialized as specified in the configuration.
    Extension modules are loaded and initialized.

    After constructing and setting up Capsule, call the
    :func:`~gmcapsule.Capsule.run` method to begin accepting incoming
    connections.

    Args:
        cfg (Config): Server configuration.
    """

    _capsule = None

    def __init__(self, cfg):
        Capsule._capsule = self
        self.cfg = cfg
        self.sv = Server(
            cfg.hostnames(),
            cfg.certs_dir() / 'cert.pem',
            cfg.certs_dir() / 'key.pem',
            address=cfg.address(),
            port=cfg.port(),
            session_id=f'GmCapsule:{cfg.port()}'.encode('utf-8'),
            max_upload_size=cfg.max_upload_size(),
            num_threads=cfg.num_threads()
        )
        # Modules define the entrypoints.
        self.load_modules()

    @staticmethod
    def config():
        """
        Returns:
            Config: Server configuration.
        """
        return Capsule._capsule.cfg

    def add(self, path, entrypoint, hostname=None, protocol='gemini'):
        """
        Register a URL entry point.

        Extension modules must call this to become visible in the server's
        path hierarchy. Entry points are looked up in the order the modules
        were loaded, with earlier modules getting precedence.

        Args:
            path (str): URL path. Must begin with a slash (``/``). Asterisk
                wildcards (``*``) are supported. Note that if the path
                ``/*`` is registered, it will match any requested URL.
            entrypoint (callable): Function or other callable object that
                gets called when a request is processed with a matching
                URL path. A :class:`~gmcapsule.gemini.Request` is passed in as the
                only argument.
            hostname (str): Hostname for the entry point. If omitted,
                the entry point applies to all configured hostnames.
            protocol (str): Protocol for the entry point.
        """
        if hostname:
            self.sv.add_entrypoint(protocol, hostname, path, entrypoint)
        else:
            for hostname in self.cfg.hostnames():
                if not hostname:
                    raise Exception(f'invalid hostname: "{hostname}"')
                self.sv.add_entrypoint(protocol, hostname, path, entrypoint)

    def add_cache(self, cache):
        """
        Install a cache.

        All installed caches will attempt to save and load content until one
        succeeds. The caches installed first get precedence.

        Args:
            cache (Cache): Cache instance.
        """
        self.sv.add_cache(cache)

    def load_modules(self):
        name_pattern = re.compile(r'[0-9][0-9]_(.*)\.py')
        dirs = []
        for user_dir in self.cfg.mod_dirs():
            if user_dir not in dirs:
                dirs.append(user_dir)
        dirs += [Path(__file__).parent.resolve() / 'modules']
        for mdir in dirs:
            for mod_file in sorted(os.listdir(mdir)):
                m = name_pattern.match(mod_file)
                if m:
                    path = (mdir / mod_file).resolve()
                    name = m.group(1)
                    loader = importlib.machinery.SourceFileLoader(name, str(path))
                    spec = importlib.util.spec_from_loader(name, loader)
                    mod = importlib.util.module_from_spec(spec)
                    loader.exec_module(mod)
                    print('MODULE:', mod.__doc__)
                    mod.init(self)

    def shutdown_event(self):
        """
        Returns:
            threading.Event: Event that is set when the server is
            shutting down. Background workers must wait on this and stop
            when the event is set.
        """
        return self.sv.shutdown_event

    def run(self):
        """
        Start worker threads and begin accepting incoming connections. The
        server will run until stopped with a KeyboardInterrupt (^C).
        """
        self.sv.run(memtrace=self.cfg.debug_memtrace)


def get_mime_type(path):
    """
    Determine the MIME type of a file. A handful of common file extensions
    are detected as special cases, such as ".gmi" and ".txt". Other files
    are detected with Python's ``mimetypes`` standard library module, and as
    a final fallback, the ``file`` command line utility.

    Args:
        path (str): File path.

    Returns:
        str: Detected MIME type, for example, "image/jpeg". Returns
        "application/octet-stream" if the correct type could not be
        determined.
    """
    p = str(path)
    lp = p.lower()
    if lp.endswith('.txt'):
        return 'text/plain'
    if lp.endswith('.gmi') or lp.endswith('.gemini'):
        return 'text/gemini'
    if lp.endswith('.md') or lp.endswith('.markdown') or lp.endswith('.mdown'):
        return 'text/markdown'

    if not Path(p).exists():
        return None

    mt = mimetypes.guess_type(p)[0]
    if mt is not None:
       return mt

    try:
        return subprocess.check_output([
            '/usr/bin/env', 'file', '--mime-type', '-b', p
            ]).decode('utf-8').strip()
    except:
        return 'application/octet-stream'


def run_server():
    print(f"GmCapsule v{__version__}")

    import argparse
    argp = argparse.ArgumentParser(
        description='GmCapsule is an extensible server for Gemini and Titan.')
    argp.add_argument('-c', '--config',
                      dest='config_file',
                      default=Path.home() / '.gmcapsulerc',
                      help='Configuration file to load at startup')
    argp.add_argument('--trace-malloc',
                      action='store_true',
                      help='Enable memory allocation tracing (for debugging)')
    args = argp.parse_args()

    cfg = Config(args.config_file)
    cfg.debug_memtrace = args.trace_malloc

    try:
        capsule = Capsule(cfg)
        capsule.run()
        return 0
    except Exception as er:
        print('ERROR:', er)
        return -1
