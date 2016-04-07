# -*- coding: utf-8 -*-
from Tkinter import *
from os import getcwd

import webbrowser
from random import randint
from subprocess import call


def speech_exec(line):
    """
    checks the line and executes something
    """
    if (line.find(u'тест') > -1):
        call(["ls", "-l"])

    if (line.find(u'узи почк') > -1):
        webbrowser.open(getcwd() + '/res/kidney.jpg')

    if (line.find(u'рентген почк') > -1):
        webbrowser.open(getcwd() + '/res/kidney_xray.jpg')

    if (line.find(u'анализ крови') > -1):
        webbrowser.open(getcwd() + '/res/blood.jpg')

    if (line.find(u'пульс') > -1):
        print randint(50, 150)

    if (line.find(u'давление') > -1):
        print randint(100, 160)
        print randint(40, 100)