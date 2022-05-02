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


segmenter = Segmenter()
morph_vocab = MorphVocab()
emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)
syntax_parser = NewsSyntaxParser(emb)
ner_tagger = NewsNERTagger(emb)
names_extractor = NamesExtractor(morph_vocab)

def clean_text(html_text):
    soup = BeautifulSoup(html_text, "html.parser")

    for s in soup.select('a'):
        s.extract()

    clean_txt = soup.get_text()

    start = clean_txt.find('№№ по порядку')
    end = clean_txt.find('---')

    clean_txt = clean_txt[start:end].strip('\n')

    return clean_txt

#doc = Doc(new_text)
#doc.segment(segmenter)
#doc.tag_morph(morph_tagger)
#doc.tag_ner(ner_tagger)