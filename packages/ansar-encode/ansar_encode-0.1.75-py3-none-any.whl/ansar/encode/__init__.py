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

"""Persistence of complex application data.

Repo: git@github.com:mr-ansar/ansar-encode.git
Branch: main
Commit: 07d41b16fec830c88b0ff5f8fee6a80e17bde747
Version: 0.1.74 (2023-05-15@14:16:40+NZST)
"""

from .portable import Boolean
from .portable import Byte, Character, Rune
from .portable import Integer2, Integer4, Integer8
from .portable import Unsigned2, Unsigned4, Unsigned8
from .portable import Float4, Float8
from .portable import Block, String, Unicode
from .portable import Enumeration
from .portable import ClockTime, TimeSpan
from .portable import WorldTime, TimeDelta
from .portable import UUID
from .portable import ArrayOf, VectorOf, SetOf, MapOf, DequeOf
from .portable import UserDefined
from .portable import Type
from .portable import PointerTo
from .portable import TargetAddress, Address
from .portable import Word, Any
from .portable import complete_list, complete_set
from .portable import is_portable, is_container, is_structural, is_portable_class, is_container_class
from .portable import NO_SUCH_ADDRESS
from .portable import is_address, address_on_proxy
from .portable import deque

from .runtime import USER_LOG_FAULT, USER_LOG_WARNING, USER_LOG_CONSOLE, USER_LOG_OBJECT, USER_LOG_TRACE, USER_LOG_DEBUG, USER_LOG_NONE
from .runtime import TAG_CREATED, TAG_DESTROYED, TAG_SENT, TAG_RECEIVED, TAG_STARTED, TAG_ENDED
from .runtime import TAG_FAULT, TAG_WARNING, TAG_CONSOLE, TAG_TRACE, TAG_DEBUG, TAG_CHECK
from .runtime import tag_to_number
from .runtime import Runtime
from .runtime import CodingProblem, PlatformFailure

from .message import MessageError, MessageRegistrationError
from .message import Message, is_message, is_message_class
from .message import Unknown, Incognito
from .message import TypeTrack, correct_track
from .message import default_clock, default_span
from .message import default_world, default_delta, default_uuid
from .message import default_vector, default_set, default_map, default_deque
from .message import make, make_self, fake
from .message import fix_expression, fix_schema, compile_schema, compile_history
from .message import encode_type, decode_type
from .message import Added, Moved, Deleted
from .message import major_minor, bind_message, change_history, equal_to
from .message import type_to_text
from .message import INITIAL_VERSION, INITIAL_SUPPORT
from .message import SCENARIO_INAPPROPRIATE, SCENARIO_UNSUPPORTED, SCENARIO_BEHIND, SCENARIO_AHEAD, SCENARIO_SAME
from .message import version_scenario
from .message import get_history, get_version, get_slice
from .message import effective_type, type_version

from .release import released_document

from .convert import ConversionError, ConversionEncodeFailed, ConversionDecodeFailed

from .convert import clock_to_text, text_to_clock, span_break, span_to_text, text_to_span
from .convert import world_to_text, text_to_world, delta_to_text, text_to_delta
from .convert import uuid_to_text, text_to_uuid
from .convert import UTC
from .convert import clock_now, clock_at, clock_break, clock_span
from .convert import world_now, world_at, world_break, world_delta

from .codec import TypeType, NoneType
from .codec import CodecError, CodecUsage, CodecFailed, EnumerationFailed
from .codec import python_to_word, word_to_python
from .codec import Codec

from .json import word_to_json, json_to_word, CodecJson
from .xml import word_to_xml, xml_to_word, CodecXml

from .file import FileFailure, FileNotFound, FileNoAccess, FileNotAFile, FileIoFailed, FileEncoding
from .file import File
from .file import read_from_file, write_to_file

from .folder import Folder, remove_contents, remove_folder, shape_of_folder

from .version import migrate, cannot_upgrade

# Provide default registration function at the
# level of this library
bind = bind_message
