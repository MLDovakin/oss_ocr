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
import re

st.title('Проверка орфографии дигорского языка')

hobj = hunspell.HunSpell('./os_dict/dig_os_OS.dic', './os_dict/dig_os_OS.aff')
words_st = st.text_area('Введите текст ', height=250)

if st.button('Исправить'):

    if words_st:
        words = words_st.split(' ')
        for i in range(len(words)):

            try:
                words[i] =  re.sub(r'[^\w\s]', '', words[i])
                sp = hobj.spell(words[i])
                if sp != True:
                    w = ', '.join(hobj.suggest(words[i]))
                    st.write(f"Слово с ошибкой : :red[{words[i]}]")
                    st.write(f'Возможный вариант : :green[{w}]')
                    st.text("")
            except IndexError:
                st.write(f'Слова {words[i]} нет в словаре')
              
