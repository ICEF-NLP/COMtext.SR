import cyrtranslit
import pandas as pd
import os

from src.paths import get_dataset_filepath

#TODO: check which data files were including
#if we are including the trans its fine like this,
#if not prepare a function for creating the trans column for the datasets


def load_corpus(dataset = "comtext", columns=['sentence_order', 'sentence_id', 'token_id', 'token', 'lemma', 'msd', 'ner', 'trans'], 
                is_ekavica:bool=True, is_latin:bool=True):
    
    filepath = get_dataset_filepath(dataset, is_ekavica)

    sentences = []
    sent_order = 0
    sent_id = ''

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            if line.startswith("# sent_id"):
                sent_order += 1
                sent_id = line.split('=')[1].strip()
                continue
            elif line.startswith("#"):
                continue

            parts = line.split('\t')
            if len(parts) < 2:
                continue

            token_id = int(parts[0])
            token = parts[1]
            lemma = parts[2]
            trans = None
            if dataset == "comtext":
                msd = parts[3]
                ner = parts[4]  
                trans = parts[5]
            elif dataset == "setimes":
                msd = parts[4]
                misc = parts[9]
                ner = 'O'
                if misc != '_':
                    for item in misc.split("|"):
                        if item.strip().startswith("NER="):
                            ner = item.split("=")[1].upper()

            if not is_latin:
                token = cyrtranslit.to_cyrillic(token, "sr")
                lemma = cyrtranslit.to_cyrillic(lemma, "sr")
                #TODO: check if trans should be converted to cyrillic as well

            sentences.append({
                "sentence_order": sent_order,
                "sentence_id": sent_id,
                "token_id": token_id,
                "token": token,
                "lemma": lemma,
                'msd': msd,
                "ner": ner,
                "trans": trans
            })
    df = pd.DataFrame(sentences)
    df = df[columns]
    return df

def load_untokenized_corpus(dataset = "comtext", columns=['sentence_order', 'sentence_id', 'text'], 
                            is_ekavica:bool=True, is_latin:bool=True):
    filepath = get_dataset_filepath(dataset, is_ekavica)

    sentences = []
    sent_order = 0
    sent_id = ''
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            if line.startswith("# sent_id"):
                sent_order += 1
                sent_id = line.split('=')[1].strip()
                continue
            elif line.startswith("# text"):
                text = line.split('=')[1].strip()
                if not is_latin:
                    text = cyrtranslit.to_cyrillic(text, 'sr')
                sentences.append({
                    "sentence_id": sent_id,
                    "sentence_order": sent_order,
                    "text": text
                })
            else:
                continue
            
    df = pd.DataFrame(sentences)
    df = df[columns]
    return df
