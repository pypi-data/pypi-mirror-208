#!/usr/bin/env python3
import click
import subprocess
import locale
import sys
import os
import signal
import multiprocessing
from contextlib import suppress


def print_command_result(id, status, stdout, stderr):
    click.secho('[%s] status %s' % (id, status) if status else '[%s] success' %
                id, fg='black', bg='white', err=True, bold=True)
    if stderr:
        click.secho(stderr, err=True, fg='red')
    if stdout:
        click.echo(stdout)


def get_output(cmd, stdin_bytes=b'', timeout=None, id=None, exit_on_success=True):
    p = None

    def h(signum, frame):
        with suppress(Exception):
            os.kill(p.pid, signal.SIGKILL)
        with suppress(Exception):
            os.kill(os.getpid(), signal.SIGKILL)
    signal.signal(signal.SIGINT, h)
    signal.signal(signal.SIGTERM, h)
    cmd = list(c.encode(locale.getpreferredencoding()) for c in cmd)
    n = 0
    while True:
        try:
            n += 1
            p = subprocess.Popen(
                cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
            stdout, stderr = p.communicate(stdin_bytes, timeout=timeout)
            if exit_on_success:
                return id, p.returncode, stdout, stderr
            else:
                print_command_result(id, p.returncode, stdout, stderr)
        except subprocess.TimeoutExpired as err:
            p.kill()
            click.secho('[%s.%s] %s' % (id, n, err), err=True, fg='red')


def decode_bytes(s):
    with suppress(Exception):
        s = s.decode('utf-8', 'ignore')
    return str(s)


def exec(args):
    command, timeout, id, exit_on_success = args
    def escape_spaces(cmd): return " ".join(
        ("\'%s\'" % c if " " in c else c) for c in cmd)
    click.secho('[%s] %s ' % (id, escape_spaces(command)),
                fg='yellow', underline=True, bold=True, err=True)
    id, status, stdout_bytes, stderr_bytes = get_output(
        command, timeout=timeout, id=id, exit_on_success=exit_on_success)
    stdout = decode_bytes(stdout_bytes).strip() if stdout_bytes else ''
    stderr = decode_bytes(stderr_bytes).strip() if stderr_bytes else ''
    return id, status, stdout, stderr


pool = None


@click.command(help='Execute command until success')
@click.option('--threads', '-j', help='thread count', type=int, default=1)
@click.option('--timeout', '-t', help='timeout in seconds', type=int, default=None)
@click.option('--iterations', '-i', help='number of successful runs', type=int, default=1)
@click.argument('command', type=str, nargs=-1)
def run(command, threads, timeout, iterations):
    if not command:
        click.secho('error: missing command', err=True, fg='red')
        sys.exit(1)
    global pool
    finished = 0
    task_count = (iterations + threads - 1) if iterations else threads
    tasks = list((command, timeout, i, iterations > 0,)
                 for i in range(task_count))
    pool = multiprocessing.Pool(threads)
    pool.daemon = True
    results = pool.imap_unordered(exec, tasks)
    for id, status, stdout, stderr in results:
        print_command_result(id, status, stdout, stderr)
        if iterations:
            finished += 1
            if finished == iterations:
                sys.exit()


if __name__ == '__main__':
    run()
