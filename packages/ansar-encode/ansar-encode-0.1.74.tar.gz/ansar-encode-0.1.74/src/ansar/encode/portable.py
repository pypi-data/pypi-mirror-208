# Author: Scott Woods <scott.suzuki@gmail.com>
# MIT License
#
# Copyright (c) 2017-2022
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

"""Definition of the abstract type system.

* ``NO_SUCH_ADDRESS`` - `correct value for a null address`
* ``complete_list`` - `a list containing every abstract type`
* ``complete_set`` - `a set containing every abstract type`

.. autoclass:: Boolean
.. autoclass:: Byte
.. autoclass:: Character
.. autoclass:: Rune
.. autoclass:: Integer2
.. autoclass:: Integer4
.. autoclass:: Integer8
.. autoclass:: Unsigned2
.. autoclass:: Unsigned4
.. autoclass:: Unsigned8

.. autoclass:: Float4
.. autoclass:: Float8

.. autoclass:: Block
.. autoclass:: String
.. autoclass:: Unicode

.. autoclass:: Enumeration
   :members: to_name, to_number
   :member-order: bysource

.. autoclass:: ClockTime
.. autoclass:: TimeSpan
.. autoclass:: WorldTime
.. autoclass:: TimeDelta

.. autoclass:: UUID

.. autoclass:: ArrayOf
.. autoclass:: VectorOf
.. autoclass:: SetOf
.. autoclass:: MapOf
.. autoclass:: DequeOf

.. autoclass:: UserDefined
.. autoclass:: Type
.. autoclass:: PointerTo

.. autoclass:: TargetAddress
.. autoclass:: Address

.. autoclass:: Word
.. autoclass:: Any

.. autofunction:: is_portable
.. autofunction:: is_container
.. autofunction:: is_portable_class
.. autofunction:: is_container_class
.. autofunction:: is_address
"""

__docformat__ = 'restructuredtext'


from collections import deque
import sys
import time
import calendar
import re
import uuid

__all__ = [
    'Portable',
    'Container',

    'Boolean',          # The basic types. Integrals.
    'Byte',
    'Character',
    'Rune',
    'Integer2',
    'Integer4',
    'Integer8',
    'Unsigned2',
    'Unsigned4',
    'Unsigned8',

    'Float4',           # Floating point.
    'Float8',

    'Block',            # Sequence of basic units
    'String',
    'Unicode',

    'Enumeration',

    'ClockTime',        # Time.
    'TimeSpan',
    'WorldTime',
    'TimeDelta',

    'UUID',             # UUID - RFC 4122

    'ArrayOf',          # Containers.
    'VectorOf',
    'SetOf',
    'MapOf',
    'DequeOf',

    'UserDefined',      # User-defined type.
    'Type',             # Type of a message.
    'PointerTo',        # Reference to one of the above.

    'TargetAddress',    # Destination.
    'Address',          # An address, such as the sender.

    'Word',             # Instance of generic form, e.g. results of python_to_word
    'Any',              # Any message - on-the-wire, a tuple of Type and Word.

    'complete_list',
    'complete_set',

    'is_portable',
    'is_container',
    'is_structural',
    'is_portable_class',
    'is_container_class',

    'NO_SUCH_ADDRESS',  # A properly formed "null" address.

    'is_address',       # Can be used to direct movement.
    'address_on_proxy',

    'deque',            # Auto-inject into namespace.
]

# Each class is used to describe a unit
# of memory.
class Portable(object):
    """Base for all portables."""

class Container(Portable):
    """The subset of portables that contain zero or more portables."""

class Boolean(Portable):
    """True or false."""

class Byte(Portable):
    """The smallest unit of data - 8 bit, unsigned integer."""

class Character(Portable):
    """A byte that more often contains a printable ASCII character, than not."""

class Rune(Portable):
    """A Unicode codepoint."""


class Integer2(Portable):
    """A 2-byte, signed integer."""

class Integer4(Portable):
    """A 4-byte, signed integer."""

class Integer8(Portable):
    """An 8-byte, signed integer."""

class Unsigned2(Portable):
    """A 2-byte, unsigned integer."""

class Unsigned4(Portable):
    """A 4-byte, unsigned integer."""

class Unsigned8(Portable):
    """An 8-byte, unsigned integer."""

class Float4(Portable):
    """A 4-byte, floating point number."""

class Float8(Portable):
    """An 8-byte, floating point number."""


class Block(Portable):
    """A sequence of Byte."""

class String(Portable):
    """A sequence of Characters."""

class Unicode(Portable):
    """A sequence of codepoints."""

class Enumeration(Portable):
    """Integers that have names.

    :param kv: map of strings and their integer value.
    :type kv: dict
    """

    def __init__(self, **kv):
        """Refer to class."""
        self.kv = kv
        for k, v in kv.items():
            setattr(self, k, v)
        self.vk = {v: k for k, v in kv.items()}

    def to_name(self, v):
        """Accept an integer and return the related name (string).

        :param v: previously registered number.
        :type v: int
        :returns: associated name.
        :rtype: str
        """
        return self.vk[v]

    def to_number(self, k):
        """Accept a name and return the related number.

        :param k: previously registered name.
        :type k: str
        :returns: associated number.
        :rtype: int
        """
        return self.kv[k]

class ClockTime(Portable):
    """The time on the wall clock as an epoch value; a float."""

class TimeSpan(Portable):
    """Difference between two ``ClockTime`` values; a float."""

class WorldTime(Portable):
    """The time at the Greenwich meridian; a datetime object."""

class TimeDelta(Portable):
    """Difference between two ``WorldTime`` values; a timedelta object."""

class UUID(Portable):
    """An RFC 4122 UUID (random); a ``uuid.UUID`` object."""

class ArrayOf(Container):
    """A fixed-length sequence of elements.

    :param element: type of the content.
    :type element: :ref:`type expression<type-expressions>`
    :param size: fixed size.
    :type size: int
    """

    def __init__(self, element, size):
        """Refer to class."""
        self.element = element
        self.size = size

class VectorOf(Container):
    """A variable-length sequence of elements.

    :param element: type of the content.
    :type element: :ref:`type expression<type-expressions>`
    """

    def __init__(self, element):
        """Refer to class."""
        self.element = element

class SetOf(Container):
    """A collection of unique elements.

    :param element: type of the content, a hash-able value.
    :type element: :ref:`type expression<type-expressions>`
    """

    def __init__(self, element):
        """Refer to class."""
        self.element = element

class MapOf(Container):
    """A map of unique, key-value pairs.

    :param key: type of the key, a hash-able value.
    :type key: :ref:`type expression<type-expressions>`
    :param value: type of the content.
    :type value: :ref:`type expression<type-expressions>`
    """

    def __init__(self, key, value):
        """Refer to class."""
        self.key = key
        self.value = value

class DequeOf(Container):
    """A double-ended sequence of elements.

    :param element: type of the content.
    :type element: :ref:`type expression<type-expressions>`
    """

    def __init__(self, element):
        """Refer to class."""
        self.element = element

class UserDefined(Container):
    """A structure of named elements.

    :param element: registered class.
    :type element: class
    """

    def __init__(self, element):
        """Refer to class."""
        self.element = element

class PointerTo(Container):
    """An object that refers to another object.

    :param element: type of the object being pointed to.
    :type element: :ref:`type expression<type-expressions>`
    """

    def __init__(self, element):
        """Refer to class."""
        self.element = element

class Type(Portable):
    """The unique, portable identity of a registered message."""

class Word(Portable):
    """A well-formed but untyped unit of data."""

class Any(Portable):
    """The combination of a Type and a Word."""

    def __init__(self, *possibles):
        """Accept these types in a version-managed scenario."""
        self.possibles = possibles

class TargetAddress(Portable):
    """The address of a receiving object."""

class Address(Portable):
    """The address of a sending object."""

# List of the library types.
complete_list = [
    Boolean,
    Byte,
    Character,
    Rune,
    Integer2,
    Integer4,
    Integer8,
    Unsigned2,
    Unsigned4,
    Unsigned8,
    Float4,
    Float8,
    String,
    Unicode,
    Block,
    Enumeration,
    ClockTime,
    TimeSpan,
    WorldTime,
    TimeDelta,
    UUID,
    UserDefined,
    ArrayOf,
    VectorOf,
    SetOf,
    MapOf,
    DequeOf,
    PointerTo,
    Type,
    Word,
    Any,
    TargetAddress,
    Address,
]

# Set of the library types.
complete_set = set(complete_list)

# Few handy type predicates.
#

def is_portable(a):
    """Is object *a* an instance of one of the portable types."""
    return isinstance(a, Portable)

def is_container(a):
    """Is object *a* an instance of one of the portable container types."""
    return isinstance(a, Container)

def is_structural(a):
    """Is object *a* an instance of one of the portable container types and not a pointer."""
    b = isinstance(a, Container) and not isinstance(a, PointerTo)
    return b

def is_portable_class(c):
    """Is object *c* one of the portable types."""
    try:
        return issubclass(c, Portable)
    except TypeError:
        return False

def is_container_class(c):
    """Is object *c* one of the portable container types."""
    try:
        return issubclass(c, Container)
    except TypeError:
        return False

# This is the official null address and where required the
# default value for an address.
NO_SUCH_ADDRESS = [0]

def is_address(a):
    """Is object *a* is a valid point address."""
    try:
        return isinstance(a, tuple) and len(a) > 0
    except (TypeError, ValueError):
        return False

def address_on_proxy(a, p):
    """Check that address *a* refers to an object behind the proxy address, p."""
    if a[-1] == p[-1]:
        if len(p) == 1 and len(a) > 1:
            return True
    return False
