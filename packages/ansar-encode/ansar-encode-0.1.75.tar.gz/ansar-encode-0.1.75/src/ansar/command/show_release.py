# Author: Scott Woods <scott.suzuki@gmail.com>
# MIT License
#
# Copyright (c) 2022 Scott Woods
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

"""Verification of changes to message versions.

A file is used to hold the version information associated with a collection
of released messages, i.e. messages converted to a portable form and sent
out into the world, as a file on disk or blocks on a network transport.

A module is passed that is loaded, causing the creation of the internal
message information - most importantly the table of types registered for
release. A fragment of code is executed to write the current image of
version information to a temporary file.

Version information is structured as below;

<table>
    <released-type>
        <reachable-type, version>
        <reachable-type, version>
        ..
    <released-type>
        <reachable-type, version>
        ..
    ..

Information saved in the file is compared to the latest information
extracted from the module. Differences are detected and depending on
command-line flags, printed on stdout.

There are 4 significant outcomes;

1. The file holding saved information does not exist. The current
information is used to create the named file. The process succeeds.
2. The 2 sets of information are equal. The process succeeds.
3. There are differences between the two sets that do not affect the
operation of the version machinery, e.g. released types are added
or removed. The file of saved information is updated and the
process succeeds.
4. There are differences between the two sets that affect the
operation of the version machinery, e.g. the set of reachable types for
a registered type has changed somehow while the version of the registered
type has not. The file of saved information is NOT updated and the
process fails.
"""
__docformat__ = 'restructuredtext'

__all__ = [
    'main',
]
import sys
import os
import ansar.encode as ar
import re

#
#
KEY_EQUALS_VALUE = '([a-zA-Z][-_a-zA-Z0-9]*)(=(.*))?'
LETTERS_ONLY = '[a-zA-Z0-9]+'

kev = re.compile(KEY_EQUALS_VALUE)
lo = re.compile(LETTERS_ONLY)

program_name = '<not-set>'

def release_args(argv):
    """Breakdown command-line arguments into name=value pairs, letter flags and words.

    :param argv: the arguments passed to a process
    :type path: list of string
    """
    global program_name
    program_name = argv[0]

    kv = {}
    flags = {}
    args = []
    for a in argv[1:]:
        if a.startswith('--'):
            t = a[2:]
            m = kev.match(t)
            if m:
                underscored = m.group(1).replace('-', '_')
                if m.group(2):
                    kv[underscored] = m.group(3)
                else:
                    kv[underscored] = 'true'
                continue
            raise ValueError('non-standard long-form argument "%s"' % (t,))
        elif a.startswith('-'):
            t = a[1:]
            m = lo.match(t)
            if m:
                for c in m.group():
                    flags[c] = len(args)
                continue
            raise ValueError('non-standard short-form argument "%s"' % (t,))
        else:
            args.append(a)
    # Return the separated bundles.
    return kv, flags, args

#
#
HELP_DOCUMENT = '''\
$ ansar-releasing <sub-command> <registration-module>? <saved-release>?

The sub-command is one of;

    status  extract current version information (<registration-module>) and display
    check   compare the current version information with a <saved-release>
    set     save the current version information into <saved-release>

The ansar-releasing command is used to check the latest version information within an
application. It does this by loading a special "registration-module" within the
application codebase and extracting all the pertinent details from the resulting
environment. From this point on, the command is in possession of the exact same
message type and version histories as the application.

This command should be a step in the release process for any application that is
using version management. The application codebase will include a module containing the
registrations of all pertinent message types. The application repo will hold a
file of the version information generated for the most recent release. A successful
execution of ansar-releasing indicates that it is okay to proceed with a software release.
Either there was no change to versioning or the changes were determined to be valid.
Valid changes are written to the file of saved version information. The file will need
to be updated in the repo (e.g. commit and push)

If the file of saved information does not exist, it is created using the current information.
This is a "bootstrap" operation to begin the tracking of changes to the application.
'''

def help():
    print(HELP_DOCUMENT)

# Printed information is split into 3 different streams, 1) NOTES that can be
# ignored, 2) WARNINGS that might escalate to faults, and 3) FAULTS where the
# application should not be released in its current state.
NOTES = 'n'
WARNINGS = 'w'
FAULTS = 'f'

show_notes = False
show_warnings = False
show_faults = False

notes = 0
warnings = 0
faults = 0

def main():
    """Compare the current version configuration with a recent, saved configuration."""
    argv = sys.argv
    kv, flags, args = release_args(argv)

    global show_notes, show_warnings, show_faults

    if len(args) < 1:
        help()
        return 1
    sub_command = args[0]
    args = args[1:]

    if 'a' in flags:
        show_notes = show_warnings = show_faults = True
    else:
        if NOTES in flags: show_notes = True
        if WARNINGS in flags: show_warnings = True
        if FAULTS in flags: show_faults = True

    if sub_command == 'status':
        a = len(args)
        if a == 1:
            current = load_module(args[0])
            if current is None:
                return 1
            for k, v in current.items():
                print('%s:' % (k,))
                for x, y in v.items():
                    print('\t%s/%s' % (x, y))
            return 0
    elif sub_command == 'check':
        a = len(args)
        if a == 2:
            current = load_module(args[0])
            if current is None:
                return 1
            release = load_release(args[1])
            if release is None:
                save_release(current, args[1])
                return 0
            check = check_release(current, release)
            if check is None:
                return 1
            return 0
    elif sub_command == 'set':
        a = len(args)
        if a == 2:
            current = load_module(args[0])
            if current is None:
                return 1
            save = save_release(current, args[1])
            if not save:
                return 1
            return 0
    else:
        print('unknown sub-command "%s"' % (sub_command,))
    help()
    return 1

def check_release(current, previous):
    # Checks and balances.
    for d, r in current.items():
        try:
            p = previous[d]
        except KeyError:
            detected(NOTES, d, None, 'added registration')
            continue

        changed = False
        for k, v in r.items():
            if k == d:              # Skip the document.
                continue
            try:
                x = p[k]
            except KeyError:
                # No longer reached
                detected(WARNINGS, d, k, 'reachable added')
                changed = True
                continue
            if x != v:
                # Different version on reachable type.
                detected(WARNINGS, d, k, 'changed reachable version (%s to %s)' % (x, v))
                changed = True

        a = r.keys()
        for t in p.keys():
            if t not in a:
                detected(WARNINGS, d, t, 'reachable removed')
                changed = True

        if changed and r[d] == p[d]:
            detected(FAULTS, d, None, 'reachables have changed while registration version has not')

    c = current.keys()
    for s in previous.keys():
        if s not in c:
            detected(NOTES, s, None, 'removed registration')

    if faults:
        return None

    return current

def save_release(release, name):
    with open(name, 'w', encoding='utf-8') as f:
        for k, v in release.items():
            s = ','.join(['%s/%s' % (x, y) for x, y in v.items()])
            f.write('%s:%s\n' % (k, s))
    return True

def load_release(name):
    release = {}
    try:
        with open(name, 'r', encoding='utf-8') as f:
            contents = f.read()
    except FileNotFoundError:
        return None

    lines = contents.splitlines()
    for ln in lines:
        doc = ln.split(':')
        d = doc[0]
        reachable = doc[1].split(',')
        for r in reachable:
            kv = r.split('/')
            try:
                a = release[d]
            except KeyError:
                a = {}
                release[d] = a
            a[kv[0]] = kv[1]
        if d not in release[d]:
            raise ValueError('document does not include itself')
    return release

def load_module(current_module):
    dir, base = os.path.split(current_module)
    root, ext = os.path.splitext(base)
    if root == '':
        no_name = '%s: argument "%s" cannot be used as a python module (no name)'
        print(no_name % (ar.program_name, current_module,))
        return None
    if ext != '.py':
        bad_ext = '%s: argument "%s" cannot be used as a python module (unexpected extension)'
        print(bad_ext % (ar.program_name, current_module,))
        return None
    relocated = None
    if dir:
        relocated = os.getcwd()
        os.chdir(dir)
    cwd = os.getcwd()
    header = 'import sys\nsys.path.insert(0,"%s")\nimport %s\nOUTPUT_FILE = "%s"\n%s\n'
    code = header % (cwd, root, OUTPUT_FILE, PRINT_TO_FILE)
    try:
        # Generate.
        exec(code)
    except ModuleNotFoundError as e:
        print('%s: cannot load registrations from "%s" (%s)' % (ar.program_name, current_module, str(e)))
        return None
    # Load.
    current = load_release(OUTPUT_FILE)
    os.remove(OUTPUT_FILE)
    if relocated:
        os.chdir(relocated)
    return current

#
#
OUTPUT_FILE = 'next-release.txt'
PRINT_TO_FILE = r'''
import ansar.encode.release as rl
with open(OUTPUT_FILE,'w',encoding = 'utf-8') as f:
    for k, v in rl.reachable.items():
        s = ','.join(['%s/%s' % (x.__art__.path, y) for x, y in v.items()])
        f.write('%s:%s\n' % (k.__art__.path, s))
'''

def detected(nwf, document, reachable, text):
    global notes, warnings, faults
    if nwf == NOTES:
        notes += 1
        if not show_notes:
            return
    elif nwf == WARNINGS:
        warnings += 1
        if not show_warnings:
            return
    elif nwf == FAULTS:
        faults += 1
        if not show_faults:
            return

    if reachable:
        print('%s (%s) --- %s' % (document, reachable, text))
    else:
        print('%s --- %s' % (document, text))

if __name__ == '__main__':
    sys.exit(main())
