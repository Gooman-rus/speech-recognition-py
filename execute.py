# -*- coding: utf-8 -*-

from subprocess import call


def speech_exec(line):
    """
    checks line and executes something
    """
    if (line.find(u'тест') > -1):
        call(["ls", "-l"])