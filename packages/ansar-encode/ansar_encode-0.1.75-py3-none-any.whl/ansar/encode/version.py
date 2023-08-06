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

"""Helpers for implementation of version support.

Functions to assist with the coding of application version support.
"""

__docformat__ = 'restructuredtext'

__all__ = [
    'migrate',
    'cannot_upgrade',
]

def migrate(f, upgrade, *args, **kwargs):
    """Recover the specified file and store (i.e. migrate) as necessary."""
    r, v = f.recover()
    a = upgrade(r, v, *args, **kwargs)
    if id(a) != id(r):
        f.store(a)
    return a

def cannot_upgrade(r, v):
    """Raise a ValueError with relevant information about the failed upgrade of an object."""
    raise ValueError('cannot upgrade "%s" (version "%s")' % (r.__class__.__name__, v))
