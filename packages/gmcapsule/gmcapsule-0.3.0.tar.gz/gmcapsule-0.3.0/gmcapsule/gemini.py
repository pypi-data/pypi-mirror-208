# Copyright (c) 2021-2022 Jaakko Keränen <jaakko.keranen@iki.fi>
# License: BSD-2-Clause

import fnmatch
import gc
import hashlib
import queue
import os.path
import select
import socket
import threading
import time
from urllib.parse import urlparse

import OpenSSL.crypto
from OpenSSL import SSL, crypto


class AbortedIOError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


def wait_for_read(stream, timeout):
    fno = stream._socket.fileno()
    r, _, x = select.select([fno], [], [fno], timeout)
    if len(x):
        raise AbortedIOError('recv: socket in error state')
    if len(r) == 0:
        raise socket.timeout('stalled: not ready for reading')


def wait_for_write(stream, timeout):
    fno = stream._socket.fileno()
    _, w, x = select.select([], [fno], [fno], timeout)
    if len(x):
        raise AbortedIOError('send: socket in error state')
    if len(w) == 0:
        raise socket.timeout('stalled: not ready for writing')


def safe_recv(stream, max_len, stall_timeout=10):
    data = bytearray()
    remain = max_len
    while remain > 0:
        try:
            incoming = stream.recv(remain)
            remain -= len(incoming)
            data += bytearray(incoming)

            if len(data):
                # Got something, return it asap.
                break

            # Wait until reading is possible.
            wait_for_read(stream, stall_timeout)

        except OpenSSL.SSL.WantReadError:
            wait_for_read(stream, stall_timeout)
        except OpenSSL.SSL.WantWriteError:
            pass
        except OpenSSL.SSL.WantX509LookupError:
            pass
    return data


def safe_sendall(stream, data, stall_timeout=30):
    """
    Send data over an SSL connection, accounting for stalls and retries
    required by OpenSSL.

    Args:
        stream (OpenSSL.SSL.Connection): Network stream.
        data (bytes or file-like): Data to sent. If not a bytes/bytearray,
            ``read()`` will be called to get more data.
        stall_timeout (float): Number of seconds to wait until
            terminating a stalled send.
    """
    if type(data) == bytes or type(data) == bytearray:
        streaming = False
    else:
        streaming = True

    # We may need to retry sending with the exact same buffer,
    # so keep it around until successful.
    BUF_LEN = 32768
    if streaming:
        send_buf = data.read(BUF_LEN)
    else:
        send_buf = data[:BUF_LEN]

    last_time = time.time()
    pos = 0
    while len(send_buf) > 0:
        try:
            if time.time() - last_time > stall_timeout:
                raise AbortedIOError('stalled')
            sent = stream.send(send_buf)
            if sent < 0:
                raise AbortedIOError('failed to send')
            pos += sent
            if streaming:
                send_buf = send_buf[sent:]
                if len(send_buf) < BUF_LEN / 2:
                    send_buf += data.read(BUF_LEN)
            else:
                send_buf = data[pos : pos + BUF_LEN]
            if sent > 0:
                last_time = time.time()
            else:
                wait_for_write(stream, stall_timeout)
        except OpenSSL.SSL.WantReadError:
            pass
        except OpenSSL.SSL.WantWriteError:
            # Wait until the socket is ready for writing.
            wait_for_write(stream, stall_timeout)
        except OpenSSL.SSL.WantX509LookupError:
            pass


def safe_close(stream):
    if not stream:
        return
    try:
        stream.shutdown()
    except Exception as er:
        print('stream shutdown error:', er)
    try:
        stream.close()
    except Exception as er:
        print('stream close error:', er)


def report_error(stream, code, msg):
    print(time.strftime('%Y-%m-%d %H:%M:%S'), f'   ', '--', code, msg)
    #stream.sendall(f'{code} {msg}\r\n'.encode('utf-8'))
    safe_sendall(stream, f'{code} {msg}\r\n'.encode('utf-8'))
    safe_close(stream)


memtrace_lock = threading.Lock()


def display_memtop(snapshot, prev_snapshot, key_type='lineno', limit=1000):
    import tracemalloc
    import linecache
    filters = (
        tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
        tracemalloc.Filter(False, "<unknown>"),
        tracemalloc.Filter(False, "*/linecache.py"),
        tracemalloc.Filter(False, "*/tracemalloc.py")
    )
    snapshot = snapshot.filter_traces(filters)
    if prev_snapshot:
        prev_snapshot = prev_snapshot.filter_traces(filters)
        top_stats = snapshot.compare_to(prev_snapshot, key_type)
        top_type = 'delta'
        limit = 200
    else:
        top_stats = snapshot.statistics('traceback') #key_type)
        top_type = 'malloc'

    with memtrace_lock:
        print("\n\nTop %s %s" % (limit, top_type))
        for index, stat in enumerate(top_stats[:limit], 1):
            if prev_snapshot:
                frame = stat.traceback[0]
                if stat.size_diff <= 0:
                    continue
                print("#%s: \x1b[1m%.1f\x1b[0m KiB (%+.1f KiB) count=%d (%+d)"
                    % (index,
                       stat.size / 1024, stat.size_diff / 1024, stat.count, stat.count_diff))
            else:
                print("#%s: \x1b[1m%.1f\x1b[0m KiB count=%d"
                      % (index, stat.size / 1024, stat.count))
            for frame in stat.traceback:
                line = linecache.getline(frame.filename, frame.lineno).strip()
                if 'python3.' in frame.filename: continue
                if line:
                    print('\x1b[0;31m  %35s:%-5s ' % (frame.filename[-35:], str(frame.lineno) + ':'))
                    print('\x1b[0;36m    %s\x1b[0m' % line)

        other = top_stats[limit:]
        if other:
            size = sum(stat.size for stat in other)
            print("%s other: %.1f KiB" % (len(other), size / 1024))
        total = sum(stat.size for stat in top_stats)
        print("Total size: %.1f KiB\n\n" % (total / 1024))


class Identity:
    """
    Client certificate.

    SHA-256 hashes are calculated automatically for the whole certificate and
    just for the public key.

    Attributes:
        cert (OpenSSL.SSL.X509): Certificate.
        pubkey (OpenSSL.SSL.PKey): Public key.
        fp_cert (str): SHA-256 hash of the certificate.
        fp_pubkey (str): SHA-256 hash of the public key.
    """
    def __init__(self, cert):
        self.cert = cert
        m = hashlib.sha256()
        m.update(crypto.dump_certificate(crypto.FILETYPE_ASN1, self.cert))
        self.fp_cert = m.hexdigest()
        self.pubkey = self.cert.get_pubkey()
        m = hashlib.sha256()
        m.update(crypto.dump_publickey(crypto.FILETYPE_ASN1, self.pubkey))
        self.fp_pubkey = m.hexdigest()

    def __str__(self):
        return f"{self.fp_cert};{self.fp_pubkey}"

    def subject(self):
        """
        Returns:
            dict: Name components of the certificate subject, e.g.: ``{'CN': 'Name'}``
        """
        comps = {}
        for name, value in self.cert.get_subject().get_components():
            comps[name.decode()] = value.decode()
        return comps

    def issuer(self):
        """
        Returns:
            dict: Name components of the certificate issuer, e.g.: ``{'CN': 'Name'}``
        """
        comps = {}
        for name, value in self.cert.get_issuer().get_components():
            comps[name.decode()] = value.decode()
        return comps


class Request:
    """
    Request received from a client.

    Request objects are used to pass information to entry points handlers.
    One does not need to construct them directly.

    Attributes:
        remote_address (str): IP address of the client.
        scheme (str): Request protocol scheme. Either ``gemini`` or ``titan``.
        identity (gmcapsule.gemini.Identity): Client certificate.
            May be ``None``.
        hostname (str): Hostname.
        path (str): URL path. Always begins with a ``/``.
        query (str): Encoded query string. You can use `urllib.parse.unquote()
            <https://docs.python.org/3/library/urllib.parse.html#urllib.parse.unquote>`_
            to decode the percent-coding. ``None`` if the URL does not have a query
            string.
        content_token (str): Encoded token specified in Titan URLs.
            May be ``None``.
        content_mime (str): MIME type specified in Titan URls. May be ``None``.
        content (bytes): Content uploaded by the client in a Titan request.
            May be ``None``.
    """
    def __init__(self, identity=None, scheme='gemini', hostname='', path='', query=None,
                 remote_address=None, content_token=None, content_mime=None, content=None):
        self.remote_address = remote_address
        self.scheme = scheme
        self.identity = identity
        self.hostname = hostname
        self.path = path
        self.query = query
        self.content_token = content_token
        self.content_mime = content_mime
        self.content = content


def verify_callback(connection, cert, err_num, err_depth, ret_code):
    #print("verify_callback:", connection, cert, ret_code)
    return True


class Cache:
    """
    Response cache base class.

    Derived classes are expected to override the save() and try_load()
    methods to save and load response content as appropriate.

    The server will not try to load or save cached content when a request
    includes a query string or a client certificate is provided. When multiple
    Cache objects have been installed, the save/load operation is attempted
    on each in turn until one cache succeeds in saving or loading content.

    The mapping from URLs to cache paths is::

        gemini://example.com/path/file.gmi
         ↓
        /example.com/path/file.gmi

    """

    def __init__(self):
        pass

    def save(self, path, media_type, content):
        """
        Save content to the cache.

        Args:
            path (str): URL path being loaded with the hostname prepended as
                the top-level directory.
            media_type (str): MIME type, e.g., "text/plain".
            content (bytes): Content to save.

        Returns:
            bool: True if successfully saved.
        """
        return False

    def try_load(self, path):
        """
        Load content from the cache.

        Args:
            path (str): URL path being loaded with the hostname prepended as
                the top-level directory.

        Returns:
            tuple(str, bytes): Content MIME type and data. Returns
            (None, None) if nothing is cached for the given path.
        """
        return None, None


class Worker(threading.Thread):
    """Thread that processes incoming requests from clients."""

    def __init__(self, id, server):
        super().__init__()
        self.id = id
        self.server = server
        self.jobs = server.work_queue

    def run(self):
        while True:
            stream, from_addr = self.jobs.get()
            if stream is None:
                break

            try:
                self.process_request(stream, from_addr)
            except OpenSSL.SSL.SysCallError as error:
                self.log(f'OpenSSL error: ' + str(error))
            except AbortedIOError as error:
                self.log(f'Send aborted: ' + str(error))
            except Exception as error:
                self.log(f'Problem: ' + str(error))
                # Some unexpected problem...
                #import traceback
                #traceback.print_exc()
                # try:
                #     report_error(stream, 42, str(error))
                # except:
                #     pass

            safe_close(stream)
            stream, from_addr = None, None

    def log(self, *args):
        print(time.strftime('%Y-%m-%d %H:%M:%S'), f'[{self.id}]', '--', *args)

    def process_request(self, stream, from_addr):
        data = bytes()
        MAX_LEN = 1024
        MAX_RECV = MAX_LEN + 2  # includes terminator "\r\n"
        request = None
        expected_size = 0
        req_token = None
        req_mime = None
        incoming = safe_recv(stream, MAX_RECV)

        try:
            while len(data) < MAX_RECV:
                data += incoming
                crlf_pos = data.find(b'\r\n')
                if crlf_pos >= 0:
                    request = data[:crlf_pos].decode('utf-8')
                    data = data[crlf_pos + 2:]
                    break
                elif len(data) > MAX_LEN:
                    # At this point we should have received the line terminator.
                    self.log(from_addr, 'sent a malformed request')
                    report_error(stream, 59, "Request exceeds maximum length")
                    return

                incoming = safe_recv(stream, MAX_RECV - len(data))
                if len(incoming) <= 0:
                    break
        except UnicodeDecodeError:
            report_error(stream, 59, "Request contains malformed UTF-8")
            return

        if not request or len(data) > MAX_RECV:
            report_error(stream, 59, "Invalid request")
            return
        if not (request.startswith('gemini:') or request.startswith('titan:')):
            report_error(stream, 59, "Unsupported protocol")
            return

        cl_cert = stream.get_peer_certificate()
        identity = Identity(cl_cert) if cl_cert else None

        if request.startswith('titan:'):
            if identity is None and self.server.require_upload_identity:
                report_error(stream, 60, "Client certificate required for upload")
                return

            # Read the rest of the data.
            parms = request.split(';')
            request = parms[0]
            for p in parms:
                if p.startswith('size='):
                    expected_size = int(p[5:])
                elif p.startswith('token='):
                    req_token = p[6:]
                elif p.startswith('mime='):
                    req_mime = p[5:]
            self.log(f'Receiving Titan content: {expected_size}')
            if expected_size > self.server.max_upload_size and self.server.max_upload_size > 0:
                report_error(stream, 59, "Maximum content length exceeded")
                return
            while len(data) < expected_size:
                incoming = safe_recv(stream, 65536)
                if len(incoming) == 0:
                    break
                data += incoming
            if len(data) != expected_size:
                report_error(stream, 59, "Invalid content length")
                return
        else:
            # No Payload in Gemini.
            if len(data):
                report_error(stream, 59, "Gemini disallows request content")
                return

        self.log(request)

        url = urlparse(request)
        path = url.path
        if url.port != None and url.port != self.server.port:
            report_error(stream, 59, "Invalid port number")
            return
        if path == '':
            path = '/'
        hostname = url.hostname
        entrypoint = self.server.find_entrypoint(url.scheme, hostname, path)

        # Server name indication is required.
        if not stream.get_servername():
            report_error(stream, 59, "Missing TLS server name indication")
            return
        if stream.get_servername().decode() != url.hostname:
            report_error(stream, 53, "Proxy request refused")
            return

        caches = [] if (url.scheme != 'gemini' or identity or len(url.query) > 0) \
            else self.server.caches
        from_cache = None

        # print(f'Request : {request}')
        # print(f'Cert    : {cl_cert}')

        if entrypoint:
            # Check the caches first.
            for cache in caches:
                media, content = cache.try_load(hostname + path)
                if not media is None:
                    response = 20, media, content
                    from_cache = cache
                    if hasattr(content, '__len__'):
                        print('%d bytes from cache, %s' % (len(content), media))
                    else:
                        print('stream from cache,', media)
                    break

            # Process the request normally if there is nothing cached.
            if not from_cache:
                try:
                    response = entrypoint(Request(
                        identity,
                        remote_address=from_addr,
                        scheme=url.scheme,
                        hostname=hostname,
                        path=path,
                        query=url.query if '?' in request else None,
                        content_token=req_token,
                        content_mime=req_mime,
                        content=data if len(data) else None
                    ))
                except Exception as x:
                    import traceback
                    traceback.print_exception(x)
                    report_error(stream, 40, 'Temporary failure')
                    return

            # Determine status code, meta line, and body content.
            if type(response) == tuple:
                if len(response) == 2:
                    status = response[0]
                    meta = response[1]
                    response = ''
                else:
                    status = response[0]
                    meta = response[1]
                    response = response[2]
            else:
                status = 20
                meta = 'text/gemini; charset=utf-8'

            if response == None:
                response_data = b''
            elif type(response) == str:
                response_data = response.encode('utf-8')
            else:
                response_data = response

            safe_sendall(stream, f'{status} {meta}\r\n'.encode('utf-8'))
            safe_sendall(stream, response_data)

            # Save to cache.
            if not from_cache and status == 20 and \
                    (type(response_data) == bytes or type(response_data) == bytearray):
                for cache in caches:
                    if cache.save(hostname + path, meta, response_data):
                        break

            # Close handles.
            if hasattr(response_data, 'close'):
                response_data.close()

        else:
            report_error(stream, 50, 'Permanent failure')


class Server:
    def __init__(self, hostname_or_hostnames, cert_path, key_path,
                 address='localhost', port=1965,
                 cache=None, session_id=None, max_upload_size=0, num_threads=1,
                 require_upload_identity=True):
        self.hostnames = [hostname_or_hostnames] \
            if type(hostname_or_hostnames) == str else hostname_or_hostnames
        self.address = address
        self.port = port
        self.entrypoints = {'gemini': {}, 'titan': {}}
        for proto in ['gemini', 'titan']:
            self.entrypoints[proto] = {}
            for hostname in self.hostnames:
                self.entrypoints[proto][hostname] = []
        self.caches = []
        if cache:
            self.caches.append(cache)
        self.max_upload_size = max_upload_size
        self.require_upload_identity = require_upload_identity

        if not os.path.exists(cert_path):
            raise Exception("certificate file not found: " + str(cert_path))
        if not os.path.exists(key_path):
            raise Exception("private key file not found: " + str(key_path))

        self.context = SSL.Context(SSL.TLS_SERVER_METHOD)
        self.context.use_certificate_file(str(cert_path))
        self.context.use_privatekey_file(str(key_path))
        self.context.set_verify(SSL.VERIFY_PEER, verify_callback)
        if session_id:
            if type(session_id) != bytes:
                raise Exception("session_id type must be `bytes`")
            self.context.set_session_id(session_id)

        # Spawn the worker threads.
        self.shutdown_event = threading.Event()
        self.workers = []
        self.work_queue = queue.Queue()
        for worker_id in range(max(num_threads, 1)):
            worker = Worker(worker_id, self)
            self.workers.append(worker)

        self.sock = None
        self.sv_conn = None

    def add_cache(self, cache):
        self.caches.append(cache)

    def add_entrypoint(self, protocol, hostname, path_pattern, entrypoint):
        self.entrypoints[protocol][hostname].append((path_pattern, entrypoint))

    def __setitem__(self, key, value):
        for hostname in self.hostnames:
            self.add_entrypoint('gemini', hostname, key, value)

    def run(self, memtrace=False):
        self.memtrace = memtrace
        if self.memtrace:
            import tracemalloc
            tracemalloc.start(10)

        attempts = 60
        print(f'Opening port {self.port}...')
        while True:
            try:
                self.sock = socket.socket()
                self.sock.bind((self.address, self.port))
                self.sock.listen(5)
                self.sv_conn = SSL.Connection(self.context, self.sock)
                self.sv_conn.set_accept_state()
                break
            except:
                attempts -= 1
                if attempts == 0:
                    raise Exception(f'Failed to open port {self.port} for listening')
                time.sleep(2.0)
                print('...')
        print(f'Server started on port {self.port}')

        MULTITHREAD = True

        if MULTITHREAD:
            for worker in self.workers:
                worker.start()
            print(len(self.workers), 'worker(s) started')

        snapshot = None

        while True:
            stream = None
            try:
                stream, from_addr = self.sv_conn.accept()
                stream._socket.settimeout(10)
                self.work_queue.put((stream, from_addr))

                if not MULTITHREAD:
                    self.work_queue.put((None, None)) # single iteration only
                    self.workers[0].run()

                del stream
                del from_addr
            except KeyboardInterrupt:
                print('\nStopping the server...')
                break
            except Exception as ex:
                #import traceback
                #traceback.print_exc()
                print(ex)

            if self.memtrace:
                old_snapshot = snapshot
                gc.collect()
                snapshot = tracemalloc.take_snapshot()
                filters = (
                    tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
                    tracemalloc.Filter(False, "<unknown>"),
                    tracemalloc.Filter(False, "*/linecache.py"),
                    tracemalloc.Filter(False, "*/tracemalloc.py"),
                    tracemalloc.Filter(False, "*/mimetypes.py"),
                    tracemalloc.Filter(False, "*/fnmatch.py")
                )
                snapshot = snapshot.filter_traces(filters)
                top_stats = snapshot.statistics('lineno')
                display_memtop(snapshot, None) #old_snapshot)

        # Close the server socket.
        self.sv_conn = None
        self.sock.close()
        self.sock = None

        # Stop all workers.
        self.shutdown_event.set()
        if MULTITHREAD:
            for i in range(len(self.workers)):
                self.work_queue.put((None, None))
            for worker in self.workers:
                worker.join()

        print('Done')

    def find_entrypoint(self, protocol, hostname, path):
        try:
            for entry in self.entrypoints[protocol][hostname]:
                path_pattern, handler = entry
                if handler != None:
                    # A path string, possibly with wildcards.
                    if len(path_pattern) == 0 or fnmatch.fnmatch(path, path_pattern):
                        return handler
                else:
                    # A callable generic path matcher.
                    handler = path_pattern(path)
                    if handler:
                        return handler
        except:
            return None

        return None
