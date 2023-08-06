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

"""Manage the versioning of documents, requests and protocols.

Functions to support the full, formal management of object versioning.
"""

__docformat__ = 'restructuredtext'

__all__ = [
    'reachable',
    'released_document',
]

import sys

from .portable import *
from .runtime import *
from .message import *

__all__ = [
    'reachable',
    'released_document',
]

reachable = {}

#
#
def released_document(doc):
    """Register an application object for saving to disk.

    This function registers a document for the purposes of version
    support. Registered information is used during encoding to select
    the proper name slice.

    Registered materials are also used during building and releasing
    to enforce the broader application versioning strategy.

    :param doc: the base document type
    :type doc: a registered message type
    :return: None
    """
    e = UserDefined(doc)

    # Compile the set of all messages reachable from the
    # specified type.
    r = set(t for t in reachable_type(e, set()))

    # Compile a type-version dictionary for the set of
    # reachable classes.
    d = {}
    for t in r:
        v = get_version(t)
        if v is None:
            n1 = e.element.__name__
            n2 = t.__name__
            s = 'cannot register "%s" for version management - "%s" is unversioned.' % (n1, n2)
            raise CodingProblem(s)
        d[t] = v

    reachable[e.element] = d


def reachable_type(t, bread):
    """Determine the main type, e.g. portable, UDT or content of a container."""
    if isinstance(t, UserDefined):
        e = t.element
        for _, v in e.__art__.value.items():
            yield from reachable_type(v, bread)
        yield e
    elif isinstance(t, (VectorOf, ArrayOf, DequeOf, SetOf)):
        yield from reachable_type(t.element, bread)
    elif isinstance(t, MapOf):
        yield from reachable_type(t.value, bread)
    elif isinstance(t, PointerTo):
        k = id(t)
        if k not in bread:
            bread.add(k)
            yield from reachable_type(t.element, bread)
    elif isinstance(t, Any):
        for p in t.possibles:
            yield from reachable_type(p, bread)
