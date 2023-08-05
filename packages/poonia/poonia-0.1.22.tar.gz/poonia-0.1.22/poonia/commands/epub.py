#!/usr/bin/python3
import fnmatch
import glob
import itertools
import sys
import click
import subprocess
import re
import os
import tempfile
import locale
from collections import OrderedDict
import random
import string
from contextlib import contextmanager


@click.group(help="ePub utilities")
def epub():
    Utils.require_exe('pandoc')


class Utils(object):
    @staticmethod
    def where(program):
        import os
        import sys

        if sys.platform == "win32" and not program.lower().endswith(".exe"):
            program += ".exe"

        def is_exe(fpath):
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

        fpath, fname = os.path.split(program)
        if fpath:
            if is_exe(program):
                return program
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                path = path.strip('"')
                exe_file = os.path.join(path, program)
                if is_exe(exe_file):
                    return exe_file
        return None

    @classmethod
    def require_exe(cls, exe):
        if not cls.where(exe):
            click.secho("error: cannot find executable '%s'" %
                        exe, fg='red', bold=True, err=True)
            sys.exit(1)

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
    def safe_filename(s):
        s = re.sub('(\w)(: +)', r'\1 - ', s)
        for c in '/\\:':
            s = s.replace(c, '-')
        s = s.replace('"', "'")
        for c in '?<>|*':
            s = s.replace(c, '_')
        return s.strip()


@contextmanager
def temp_with_content(content):
    fd, path = tempfile.mkstemp()
    try:
        with os.fdopen(fd, 'w') as tmp:
            tmp.write(content)
            tmp.flush()
        yield path
    finally:
        os.remove(path)


LUA = r'''
function remove_attr (x)
  if x.classes then
    x.classes = {}
  end
  if x.attr then
    x.attr = pandoc.Attr()
  end
  return x
end
return {
  { Image = (function()
        return {}
    end) },
  { Blocks = remove_attr },
}
'''

CSS = r'''
body { margin: 0; text-align: justify; font-size: medium; font-family: Athelas, Georgia, serif; }
code { font-family: monospace; font-size: small }
h1 { text-align: left; }
h2 { text-align: left; }
h3 { text-align: left; }
h4 { text-align: left; }
h5 { text-align: left; }
h6 { text-align: left; }
h1.title { }
h2.author { }
h3.date { }
ol.toc { padding: 0; margin-left: 1em; }
ol.toc li { list-style-type: none; margin: 0; padding: 0; }

h1, h2 { -epub-hyphens: none; -webkit-hyphens: none; -moz-hyphens: none; hyphens: none;}
p, blockquote { orphans: 2; widows: 2;}
p, figcaption { -epub-hyphens: auto; -webkit-hyphens: auto; -moz-hyphens: auto; hyphens: auto;}

h1, h2, h3, h4, h5, h6,table, img, figure, video,[data-page-break~=inside][data-page-break~=avoid] { page-break-inside: avoid; }
[data-page-break~=after] { page-break-after: always; }
h1, h2, h3, h4, h5, h6, [data-page-break~=after][data-page-break~=avoid] { page-break-after: avoid; }
[data-page-break~=before] { page-break-before: always; }
[data-page-break~=before][data-page-break~=avoid] { page-break-before: avoid; }
img[data-page-break~=before] { page-break-before: left; }

p { margin-bottom: 0; text-indent: 1.5em; margin-top: 0 }
'''

CSS_DASH_LIST_STYLE = '''
ul { list-style-type: none; }
ul > li:before { content: "–"; position: absolute; margin-left: -1.1em; }
'''

PANDOC_TO_MARKDOWN_CMD = 'pandoc -t markdown --reference-location=block --wrap=none'.split(
    ' ')


def pandoc_to_markdown(fn, header_shift=0):
    try:
        fn = fn.encode(locale.getpreferredencoding())
        CMD = PANDOC_TO_MARKDOWN_CMD[:]
        if header_shift:
            CMD += ['--shift-heading-level-by=%d' % header_shift]
        CMD += ['--id-prefix=%s' %
                (''.join(random.choice(string.ascii_uppercase) for _ in range(20)))]
        r = subprocess.check_output(CMD + [fn], stderr=subprocess.STDOUT)
        return r.decode('utf-8')
    except subprocess.CalledProcessError as e:
        return str(e.output)


def clear_markdown(src):
    html = subprocess.check_output(['pandoc', '--from=markdown', '--to=html'],
                                   stderr=subprocess.STDOUT, input=bytes(src, 'utf-8')).decode('utf-8')
    markdown = subprocess.check_output(['pandoc', '--from=html', '--to=markdown-raw_html-native_divs'],
                                       stderr=subprocess.STDOUT, input=bytes(html, 'utf-8')).decode('utf-8')
    return markdown


# --epub-cover-image=
PANDOC_MARKDOWN_TO_EPUB_CMD = 'pandoc -f markdown -t epub --strip-comments'.split(
    ' ')


def markdown_to_epub(target_fn, src, toc_depth=1, css=None, cover=None):
    try:
        target_fn = target_fn.encode(locale.getpreferredencoding())
        src = bytes(src, 'utf-8')
        CMD = PANDOC_MARKDOWN_TO_EPUB_CMD[:]
        CMD += ['--toc-depth=%d' % toc_depth]
        if cover:
            CMD += ['--epub-cover-image=%s' % cover]
        if css:
            for c in css:
                CMD += ['--css=%s' % c]
        with temp_with_content(CSS) as css_path, temp_with_content(LUA) as lua_path:
            CMD += ['--lua-filter=%s' % lua_path]
            CMD += ['--css=%s' % css_path]
            r = subprocess.check_output(
                CMD + ['-o', target_fn], stderr=subprocess.STDOUT, input=src)
        return r.decode('utf-8')
    except subprocess.CalledProcessError as e:
        return str(e.output)


def safe_filename(s):
    s = re.sub('(\w)(: +)', r'\1 - ', s)
    for c in '/\\:':
        s = s.replace(c, '-')
    s = s.replace('"', "'")
    for c in '?<>|*':
        s = s.replace(c, '_')
    return s.strip()


def until_unchanged(s, f):
    s1 = s
    while True:
        s2 = f(s1)
        if s2 == s1:
            break
        s1 = s2
    return s2


def re_first_match_or_empty(regexp, s):
    m = re.findall(regexp, s)
    return m[0] if m else ''


def markdown_header_level(s): return len(s)-len(s.lstrip('#'))


def find_chapters(src):
    p = re.compile("^#+.+$", re.MULTILINE)
    chapters = [(m.start(), m.group(), markdown_header_level(m.group()))
                for m in p.finditer(src)]
    return chapters


def capitalize_title(s): return ' '.join(
    [w.capitalize() if len(w) > 1 and w[0].isupper() else w for w in s.split(' ')])


@epub.command(help='Merge books to one epub')
@click.argument('files', type=click.Path(exists=True, dir_okay=False), nargs=-1)
@click.option('-t', '--book-title', type=str, prompt=True, required=True)
@click.option('-h', '--add-headers', is_flag=True, help='Include source file name as header')
@click.option('-o', '--output', required=True, type=str, prompt=True)
@click.option('-c', '--capitalize-headers', is_flag=True)
@click.option('-sep', '--title-separator', default=' - ', type=str)
@click.option('-seg', '--header-segments', default=100, type=int)
@click.option('-tsep', '--target-separator', type=str)
@click.option('-l', '--language', type=str, default='pl-PL')
@click.option('-css', '--css', type=click.Path(exists=True, dir_okay=False), multiple=True)
@click.option('-cov', '--cover', type=click.Path(exists=True, dir_okay=False))
def merge(files, book_title, add_headers, output, capitalize_headers, title_separator, header_segments, target_separator, language, css, cover):
    click.secho("<Processing %s>" % repr(files), fg="yellow", err=True)
    books = []
    with click.progressbar(files, label='Reading input files') as bar:
        for f in bar:
            title, _ = os.path.splitext(f)
            section = title_separator.join(
                s for s in title.split(title_separator)[:-header_segments])
            title = (target_separator or title_separator).join(
                s for s in title.split(title_separator)[-header_segments:])
            if capitalize_headers:
                title = capitalize_title(title)

            pandoc_src = pandoc_to_markdown(f)
            chapters = find_chapters(pandoc_src)
            min_header_level = min(c[2] for c in chapters) if chapters else 0
            if min_header_level:
                header_shift = (4 if section else 3) - min_header_level
                if header_shift:
                    pandoc_src = pandoc_to_markdown(f, header_shift)
                # min_header_level = min(c[2] for c in chapters) if chapters else 2
                # if min_header_level < (3 if section else 2):
                #     pandoc_src = pandoc_to_markdown(f, min_header_level + (1 if section else 0))

            books.append({
                'title': title,
                'src': pandoc_src,
                'section': section
            })

    out = u'''---
title: "%s"
language: "%s"
strip-empty-paragraphs: true
table-of-contents: false
---

''' % (book_title.replace('"', r'\"'), language.replace('"', r'\"'))

    has_sections = any(b['section'] for b in books)
    if not has_sections:
        for b in books:
            out += u'''## %s

%s

<div style="page-break-before:always;"></div>

''' % (b['title'], b['src'])
    else:
        sections = OrderedDict()
        for b in books:
            s = b['section']
            if s in sections:
                sections[s].append(b)
            else:
                sections[s] = [b]

        for s, section_books in sections.items():
            out += u'## %s\n\n' % s
            for b in section_books:
                out += u'''### %s

%s

<div style="page-break-before:always;"></div>

''' % (b['title'], b['src'])

    _, ext = os.path.splitext(output)
    if ext.lower() == '.epub':
        markdown_to_epub(
            output, out, toc_depth=2 if not has_sections else 3, css=css, cover=cover)
        click.secho("</saved '%s'>" % output, fg="yellow", err=True)
    elif ext.lower() == '.md':
        with open(output, 'w') as f:
            f.write(out)
        click.secho("</saved '%s'>" % output, fg="yellow", err=True)
    else:
        click.secho('cannot write to %s file' % output, err=True, fg='red')


def until_unchanged(s, f):
    s1 = s
    while True:
        s2 = f(s1)
        if s2 == s1:
            break
        s1 = s2
    return s2


def re_first_match_or_empty(regexp, s):
    m = re.findall(regexp, s)
    return m[0] if m else ''


def list_val_order(lst):
    i = 0
    mapping = {}
    for e in lst:
        if e in mapping:
            continue
        i += 1
        mapping[e] = i
    return mapping


class Pandoc(object):
    @staticmethod
    def _markdown_header_level(s):
        return len(s)-len(s.lstrip('#'))

    @staticmethod
    def _markdown_title(s):
        orig = '/'+s
        s = s.replace('\xa0', ' ')  # replace non-breaking space
        invisible_title = re_first_match_or_empty('{.*title="(.+?)".*}', s)
        s = re.sub('(^#+\s+|{.+?})', '', s)  # delete header and attributes
        s = re.sub('[\[\]]', '', s)
        s = re.sub('\s+', ' ', s)
        s = s.rstrip()
        s = until_unchanged(
            s, lambda s: s[1:-1] if s.startswith('[') and s.endswith(']') else s)
        s = until_unchanged(
            s, lambda s: s[1:-1] if s.startswith('*') and s.endswith('*') else s)
        return s or invisible_title or orig

    @classmethod
    def find_chapters(cls, src):
        p = re.compile("^#+.+$", re.MULTILINE)
        chapters = [(m.start(), cls._markdown_title(m.group()),
                    cls._markdown_header_level(m.group())) for m in p.finditer(src)]
        if len(chapters) < 2:  # try calibre formatting
            p = re.compile("^.+$", re.MULTILINE)
            chapters = [(m.start(), m.group()) for m in p.finditer(src)]

            def calibre_level(s):
                classes = re.findall('{(.+?)}', s)
                if not '.bold' in classes:
                    return 0
                nums = [re.sub('[^\d]', '', c) for c in classes]
                nums = [int(e) for e in nums if e]
                return max(nums)
            chapters = [(c[0], cls._markdown_title(c[1]), calibre_level(c[1]))
                        for c in chapters if calibre_level(c[1])]
        if len(chapters) < 2:  # try bold lines
            p = re.compile("^\*\*.+\*\*$", re.MULTILINE)
            chapters = [(m.start(), m.group(), 1) for m in p.finditer(src)]
            def font_size(s): return int(re_first_match_or_empty(
                'font-size\s*:\s*(\d+)', s.lower()) or '1')
            chapter_font_size = [font_size(c[1]) for c in chapters]
            font_size_order = list_val_order(chapter_font_size)
            chapter_rank = [font_size_order[c] for c in chapter_font_size]
            chapters = [(c[0], cls._markdown_title(c[1]), r)
                        for c, r in zip(chapters, chapter_rank)]
        return chapters

    @staticmethod
    def pandoc_to_markdown(fn):
        PANDOC_CMD = 'pandoc -t markdown-auto_identifiers --wrap=none'.split(
            ' ')
        try:
            fn = fn.encode(locale.getpreferredencoding())
            r = subprocess.check_output(
                PANDOC_CMD + [fn], stderr=subprocess.STDOUT)
            return r.decode('utf-8')
        except subprocess.CalledProcessError as e:
            return str(e.output)


@epub.command(help='Extract chapters to new markdown file')
@click.argument('filename', type=click.Path(exists=True, dir_okay=False))
@click.option('-i', '--include-filename', is_flag=True, help='Include source file name')
def split(filename, include_filename):
    Utils.require_exe('pandoc')
    pandoc_src = Pandoc.pandoc_to_markdown(filename)
    chapters = Pandoc.find_chapters(pandoc_src)
    for i, c in enumerate(chapters, 1):
        next_level = chapters[i][2] if len(chapters) > i else 0
        click.secho(u'% 3d: ' % i, nl=False)
        tree = ''.join(
            ['├─' if next_level > level else '└─' for level in range(1, c[2])])
        click.secho(tree, fg='red', bold=True, nl=False)
        click.secho(c[1], fg='green')

    while True:
        selected_index = click.prompt(
            'Select chapter to extract', type=click.IntRange(1, len(chapters)))-1
        selected_level = chapters[selected_index][2]
        selected_chapters = [chapters[selected_index]] + list(
            itertools.takewhile(lambda c: c[2] > selected_level, chapters[selected_index+1:]))
        start_pos = selected_chapters[0][0]
        end_pos = chapters[selected_index+len(selected_chapters)][0] if len(
            chapters) > selected_index+len(selected_chapters) else len(pandoc_src)

        target_filename = selected_chapters[0][1]
        if len(selected_chapters) <= 3:
            target_filename = ' - '.join(c[1]
                                         for c in selected_chapters if c[1] and not c[1].startswith('/'))
        if include_filename:
            base, _ = os.path.splitext(filename)
            target_filename = u'%s - %s' % (base, target_filename)

        target_filename = Utils.safe_filename(target_filename + '.md')
        target_filename = click.prompt(
            'Target filename', type=str, default=target_filename)
        with open(target_filename, 'w') as f:
            f.write(pandoc_src[start_pos:end_pos])


if __name__ == '__main__':
    epub()
