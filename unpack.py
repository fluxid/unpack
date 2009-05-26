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

def recursive_rmdir(dir):
    for root, dirs, files in os.walk(dir, topdown=False):
        for name in files:
            os.remove(path.join(root, name))
        for name in dirs:
            os.rmdir(path.join(root, name))
    os.rmdir(dir)

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


def unpack(filepath, destination, createdir):
    print 'lol'
    filename = path.basename(filepath)

    if not path.isfile(filepath):
        pprint('%s does not exist or isn\'t a file' % filename, 3, False)
        return

    filename2 = filename.lower()
    
    for ext, cmd in cmds:
        if filename2.endswith(ext):
            import tempfile, subprocess

            archname = filename[:-len(ext)]

            #cmd2 = cmd + ' \'' + filepath.replace('\\', '\\\\' + '\''
            cmd2 = cmd + (filepath,)

            tmp = tempfile.mkdtemp(prefix='unpack_', dir=destination)
            os.chdir(tmp)

            try:
                p = subprocess.Popen(cmd2, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
                pstdout, pstderr = p.communicate()
            except OSError, e:
                print >>sys.stderr, 'unpack: Error when trying to run `%s`. Exception was: "%s"' % (' '.join(cmd2), e)
                rmdir(tmp)
                return
                
            if (p.returncode):
                print >>sys.stderr, 'unpack: Error when running `%s`, process returned code %d. Try it yourself to get the actual error.' % (' '.join(cmd2), p.returncode)
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
                print >>sys.stderr, 'unpack: No files or directories found in %s' % filename
                os.rmdir(tmp)

            return
    print >>sys.stderr, 'unpack: Unsupported filetype of %s' % filepath


def main():
    g = True
    d = True
    args = True
    sys.argv.pop(0)

    if not sys.argv:
        print """unpack-0.1 - universal decompressing script
Copyright (c) 2009 Tomasz Kowalczyk

Arguments:
    +g  Turn globbing on (default)
    -g  Turn globbing off
    +d  Turn creating directories on (default)
    -d  Turn creating directories off (unimplemented)

Globbing and creating directories can be turned on and off many times e.g.:
    unpack -g file1[0-1] -d +g file2* +d file3

Everything after -- will not be treated as argument e.g.:
    unpack -- -g
instead of turning globbing off, will try to unpack file -g

Unpack will create directories in working directory only if archive contains
two or more directories/files.

If extracted file already exists, it will get a number e.g.:
    somefile.png -> somefile[1].png
    somedir -> somedir[1]
"""
        return

    cwd = os.getcwd()

    for i in sys.argv:
        if i == '--':
            args = False
            continue

        if args:
            arg = i.lower()
            if arg == '+g':
                g = True
                continue
            elif arg == '-g':
                g = False
                continue
            elif arg == '+d':
                d = True
                continue
            elif arg == '-d':
                d = False
                continue

        i = path.expanduser(i)
        i = path.abspath(i)
        
        if g:
            import glob
            files = glob.glob(i)

            for j in files:
                unpack(j, cwd, d)
        else:
            unpack(i, cwd, d)
        os.chdir(cwd)

if __name__ == '__main__':
    main()
