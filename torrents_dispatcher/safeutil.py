#!/usr/bin/env python
"""
Original author: Alex Chan

Handles overwrite with shutil move and copy functions
"""

import os
import shutil


def _increment_filename(filename, marker='-'):
    """
    Returns a generator that yields filenames with a counter. This counter
    is placed before the file extension, and incremented with every iteration.

    For example:

        f1 = increment_filename("myimage.jpeg")
        f1.next() # myimage-1.jpeg
        f1.next() # myimage-2.jpeg
        f1.next() # myimage-3.jpeg

    If the filename already contains a counter, then the existing counter is
    incremented on every iteration, rather than starting from 1.

    For example:

        f2 = increment_filename("myfile-3.doc")
        f2.next() # myfile-4.doc
        f2.next() # myfile-5.doc
        f2.next() # myfile-6.doc

    The default marker is an underscore, but you can use any string you like:

        f3 = increment_filename("mymovie.mp4", marker="_")
        f3.next() # mymovie_1.mp4
        f3.next() # mymovie_2.mp4
        f3.next() # mymovie_3.mp4

    Since the generator only increments an integer, it is practically unlimited
    and will never raise a StopIteration exception.
    """
    # First we split the filename into three parts:
    #
    #  1) a "base" - the part before the counter
    #  2) a "counter" - the integer which is incremented
    #  3) an "extension" - the file extension
    basename, fileext = os.path.splitext(filename)

    # Check if there's a counter in the filename already - if not, start a new
    # counter at 0.
    if marker not in basename:
        base = basename
        value = 0

    # If it looks like there might be a counter, then try to coerce it to an
    # integer to get its value. Otherwise, start with a new counter at 0.
    else:
        base, counter = basename.rsplit(marker, 1)

        try:
            value = int(counter)
        except ValueError:
            base = basename
            value = 0

    # The counter is just an integer, so we can increment it indefinitely.
    while True:
        if value == 0:
            value += 1
            yield filename
        value += 1
        yield '%s%s%d%s' % (base, marker, value, fileext)


def copyfile(src, dst):
    """
    Copies a file from path src to path dst.

    If a file already exists at dst, it will not be overwritten, but:

     * If it is the same as the source file, do nothing
     * If it is different to the source file, pick a new name for the copy that
       is distinct and unused, then copy the file there.

    Returns the path to the copy.
    """
    if not os.path.exists(src):
        raise ValueError('Source file does not exist: {}'.format(src))
    elif len(os.path.basename(dst)) == 0 and os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))

    dst_gen = _increment_filename(dst)
    dst = next(dst_gen)
    while os.path.exists(dst):
        dst = next(dst_gen)
    shutil.copy(src, dst)


def move(src, dst):
    """
    Moves a file from path src to path dst.

    If a file already exists at dst, it will not be overwritten, but:

     * If it is the same as the source file, do nothing
     * If it is different to the source file, pick a new name for the copy that
       is distinct and unused, then copy the file there.

    Returns the path to the new file.
    """
    dst = copyfile(src, dst)
    os.remove(src)
    return dst
