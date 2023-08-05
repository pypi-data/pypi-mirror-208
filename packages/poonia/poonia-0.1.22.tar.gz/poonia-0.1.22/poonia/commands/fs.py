#!/usr/bin/env python3
import codecs
import fnmatch
import functools
import glob
from operator import itemgetter
from collections import defaultdict
import datetime
import hashlib
import json
import locale
import math
import random
import shutil
import subprocess
import time
import unicodedata
import uuid
import click
import os
import sys
import re


@click.group(help="File tools")
def fs(): pass


class Utils(object):
    @staticmethod
    def pglob(pattern, recurse=False):
        matches = []
        if recurse:
            for root, dirnames, filenames in os.walk('.', topdown=False):
                for filename in fnmatch.filter(filenames, pattern):
                    m = os.path.join(root, filename)
                    if os.path.isfile(m):
                        matches.append(m)
        else:
            for fn in glob.glob(pattern):
                matches.append(fn)
        return matches

    @staticmethod
    def get_in(obj, *keys):
        for k in keys:
            v = None
            try:
                v = itemgetter(k)(obj)
            except:
                pass
            if v is None:
                return None
            obj = v
        return obj

    @classmethod
    def sget_in(cls, obj, *keys):
        r = cls.get_in(obj, *keys)
        if r is None:
            return ''
        return str(r)

    @staticmethod
    def partition(pred, arr):
        t, f = [], []
        for e in arr:
            (t if pred(e) else f).append(e)
        return t, f

    @staticmethod
    def sizeof_fmt(num, suffix='B'):
        num = float(num)
        for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Yi', suffix)


def natural_sort_key(s, _nsre=re.compile('([0-9]+)')):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(_nsre, s)]


@fs.command(help='Rename files/directories inside a text editor')
@click.argument('path', default='.', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('-d', '--rename-dirs', is_flag=True)
def rename(path, rename_dirs):
    objects = os.listdir(path)
    objects.sort(key=natural_sort_key)
    dirs, files = Utils.partition(os.path.isdir, objects)

    to_rename = dirs if rename_dirs else files

    original = '\n'.join(to_rename)
    renamed = click.edit(original)
    if renamed:
        renamed = renamed.strip()

    if (not renamed or renamed == original):
        click.echo('nothing''s changed')
        sys.exit()

    renamed = renamed.split('\n')

    if (len(renamed) != len(to_rename)):
        click.echo('wrong number of rows')
        sys.exit()

    changed = [(a, b) for a, b in zip(to_rename, renamed) if a != b]
    for a, b in changed:
        click.secho(a, bold=True, nl=False)
        click.echo(' -> ', nl=False)
        click.secho(b, bold=True, nl=True)

    confirmed = click.confirm('Do you want to continue?', abort=True)

    if confirmed:
        for a, b in changed:
            os.rename(a, b)
        click.secho('Objects has been renamed!', fg='green', bold=True)


def hasext(fn, ext):
    _, fileext = os.path.splitext(fn)
    return fileext.lstrip('.').lower() in ext


@fs.command(help='Delete files without pair')
@click.option('-e', '--extensions', type=str, default='jpg,rw2', show_default=True)
def pairdel(extensions):
    extensions = set(e.lower() for e in extensions.split(','))
    files = [f for f in os.listdir('.') if os.path.isfile(
        f) and hasext(f, extensions)]
    filext = defaultdict(set)
    for fn in files:
        name, ext = os.path.splitext(fn)
        filext[name].add(ext)
    todelete = []
    for fn, fes in filext.items():
        accept = True
        for e in extensions:
            if not any(hasext(fn+fe, [e]) for fe in fes):
                accept = False
        if not accept:
            todelete.append([fn, fes])

    total_bytes = 0
    filenames_to_delete = []
    for fn, fes in sorted(todelete):
        for a in [fn+fe for fe in fes]:
            filenames_to_delete.append(a)
            click.echo(a, nl=False)
            click.echo(' [', nl=False)
            fsize = os.path.getsize(a)
            total_bytes += fsize
            click.secho('%s' % Utils.sizeof_fmt(fsize), nl=False, fg='red')
            click.echo(']')
    click.echo()
    if click.confirm('Delete listed files [%s]?' % Utils.sizeof_fmt(total_bytes)):
        for a in filenames_to_delete:
            os.remove(a)


@fs.command(help='Securely delete specified file')
@click.argument('file', type=click.File(mode='r+b', lazy=False))
def sdel(file):
    def _getsize(f):
        old_file_position = f.tell()
        f.seek(0, os.SEEK_END)
        size = f.tell()
        f.seek(old_file_position, os.SEEK_SET)
        return size

    def _randombytes(size):
        return bytearray(os.urandom(size))

    filesize = _getsize(file)
    MB = 1024**2
    with click.progressbar(range(0, filesize, MB)) as bar:
        for i in range(0, filesize, MB):
            remains = min(MB, filesize - i)
            file.write(_randombytes(remains))
            bar.update(remains)
    os.fsync(file)
    file.close()
    for c in '0123456789abcdefABCDEF':
        new_name = c * len(file.name)
        if new_name != file.name and not os.path.exists(new_name):
            os.rename(file.name, new_name)
            os.remove(new_name)
            break


@fs.command(help='Reverse random bits in file')
@click.argument('file', type=click.File(mode='rb', lazy=False))
@click.option('-n', type=int, default=1, show_default=True, help='How many bits to swap')
def bitrot(file, n):
    original_data = bytearray(file.read())
    tries = 0
    while tries < 10:
        data = original_data.copy()
        # Generate random bit locations to swap
        bit_locations = random.sample(range(len(data)*8), n)

        # Reverse the bits at the selected locations
        for loc in bit_locations:
            byte_index = loc // 8
            bit_index = loc % 8
            data[byte_index] ^= (1 << bit_index)

        # Create new filename with bit locations added
        new_filename = os.path.splitext(file.name)[
            0] + '_' + '_'.join(str(x) for x in sorted(bit_locations)) + os.path.splitext(file.name)[1]
        try:
            # Write modified data to new file
            with open(new_filename, 'xb') as f:
                f.write(data)
        except FileExistsError:
            click.secho("warning: file '%s' already exists" % new_filename,
                        err=True, fg='yellow')
            tries += 1
            continue
        click.echo('File saved as \'', nl=False)
        click.secho(new_filename, fg='green', nl=False)
        click.echo('\'')
        sys.exit(0)
    click.secho('error: too many tries',
                err=True, fg='red')
    sys.exit(1)


def duration_fmt(num):
    if math.isnan(num):
        return '--'
    for unit, m in [('s', 60), ('m', 60), ('h', 24), ('d', 7)]:
        if abs(num) < m:
            return "%3.1f%s" % (num, unit)
        num /= m
    return "%.1f%s" % (num, 'w')


def statformat(stattime, format):
    return time.strftime(format, time.localtime(stattime))


def mtime(fn):
    return os.stat(fn).st_mtime


def h(data): return hashlib.sha1(data).hexdigest()
def avg(lst): return sum(lst) / float(len(lst))


EXIFTOOL_CMD = 'exiftool -j -CreateDate -FileModifyDate --DateTimeOriginal --'.split(
    ' ')


def exiftool(fn):
    try:
        fn = fn.encode(locale.getpreferredencoding())
        r = subprocess.check_output(
            EXIFTOOL_CMD + [fn], stderr=subprocess.STDOUT)
        j = json.loads(r.decode('utf-8'))
        d = (Utils.sget_in(j, 0, 'CreateDate') or Utils.sget_in(
            j, 0, 'FileModifyDate'))[:19]
        return time.mktime(datetime.datetime.strptime(d, '%Y:%m:%d %H:%M:%S').timetuple())
    except subprocess.CalledProcessError as e:
        raise Exception(str(e.output))


class UnixTable:
    CHAR_INNER_VERTICAL = '\033(0\x78\033(B'  # (│)
    CHAR_OUTER_BOTTOM_RIGHT = '\033(0\x6a\033(B'  # (┘)
    CHAR_OUTER_TOP_RIGHT = '\033(0\x6b\033(B'  # (┐)


class WindowsTable:
    """Draw a table using box-drawing characters on Windows platforms. This uses Code Page 437. Single-line borders.
    From: http://en.wikipedia.org/wiki/Code_page_437#Characters
    """
    CHAR_INNER_VERTICAL = b'\xb3'.decode('ibm437')
    CHAR_OUTER_BOTTOM_RIGHT = b'\xd9'.decode('ibm437')
    CHAR_OUTER_TOP_RIGHT = b'\xbf'.decode('ibm437')


class SingleTable(WindowsTable if sys.platform == 'win32' else UnixTable):
    pass


def window(lst):
    a = list(lst)
    return list(zip([None]+a, a, a[1:]+[None]))


@fs.command(help='Group files by creation time')
@click.option('--mtime', 'date_source', type=click.UNPROCESSED, flag_value=mtime, default=True, help='Use file modification date')
@click.option('--exiftool', 'date_source', type=click.UNPROCESSED, flag_value=exiftool, help='Use exiftool to obtain creation date')
@click.option('--cutoff', '-c', type=int, default=10, help='Cut-off in seconds')
@click.option('--target', '-t', type=click.Path(exists=False, file_okay=False, writable=True), default='output', help='Target directory')
@click.argument('paths', nargs=-1, type=click.Path(exists=True, dir_okay=False))
@click.pass_context
def fileseries(ctx, paths, date_source, cutoff, target):
    with click.progressbar(paths) as bar:
        print(date_source('DXO_0207.JPG'))
        paths = [(p, date_source(p)) for p in bar]
    if not paths:
        click.secho('no files to process', fg='red')
        ctx.exit(1)
    paths.sort(key=lambda x: x[1])
    max_length = max(len(x[0]) for x in paths)
    group_total = 0
    group_n = 0
    new_names = []
    for pre, curr, post in window(paths):
        p, mtime = curr
        diff_prev = mtime - pre[1] if pre else float('nan')
        diff_next = post[1] - mtime if post else float('nan')
        state = ''
        if diff_prev < cutoff and diff_next < cutoff:
            state = SingleTable.CHAR_INNER_VERTICAL
        elif diff_prev < cutoff:
            state = SingleTable.CHAR_OUTER_BOTTOM_RIGHT
        elif diff_next < cutoff:
            group_total += 1
            group_n = 0
            state = SingleTable.CHAR_OUTER_TOP_RIGHT
        group_n += 1

        if state:
            _, ext = os.path.splitext(p)
            new_name = '%d_%d%s' % (group_total, group_n, ext)
        else:
            new_name = ''

        click.secho("%s  " % p.ljust(max_length), nl=False)
        click.secho(statformat(mtime, r"%Y.%m.%d %H:%M:%S "),
                    nl=False, fg='yellow', bold=True)
        click.secho("%10s " % duration_fmt(diff_prev), fg=(
            'red' if diff_prev > cutoff else 'green'), bold=True, nl=False)
        click.echo(state, nl=False)
        click.secho(" %s" % new_name, fg='blue', bold=True)
        d = mtime
        new_names.append(new_name)
    if click.confirm('Proceed?'):
        if any(new_names):
            os.mkdir(target)
        for path, dst in zip(paths, new_names):
            if not dst:
                continue
            d = os.path.join(target, dst)
            click.echo('%s -> %s' % (path[0], d))
            os.link(path[0], d)


@fs.command(help='Process file in place through a command stdin/stdout')
@click.argument('command', nargs=1, required=True)
@click.argument('files', type=click.Path(exists=True, dir_okay=False), nargs=-1)
def processfile(command, files):
    for file in files:
        click.secho("Start processing '%s'" % file, fg='yellow', err=True)
        with open(file, 'r+b') as f:
            content = f.read()
            output = subprocess.check_output(command.split(
                ' '), stderr=subprocess.STDOUT, input=content)
            f.seek(0)
            f.write(output)
            f.truncate()
        click.secho("File '%s' saved succesfully" % file, fg='green', err=True)


@fs.command(help='Move content of a directory up while combining the filename with dirname')
@click.argument('directories', type=click.Path(exists=True), nargs=-1)
@click.option('--sep', '-s', default='.', help='separator for joining directory names')
@click.option('--namefromlargest', '-b', is_flag=True, help='Get name prefix from biggest file in parent directory')
@click.option('--yes', '-y', is_flag=True, help='Do not ask for confirmation')
def moveup(directories, sep, namefromlargest, yes):

    def splitpath(path):
        segments = os.path.normpath(path).split(os.path.sep)
        if segments:
            segments[0] += os.sep
        return segments

    def up(path, level=1):
        segments = splitpath(path)
        return os.path.join(*segments[:-level])

    def dircontent(path, _type=None):
        content = [os.path.join(path, f) for f in os.listdir(path)]
        if _type == 'f':
            content = [a for a in content if os.path.isfile(a)]
        return content

    def up_with_prefix(path, prefix):
        base = os.path.basename(path)
        return os.path.join(up(path, 2), prefix+base)

    for directory in directories:
        directory = os.path.abspath(directory)
        if not os.path.isdir(directory):
            click.secho("'%s' is not a directory" %
                        directory, fg='red', err=True)
            continue
        parent = up(directory)
        content = [os.path.join(directory, f) for f in os.listdir(directory)]
        if not content:
            click.secho("'%s' is empty" % directory, fg='red', err=True)
            continue

        prefix = os.path.basename(directory)
        if namefromlargest:
            largest = sorted(dircontent(parent, 'f'),
                             key=os.path.getsize, reverse=True)[:1]
            if not largest:
                click.secho("'%s' contains no files: cannot find largest" %
                            parent, fg='red', err=True)
                continue
            prefix, _ = os.path.splitext(os.path.basename(largest[0]))
        prefix += sep

        job = [(p, up_with_prefix(p, prefix)) for p in content]
        for src, dst in job:
            click.secho(src, fg='yellow', nl=False)
            click.echo(' -> ')
            click.secho(dst, fg='green')
            click.echo()

        if yes or click.confirm('do you want to continue'):
            for src, dst in job:
                shutil.move(src, dst)
            if not dircontent(directory):
                os.rmdir(directory)
            click.secho('done.', bold=True)


@fs.command(help='Move single dirs one level up, combine names')
@click.option('--sep', default=' - ', help='separator for joining directory names')
def flatten(sep):
    def split(path):
        return os.path.normpath(path).split(os.path.sep)

    def random_name():
        return uuid.uuid4().hex

    def is_single_child(path):
        base, _ = os.path.split(path)
        if base in ('', '.'):
            return False
        return len(os.listdir(base)) == 1

    def replace(path, newname, level=0):
        segments = split(path)
        level = len(segments)-level
        segments[level-1] = newname
        return os.path.join(*segments)

    def renamedir(path, newname, level=0):
        segments = split(path)
        level = len(segments)-level
        oldpath = os.path.join(*segments[:level])
        newpath = replace(oldpath, newname)
        # print 'rename %s\n       %s' % (oldpath, newpath)
        os.rename(oldpath, newpath)
        return newpath

    def moveall(src, dest):
        # print 'move %s\n     %s' % (src, dest)
        files = os.listdir(src)
        for f in files:
            shutil.move(os.path.join(src, f), dest)

    def moveup(src, separator):
        segments = split(src)
        name = separator.join([segments[-2], segments[-1]])
        rnd = renamedir(src, random_name())
        renamedir(src, name, level=1)
        rnd = replace(rnd, name, level=1)
        moveall(rnd, os.path.dirname(rnd))
        os.rmdir(rnd)

    def walkdirs(path='.'):
        out = []
        for root, dirs, files in os.walk(".", topdown=False):
            for name in dirs:
                dirpath = os.path.join(root, name)
                out.append(dirpath)
        return out

    def dir_to_flatten():
        try:
            return next(d for d in walkdirs() if is_single_child(d))
        except:
            return None

    while dir_to_flatten():
        d = dir_to_flatten()
        if click.confirm(d):
            moveup(d, sep)


_LANGUAGES = {
    'pl': (u'ąćńłżźę', ['iso-8859-2', 'windows-1250']),
    'es': (u'áéíóúüñ¿¡', ['iso-8859-1', 'windows-1252']),
    'gr': (u'αβγδεζηθικλμνξοπρςστυφχψω', ['iso-8859-7', 'windows-1257']),
    'de': (u'äöüß', ['iso-8859-15', 'windows-1252', 'cp273']),
    'ru': (u'абвгдеёжзийклмнопрстуфхцчшщъыьэюя', ['iso-8859-5', 'windows-1251', 'koi8-r']),
    'ua': (u'абвгдеёжзийклмнопрстуфхцчшщъыьэюя', ['iso-8859-5', 'windows-1251', 'koi8-u']),
}


def fix_encoding(text, language, encoding='utf-8'):
    def strip_accents(s):
        s = ''.join(c for c in unicodedata.normalize(
            'NFD', s) if unicodedata.category(c) != 'Mn')
        s = s.replace('ł', 'l').replace('Ł', 'L')
        return s
    lang_data = _LANGUAGES.get(language)
    if not lang_data:
        return text

    def grade(s): return sum([s.count(c) for c in lang_data[0]])
    try:
        decoded = []
        for e in lang_data[1] + ['utf-8', 'utf-16', 'utf-32']:
            try:
                decoded.append((e, text.decode(e, 'ignore')))
            except:
                pass
        enc, text = sorted(decoded, key=lambda e: grade(e[1]), reverse=True)[0]
    except:
        pass
    text = text[3:] if text[0:3] == codecs.BOM_UTF8 else text
    if encoding == 'ascii':
        return strip_accents(text).encode(encoding)
    return enc, text.encode(encoding)


@fs.command(help='Fix text encoding')
@click.option('-ext', '--extension', default='srt,txt,ass', show_default=True)
@click.option('-e', '--encoding', default='utf-8', show_default=True)
@click.option('-r', '--recurse', is_flag=True)
@click.option('-l', '--language', default='pl', show_default=True)
@click.option('-b', '--backup', is_flag=True)
def encoding(extension, encoding, recurse, language, backup):
    exts = set(extension.split(','))
    to_fix = []
    language = language.lower()
    if not language in _LANGUAGES.keys():
        click.echo('unknown language', err=True)
        sys.exit(1)
    for fn in Utils.pglob('*', recurse=recurse):
        _, ext = os.path.splitext(fn)
        if ext[1:] not in exts:
            continue
        with open(fn, 'rb') as f:
            text = f.read()
        fixed = fix_encoding(text, language, encoding)
        if fixed[1] != text:
            to_fix.append([fn, fixed])
    if not to_fix:
        click.echo('nothing to process')
        return
    for fn, (encoding, content) in to_fix:
        click.secho(fn, fg='green', nl=False)
        click.secho(' [%s]' % encoding, fg='blue')
    if click.confirm('do you want to continue?'):
        for fn, (encoding, content) in to_fix:
            if backup:
                base, ext = os.path.splitext(fn)
                backup_fn = os.path.join(base + '_bak' + ext)
                shutil.copyfile(fn, backup_fn)
            with open(fn, 'wb') as f:
                f.write(content)
            with open(fn, 'wb') as f:
                f.write(content)
        click.echo('success')


def levenshtein_distance(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1
    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(
                    1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]


@fs.command(help='Rename files to closest match with different extension')
@click.option('--change', type=str, default='srt', show_default=True)
@click.option('--match', type=str, default='mkv,avi,mp4', show_default=True)
def pairmatch(change, match):
    def get_files_with_extensions(exts):
        def hasext(fn, ext):
            _, fileext = os.path.splitext(fn)
            return fileext.lstrip('.').lower() in ext
        extensions = set(e.lower() for e in exts)
        return sorted([f for f in os.listdir('.') if os.path.isfile(f) and hasext(f, extensions)])

    def tokenize_unique(arr):
        def tokenize(s):
            s = s.replace("'", '')
            return [x.strip().lstrip('0') for x in re.split('(\d+|\W+)', s.lower()) if x and not re.findall('^([^a-z0-9]+)$', x)]
        tokenized = [tokenize(e) for e in arr]
        if not tokenized:
            return []
        common = set(functools.reduce(
            lambda x, y: x.intersection(y), (set(e) for e in tokenized)))
        for c in common:
            for e in tokenized:
                e.remove(c)
        return tokenized

    def common_elements(l1, l2):
        return len([x for x in l1 if x in l2])

    def highrank(arr, key=None):
        if not arr:
            return []
        if not key:
            def key(x): return x
        s = sorted(arr, key=key, reverse=True)
        highkey = key(s[0])
        return [x for x in arr if key(x) == highkey]

    def base(fn): return os.path.splitext(fn)[0]

    to_match = [x for x in get_files_with_extensions(match.split(','))]
    to_match = list(zip(to_match, tokenize_unique(base(f) for f in to_match)))

    files_to_change = [x for x in get_files_with_extensions(change.split(','))]
    tokens = tokenize_unique(base(e) for e in files_to_change)
    used = set()
    to_rename = []
    for f, t in zip(files_to_change, tokens):
        ranked = [(x[0], common_elements(t, x[1]))
                  for x in to_match if x[0] not in used]
        high = highrank(ranked, key=lambda x: x[1])
        if len(high) == 1:
            new_fn = high[0][0]
            used.add(new_fn)
            _, ext = os.path.splitext(f)
            to_rename.append([f, base(new_fn) + ext])
        else:
            to_rename.append([f, None])

    errors = {f[1] for f in to_rename if not f[1] or os.path.exists(f[1])}
    to_rename = [(a, b, b in errors) for a, b in to_rename]
    click.echo('Files to rename:')
    for src, dst, err in to_rename:
        click.secho('  %s' % src, nl=False, fg='red' if err else 'blue')
        click.echo(' -> ', nl=False)
        click.secho(dst, fg='green')
    click.echo()
    to_rename = [(a, b) for a, b, c in to_rename if not c]
    if click.confirm('Rename listed files [%d]?' % len(to_rename)):
        for a, b in to_rename:
            os.rename(a, b)


if __name__ == '__main__':
    fs()
