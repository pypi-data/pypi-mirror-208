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

"""Registration of messages.

Bind additional information about a message to its class definition. This
includes more complete type information about its members but also settings
associated with how an instance of the message should be treated, e.g. during
logging.

.. autoclass:: Message
.. autoclass:: Unknown
.. autoclass:: Incognito

.. autofunction:: default_clock
.. autofunction:: default_span
.. autofunction:: default_world
.. autofunction:: default_delta
.. autofunction:: default_uuid
.. autofunction:: default_vector
.. autofunction:: default_set
.. autofunction:: default_map
.. autofunction:: default_deque

.. autofunction:: make
.. autofunction:: make_self

.. autofunction:: decode_type
.. autofunction:: encode_type
.. autofunction:: bind_message
"""

__docformat__ = 'restructuredtext'

import sys
import uuid
from datetime import MINYEAR, datetime, timedelta, timezone
from .portable import *
from .runtime import *

from copy import deepcopy

__all__ = [
    'MessageError',
    'MessageRegistrationError',

    'Message',
    'Unknown',
    'Incognito',

    'TypeTrack',
    'correct_track',

    'UTC',

    # No parameters.
    'default_clock',
    'default_span',
    'default_world',
    'default_delta',
    'default_uuid',
    'default_vector',
    'default_set',
    'default_map',
    'default_deque',

    # Require parameters.
    'make',
    'make_self',
    'fake',

    'is_message',
    'is_message_class',

    'fix_expression',
    'fix_schema',
    'compile_schema',
    'compile_history',

    'encode_type',
    'decode_type',

    'Added',
    'Moved',
    'Deleted',

    'major_minor',
    'bind_message',
    'change_history',
    'equal_to',

    'type_to_text',

    'INITIAL_VERSION',
    'INITIAL_SUPPORT',
    'SCENARIO_INAPPROPRIATE',
    'SCENARIO_UNSUPPORTED',
    'SCENARIO_BEHIND',
    'SCENARIO_AHEAD',
    'SCENARIO_SAME',
    'version_scenario',

    'get_history',
    'get_version',
    'get_slice',
    'effective_type',
    'type_version'
]

UTC = timezone.utc

# Exceptions
#
class MessageError(Exception):
    """Base exception for all message exceptions."""

class MessageRegistrationError(MessageError):
    """A request to register a class cannot be fulfilled.

    :param name: the name of the class being registered
    :type name: str
    :param reason: a short description
    :type reason: str
    """

    def __init__(self, name, reason):
        """Refer to class."""
        self.name = name
        self.reason = reason

    def __str__(self):
        """Compose a readable diagnostic."""
        if self.name:
            return 'cannot register "%s" (%s)' % (
                self.name, self.reason)
        return 'registration failure "%s"' % (self.reason,)

#
#
class Message(object):
    """Internal placeholder class used for dispatching."""

class Unknown(object):
    """An abstract class used to indicate an unexpected message."""

#
#

class Incognito(object):
    """A class that holds the recovered materials of an unregistered message.

    :param type_name: portable identity of the associated word
    :type type_name: str
    :param decoded_word: parsed but unmarshaled object
    :type decoded_word: word
    """

    def __init__(self, type_name=None, decoded_word=None, saved_pointers=None):
        """Refer to class."""
        self.type_name = type_name
        self.decoded_word = decoded_word
        self.saved_pointers = saved_pointers

# A group of functions that exist to allow type descriptions for
# messages to make use of *classes* rather than *instances* of those
# classes;
#     VectorOf(Float8)
# instead of;
#     VectorOf(Float8())
# Unclear on best design/engineering response to the issue but
# certainly this results in fewer parentheses and quicker development.
# Fully correct declaration of user-defined messages quite verbose
# and consequently less clear;
#     VectorOf(SomeMessage)
# vs;
#     VectorOf(UserDefined(SomeMessage))

def is_message(m):
    """Is *m* an instance of a registered class; return a bool."""
    try:
        c = m.__class__
    except AttributeError:
        return False
    b = hasattr(c, '__art__')
    return b

def is_message_class(c):
    """Has *c* been registered with the library; return a bool."""
    try:
        p = c.__class__     # Parent class.
    except AttributeError:
        return hasattr(c, '__art__')
    b = not hasattr(p, '__art__') and hasattr(c, '__art__')
    return b

# Holds nested names that would be helpful in the event
# of an error.
class TypeTrack(Exception):
    """Construct a readable name for a message.member.member, during exceptions."""

    def __init__(self, name, reason):
        """Keep building the trace."""
        Exception.__init__(self)
        if name:
            self.path = [name]
        else:
            self.path = []
        self.reason = reason

def correct_track(e):
    """Generate a readable version of a TypeTrack exception."""
    t = '.'.join(reversed(e.path))
    return t

# Default initializers (i.e. no parameters available) for tricky
# types. Want an instance of the type but preferrably without
# side-effects and at the least cost. Most containers need
# a fresh instance of themselves (i.e. list,
# deque...) but other types are objects that are immutable,
# such as bytes and datetime. These can be initialized with a
# single constant value to reduce the cycles consumed by
# initialization. This whole issue is further complicated by
# the merging of the two type systems - ansar and python - and
# how String does not map to str.

# Immutable initializer constants.
DEFAULT_STRING = bytes()
DEFAULT_UNICODE = str()
DEFAULT_CLOCK = float(0)
DEFAULT_SPAN = float(0)
DEFAULT_WORLD = datetime(MINYEAR, 1, 1)
DEFAULT_DELTA = timedelta()
DEFAULT_ZONE = UTC
DEFAULT_UUID = uuid.uuid4()

def default_byte():
    """Initialize the smallest, integer value, i.e. ``Byte``.

    :return: byte
    :rtype: int
    """
    return int()

def default_character():
    """Initialize a single, printable character, i.e. ``Character``.

    :return: character
    :rtype: bytes
    """
    return b' '

def default_rune():
    """Initialize a single Unicode codepoint, i.e. ``Unicode``.

    :return: codepoint
    :rtype: str
    """
    return ' '

def default_block():
    """Initialize a sequence of the smallest integers, i.e. ``Block``.

    :return: fresh instance of an empty block
    :rtype: bytearray
    """
    return bytearray()  # New object every time.

def default_string():
    """Initialize a sequence of printable characters, i.e. ``String``.

    :return: an empty sequence of characters
    :rtype: bytes
    """
    return DEFAULT_STRING

def default_unicode():
    """Initialize a sequence of Unicode codepoints, i.e. ``Unicode``.

    :return: empty sequence of codepoints
    :rtype: str
    """
    return DEFAULT_UNICODE

def default_clock():
    """Initialize a local time variable, i.e. ``ClockTime``.

    :return: the beginning of time
    :rtype: datetime
    """
    return DEFAULT_CLOCK

def default_span():
    """Initialize a local time difference variable, i.e. ``TimeSpan``.

    :return: no time
    :rtype: timedelta
    """
    return DEFAULT_SPAN

def default_world():
    """Initialize a date-and-time variable, i.e. ``WorldTime``.

    :return: the beginning of time
    :rtype: datetime
    """
    return DEFAULT_WORLD

def default_delta():
    """Initialize a date-and-time delta variable, i.e. ``TimeDelta``.

    :return: no time
    :rtype: timedelta
    """
    return DEFAULT_DELTA

def default_uuid():
    """Initialize a UUID variable.

    :return: a global, constant UUID value
    :rtype: uuid.UUID
    """
    return DEFAULT_UUID

def default_vector():
    """Initialize a vector variable.

    :return: a fresh, empty vector
    :rtype: list
    """
    return list()   # New object.

def default_set():
    """Initialize a set variable.

    :return: a fresh, empty set
    :rtype: set
    """
    return set()

def default_map():
    """Initialize a map variable.

    :return: a fresh, empty map
    :rtype: dict
    """
    return dict()

def default_deque():
    """Initialize a deque variable.

    :return: a fresh, empty double-ended queue
    :rtype: collections.deque
    """
    return deque()

# A group of functions that convert type expressions into
# a useful default, then perhaps assign it somewhere.
def make(e):
    """Initialize any variable using a type expression.

    :param te: see :ref:`type expression<type-expressions>`
    :return: an item of application data
    """
    f = fix_expression(e, dict())
    v = from_type(f)
    return v

def make_self(a, schema):
    """Initialize all the members of an object that are not present or set to None, to a useful default."""
    for k, t in schema.items():
        v = getattr(a, k)
        if v is None:
            v = from_type(t)
            setattr(a, k, v)

#
#
def fake(e):
    """Fake an instance of any variable starting from a type expression.

    :param e: see :ref:`type expression<type-expressions>`
    :return: an item of application data
    """
    v = fake_type(e)
    return v


# Allow the use of basic python types
# in type expressions.
equivalent = {
    bool: Boolean(),
    int: Integer8(),
    float: Float8(),
    datetime: WorldTime(),
    timedelta: TimeDelta(),
    bytearray: Block(),
    bytes: String(),
    str: Unicode(),
    uuid.UUID: UUID(),
}

def fix_expression(a, bread):
    """Promote parameter a from class to instance, as required."""
    if is_portable(a):
        if not is_container(a):
            return a    # No change.
        # Fall thru for structured processing.
    elif is_portable_class(a):
        if not is_container_class(a):
            return a()  # Promotion of simple type.
        raise TypeTrack(a.__name__, 'container class used in type information, instance required')
    elif is_message_class(a):
        return UserDefined(a)
    else:
        # Is it one of the mapped Python classes.
        try:
            e = equivalent[a]
            return e
        except KeyError:
            pass
        except TypeError:   # Unhashable - list.
            pass
        # Is it an instance of a mapped Python class.
        try:
            e = equivalent[a.__class__]
            return e
        except KeyError:
            pass
        except AttributeError:   # No class.
            pass
        raise TypeTrack(None, 'not one of the portable types')

    # We have an instance of a structuring.
    try:
        name = a.__class__.__name__
        if isinstance(a, ArrayOf):
            a.element = fix_expression(a.element, bread)
        elif isinstance(a, VectorOf):
            a.element = fix_expression(a.element, bread)
        elif isinstance(a, SetOf):
            a.element = fix_expression(a.element, bread)
        elif isinstance(a, MapOf):
            a.key = fix_expression(a.key, bread)
            a.value = fix_expression(a.value, bread)
        elif isinstance(a, DequeOf):
            a.element = fix_expression(a.element, bread)
        elif isinstance(a, UserDefined):
            if not is_message_class(a.element):
                raise TypeTrack(None, '"%s" is not a user-defined message' % (name,))
        elif isinstance(a, PointerTo):
            try:
                e = bread[id(a)]
            except KeyError:
                e = fix_expression(a.element, bread)
                bread[id(a)] = e
            a.element = e
        else:
            raise TypeTrack(None, 'unexpected container type')
    except TypeTrack as e:
        e.path.append(name)
        raise e
    return a

def fix_schema(name, schema):
    """Promote schema items from class to instance, as required.

    :param name: name of the message
    :type name: str
    :param schema: the current schema
    :type name: a map of <name, portable declaration> pairs
    :return: the modified schema
    """
    if schema is None:
        return
    d = {}
    for k, t in schema.items():
        try:
            d[k] = fix_expression(t, dict())
        except TypeTrack as e:
            track = correct_track(e)
            raise MessageRegistrationError('%s.%s (%s)' % (name, k, track), e.reason)
    schema.update(d)

def override(name, explicit):
    """Is there explicit information for the named item.

    :param name: name of the message
    :type name: str
    :param explicit: a supplied schema
    :type explicit: a map of <name, portable declaration> pairs
    :return: the explicit information or None
    """
    if not explicit:
        return None

    try:
        t = explicit[name]
        return t
    except KeyError:
        return None

def compile_schema(message, explicit_declarations):
    """Produce the best-possible type information for the specified message.

    Use the class and the application-supplied declarations. The
    declarations override any default info that might otherwise be
    acquired from the message.
    """
    name = message.__name__

    fix_schema(name, explicit_declarations)
    try:
        m = message()
    except TypeError:
        raise MessageRegistrationError('%s' % (name,), 'not default constructable')
    d = getattr(m, '__dict__', None)
    r = {}
    if d:
        for k, a in d.items():
            explicit = override(k, explicit_declarations)
            if explicit:
                t = explicit
            else:
                t = infer_type(a)

            if not t:
                name_k = "%s.%s" % (name, k)
                reason = 'not enough type information provided/discoverable'
                raise MessageRegistrationError(name_k, reason)
            r[k] = t
    return r

def compile_history(vh, schema, message_name):
    """Produce the per-version set of member names for a message.

    Use the class dict and the application-supplied history to.
    """
    if vh is None:
        return None

    #
    #
    keys = set(schema.keys())

    added = set()
    added_at = {}
    deleted = set()
    deleted_so_far = {}

    for v, h, _ in vh:
        # Sum the changes on this line of
        # the history.
        if not isinstance(h, (tuple, list)):
            h = (h,)
        a = set()
        d = set()
        for x in h:
            if isinstance(x, Added):
                a.add(x.name)
            elif isinstance(x, Moved):
                if x.previous == x.latest:
                    s = 'moving "%s" to the same name'
                    raise CodingProblem(s % (message_name,))
                d.add(x.previous)
                a.add(x.latest)
            elif isinstance(x, Deleted):
                d.add(x.name)
            else:
                continue

        # Check intended changes against the current
        # situation.
        t = a & keys
        if len(t) < len(a):
            j = ','.join(a)
            s = 'addition(s) to "%s" (%s) at version "%s" not reflected in schema' % (message_name, j, v)
            raise CodingProblem(s)

        t = d & keys
        if len(t) < len(d):
            j = ','.join(d)
            s = 'deletion(s) from "%s" (%s) at version "%s" still expected in schema' % (message_name, j, v)
            raise CodingProblem(s)

        t = a & added
        if len(t) > 0:
            j = ','.join(t)
            s = 'duplicate add to "%s" (%s) at version "%s"' % (message_name, j, v)
            raise CodingProblem(s)

        t = a & deleted
        if len(t) > 0:
            j = ','.join(t)
            s = 'cannot delete-add to "%s" (%s) at version "%s"' % (message_name, j, v)
            raise CodingProblem(s)

        t = d & deleted
        if len(t) > 0:
            j = ','.join(t)
            s = 'duplicate delete from "%s" (%s) at version "%s"' % (message_name, j, v)
            raise CodingProblem(s)

        t = a & d
        if len(t) > 0:
            j = ','.join(t)
            s = 'strange add-delete to "%s" (%s) at version "%s"' % (message_name, j, v)
            raise CodingProblem(s)

        # Apply the changes and loop
        # for the next.
        added_at[v] = a
        added.update(a)

        deleted.update(d)
        deleted_so_far[v] = deleted.copy()

    # Roll through the history backwards to collect
    # those names that should be deleted from slices
    # before those names were added.
    added = set()
    added_after = {}
    for v, d, _ in reversed(vh):
        added_after[v] = added.copy()
        added.update(added_at[v])

    # Create a slice for every version. Start with a full
    # set from the schema and make appropriate removal at
    # each version.
    slice = {h[0]: keys.copy() for h in vh}

    for v, h, _ in vh:
        a = added_after[v]
        d = deleted_so_far[v]
        slice[v] -= a           # Remove names yet to be added.
        slice[v] -= d           # Remove names deleted here or before.

    return slice

def infer_type(a):
    """Map an instance of a Python type to the proper memory description, or None."""
    try:
        t = equivalent[a.__class__]
        return t
    except AttributeError:
        return None     # No class.
    except KeyError:
        pass
    if is_message(a):
        return UserDefined(a.__class__)
    return None

# A mapping from ansar to a constructor where
# no parameter is needed.
def default_none():
    return None

from_class = {
    Boolean: default_none,
    Byte: default_none,
    Character: default_none,
    Rune: default_none,
    Integer2: default_none,
    Integer4: default_none,
    Integer8: default_none,
    Unsigned2: default_none,
    Unsigned4: default_none,
    Unsigned8: default_none,
    Float4: default_none,
    Float8: default_none,
    Block: default_none,
    String: default_none,
    Unicode: default_none,
    Enumeration: default_none,
    ClockTime: default_none,
    TimeSpan: default_none,
    WorldTime: default_none,
    TimeDelta: default_none,
    UUID: default_none,
    Type: default_none,
    TargetAddress: default_none,
    Address: default_none,
    PointerTo: default_none,
    Any: default_none,
    VectorOf: default_vector,
    SetOf: default_set,
    MapOf: default_map,
    DequeOf: default_deque,
    # Need parameters;
    # ArrayOf
    # UserDefined
}

#
#
def from_type(t):
    """Manufactures the Python equivalent of the memory description, or None."""
    if not is_portable(t):
        raise MessageRegistrationError(None, 'non-memory type presented for construction - %r' % (t,))

    try:
        c = from_class[t.__class__]
        return c()
    except KeyError:
        pass
    except AttributeError:
        raise MessageRegistrationError(None, 'internal failure to create from class')

    # Following types are more involved - cant be
    # ctor'd solely from the class.
    if isinstance(t, ArrayOf):
        d = [None] * t.size
        for i in range(t.size):
            d[i] = from_type(t.element)
        return d

    if isinstance(t, UserDefined):
        return t.element()

    raise MessageRegistrationError(None, 'internal failure to create from memory')

#
#
def character_bytes(): return b'c'
def rune_str(): return 'C'
def block_bytearray(): return bytearray([0x0c, 0x0a, 0x0f, 0x0e])
def string_bytes(): return b'CAFE'
def unicode_str(): return 'CAFE'

def fake_clock(): return datetime(1963, 3, 26).timestamp()
def fake_span(): return 0.5
def fake_world(): return datetime(1963, 3, 26)
def fake_delta(): return timedelta(seconds=0.5)
def fake_uuid(): return uuid.uuid4()
def fake_type_(): return Unknown
def fake_target(): return [0x0c, 0x0a, 0x0f, 0x0e]
def fake_address(): return [0x0c, 0x0a, 0x0f, 0x0e]
def fake_any(): return Unknown()

fake_class = {
    Boolean: bool,
    Byte: int,
    Character: character_bytes,
    Rune: rune_str,
    Integer2: int,
    Integer4: int,
    Integer8: int,
    Unsigned2: int,
    Unsigned4: int,
    Unsigned8: int,
    Float4: float,
    Float8: float,
    Block: block_bytearray,
    String: string_bytes,
    Unicode: unicode_str,
    Enumeration: lambda: "MOTORCYCLE",
    ClockTime: fake_clock,
    TimeSpan: fake_span,
    WorldTime: fake_world,
    TimeDelta: fake_delta,
    UUID: fake_uuid,
    Type: fake_type_,
    TargetAddress: fake_target,
    Address: fake_address,
    Any: fake_any,
}

def fake_type(t):
    """Synthesizes an example of the Python equivalent, or None."""
    if not is_portable(t):
        raise MessageRegistrationError(None, 'non-memory type presented for construction - %r' % (t,))

    try:
        c = fake_class[t.__class__]
        return c()
    except KeyError:
        pass
    except AttributeError:
        raise MessageRegistrationError(None, 'internal failure to create from class')

    # Following types are more involved - cant be
    # ctor'd solely from the class.
    if isinstance(t, VectorOf):
        e = fake_type(t.element)
        d = [e]
        return d
    elif isinstance(t, ArrayOf):
        d = [None] * t.size
        for i in range(t.size):
            d[i] = fake_type(t.element)
        return d
    elif isinstance(t, DequeOf):
        e = fake_type(t.element)
        d = deque()
        d.append(e)
        return d
    elif isinstance(t, SetOf):
        e = fake_type(t.element)
        d = set()
        d.add(e)
        return d
    elif isinstance(t, MapOf):
        k = fake_type(t.key)
        v = fake_type(t.value)
        d = {}
        d[k] = v
        return d
    elif isinstance(t, UserDefined):
        element = t.element
        schema = element.__art__.value
        d = element()
        for k, v in schema.items():
            setattr(d, k, fake_type(v))
        return d
    elif isinstance(t, PointerTo):
        return fake_type(t.element)

    raise MessageRegistrationError(None, 'internal failure to create from memory')

#
#
def decode_type(s):
    """Convert the dotted string *s* to a class, or None."""
    try:
        i = s.rindex('.')
    except ValueError:
        return None
    module = s[:i]
    name = s[i + 1:]
    try:
        m = sys.modules[module]
    except KeyError:
        return None

    try:
        c = m.__dict__[name]
    except KeyError:
        return None
    return c

def encode_type(c):
    """Convert the class *c* to a dotted string representation."""
    b = c.__art__     # Ansar runtime.
    e = '%s.%s' % (b.module, b.name)
    return e

# Objects to express and hold message deltas.
class Added(object):
    """Perfom an addition within the history of a class."""

    def __init__(self, name):
        """Add *name* to the set of expected members."""
        self.name = name

class Moved(object):
    """Perfom a rename within the history of a class."""

    def __init__(self, previous, latest):
        """Remove *previous* and replace with "latest" in the set of expected members."""
        self.previous = previous
        self.latest = latest

class Deleted(object):
    """Perfom a deletion within the history of a class."""

    def __init__(self, name):
        """Remove *name* from the set of expected members."""
        self.name = name

#
#
INITIAL_VERSION = "0.0"
INITIAL_SUPPORT = [INITIAL_VERSION, INITIAL_VERSION]

SCENARIO_INAPPROPRIATE = 0
SCENARIO_UNSUPPORTED = 1
SCENARIO_BEHIND = 2
SCENARIO_AHEAD = 3
SCENARIO_SAME = 4

def major_minor(tag):
    """Split the composite string into 2 parts and return major and minor integers."""
    s = tag.split('.')
    try:
        m = int(s[0])
        n = int(s[1])
    except IndexError:
        raise MessageError('cannot access major/minor numbers in %r' % (tag,))
    except ValueError:
        raise MessageError('cannot use major/minor in %r' % (tag,))
    except TypeError:
        raise MessageError('non-integer version tag %r' % (tag,))

    try:
        r = int(s[2])
    except IndexError:
        return [m, n, 0]
    except ValueError:
        raise MessageError('cannot use major/minor in %r' % (tag,))
    except TypeError:
        raise MessageError('non-integer version tag %r' % (tag,))

    return [m, n, r]

def version_scenario(remote, local):
    """Resolve the proper understanding of loading the remote data, return an enum."""
    # If either is unmanaged, allow anything that
    # passed rules to go through.
    if remote is None:
        if local is None:
            # Both unversioned. Pass through.
            return None, SCENARIO_SAME
        # Local is expecting version info.
        # Allow through with unique tag.
        return '', SCENARIO_SAME
    elif local is None:
        # Not expecting version info.
        # Allow through.
        return None, SCENARIO_SAME

    # Access the major+minor arrays.
    remote_current = major_minor(remote)
    local_support = major_minor(local[0])
    local_current = major_minor(local[1])

    if remote_current[0] != local_current[0]:
        return None, SCENARIO_INAPPROPRIATE

    # Drop down to consider the minor and reachable numbers.
    # Fake a single number to make calculations easier.
    remote_current = remote_current[1] * 10000 + remote_current[2]
    local_support = local_support[1] * 10000 + local_support[2]
    local_current = local_current[1] * 10000 + local_current[2]

    if remote_current < local_current:
        if remote_current < local_support:
            return None, SCENARIO_UNSUPPORTED   # Too far behind.
        return remote, SCENARIO_BEHIND
    elif remote_current > local_current:
        return None, SCENARIO_AHEAD
    return None, SCENARIO_SAME

def get_history(c):
    """Return the range of versions as an oldest-latest tuple, or none."""
    try:
        rt = c.__art__
    except AttributeError:
        return None
    vh = rt.version_history
    if vh is None:
        return None
    b = vh[0][0]
    e = vh[-1][0]
    return [b, e]

def get_version(c):
    """Return the current version tag for the specified class or none."""
    try:
        rt = c.__art__
    except AttributeError:
        return None
    vh = rt.version_history
    if vh is None:
        return None
    e = vh[-1][0]
    return e

def get_slice(c):
    """Return the map of versioning name slices."""
    try:
        rt = c.__art__
    except AttributeError:
        return None
    return rt.version_slice

def effective_type(t, bread):
    """Determine the main type, e.g. portable, UDT or content of a container."""
    if isinstance(t, UserDefined):
        return t.element
    elif isinstance(t, (VectorOf, ArrayOf, DequeOf, SetOf)):
        return effective_type(t.element, bread)
    elif isinstance(t, MapOf):
        return effective_type(t.value, bread)
    elif isinstance(t, PointerTo):
        k = id(t)
        try:
            b = bread[k]
        except KeyError:
            b = effective_type(t.element, bread)
            bread[k] = b
        return b

    return None

def type_version(t):
    """Determine the current version of the specified type."""
    if not isinstance(t, UserDefined):
        return None
    t = t.element
    try:
        h = t.__art__.version_history
    except AttributeError:
        return None
    if h is None:
        return None
    b = h[0][0]
    e = h[-1][0]
    noop = b == INITIAL_VERSION and e == INITIAL_VERSION
    if noop:
        return None
    return e

#
#
def bind_message(message, object_schema=None, version_history=None,
        message_trail=True, execution_trace=True,
        copy_before_sending=True, not_portable=False):
    """Set the type information and runtime controls for the given message type.

    :param message: a message class.
    :type message: class
    :param object_schema: application-supplied type information.
    :type object_schema: a map of <name,portable declaration> pairs.
    :param message_trail: log every time this message is sent.
    :type message_trail: bool
    :param version_history: a version table.
    :type version_history: a list of version changes.
    :param execution_trace: log every time this message is received.
    :type execution_trace: bool
    :param copy_before_sending: make a copy of the message before each send.
    :type copy_before_sending: bool
    :param not_portable: prevent serialization/transfer, e.g. of a file handle.
    :type not_portable: bool
    :return: nothing.

    Values assigned in this function affect the behaviour for all instances of
    the given type.
    """
    rt = Runtime(message.__name__, message.__module__, None,
        version_history,
        message_trail=message_trail,
        execution_trace=execution_trace,
        copy_before_sending=copy_before_sending,
        not_portable=not_portable)

    setattr(message, '__art__', rt)
    if not not_portable:
        rt.value = compile_schema(message, object_schema)
        if rt.value:
            rt.version_slice = compile_history(rt.version_history, rt.value, rt.name)

    # TODO
    # Crude check for whether the new type is
    # properly registered - can an instance
    # be created from its portable type id.
    if not decode_type(rt.path):
        raise MessageRegistrationError(message.__name__, 'not a global level class?')

def change_history(message, history):
    """Explicit and safe assignment of version history."""
    try:
        rt = message.__art__
    except AttributeError:
        return None
    previous = rt.version_history
    rt.version_history = history
    if history and rt.value:
        rt.version_slice = compile_history(history, rt.value, rt.name)
    else:
        rt.version_slice = None
    return previous

bind_message(Unknown)

# This should not need be needed as they are never on-the-wire.
# But registration needed for dispatching within encode/decode
# process.
bind_message(Incognito, object_schema={
    'type_name': String,
    'decoded_word': Word,
    'saved_pointers': MapOf(String, Word),
})

def equal_to(a, b, t=None):
    """Compare the two operands as instances of portable memory."""
    if t is None:
        if not is_message(b):
            return a == b
        if not isinstance(a, b.__class__):
            return False
        t = UserDefined(b.__class__)

    if isinstance(t, ArrayOf):
        if len(a) != len(b):
            return False
        return all(equal_to(i, j, t.element) for i, j in zip(a, b))
    elif isinstance(t, VectorOf):
        if len(a) != len(b):
            return False
        return all(equal_to(i, j, t.element) for i, j in zip(a, b))
    elif isinstance(t, DequeOf):
        if len(a) != len(b):
            return False
        return all(equal_to(i, j, t.element) for i, j in zip(a, b))
    elif isinstance(t, SetOf):
        # if len(a) != len(b):
        #    return False
        # return all(i in a for i in b)
        return a == b
    elif isinstance(t, MapOf):
        if len(a) != len(b):
            return False
        return all(k in b and equal_to(a[k], v, t.value) for k, v in b.items())
    elif isinstance(t, UserDefined):
        x = t.element.__art__
        for k, v in x.value.items():
            try:
                lhs = getattr(a, k)
                rhs = getattr(b, k)
            except AttributeError:
                return False
            if not equal_to(lhs, rhs, v):
                return False
        return True
    elif isinstance(t, PointerTo):
        # Difficult issue. Have to consider circular
        # references and graphs, i.e. infinite loops.
        # Its also true that its intended for comparision
        # of messages and 2 messages should never, ever
        # refer to common data.
        return False
    elif isinstance(t, Any):
        if equal_to(a, b):
            return True
        return False
    else:
        return a == b

#
#
NON_CONTAINER = {t: '%s()' % (t.__name__,) for t in complete_list if not is_container_class(t)}

def type_to_text(t, bread={}):
    """."""
    try:
        s = NON_CONTAINER[type(t)]
        return s
    except KeyError:
        pass

    if isinstance(t, UserDefined):
        return 'UserDefined({element})'.format(element=t.element.__art__.path)
    elif isinstance(t, (VectorOf, ArrayOf, DequeOf, SetOf)):
        container = t.__class__.__name__
        element = type_to_text(t.element, bread)
        return '{container}({element})'.format(container=container, element=element)
    elif isinstance(t, MapOf):
        key = type_to_text(t.key, bread)
        value = type_to_text(t.value, bread)
        return 'MapOf({key},{value})'.format(key=key, value=value)
    elif isinstance(t, PointerTo):
        k = id(t)
        try:
            e = bread[k]
        except KeyError:
            e = type_to_text(t.element, bread)
            bread[k] = e
        return 'PointerTo({element})'.format(element=e)
    return None
