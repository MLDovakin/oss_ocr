import PIL
from pathlib import Path
import streamlit as st
import easyocr
import os
from PIL import Image
import cv2
from load_model import load_model, get_config, inference

import easyocr
import numpy as np
from spell_words import get_spell
import hunspell
 

st.title('Проверка орфографии дигорского языка')

hobj = hunspell.HunSpell('./os_dict/dig_os_OS.dic', './os_dict/dig_os_OS.aff')
words_st = st.text_area('Введите текст ')

if st.button('Исправить'):

    if words_st:
        words = words_st.split(' ')
        for i in range(len(words)):
            sp = hobj.spell(words[i])
            if sp != True:
                print(st.write(f"слово с ошибкой : :red[{words[i]}]"))
                words[i] = hobj.suggest(words[i])[0]
        st.write('Правильный вариант: ' ' '.join(words))

