import PIL
from pathlib import Path
import streamlit as st
import easyocr
import os
from PIL import Image
import cv2
from load_model import load_model, get_config, inference
import torch
import easyocr
import numpy as np
import gc
from pypdf import PdfReader






def define_doc_state(doc):
    img = cv2.imread(doc.name)
    
    opt=get_config('./en_filtered_config_t.yaml')
    model=load_model('best_accuracy_t.pth',opt=opt)
    
    reader = easyocr.Reader(['ru'],
                            model_storage_directory='model',
                            user_network_directory='user_network',
                            recog_network='custom_example')
    st.image(img, caption='Detection')

    result = reader.readtext(doc.name)
    for i in result:
      st.write(i[1].replace('~',' ').replace('-',','))
    torch.cuda.empty_cache()
    gc.collect()
    del model, reader 

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


st.write('Перевод файлов в текстовый документ')

pdf_uploaded_file = st.file_uploader("Выберите файл", type=[".pdf",], accept_multiple_files=False)
if pdf_uploaded_file:

    pdf_reader = PdfReader(pdf_uploaded_file.name)
    number_of_pages = len(pdf_reader.pages)
    text = ''
    for i in range(len(number_of_pages)):
      page = pdf_reader.pages[i]
      text += '\n' + '\n'.join(page.extract_text().replace('ё','ӕ').replace('Ё','Ӕ'))

    st.download_button('Скачать текст', text)
    del text
    del pdf_reader
    del number_of_pages


