# ansar-encode

The **ansar-encode** library provides for the convenient storage and recovery of
application data using system files. Files are created using standard encodings - the
default is JSON - and are human readable. Complex application data can be stored
including containers, instances of classes and object graphs.

## Features

- Broad suite of primitive types, e.g. integers, floats, strings, times and enumerations.
- Structured data, e.g. an 8-by-8 table of user-defined class instances.
- Recovered data is fully-typed, e.g. reading a ``class User`` produces a ``User`` instance.
- Graphs and graphs that include cycles, e.g. circular lists, syntax trees and state diagrams.
- Polymorphism, e.g. read an object of unknown type.
- Type-checking.
- Plain text files.
- Managed folders of files.
- Object versioning.
