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

"""Status and control settings bound to objects and messages.

The flags, enumerations and other values used to control handling
and behaviour and a class to hold this collection of administrative
details.

.. autoclass:: Runtime
"""

__docformat__ = 'restructuredtext'


__all__ = [
    'USER_LOG_NONE',

    'USER_LOG_FAULT',
    'USER_LOG_WARNING',
    'USER_LOG_CONSOLE',
    'USER_LOG_OBJECT',
    'USER_LOG_TRACE',
    'USER_LOG_DEBUG',

    'TAG_CREATED',
    'TAG_DESTROYED',
    'TAG_SENT',
    'TAG_RECEIVED',
    'TAG_STARTED',
    'TAG_ENDED',

    'TAG_FAULT',
    'TAG_WARNING',
    'TAG_CONSOLE',
    'TAG_TRACE',
    'TAG_DEBUG',
    'TAG_CHECK',

    'tag_to_number',

    'Runtime',
    'CodingProblem',
    'PlatformFailure',
]

# Logging levels. Moderate the quantity
# of logging by its designated significance.
USER_LOG_NONE = 100     # No user logs at all.

USER_LOG_FAULT = 6      # A definite problem that will compromise the service.
USER_LOG_WARNING = 5    # Something unexpected that may compromise the service.
USER_LOG_CONSOLE = 4    # An operational milestone worthy of note.
USER_LOG_OBJECT = 3     # Async operation.
USER_LOG_TRACE = 2      # Progress of the service. Suitable for public viewing.
USER_LOG_DEBUG = 1      # Not suitable for customer or support.

# Async operation.
TAG_CREATED   = '+'
TAG_DESTROYED = 'X'     # Provides completion type.
TAG_SENT      = '>'     # Type.
TAG_RECEIVED  = '<'     # ..
TAG_STARTED   = '('     # Sub-process running.
TAG_ENDED     = ')'     # Exited.

# Operational significance.
TAG_FAULT     = '!'     # Compromised.
TAG_WARNING   = '?'     # May be compromised.
TAG_CONSOLE   = '^'     # Application milestone.

TAG_TRACE     = '~'     # Technical, networks, files and devices.
TAG_DEBUG     = '_'     # Developer, raw.

TAG_CHECK     = '='		# Check a condition.

TAG_LEVEL = {
    TAG_FAULT: USER_LOG_FAULT,
    TAG_WARNING: USER_LOG_WARNING, TAG_CHECK: USER_LOG_WARNING,
    TAG_CONSOLE: USER_LOG_CONSOLE,
    TAG_CREATED: USER_LOG_OBJECT, TAG_DESTROYED: USER_LOG_OBJECT, TAG_SENT: USER_LOG_OBJECT, TAG_RECEIVED: USER_LOG_OBJECT,
    TAG_STARTED: USER_LOG_OBJECT, TAG_ENDED: USER_LOG_OBJECT,
    TAG_TRACE: USER_LOG_TRACE,
    TAG_DEBUG: USER_LOG_DEBUG
}

def tag_to_number(tag):
    """Convert tag to level. Return int."""
    number = TAG_LEVEL[tag]
    return number

class Runtime(object):
    """Settings to control logging and other behaviour, for objects and messages."""

    def __init__(self,
            name, module, value,
            version_history,
            lifecycle=True, message_trail=True,
            execution_trace=True,
            copy_before_sending=True,
            not_portable=False,
            user_logs=USER_LOG_DEBUG):
        """Construct the settings.

        :param name: the name of the class being registered
        :type name: str
        :param module: the name of the module the class is located in
        :type module: str
        :param value: the application value, e.g. a function
        :type value: any
        :param version_history: table of message changes
        :type version_history: list
        :param lifecycle: enable logging of created, destroyed
        :type lifecycle: bool
        :param message_trail: enable logging of sent
        :type message_trail: bool
        :param execution_trace: enable logging of received
        :type execution_trace: bool
        :param copy_before_sending: enable auto-copy before send
        :type copy_before_sending: bool
        :param not_portable: prevent inappropriate send
        :type not_portable: bool
        :param user_logs: log level
        :type user_logs: int
        """
        self.name = name        # Last component of dotted name.
        self.module = module    # Full path up to the name.
        self.value = value      # Value of this binding, e.g. pointer to a function
        self.version_history = version_history

        self.lifecycle = lifecycle              # Create, destroy objects
        self.message_trail = message_trail      # Sending
        self.execution_trace = execution_trace  # Receiving
        self.copy_before_sending = copy_before_sending
        self.not_portable = not_portable
        self.user_logs = user_logs              # Object trace, warning...

        self.path = '%s.%s' % (module, name)
        self.version_slice = {}

#
#
class CodingProblem(Exception):
    """Exception indicating poor construction of an async entity."""

    def __init__(self, identify_and_help):
        """Construct the exception.

        :param identity_and_help: description of the problem and a suggestion
        :type name: str
        """
        Exception.__init__(self, identify_and_help)

#
#
class PlatformFailure(Exception):
    """Exception indicating that the underlying platform is not meeting its end of the deal."""

    def __init__(self, identify_and_help):
        """Construct the exception.

        :param identity_and_help: the problem and a suggestion
        :type name: str
        """
        Exception.__init__(self, identify_and_help)
