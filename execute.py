# -*- coding: utf-8 -*-

from os import getcwd

import webbrowser
from random import randint


def speech_exec(line):
    """
    выполняет действия в зависимости от строки line
    """

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