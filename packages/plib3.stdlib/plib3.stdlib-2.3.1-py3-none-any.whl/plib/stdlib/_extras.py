#!/usr/bin/env python3
"""
Module _EXTRAS -- Enhancing the builtin namespace
Sub-Package STDLIB of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""

from operator import mul as _mul
from functools import reduce
from collections import deque as _deque


class bbytes(bytes):
    """Sane replacement for built-in ``bytes`` type.
    
    Indexing returns an object of the same type, not int.
    
    >>> b = b'abc'
    >>> bb = bbytes(b)
    >>> b[0]
    97
    >>> type(b[0])
    <class 'int'>
    >>> bb[0]
    b'a'
    >>> type(bb[0])
    <class 'plib.stdlib._extras.bbytes'>
    """
    
    __slots__ = ()
    
    def __getitem__(self, index):
        i = bytes.__getitem__(self, index)
        return bbytes([i] if isinstance(index, int) else i)


class bbytearray(bytearray):
    """Sane replacement for built-in ``bytearray`` type.
    
    Indexing returns an object of the same type, not int.
    A single item can be set using a byte-like object as well as an int.
    
    >>> ba = bytearray(b'abc')
    >>> bba = bbytearray(ba)
    >>> ba[0]
    97
    >>> type(ba[0])
    <class 'int'>
    >>> bba[0]
    bbytearray(b'a')
    >>> type(bba[0])
    <class 'plib.stdlib._extras.bbytearray'>
    >>> ba[0] = b'b'
    Traceback (most recent call last):
    ...
    TypeError: 'bytes' object cannot be interpreted as an integer
    >>> bba[0] = b'b'
    >>> bba
    bbytearray(b'bbc')
    >>> bba[0] = 97
    >>> bba
    bbytearray(b'abc')
    >>> ba[:2] = b'ba'
    >>> ba
    bytearray(b'bac')
    >>> bba[:2] = b'ba'
    >>> bba
    bbytearray(b'bac')
    >>> ba[:2] = [97, 98]
    >>> ba
    bytearray(b'abc')
    >>> bba[:2] = [97, 98]
    >>> bba
    bbytearray(b'abc')
    """
    
    __slots__ = ()
    
    def __getitem__(self, index):
        i = bytearray.__getitem__(self, index)
        return bbytearray([i] if isinstance(index, int) else i)
    
    def __setitem__(self, index, value):
        if isinstance(index, int) and not isinstance(value, int):
            if not isinstance(value, (bytes, bytearray)):
                raise TypeError("'{}' object cannot be interpreted as byte".format((type(value).__name__)))
            if len(value) != 1:
                raise ValueError("Cannot assign {} bytes to single index".format(len(value)))
            value = value[0]
            if not isinstance(value, int):
                value = ord(value)
        bytearray.__setitem__(self, index, value)


def first(iterable, default=None):
    """Return first item in iterable, or default if empty.
    """
    for item in iterable:
        return item
    return default


def inverted(mapping, keylist=None):
    """Return a mapping that is the inverse of the given mapping.
    
    The optional argument ``keylist`` limits the keys that are inverted.
    """
    if keylist is not None:
        return mapping.__class__((mapping[key], key)
                                 for key in keylist)
    return mapping.__class__((value, key)
                             for key, value in mapping.items())


def last(iterable, default=None, deque=_deque):
    """Return last item in iterable, or default if empty.
    """
    q = deque(iterable, maxlen=1)  # consumes iterable at C speed
    return q[0] if q else default


def prod(iterable, mul=_mul):
    """Return the product of all items in iterable.
    """
    return reduce(mul, iterable, 1)


def type_from_name(name):
    """Return type object corresponding to ``name``.
    
    Currently searches only the built-in types. No checking is done to
    make sure the returned object is actually a type.
    """
    import builtins
    try:
        return getattr(builtins, name)
    except AttributeError:
        raise ValueError("no type corresponding to {}".format(name))
