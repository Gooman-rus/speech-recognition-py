#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
# import sys
from ctypes import *
from contextlib import contextmanager

import pyaudio
from pocketsphinx.pocketsphinx import *
from sphinxbase.sphinxbase import *

from execute import speech_exec

script_dir = os.path.dirname(os.path.realpath(__file__))
model_dir = '/home/yura/practics/'

hmm = os.path.join(model_dir, 'zero_ru_cont_8k_v3/zero_ru.cd_cont_4000')
# lm = os.path.join(model_dir, "speech_reconginition_project/lmbase.lm.DMP")
dict = os.path.join(model_dir, 'speech_reconginition_project/words.dict')
fsg_gram = os.path.join(model_dir, 'speech_reconginition_project/gram.fsg')

# sys.stderr = open(os.path.join(script_dir, "stderr.log"), "a")

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)


def py_error_handler(filename, line, function, err, fmt):
    pass
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)


@contextmanager
def noalsaerr():
    asound = cdll.LoadLibrary('libasound.so')
    asound.snd_lib_error_set_handler(c_error_handler)
    yield
    asound.snd_lib_error_set_handler(None)

config = Decoder.default_config()
config.set_string('-hmm', hmm)
#config.set_string('-lm', lm)
config.set_string('-dict', dict)
config.set_string('-logfn', 'log.log')
decoder = Decoder(config)

# Switch to JSGF grammar
jsgf = Jsgf(os.path.join(model_dir, 'speech_reconginition_project/gram.jsgf'))
rule = jsgf.get_rule('mygrammar.query')
fsg = jsgf.build_fsg(rule, decoder.get_logmath(), 7.5)
fsg.writefile(fsg_gram)
config.set_string('-fsg', fsg_gram)

decoder.set_fsg('mygrammar', fsg)
decoder.set_search('mygrammar')
decoder.start_utt()

with noalsaerr():
    p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
stream.start_stream()
in_speech_bf = True

print 'Start.'
while True:
    buf = stream.read(1024)
    if buf:
        decoder.process_raw(buf, False, False)
        # try:
        #     if decoder.hyp().hypstr != '':
        #         print('Partial decoding result:', decoder.hyp().hypstr)
        # except AttributeError:
        #     pass
        #if decoder.get_in_speech():
        #sys.stdout.write('.')
        #sys.stdout.flush()
        if decoder.get_in_speech() != in_speech_bf:
            in_speech_bf = decoder.get_in_speech()
            if not in_speech_bf:
                decoder.end_utt()
                try:
                    if decoder.hyp().hypstr != '':
                        str = decoder.hyp().hypstr.decode('utf-8')
                        print str
                        speech_exec(str)

                except AttributeError:
                    pass
                decoder.start_utt()
    else:
        break
decoder.end_utt()
print('An Error occured:', decoder.hyp().hypstr)