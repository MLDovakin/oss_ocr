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

opt=get_config('./en_filtered_config_t.yaml')
model=load_model('best_accuracy_t.pth',opt=opt)
reader = easyocr.Reader( lang_list=['ru'],) # this needs to run only once to load the model into memory


def define_doc_state(doc):

    result = reader.readtext(doc.name)
    img = cv2.imread(doc.name)
    st.image(img, caption='Detection')
    for (coord, text, prob) in result:
        (topleft, topright, bottomright, bottomleft) = coord
        tx, ty = (int(topleft[0]), int(topleft[1]))
        bx, by = (int(bottomright[0]), int(bottomright[1]))
        q = Image.fromarray(img[ty:by, tx:bx]).convert('RGB').resize((600, 100)).convert('L')
        st.write(inference(model, q, opt))


uploaded_file = st.file_uploader("Выберите файл", type=[".JPG", ".jpg", ".png",], accept_multiple_files=False)
if uploaded_file:
    st.success("Файл успешно загружен", icon="✅")
    define_button_state = st.button("Определить")
    save_folder = os.getcwd()
    save_path = uploaded_file.name
    print(save_path)
    img_arr = cv2.imdecode(np.frombuffer(uploaded_file.getvalue(), np.uint8), cv2.IMREAD_UNCHANGED,)
    cv2.imwrite(save_path, img_arr)

    if define_button_state:
         define_doc_state(uploaded_file)

         #res_image = PIL.Image.open(uploaded_file.name)

         #st.image(res_image, caption='Detection')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
