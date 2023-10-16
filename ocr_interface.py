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
import re
from pypdf import PdfReader
import itertools
import subprocess
import traceback 


st.markdown("<h1 style='text-align: start; font-size:30px; ;'>OCR ДИГОРСКОГО ЯЗЫКА</h1>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: start; font-size:20px; font-weight: normal;'>Конвертирование изображения в текст</h1>", unsafe_allow_html=True)

def define_doc_state(doc):

    opt = get_config('./en_filtered_config_t.yaml')
    model = load_model('best_accuracy_t2.pth', opt=opt)

    reader = easyocr.Reader(['ru'],
                            model_storage_directory='model',
                            user_network_directory='user_network',
                            recog_network='custom_example')
    st.image(doc.name, caption='Detection')

    result = reader.readtext(doc.name)
    tt = []



    for i in result:
        tt.append(i[1].replace('~', ' ').replace('-', ', ').replace('/', '-'))

    tt = [i.split(' ') for i in tt]
    tt = [i for i in list(itertools.chain(*tt)) if i !='']

    for i in range(len(tt) - 1):

        if '.' in tt[i] and tt[i][-1] != '.':
            tt[i] = tt[i].replace('.', '-')

        if ';' in tt[i] and tt[i][-1] == ';' and tt[i + 1][0].isupper() == False:
            tt[i] = tt[i].replace(';', '-')

        if tt[i][-1] == '-' and tt[i + 1][0].isupper():
            tt[i] = tt[i].replace('-', '.')


    for i in range(len(tt) - 1):
        try:

            print(tt[i],tt[i+1])
            if i != '':
                if tt[i][-1] == '-' :
                    tt[i] = tt[i].replace('-', '') + tt[i + 1]
                    tt[i + 1] = ''
        except IndexError:
            pass
    if  tt[-1][-1] == '-':
        tt[-1] = tt[-1][:-1] + '.'

    tt = [i for i in tt if i != '']
    st.write(' '.join(tt))

    torch.cuda.empty_cache()
    gc.collect()
    del model, reader


uploaded_file = st.file_uploader("Выберите изображение", type=[".jpg", ".png",], accept_multiple_files=False)
if uploaded_file:
    st.success("Файл успешно загружен", icon="✅")
    define_button_state = st.button("Определить")
    save_folder = os.getcwd()
    save_path = uploaded_file.name
    img_arr = cv2.imdecode(np.frombuffer(uploaded_file.getvalue(), np.uint8), cv2.IMREAD_UNCHANGED,)
    cv2.imwrite(save_path, img_arr)
    
    if define_button_state:
      
         define_doc_state(uploaded_file)

         #res_image = PIL.Image.open(uploaded_file.name)

         #st.image(res_image, caption='Detection')

st.markdown("<h1 style='text-align: start; font-size:20px; font-weight: normal;'>Конвертирование PDF, DjVu в формат TXT</h1>", unsafe_allow_html=True)

pdf_uploaded_file = st.file_uploader("Выберите PDF, DjVu файл", type=[".pdf", ".djvu"], accept_multiple_files=False)

def reflow(infile, outfile):
    with open(infile, encoding='utf-8',errors='ignore') as source, open(outfile, "w",encoding='utf-8',errors='ignore') as dest:
        holdover = ""
        for line in source.readlines():
            st.write(line)

            line = line.strip().replace(' -','-').replace(' –','-')
            if line.endswith("-") or line.endswith('–') or line.endswith(' -') \
                    or line.endswith(' –') or line.endswith(' – ') or line.endswith(' - ') \
                    or line.endswith('- ') or line.endswith('– '):

                lin, _, e = line.rpartition(" ")
                lin = lin.rstrip("\n")

            else:
                lin, e = line, ""
                
            dest.write(f"{holdover}{lin}\n")
            holdover = e[:-1].replace(' ','')

def prep_pdf(pdf_reader):

    number_of_pages = len(pdf_reader.pages)
    text = ''
    for i in range(0, number_of_pages):
        page = pdf_reader.pages[i]
        text += page.extract_text().replace('ё', 'ӕ').replace('Ё', 'Ӕ')
    with open('source.txt', 'w', encoding='utf-8',errors='ignore') as f:
        f.write(text)

    reflow('source.txt','dest.txt')

    text = open('dest.txt', encoding='utf-8',errors='ignore').read()
    st.write(text)
    return text
            

if pdf_uploaded_file:
    
    with open(pdf_uploaded_file.name, 'wb') as f:
         f.write(pdf_uploaded_file.read())
       
    if pdf_uploaded_file.name.endswith('.pdf'):
        
        open('dest.txt', 'a').close()
        pdf_reader = PdfReader(pdf_uploaded_file.name)

        text = prep_pdf(pdf_reader)
        text = re.sub(r'-\n(\w+ *)', r'\1\n', text)
        st.download_button('Скачать текст', text, file_name=pdf_uploaded_file.name.replace('.pdf', '.txt'), )
        del text
        os.remove(pdf_uploaded_file.name.replace('.djvu', '.txt'))
        os.remove(pdf_uploaded_file.name) 
        
    if pdf_uploaded_file.name.endswith('.djvu'):
        subprocess.run(('djvutxt', f'{pdf_uploaded_file.name}',  f'DK.txt'))
        text = open('DK.txt', encoding='utf-8').read()
        st.download_button('Скачать текст', text, file_name=pdf_uploaded_file.name.replace('.djvu', '.txt'), )
        del text
        os.remove('DK.txt')
        os.remove(pdf_uploaded_file.name) 
