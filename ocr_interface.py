import PIL
from pathlib import Path
import streamlit as st
import easyocr
import os
from PIL import Image
import cv2
import numpy as np


print(os.listdir('user_network'))
def define_doc_state(doc):
    reader = easyocr.Reader(['ru'],
                            model_storage_directory='model',
                            user_network_directory='user_network',
                            recog_network='custom_example')

    print(doc.name)
    img = cv2.imread(doc.name, cv2.COLOR_BGR2GRAY)
    img = cv2.resize(img,(600,100),interpolation=Image.ANTIALIAS)
    cv2.imwrite(doc.name, img)
    result = reader.readtext(doc.name, allowlist='(),.ӔӕАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ-',paragraph=False)
    st.write(result[0][1])

    top_left = tuple(result[0][0][0])
    bottom_right = tuple(result[0][0][2])
    text = result[0][1]
    font = cv2.FONT_HERSHEY_SIMPLEX

    img = cv2.rectangle(img, top_left, bottom_right, (0, 255, 0), 3)
    img = cv2.putText(img, 'text', top_left, font, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

    st.image(img, caption='Detection')

uploaded_file = st.file_uploader("Выберите файл", type=[".JPG", ".jpg", ".png",], accept_multiple_files=False)
if uploaded_file:
    st.success("Файл успешно загружен", icon="✅")
    define_button_state = st.button("Определить")
    save_folder = os.getcwd()
    save_path = uploaded_file.name
    print(save_path)
    img_arr = cv2.imdecode(np.frombuffer(uploaded_file.getvalue(), np.uint8), cv2.IMREAD_COLOR)
    cv2.imwrite(save_path, img_arr)

    if define_button_state:
         define_doc_state(uploaded_file)

         #res_image = PIL.Image.open(uploaded_file.name)

         #st.image(res_image, caption='Detection')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/