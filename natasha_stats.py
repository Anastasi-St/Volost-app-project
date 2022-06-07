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
import codecs, os, re
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
    if not end:
        end = clean_txt.find('Архивный')
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
        with codecs.open(str(path), 'r', encoding='utf-8') as f:
            text = f.read()
            clean_txt = clean_text(text)
            new_dir = 'clean_texts'
            with codecs.open(new_dir+'/'+'clean_'+os.path.basename(path), 'w', encoding='utf-8') as new_f:
                new_f.write(clean_txt)

def all_statistics():
    stats = {}
    for path in clean_pathlist:
        with codecs.open(str(path), 'r', encoding='utf-8') as f:
            text = f.read()
            stats = statistics_pos(text, stats)
    stats = {k: v for k, v in sorted(stats.items(), key=lambda item: item[1])}
    stats['pos'] = "Части речи"
    return stats

#stats = all_statistics()

val_pos = ['NOUN', 'PROPN', 'ADJ', 'AUX', 'VERB', 'PRON']
words = [ "AUX", "DET", "SCONJ", "ADV", "PART", "PRON", "CCONJ", "NUM", "ADJ", "ADP", "VERB", "PROPN", "NOUN"]

def lemmas_dist(text, stats):
    doc = Doc(text)
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)
    for token in doc.tokens:
        token.lemmatize(morph_vocab)
        #print(token)
        if token.pos in val_pos:
            if token.lemma in stats:
                stats[token.lemma] += 1
            else:
                stats[token.lemma] = 1
    return stats

def lemmas():
    stats = {}
    for path in clean_pathlist:
        with codecs.open(str(path), 'r', encoding='utf-8') as f:
            text = f.read()
            stats = lemmas_dist(text, stats)
    short_stats = {}
    for tok in stats:
        if stats[tok] >= 10:
            short_stats[tok] = stats[tok]
    short_stats = {k: v for k, v in sorted(short_stats.items(), key=lambda item: item[1])}
    short_stats['lem'] = "Леммы"
    return short_stats

def general_stats(text, wcount, scount):
    doc = Doc(text)
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)
    for token in doc.tokens:
        if token.pos in words:
            #print(token.text)
            wcount += 1
    scount += len(doc.sents)
    return wcount, scount

def count_stats():
    wcount = 0
    scount = 0
    for path in clean_pathlist:
        with codecs.open(str(path), 'r', encoding='utf-8') as f:
            text = f.read()
            wcount, scount = general_stats(text, wcount, scount)
    return wcount, scount

def ner_stats(id, text, stats):
    doc = Doc(text)
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)
    doc.tag_ner(ner_tagger)
    for token in doc.spans:
        token.normalize(morph_vocab)
        stats.append((id, token.type, token.normal))
    return stats

def all_ner():
    stats = []
    for path in clean_pathlist:
        with codecs.open(str(path), 'r', encoding='utf-8') as f:
            text = f.read()
            id = int(re.search(r'clean_text_([0-9]*?)\.txt', str(path)).group(1))
            stats = ner_stats(id, text, stats)
    #print(len(stats))
    return stats

#print(all_ner())
text_47 = '''№№ по порядку:
16/116.
Время поступления жалоб или просьб:
Марта 10 [1914 г.].
Содержание жалобы:
Крестьянка деревни Бороздиной Александра Христофорова Бороздина просит взыскать за работу с крестьянина деревни Атамановой Варлама Лукина Шилова 9 рублей.
Показания свидетелей и иные доказательства. Решение суда.
1914 года марта 22 дня Тулинский волостной суд в составе судей: Останина, Зверева и Рогожкина рассматривал дело по иску Александры Бороздиной с Варлама Лукина Шилова.
1, На суд явились просительница Бороздина и ответчик Шилов.
2, Предложенное примирение не состоялось,.
3, Просительница Александра Бороздина иск свой подтвердила и объяснила, что летом минувшего года ее дочери работали у Шилова 9 дней по 70 копеек и заработали 12 рублей 60 копеек, в число каковых денег Шилов дал ей муки 8 пудов 26 фунтов, по какой цене не сказал и остальные деньги не доплачивает.
4, ответчик Варлам Шилов возразил, что он цену за работу кладет по 70 копеек одной девице, и другой по 60 копеек, а всего на сумму 11 рублей 70 копеек, отдал Бороздиной 8 пудов 26 фунтов муки по полагая по 80 копеек на 6 рублей 93 копейки, следовательно, состоит должен ей 4 рубля 7 копеек, каковой долг не отрицает.
5, Волостной суд находя, что Шилов обязан был уплатить обеим поденщицам одинаково по 70 копеек, а всего 12 рублей 60 копеек и что цена на муку тогда была не 80 копеек, а в среднем 55 копеек, следовательно, уплачено им Бороздиной муки на 4 рубля 66 копеек, осталось доплатить 7 рублей 94 копейки – постановил: взыскать с Варлама Лукина Шилова в пользу Александры Бороздиной 7 рублей 94 копейки. О чем объявлено тяжущимся с правом обжалования в 30-дневный срок Крестьянскому начальнику 4 участка Барнаульского уезда подачей жалобы в 2-х экземплярах через сей суд.
Волостные судьи: 1. Останин 2. Зверев 3. Рогожкин 4. Харев.
Расписка в выслушании решения или приговора:
Решение выслушали: Варлам Шилов, Бороздина (неграмотная).
Время исполнения решений или приговоров и кто приводил их в исполнение:
Об исполнении предписано Атамановскому старосте 24 апреля 1914 г.'''

def pos_words(text):
    stats = {}
    doc = Doc(text)
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)
    for token in doc.tokens:
        if token.pos in stats:
            if token.text not in stats[token.pos]:
                stats[token.pos].append(token.text)
        else:
            stats[token.pos] = [token.text]
    return stats

# print(pos_words(text_47))

def dict_to_json(dct, name):
    with codecs.open('static/js/'+name+'.json', 'w', encoding="utf-8") as f:
        json.dump(dct, f, indent=4)

#dict_to_json(stats, 'lemmas')

