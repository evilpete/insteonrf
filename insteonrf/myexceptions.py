#!/usr/bin/env python

class InvalidManchesterEncoding(Exception):
    def __init__(self, s1, s2):
        self.value = "%s == %s" % (s1, s2)
        self.s1 = s1
        self.s2 = s2

    def __str__(self):
        err = "Invalid Manchester Encoding: %s == %s"
        err %= (self.s1, self.s2)
        return err
