# Author: Scott Woods <scott.suzuki@gmail.com>
# MIT License
#
# Copyright (c) 2017-2022 Scott Woods
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Storage and recovery of application data using system files.

Two primitives - write_to_file and read_from_file - and the File
class to package the common usage patterns.

.. autofunction:: write_to_file
.. autofunction:: read_from_file

.. autoclass:: File
   :members: store, recover
   :member-order: bysource
"""

__docformat__ = 'restructuredtext'

__all__ = [
    'FileFailure',
    'FileNotFound',
    'FileNoAccess',
    'FileNotAFile',
    'FileIoFailed',
    'FileEncoding',
    'File',
    'read_from_file',
    'write_to_file',
]

import os
import errno

from .portable import *
from .message import *
from .codec import *
from .json import *


# Exceptions.
class FileFailure(Exception):
    """Base exception for all file exceptions.

    :param what: the failed operation
    :type what: str
    :param name: the name of the file
    :type name: str
    :param note: a short, helpful description
    :type note: str
    :param code: the associated low-level, integer, error code
    :type code: int
    """

    def __init__(self, what, name, note, code):
        """Construct an instance of FileFailure."""
        self.what = what
        self.name = name
        self.note = note
        self.code = code

    def __str__(self):
        """Auto-convert to string representation."""
        if self.code == 0:
            s = 'cannot %s "%s", %s' % (self.what, self.name, self.note)
        else:
            s = 'cannot %s "%s", %s (%s)' % (self.what, self.name, self.note, self.code)
        return s

class FileNotFound(FileFailure):
    """The named file did not exist."""

    def __init__(self, what, name, note, code=0):
        """Construct an instance of FileNotFound."""
        FileFailure.__init__(self, what, name, note, code)

class FileNoAccess(FileFailure):
    """No access or a permissions problem."""

    def __init__(self, what, name, note, code=0):
        """Construct an instance of FileNoAccess."""
        FileFailure.__init__(self, what, name, note, code)

class FileNotAFile(FileFailure):
    """Refers to a folder or the path includes a non-folder."""

    def __init__(self, what, name, note, code=0):
        """Construct an instance of FileNotAFile."""
        FileFailure.__init__(self, what, name, note, code)

class FileAlreadyExists(FileFailure):
    """The named file already exists."""

    def __init__(self, what, name, note, code=0):
        """Construct an instance of FileAlreadyExists."""
        FileFailure.__init__(self, what, name, note, code)

class FileIoFailed(FileFailure):
    """A device I/O operation failed."""

    def __init__(self, what, name, note, code=0):
        """Construct an instance of FileIoFailed."""
        FileFailure.__init__(self, what, name, note, code)

class FileEncoding(FileFailure):
    """File or object content problem, encoding or decoding failed."""

    def __init__(self, what, name, note):
        """Construct an instance of FileEncoding."""
        FileFailure.__init__(self, what, name, note, 0)

#
#
class File(object):
    """Store and recover application values using files.

    :param name: name of the file
    :type name: str
    :param expression: formal description of the content
    :type expression: :ref:`type expression<type-expressions>`
    :param encoding: selection of representation, defaults to ``CodecJson``
    :type encoding: class
    :param create_default: return default instance if file not found on read, defaults to ``False``
    :type create_default: bool
    :param pretty_format: generate human-readable file contents, defaults to ``True``
    :type pretty_format: bool
    :param decorate_names: auto-append an encoding-dependent extension to the file name, defaults to ``True``
    :type decorate_names: bool
    """

    def __init__(self, name, expression, encoding=None, create_default=False, pretty_format=True, decorate_names=True):
        """Not published."""
        self.name = name
        self.fixed = fix_expression(expression, dict())
        self.encoding = encoding
        self.create_default = create_default
        self.pretty_format = pretty_format
        self.decorate_names = decorate_names

    def store(self, value, as_version=None, as_name=None, as_path=None):
        """Generate a representation of ``value`` and write to the saved ``name``.

        :param value: any application value
        :type value: matching the saved type expression
        :return: none
        """
        if as_path:
            if as_name:
                name = os.path.join(as_path, as_name)
            else:
                h, t = os.path.split(self.name)
                name = os.path.join(as_path, t)
        elif as_name:
            h, t = os.path.split(self.name)
            name = os.path.join(h, as_name)
        else:
            name = self.name

        write_to_file(value, name, self.fixed, version=as_version, encoding=self.encoding,
            decorate_names=self.decorate_names, pretty_format=self.pretty_format)

    def recover(self, upgrade=None, migrate=False, *args, **kwargs):
        """Read from the saved ``name``, parse and marshal into an application value.

        Version handling is implemented through the optional ``upgrade``
        and ``migrate`` parameters. These can be used to automate the
        runtime promotion of the decoded object from a specific previous version to the
        version current within the application. Refer to :ref:`versions-upgrading-and-migration`
        for details.

        The return value includes the version of the main decoded object, or None
        if the encoding and decoding applications are at the same version. This value is
        the mechanism by which applications can select different code-paths in support of
        older versions of encoded materials.

        :param upgrade: promote decoded object
        :type upgrade: function
        :param migrate: if true, store any upgraded object
        :type migrate: bool
        :param args: remaining positional parameters
        :type args: tuple
        :param kwargs: remaining named parameters
        :type kwargs: dict
        :return: 2-tuple of an application value and a version.
        :rtype: value matching the saved ``expression`` and a ``str``
        """
        try:
            r, v = read_from_file(self.fixed, self.name, encoding=self.encoding, decorate_names=self.decorate_names)
        except FileNotFound:
            if self.create_default:
                c = self.fixed
                a = make(c)
                return a, None
            raise
        if v is not None and upgrade:
            a = upgrade(r, v, *args, **kwargs)
            if migrate and id(a) != id(r):
                self.store(a)
            return a, None
        return r, v

# The primitives.
def read_from_file(expression, name, encoding=None, what=None, **kv):
    """Recover an application object from the representation loaded from the named file."""
    encoding = encoding or CodecJson
    encoding = encoding(**kv)

    # What is the caller up to;
    # Cannot read from /home/root (access or permissions)
    what = what or 'read from'

    # Add the encoding suffix according
    # to automation settings.
    name = encoding.full_name(name)

    try:
        f = open(name, 'r')
    except IOError as e:
        if e.errno == errno.ENOENT:
            raise FileNotFound(what, name, 'name does not exist', e.errno)
        elif e.errno in (errno.EACCES, errno.EPERM):
            raise FileNoAccess(what, name, 'access or permissions', e.errno)
        elif e.errno == errno.ENOTDIR:
            raise FileNotAFile(what, name, 'name in path is not a folder', e.errno)
        elif e.errno == errno.EISDIR:
            raise FileNotAFile(what, name, 'name refers to a folder', e.errno)
        raise

    try:
        s = f.read()
    except IOError as e:
        if e.errno == errno.EIO:
            raise FileIoFailed(what, name, 'device I/O failed', e.errno)
        raise
    finally:
        f.close()

    try:
        d, v = encoding.decode(s, expression)
    except CodecFailed as e:
        s = str(e)
        raise FileEncoding(what, name, s)
    return d, v

#
#
def write_to_file(a, name, expression=None, version=None, encoding=None, what=None, pretty_format=True, **kv):
    """Write a representation of the application date into the named file."""
    kv['pretty_format'] = pretty_format
    encoding = encoding or CodecJson
    encoding = encoding(**kv)
    what = what or 'write to'

    # Add the encoding suffix according
    # to automation settings.
    name = encoding.full_name(name)

    if expression is None:
        if not is_message(a):
            raise FileFailure(what, name, 'type expression required for non-message', code=0)
        expression = UserDefined(a.__class__)

    try:
        s = encoding.encode(a, expression, version)
    except CodecFailed as e:
        s = str(e)
        raise FileEncoding(what, name, s)

    try:
        # json.dumps produces a str that the file
        # module will not write to a binary handle.
        # Fair enough.
        f = open(name, 'w')
    except IOError as e:
        if e.errno == errno.ENOENT:
            # Not sure this happens, but cover the
            # case anyway.
            raise FileNotFound(what, name, 'name does not exist', e.errno)
        elif e.errno == errno.EEXIST:
            raise FileAlreadyExists(what, name, 'name already exists', e.errno)
        elif e.errno in (errno.EACCES, errno.EPERM):
            raise FileNoAccess(what, name, 'access or permissions', e.errno)
        elif e.errno == errno.ENOTDIR:
            raise FileNotAFile(what, name, 'name in path is not a folder', e.errno)
        elif e.errno == errno.EISDIR:
            raise FileNotAFile(what, name, 'name refers to a folder', e.errno)
        raise

    try:
        f.write(s)
    except IOError as e:
        if e.errno == errno.EIO:
            raise FileIoFailed(what, name, 'device I/O failed', e.errno)
        raise
    finally:
        f.close()
