#!/usr/bin/env python3

# Copyright (c) 2000-2023, Board of Trustees of Leland Stanford Jr. University
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import argparse
import concurrent.futures
import getpass
import os
from datetime import date, datetime
from pathlib import Path, PurePath
import sys

import requests
import requests.auth
import rich_argparse
import tabulate
import zeep

import lockss.soap


def date_ms(ms):
    if ms is None or ms < 0:
        return None
    return date.fromtimestamp(ms / 1000)


def datetime_ms(ms):
    if ms is None or ms < 0:
        return None
    return datetime.fromtimestamp(ms / 1000)


def duration_ms(ms):
    if ms is None:
        return None
    s, ms = divmod(ms, 1000)
    if s == 0:
        return f'{ms}ms'
    m, s = divmod(s, 60)
    if m == 0:
        return f'{s}s'
    h, m = divmod(m, 60)
    if h == 0:
        return f'{m}m{s}s'
    d, h = divmod(h, 24)
    if d == 0:
        return f'{h}h{m}m{s}s'
    w, d = divmod(d, 7)
    if w == 0:
        return f'{d}d{h}h{m}m'
    return f'{w}w{d}d{h}h'


def _construct_query(select='*', where=None):
    if issubclass(type(select), str):
        query = f'SELECT {select}'
    elif hasattr(select, '__iter__'):
        query = f'SELECT {", ".join(select)}'
    else:
        raise TypeError(f'select parameter is not iterable or a string: {type(select).__name__}')
    if where is not None:
        query = f'{query} WHERE {where}'
    return query


# See https://stackoverflow.com/questions/48714523/comma-separated-inputs-instead-of-space-separated-inputs-for-argparse/60205263#60205263
def _csvtype(choices):
    def _splitarg(arg):
        values = arg.split(',')
        for value in values:
            if value not in choices:
                raise argparse.ArgumentTypeError(f'invalid choice: {value!r} (choose from {", ".join(map(repr, choices))}')
        return values
    return _splitarg


def _do(target,
        all_target_args,
        result_func,
        exception_func,
        thread_pool,
        pool_size):
    workers = pool_size if pool_size and pool_size > 0 else None
    if thread_pool:
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=workers)
    else:
        executor = concurrent.futures.ProcessPoolExecutor(max_workers=workers)
    futures = {executor.submit(target, *target_args): target_args for target_args in all_target_args}
    for future in concurrent.futures.as_completed(futures):
        target_args = futures[future]
        try:
            result = future.result()
            result_func(target_args, result)
        except Exception as exc:
            exception_func(target_args, exc)


def _file_lines(path):
    f = None
    try:
        f = open(_path(path), 'r') if path != '-' else sys.stdin
        return [line for line in [line.partition('#')[0].strip() for line in f] if len(line) > 0]
    finally:
        if f is not None and path != '-':
            f.close()


def _make_client(node_object, service):
    session = requests.Session()
    session.auth = requests.auth.HTTPBasicAuth(node_object.get_username(), node_object.get_password())
    session.verify = False
    transport = zeep.transports.Transport(session=session)
    wsdl = f'{node_object.get_url()}/ws/{service}?wsdl'
    client = zeep.Client(wsdl, transport=transport)
    return client


def _path(purepath_or_string):
    if not issubclass(type(purepath_or_string), PurePath):
        purepath_or_string = Path(purepath_or_string)
    return purepath_or_string.expanduser().resolve()


class _BaseCli(object):

    def __init__(self):
        super().__init__()
        self._args = None
        self._errors = 0
        self._nodes = None
        self._parser = None
        self._subparsers = None

    def run(self):
        self._make_parser()
        self._args = self._parser.parse_args()
        if self._args.debug_cli:
            print(self._args)
        if self._args.fun is None:
            raise RuntimeError('internal error: dispatch is unset')
        if not callable(self._args.fun):
            raise RuntimeError('internal error: dispatch is not callable')
        self._args.fun()
        sys.exit(self._errors)

    def _copyright(self):
        print(lockss.soap.__copyright__)

    def _get_nodes(self):
        if self._nodes is None:
            self._nodes = list()
            self._nodes.extend(self._args.remainder)
            self._nodes.extend(self._args.node)
            for path in self._args.nodes:
                self._nodes.extend(_file_lines(path))
            if len(self._nodes) == 0:
                self._parser.error('list of nodes to process is empty')
        return self._nodes

    def _get_password(self):
        if not self._args.password:
            self._args.password = getpass.getpass('UI password: ')
        return self._args.password

    def _get_username(self):
        if not self._args.username:
            self._args.username = getpass.getpass('UI username: ')
        return self._args.username

    def _license(self):
        print(lockss.soap.__license__)

    def _make_option_debug_cli(self, container):
        container.add_argument('--debug-cli',
                               action='store_true',
                               help='print the result of parsing command line arguments')

    def _make_option_output_format(self, container):
        container.add_argument('--output-format',
                               metavar='FMT',
                               choices=tabulate.tabulate_formats,
                               default='simple',
                               help='set tabular output format to %(metavar)s (default: %(default)s; choices: %(choices)s)')

    def _make_option_verbose(self, container):
        container.add_argument('--verbose', '-v',
                               action='store_true',
                               help='print verbose error messages')

    def _make_options_job_pool(self, container):
        group = container.add_argument_group(title='job pool options')
        mutually_exclusive_group = group.add_mutually_exclusive_group()
        group.add_argument('--pool-size',
                           metavar='SIZE',
                           type=int,
                           default=os.cpu_count(),
                           help='nonzero size of job pool (default: %(default)s)')
        mutually_exclusive_group.add_argument('--process-pool',
                                              action='store_true',
                                              help='use a process pool')
        mutually_exclusive_group.add_argument('--thread-pool',
                                              action='store_true',
                                              help='use a thread pool (default)')

    def _make_options_nodes(self, container):
        group = container.add_argument_group(title='node arguments and options')
        group.add_argument('remainder',
                           metavar='HOST:PORT',
                           nargs='*',
                           help='node to process')
        group.add_argument('--node', '-n',
                           metavar='HOST:PORT',
                           action='append',
                           default=list(),
                           help='add %(metavar)s to the list of nodes to process')
        group.add_argument('--nodes', '-N',
                           metavar='FILE',
                           action='append',
                           default=list(),
                           help='add the nodes in %(metavar)s to the list of nodes to process')
        group.add_argument('--password', '-p',
                           metavar='PASS',
                           help='UI password (default: interactive prompt)')
        group.add_argument('--username', '-u',
                           metavar='USER',
                           help='UI username (default: interactive prompt)')

    def _make_parser(self):
        for cls in [rich_argparse.RichHelpFormatter]:
            cls.styles.update({
                'argparse.args': f'bold {cls.styles["argparse.args"]}',
                'argparse.groups': f'bold {cls.styles["argparse.groups"]}',
                'argparse.metavar': f'bold {cls.styles["argparse.metavar"]}',
                'argparse.prog': f'bold {cls.styles["argparse.prog"]}',
            })

    def _make_parser_copyright(self, container):
        parser = container.add_parser('copyright',
                                      description='Show copyright and exit.',
                                      help='show copyright and exit',
                                      formatter_class=self._parser.formatter_class)
        parser.set_defaults(fun=self._copyright)

    def _make_parser_license(self, container):
        parser = container.add_parser('license',
                                      description='Show license and exit.',
                                      help='show license and exit',
                                      formatter_class=self._parser.formatter_class)
        parser.set_defaults(fun=self._license)

    def _make_parser_usage(self, container):
        parser = container.add_parser('usage',
                                      description='Show detailed usage and exit.',
                                      help='show detailed usage and exit',
                                      formatter_class=self._parser.formatter_class)
        parser.set_defaults(fun=self._usage)

    def _make_parser_version(self, container):
        parser = container.add_parser('version',
                                      description='Show version and exit.',
                                      help='show version and exit',
                                      formatter_class=self._parser.formatter_class)
        parser.set_defaults(fun=self._version)

    def _usage(self):
        self._parser.print_usage()
        print()
        uniq = set()
        for cmd, par in self._subparsers.choices.items():
            if par not in uniq:
                uniq.add(par)
                for s in par.format_usage().split('\n'):
                    usage = 'usage: '
                    print(f'{" " * len(usage)}{s[len(usage):]}' if s.startswith(usage) else s)

    def _version(self):
        print(lockss.soap.__version__)
