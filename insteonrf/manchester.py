#!/usr/bin/env python
from myexceptions import InvalidManchesterEncoding
"""
See also : http://ckp.made-it.com/encodingschemes.html

Biphase mark coding / Bi-Phase Mark / Bi-Phase-M
Differential Manchester/Bi-Phase Level (Split Phase)/Differential Bi-Phase Mark
Manchester / Bi-Phase Level (Split Phase) / Bi-Phase-L

"""

__author__ = "Peter Shipley"


def set_bit_order(invert=False):
    if invert:
        return ("1", "0")
    return ("0", "1")


def nrz_encode(data, invert=False):
    """
    NRZ-S
    Non-Return-to-Zero Space
    "One" is represented by no change in level
    "Zero" is represented by change in level.
    """

    ret_array = []
    zero, one = set_bit_order(invert=False)

    x = data[0]
    data = data[1:]
    if x == one and not invert:
        ret_array.append("0")
        prev = zero
    else:
        ret_array.append("1")
        prev = one

    for x in data:
        if x == one:
            ret_array.append(prev)
        elif x == zero:
            if prev == one:
                ret_array.append("0")
                prev = zero
            else:
                ret_array.append("1")
                prev = one

    return ''.join(ret_array)


def bpm_decode(data, invert=False):
    """
    Bi-Phase Mark / Bi-Phase-M
    Level change occurs at the beginning of every bit period
    "One" is represented by a midbit level change
    "Zero" is represented by no midbit level change

    ( inverted = Bi-Phase Space / Bi-Phase-S )
    """
    i = 1
    b = list()
    slen = len(data)
    zero, one = set_bit_order(invert=False)

    # Note that since 1 starts as "1"
    # we are testing the 2nd bit for '1' or '0'
    while(i < slen):
        if data[i] != data[i-1]:
            b.append(one)
        else:
            b.append(zero)
        i = i + 2
    return "".join(b)


def bpm_encode(data, invert=False):
    """
    Bi-Phase Mark / Bi-Phase-M
    Level change occurs at the beginning of every bit period
    "One" is represented by a midbit level change
    "Zero" is represented by no midbit level change

    ( inverted = Bi-Phase Space / Bi-Phase-S )
    """

    ret_array = []
    zero, one = set_bit_order(invert=invert)
    prev = one

    for x in data:
        if x == zero:
            if prev == zero:
                ret_array.append("11")
                prev = one
            else:
                ret_array.append("00")
                prev = zero
        elif x == one:
            if prev == one:
                ret_array.append("01")
                prev = one
            else:
                ret_array.append("10")
                prev = zero

    return ''.join(ret_array)


# BROKEN
def diff_manchester_decode(data, invert=False):
    i = 1
    b = list()
    slen = len(data)
    zero, one = set_bit_order(invert=False)
    prev = zero

    i = 0
    # Note that since 1 starts as "1"
    # we are testing the 2nd bit for '1' or '0'
    while(i < slen):
        if data[i] == data[i+1]:
            print i, ":", data
            print data[:i], data[i:]
            print i, ":", data
            raise ValueError("B Invalid Diff_Manchester Encoding")
        elif data[i] == prev:
            b.append(one)
        else:
            b.append(zero)

        if prev == one:
            prev = zero
        else:
            prev = one
        i = i + 2

    return "".join(b)


def diff_manchester_encode(data, invert=False):
    """
    Differential Manchester
    Bi-Phase Level (Split Phase) / Differential Bi-Phase Mark
    Level change occurs at the center of every bit period
    "One" is represented by no level change at the beginning of the bit period
    "Zero" is represented by a level change at the beginning of the bit period.
    """
    zero, one = set_bit_order(invert=invert)
    ret_array = []

    x = data[0]
    data = data[1:]
    if x == zero:
        ret_array.append("10")
        prev = one
    elif x == one:
        ret_array.append("01")
        prev = zero

    for x in data:
        if x == prev:
            ret_array.append("10")
            prev = zero
        else:
            ret_array.append("01")
            prev = one

    return ''.join(ret_array)


def manchester_encode(data, invert=False):
    """
    Manchester / Bi-Phase Level (Split Phase) / Bi-Phase-L

    Level change occurs at the beginning of every bit period
    "One" is represented by a "One" level with transition to the "Zero" level
    "Zero" is represented by a "Zero" level with transition to the "One" level.

    """
    zero, one = set_bit_order(invert=invert)
    ret_array = []

    for x in data:
        if x == zero:
            ret_array.append("01")
        elif x == one:
            ret_array.append("10")
    return ''.join(ret_array)


def manchester_decode(s, invert=False):
    i = 1
    b = list()
    slen = len(s)
    zero, one = set_bit_order(invert=invert)

    while(i < slen):
        if s[i] == s[i-1]:
            raise ValueError("Invalid Manchester Encoding")
        elif s[i] == "1":
            b.append(zero)
        else:
            b.append(one)
        i = i + 2

    return "".join(b)


# Simple demanchester used everywhere in the code
def demanchester(s):
    i = 1
    b = list()
    slen = len(s)

    # Note that since 1 starts as "1"
    # we are testing the 2nd bit for '1' or '0'
    while(i < slen) :
        if s[i] == s[i-1] :
            raise InvalidManchesterEncoding(s[i], s[i-1])
        if s[i] == "1":
            b.append("1")
        else:
            b.append("0")
        i = i + 2

    return "".join(b)
