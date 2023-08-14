import os, sys, gc, warnings
import logging, math, re, heapq
import pandas as pd
import numpy as np
from collections import Counter


word_list = open('all_vocab.txt', encoding='utf8').read().replace('\n', ' ').split(' ')
vocab = set(word_list)

word_count_dict = {}
word_count_dict = Counter(word_list)


probs = {}
total_words = sum(word_count_dict.values())

for word, word_count in word_count_dict.items():
    word_prob = word_count/total_words
    probs[word] = word_prob

def delete_letter(word):
    delete_list = []
    split_list = []
    split_list = [(word[:i], word[i:]) for i in range(len(word))]
    delete_list = [L+R[1:] for L, R in split_list]
    return delete_list

def switch_letter(word):
    switch_list = []
    split_list = []
    split_list = [(word[:i], word[i:]) for i in range(len(word))]
    switch_list = [L + R[1] + R[0] + R[2:] for L, R in split_list if len(R)>=2]
    return switch_list

def replace_letter(word):
    letters = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяӕ'
    replace_list = []
    split_list = []
    split_list = [(word[0:i], word[i:]) for i in range(len(word))]
    replace_list = [L + letter + (R[1:] if len(R)>1 else '') for L, R in split_list if R for letter in letters]
    replace_set = set(replace_list)
    replace_list = sorted(list(replace_set))
    return replace_list

def insert_letter(word):
    letters = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяӕ'
    insert_list = []
    split_list = []
    split_list = [(word[0:i], word[i:]) for i in range(len(word)+1)]
    insert_list = [L + letter + R for L, R in split_list for letter in letters]
    return insert_list

def edit_one_letter(word, allow_switches = True):
    edit_one_set = set()
    edit_one_set.update(delete_letter(word))
    if allow_switches: edit_one_set.update(switch_letter(word))
    edit_one_set.update(replace_letter(word))
    edit_one_set.update(insert_letter(word))
    if word in edit_one_set: edit_one_set.remove(word)
    return edit_one_set

def edit_two_letter(word, allow_switches = True):
    edit_two_set = set()
    edit_one = edit_one_letter(word, allow_switches=allow_switches)
    for word in edit_one:
        if word:
            edit_two = edit_one_letter(word, allow_switches=allow_switches)
            edit_two_set.update(edit_two)

    return edit_two_set


def get_spelling_suggestions(word, probs, vocab, n=2,):
    suggestions = []
    top_n_suggestions = []
    suggestions = list((word in vocab and word) or
                       edit_one_letter(word).intersection(vocab) or
                       edit_two_letter(word).intersection(vocab)
                       )
    top_n_suggestions = [[s, probs[s]] for s in list(suggestions)]
    return top_n_suggestions


def prepare_word(words):
    s_remove = '()*+,-./:;<=>?@[\\]№_`{|}0123456789!\"#&()*+'
    words = words.split()

    words = [''.join([sum for sum in w if sum not in s_remove]) for w in words]
    return words


def get_spell(word_list):
    my_words = prepare_word(word_list)
    tmp_corrections = []
    for word_c in my_words:
        tmp_corrections.append(get_spelling_suggestions(word_c, probs, vocab, 7))
    for i, word in enumerate(my_words):
        print(' ')
        print(f'Word - {my_words[i]}')
        for j, word_prob in enumerate(tmp_corrections[i]):
            my_words[i] = j
    return ' '.join(my_words)