#!/usr/bin/env python
import os.path as path
import os
import sys

cmds = [
    ('.tgz', ('tar', '-xzf')),
    ('.tar.gz', ('tar', '-xzf')),
    ('.tbz2', ('tar', '-xjf')),
    ('.tar.bz2', ('tar', '-xjf')),
    ('.7z', ('7z', 'x', '-p-')),
    ('.rar', ('rar', 'x', '-p-')),
    ('.zip', ('unzip', '-P-')),
    ('.bz2', ('bzip2', '-kd')),
    #('.gz', 'gzip -d'), # does not keep files
]

def safe_rename(src, dst):
    dst2 = dst
    if path.exists(dst):
        i = 1
        isfile =  path.isfile(src)
        if isfile:
            dstl, dstr = path.split(dst)
            fn = dstr.rsplit(os.extsep, 1)
            if len(fn) == 1:
                fn1 = fn[0]
                fn2 = ''
            else:
                fn1, fn2 = fn
                fn2 = os.extsep + fn2
            fn1 = path.join(dstl, fn1)
        while True:
            if isfile:
                dst2 = '%s[%d]%s' % (fn1, i, fn2)
            else:
                dst2 = '%s[%d]' % (dst, i)
            if not path.exists(dst2):
                break
            i += 1
    os.rename(src, dst2)
    return dst2

def recursive_rmdir(directory):
    for root, dirs, files in os.walk(directory, topdown=False):
        for name in files:
            os.remove(path.join(root, name))
        for name in dirs:
            os.rmdir(path.join(root, name))
    os.rmdir(directory)

def pprint(text, color=1, stderr=False):
    star = ' *'
    if stderr:
        std = sys.stderr
    else:
        std = sys.stdout

    if std.isatty():
        if color == 1:
            star = ' \033[1;92m*\033[1;0m'
        elif color == 2:
            star = ' \033[1;93m*\033[1;0m'
        elif color == 3:
            star = ' \033[1;91m*\033[1;0m'
    for line in text.splitlines():
        print >>std, star, line


def unpack(filepath, destination):
    filename = path.basename(filepath)

    if not path.isfile(filepath):
        pprint('%s does not exist or isn\'t a file' % filename, 3, False)
        return

    filename2 = filename.lower()
    
    for ext, cmd in cmds:
        if filename2.endswith(ext):
            import tempfile, subprocess

            archname = filename[:-len(ext)]
            cmd2 = cmd + (filepath,)
            tmp = tempfile.mkdtemp(prefix='unpack_', dir=destination)
            os.chdir(tmp)

            try:
                p = subprocess.Popen(cmd2, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
                pstdout, pstderr = p.communicate()
            except OSError, e:
                pprint('Error when trying to unpack %s using %s' % (filename, cmd[0]), 3, True)
                os.rmdir(tmp)
                return
                
            if (p.returncode):
                pprint('Error when unpacking %s, process %s returned status code %d. Below is the output:' % (filename, cmd[0], p.returncode), 3, True)
                print pstdout
                recursive_rmdir(tmp)
                return

            content = os.listdir(tmp)
            
            if len(content) > 1:
                safe_rename(tmp, path.join(destination, archname))
                pprint('%s -> %s' % (filename, archname))
            elif len(content) == 1:
                dst = safe_rename(path.join(tmp, content[0]), path.join(destination, content[0]))
                os.rmdir(tmp)
                pprint('%s -> %s' % (filename, path.basename(dst)))
            else:
                pprint('No files or directories found in %s' % filename, 3, True)
                os.rmdir(tmp)

            return
    pprint('Unsupported filetype of %s' % filename, 3, True)


def main():
    sys.argv.pop(0)

    if not sys.argv:
        print """unpack-0.1 - universal decompressing script
Copyright (c) 2009 Tomasz Kowalczyk

Usage:
    unpack.py [FILES]

Unpack will create directories in working directory only if archive contains
two or more directories/files.

If extracted file already exists, it will get a number e.g.:
    somefile.png -> somefile[1].png
    somedir -> somedir[1]
"""
        return

    cwd = os.getcwd()

    for i in sys.argv:
        i = path.expanduser(i)
        i = path.abspath(i)
        
        unpack(i, cwd)
        os.chdir(cwd)

if __name__ == '__main__':
    main()
