# -*- coding: utf-8 -*-

from natasha import (
    Segmenter,
    MorphVocab,
    NewsEmbedding,
    NewsMorphTagger,
    NewsSyntaxParser,
    NewsNERTagger,
    PER,
    NamesExtractor,
    Doc
)
from bs4 import BeautifulSoup
from pathlib import Path
import codecs, os
import json


segmenter = Segmenter()
morph_vocab = MorphVocab()
emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)
syntax_parser = NewsSyntaxParser(emb)
ner_tagger = NewsNERTagger(emb)
names_extractor = NamesExtractor(morph_vocab)

headers = ['№№ по порядку', 'Время поступления жалоб или просьб', 'Содержание жалобы',
           'Показания свидетелей и иные доказательства.', 'Решение суда',
           'Расписка в выслушании решения или приговора',
           'Время исполнения решений или приговоров и кто приводил их в исполнение']

def clean_text(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    for s in soup.select('a'):
        s.extract()

    clean_txt = soup.get_text()
    start = clean_txt.find(headers[0])
    end = clean_txt.find('---')
    clean_txt = clean_txt[start:end].strip('\n')
    clean_list = clean_txt.split('\n')
    new_clean_list = []
    for sent in clean_list:
        if not sent.endswith('.'):
            if sent in headers:
                sent = sent+':'
            else:
                sent = sent+'.'
        new_clean_list.append(sent)
    clean_txt = '\n'.join(new_clean_list)
    clean_txt = clean_txt.replace('&quot;', '"')
    return clean_txt

dir = 'doc_texts'
clean_dir = 'clean_texts'
pathlist = Path(dir).rglob('text_[0-9]*.txt')
clean_pathlist = Path(clean_dir).rglob('clean_text_[0-9]*.txt')

def statistics_pos(text, stats: dict):
    doc = Doc(text)
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)
    for tok in doc.tokens:
        if tok.pos in stats:
            stats[tok.pos] += 1
        else:
            stats[tok.pos] = 1
    return stats

def clean_files():
    for path in pathlist:
        with codecs.open(str(path), 'r', encoding='windows-1251') as f:
            text = f.read()
            clean_txt = clean_text(text)
            new_dir = 'clean_texts'
            with codecs.open(new_dir+'/'+'clean_'+os.path.basename(path), 'w', encoding='windows-1251') as new_f:
                new_f.write(clean_txt)

def all_statistics():
    stats = {}
    for path in clean_pathlist:
        with codecs.open(str(path), 'r', encoding='windows-1251') as f:
            text = f.read()
            stats = statistics_pos(text, stats)
    stats = {k: v for k, v in sorted(stats.items(), key=lambda item: item[1])}
    return stats

#stats = all_statistics()

def dict_to_json(dct):
    with open('statistics.json', 'w') as f:
        json.dump(dct, f, indent=4)

#dict_to_json(stats)
from urllib import request
#u2 = request.urlopen("https://www.kinopoisk.ru/film/342/")
#site = '''<img alt="Криминальное чтиво (Pulp Fiction)" class="film-poster styles_root__24Jga styles_rootInLight__GwYHH image styles_root__DZigd" data-tid="d813cf42" src="//avatars.mds.yandex.net/get-kinopoisk-image/1900788/87b5659d-a159-4224-9bff-d5a5d109a53b/300x450" srcset="//avatars.mds.yandex.net/get-kinopoisk-image/1900788/87b5659d-a159-4224-9bff-d5a5d109a53b/300x450 1x, //avatars.mds.yandex.net/get-kinopoisk-image/1900788/87b5659d-a159-4224-9bff-d5a5d109a53b/600x900 2x"/>'''#u2.read()
#u2.close()
#print(site)
#soup = BeautifulSoup(site, "html.parser")
#movie = 'Криминальное чтиво'
#for s in soup.select('img.film-poster'):
#    print(s["alt"], '\n', s["src"])
#    if movie in s["alt"]:
#        print('yass')
