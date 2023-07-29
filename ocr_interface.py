import PIL
from pathlib import Path
import streamlit as st
import easyocr
import os
from PIL import Image
import cv2
import numpy as np
def define_doc_state(doc):
    reader = easyocr.Reader(['ru'],
                            model_storage_directory='model',
                            user_network_directory='user_network',
                            recog_network='custom_example')

    print(doc.name)
    image = cv2.imread(doc.name, cv2.COLOR_BGR2GRAY)
    image = cv2.resize(image,(600,100),interpolation=Image.ANTIALIAS)
    cv2.imwrite(doc.name, image)
    result = reader.readtext(doc.name, allowlist='(),.ӔӕАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ-',detail =0,paragraph=False)
    st.write(result)

    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

    # threshold on A-channel
    r, th = cv2.threshold(lab[:, :, 1], 125, 255, cv2.THRESH_BINARY_INV)

    # create copy of cropped image
    crop_img2 = image.copy()

    # draw only first 5 results for clarity
    # borrowed from: https://pyimagesearch.com/2020/09/14/getting-started-with-easyocr-for-optical-character-recognition/
    for (bbox, text, prob) in result[:5]:
        (tl, tr, br, bl) = bbox
        tl = (int(tl[0]), int(tl[1]))
        tr = (int(tr[0]), int(tr[1]))
        br = (int(br[0]), int(br[1]))
        bl = (int(bl[0]), int(bl[1]))
        crop_img2 = cv2.rectangle(crop_img2, tl, br, (0, 0, 255), 3)
        crop_img2 = cv2.putText(crop_img2, text, (tl[0], tl[1] - 20), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 0, 0), 5)
    st.image(crop_img2, caption='Detection')

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