#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from ctypes import *
from contextlib import contextmanager

import pyaudio
from pocketsphinx.pocketsphinx import *
from sphinxbase.sphinxbase import *

from constants import *
from execute import speech_exec

#script_dir = os.path.dirname(os.path.realpath(__file__))

# путь к языковой модели
hmm = os.path.join(MODEL_DIR, 'zero_ru_cont_8k_v3/zero_ru.cd_ptm_4000')

# путь к словарю
dict = os.path.join(MODEL_DIR, 'speech_reconginition_project/words.dict')

#lm = os.path.join(MODEL_DIR, 'speech_reconginition_project/sentences.lm.DMP')

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

# создание объекта для распознавания речи (декодер)
config = Decoder.default_config()

# подключение языковой модели
config.set_string('-hmm', hmm)

#config.set_string('-lm', lm)

# подключение словаря
config.set_string('-dict', dict)

# файл с логами
config.set_string('-logfn', '/dev/null')
#config.set_string('-logfn', 'log.log')

# обновление настроек декодера
decoder = Decoder(config)

# подключение грамматики в формате JSGF
jsgf = Jsgf(os.path.join(MODEL_DIR, 'speech_reconginition_project/gram.jsgf'))
rule = jsgf.get_rule('mygrammar.query')

# преобразование грамматики в формат FSG
fsg = jsgf.build_fsg(rule, decoder.get_logmath(), 7.5)
fsg_gram = os.path.join(MODEL_DIR, 'speech_reconginition_project/gram.fsg')
fsg.writefile(fsg_gram)

config.set_float("-vad_threshold", 3.0)

config.set_float('-kws_threshold', KEY_PHRASE_THRESHOLD)
decoder = Decoder(config)
decoder.set_keyphrase("kws", KEY_PHRASE)

# переключиться на созданную грамматику
decoder.set_fsg('mygrammar', fsg)
decoder.set_search('mygrammar')
decoder.start_utt()

with noalsaerr():
    p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
stream.start_stream()
in_speech_bf = True

print 'Start.'
search_key_phrase = True
change = True
while True:
    if (search_key_phrase and change):
        change = False
        decoder.end_utt()
        decoder.set_search('kws')
        decoder.start_utt()
        #print 'Waiting for the key phrase: '

    if (not search_key_phrase and change):
        change = False
        search_key_phrase = True
        decoder.end_utt()
        decoder.set_search('mygrammar')
        decoder.start_utt()

    buf = stream.read(1024)
    if buf:
        decoder.process_raw(buf, False, False)
        if decoder.get_in_speech() != in_speech_bf:
            in_speech_bf = decoder.get_in_speech()
            if not in_speech_bf:
                decoder.end_utt()
                try:
                    if decoder.hyp().hypstr != '':
                        str = decoder.hyp().hypstr.decode('utf-8')
                        print str
                        if (str.find(KEY_PHRASE.decode('utf-8')) > -1):
                            search_key_phrase = False
                            change = True
                            #print "Say: "
                        else:
                            search_key_phrase = True
                            change = True
                            # запуск функции для обработки распознанной фразы
                            speech_exec(str)

                except AttributeError:
                    pass
                decoder.start_utt()
    else:
        break

decoder.end_utt()
print('An Error occured:', decoder.hyp().hypstr)