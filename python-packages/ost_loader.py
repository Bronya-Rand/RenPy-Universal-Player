# Copyright (C) 2021 GanstaKingofSA (Hanaka)
# Copyright 2004-2021 Tom Rothamel <pytom@bishoujo.us>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Modded loader.py file to support peeking.

import os
import renpy
import re
import io


class AltSubFile(object):
    def __init__(self, fn, base, length, start=None):
        self.fn = fn

        self.f = None

        self.base = base
        self.offset = 0
        self.length = length
        self.start = start

        if not self.start:
            self.name = fn
        else:
            self.name = None

    def open(self):
        self.f = open(self.fn, "rb")
        self.f.seek(self.base)

    def __enter__(self):
        return self

    def __exit__(self, _type, value, tb):
        self.close()
        return False

    def read(self, length=None):

        if self.f is None:
            self.open()

        maxlength = self.length - self.offset

        if length is not None:
            length = min(length, maxlength)
        else:
            length = maxlength

        rv1 = self.start[self.offset : self.offset + length]
        length -= len(rv1)
        self.offset += len(rv1)

        if length:
            rv2 = self.f.read(length)
            self.offset += len(rv2)
        else:
            rv2 = ""

        return rv1 + rv2

    def readline(self, length=None):

        if self.f is None:
            self.open()

        maxlength = self.length - self.offset
        if length is not None:
            length = min(length, maxlength)
        else:
            length = maxlength

        # If we're in the start, then read the line ourselves.
        if self.offset < len(self.start):
            rv = ""

            while length:
                c = self.read(1)
                rv += c
                if c == "\n":
                    break
                length -= 1

            return rv

        # Otherwise, let the system read the line all at once.
        rv = self.f.readline(length)

        self.offset += len(rv)

        return rv

    def readlines(self, length=None):
        rv = []

        while True:
            l = self.readline(length)

            if not l:
                break

            if length is not None:
                length -= len(l)
                if l < 0:
                    break

            rv.append(l)

        return rv

    def xreadlines(self):
        return self

    def __iter__(self):
        return self

    def __next__(self):  # @ReservedAssignment
        rv = self.readline()

        if not rv:
            raise StopIteration()

        return rv

    next = __next__

    def flush(self):
        return

    def seek(self, offset, whence=0):

        if self.f is None:
            self.open()

        if whence == 0:
            offset = offset
        elif whence == 1:
            offset = self.offset + offset
        elif whence == 2:
            offset = self.length + offset

        if offset > self.length:
            offset = self.length

        self.offset = offset

        offset = offset - len(self.start)
        if offset < 0:
            offset = 0

        self.f.seek(offset + self.base)

    def peek(self, offset):
        if self.f is None:
            self.open()
        return self.f.read()

    def tell(self):
        return self.offset

    def close(self):
        if self.f is not None:
            self.f.close()
            self.f = None

    def write(self, s):
        raise Exception("Write not supported by SubFile/AltSubFile")


def load_from_archive(name):
    """
    Returns an open python file object of the given type from an archive file.
    """

    for prefix, index in renpy.loader.archives:
        if not name in index:
            continue

        afn = renpy.loader.transfn(prefix)

        data = []

        # Direct path.
        if len(index[name]) == 1:

            t = index[name][0]
            if len(t) == 2:
                offset, dlen = t
                start = b""
            else:
                offset, dlen, start = t

            rv = AltSubFile(afn, offset, dlen, start)

        # Compatibility path.
        else:
            with open(afn, "rb") as f:
                for offset, dlen in index[name]:
                    f.seek(offset)
                    data.append(f.read(dlen))

                rv = io.BytesIO(b"".join(data))

        return rv

    return None


if renpy.version_tuple > (6, 99, 12, 4, 2187):
    renpy.loader.file_open_callbacks.remove(renpy.loader.load_from_archive)
    renpy.loader.file_open_callbacks.append(load_from_archive)


def load(name, tl=True):

    if renpy.version_tuple > (6, 99, 12, 4, 2187):
        gp = renpy.loader.get_prefixes(tl)
        if renpy.display.predict.predicting:  # @UndefinedVariable
            if threading.current_thread().name == "MainThread":
                if not (
                    renpy.emscripten or os.environ.get("RENPY_SIMULATE_DOWNLOAD", False)
                ):
                    raise Exception(
                        "Refusing to open {} while predicting.".format(name)
                    )
    else:
        gp = renpy.loader.get_prefixes()

    if renpy.config.reject_backslash and "\\" in name:
        raise Exception("Backslash in filename, use '/' instead: %r" % name)

    name = re.sub(r"/+", "/", name).lstrip("/")

    for p in gp:
        rv = renpy.loader.load_core(p + name)
        if rv is not None:
            if renpy.version_tuple > (6, 99, 12, 4, 2187):
                return rv
            else:
                return io.open(rv.name, "rb")

    raise IOError("Couldn't find file '%s'." % name)
