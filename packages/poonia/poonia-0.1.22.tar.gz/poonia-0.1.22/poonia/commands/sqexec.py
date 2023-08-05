#!/usr/bin/env python3
import re
import sqlite3
import subprocess
import sys

import click


def escape_val(s): return "'%s'" % s.replace("\x00", "\n").replace("'", "''")
def escape_id(s): return '"%s"' % s.replace('"', '""')
def escape_cmd(s): return s if not ' ' in s else "'%s'" % s


def get_table_columns(conn: sqlite3.Connection, table_name: str) -> set:
    cur = conn.cursor()
    cur.execute('PRAGMA table_info(%s);' % table_name)
    cols = cur.fetchall()
    return {c[1] for c in cols}


def get_input_params(conn: sqlite3.Connection, table_name: str, cols: list, target_col: str):
    if not cols:
        Log.fatal('column list cannot be empty')
    cur = conn.cursor()
    query = '''
    select distinct
      %s
    from %s
    where %s is null
  ''' % (', '.join(escape_id(c) for c in cols), escape_id(table_name), escape_id(target_col))
    cur.execute(query)
    for row in cur:
        yield {k: v for k, v in zip(cols, [r if r else 'null' for r in row])}


def format_where(row):
    return ' '.join('%s %s' % (escape_id(k), ("= " + escape_val(v)) if v else "IS NULL") for k, v in row.items())


def save_result(conn: sqlite3.Connection, table_name: str, row: dict, output_field: str, output_val: str):
    cur = conn.cursor()
    cur.execute('''
    update %s
      set %s = %s
      where %s
  ''' % (escape_id(table_name), escape_id(output_field), escape_val(output_val), format_where(row)))


def get_output(cmd: list, stdin_bytes=b''):
    try:
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as err:
        return -1, None, str(err)
    stdout, stderr = p.communicate(stdin_bytes)
    return (p.returncode, stdout, stderr)


class Log(object):
    def fatal(s):
        click.secho('error: ', fg='red', bold=True, nl=False, err=True)
        click.secho(s, fg='red', err=True)
        sys.exit(1)

    def warn(s):
        click.secho('warning: ', fg='yellow', bold=True, nl=False, err=True)
        click.secho(s, fg='yellow', err=True)

    def info(s):
        click.secho(s, fg='green', err=True)


def first_or_none(x): return x[0] if len(x) > 0 else None
def col_from_pattern(s): return first_or_none(re.findall('^\{(.+)\}$', s))


def columns_from_cmd(cmd: list, cols: set) -> set:
    cmd_f = [col_from_pattern(c) for c in cmd]
    cmd_f = [x for x in cmd_f if x]
    for c in cmd_f:
        if c not in cols:
            Log.warn("column '%s' doesn't exist" % c)
    return {c for c in cmd_f if c in cols}


def replace_cmd_references(cmd: list, cols: dict) -> list:
    out = []
    for c in cmd:
        ref = col_from_pattern(c)
        out.append(cols[ref] if ref else c)
    return out


@click.command(help='Execute command on sqlite table rows')
@click.argument('command', type=str, nargs=-1)
@click.option('--input', '-i', required=True, type=click.Path(exists=True, dir_okay=False), help='input sqlite db')
@click.option('--table', '-t', required=True, help='table name')
@click.option('--output-field', '-o', required=True, help='output field')
@click.option('--stdin', help='standard input column')
@click.option('--commit-after-finish', is_flag=True)
def sqexec(input, table, output_field, command, stdin, commit_after_finish):
    conn = sqlite3.connect(input)

    table_cols = get_table_columns(conn, table)
    if not table_cols:
        Log.fatal("table '%s' doesn't exist" % table)
    if not output_field in table_cols:
        Log.fatal("table '%s' (%s) doesn't contain '%s' column" %
                  (table, ', '.join(table_cols), output_field))
    fields_to_select = columns_from_cmd(command, table_cols)
    if stdin and stdin in table_cols:
        fields_to_select.add(stdin)

    change = False
    for row in get_input_params(conn, table, fields_to_select, output_field):
        cmd = replace_cmd_references(command, row)
        Log.info(' '.join(escape_cmd(c) for c in cmd))
        code, o_stdout, o_stderr = get_output(
            cmd, b'' if not stdin else bytes(row[stdin], encoding='utf-8'))
        if code == 0:
            save_result(conn, table, row, output_field,
                        o_stdout.decode('utf-8'))
            change = True
            if not commit_after_finish:
                conn.commit()
        else:
            Log.warn("%s returned status code %s: %s" %
                     (' '.join(escape_cmd(c) for c in cmd), code, o_stderr))

    if commit_after_finish and change:
        conn.commit()
    conn.close()


if __name__ == '__main__':
    sqexec()
