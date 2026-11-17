import trankit 
from evaluate import load
from seqeval.metrics import accuracy_score

from src.load_data import load_corpus, load_untokenized_corpus

#TODO ALEKSANDRA: check if the labels for NER need to be adjusted/converted

def run_trankit_pretokenized(is_ekavica, use_serbian_trankit, use_gpu=True):
    df = load_corpus(is_ekavica=is_ekavica, columns=['sentence_order', 'token', 'lemma', 'msd', 'ner'])
    if use_serbian_trankit:
        language = "serbian"
    else:
        language = "croatian"
    trankit_pipeline = trankit.Pipeline(lang=language, gpu=use_gpu)
    sentences = df.groupby('sentence_order')['token'].apply(list).tolist()
    gold_lemmas = df.groupby('sentence_order')['lemma'].apply(list).tolist()
    gold_msd = df.groupby('sentence_order')['msd'].apply(list).tolist()
    gold_ner = df.groupby('sentence_order')['ner'].apply(list).tolist()

    document = trankit_pipeline(sentences)

    pred_lemmas = []
    pred_msd = []
    pred_ner = []
    for sentence in document['sentences']:
        sentence_tokens = sentence['tokens']
        temp_lemmas = []
        temp_msd = []
        temp_ner = []
        for token in sentence_tokens:
            temp_lemmas.append(token.get('lemma', ''))
            temp_msd.append(token.get('xpos', ''))
            temp_ner.append(token.get('ner', ''))
        pred_lemmas.append(temp_lemmas)
        pred_msd.append(temp_msd)
        pred_ner.append(temp_ner)

    lemma_acc = accuracy_score(gold_lemmas, pred_lemmas)
    msd_acc = accuracy_score(gold_msd, pred_msd)
    ner_acc = accuracy_score(gold_ner, pred_ner)

    print(f"TRANKIT PRETOKENIZED RESULTS")
    print(f"{"ekavica" if is_ekavica else "ijekavica"} , trankit_variant {"serbian" if use_serbian_trankit else "croatian"}")
    print(f"Lemma Accuracy: {lemma_acc}")
    print(f"MSD Accuracy: {msd_acc}")
    print(f"NER Accuracy: {ner_acc}")

    pass

def run_trankit_untokenized(is_ekavica, use_serbian_trankit, use_gpu=True):

    df_gold = load_corpus(is_ekavica=is_ekavica, columns=['sentence_id','msd', 'lemma', 'ner'])
    gold_map = df_gold.groupby('sentence_id').agg({
        'msd': lambda x: " ".join(x.astype(str)).strip(),
        'lemma': lambda x: " ".join(x.astype(str)).strip(),
        'ner': lambda x: " ".join(x.astype(str)).strip()
    }).to_dict('index')

    df = load_untokenized_corpus(is_ekavica=is_ekavica, columns=["sentence_id", "text"])

    if use_serbian_trankit:
        language = "serbian"
    else:
        language = "croatian"
    trankit_pipeline = trankit.Pipeline(lang=language, gpu=use_gpu)

    gold_lemmas = []
    gold_msd = []
    gold_ner = []
    pred_lemmas = []
    pred_msd = []   
    pred_ner = []
    for i, row in df.iterrows():
        sentence_id = row['sentence_id']
        doc_tokens = trankit_pipeline(row['text'], is_sent=True)['tokens']

        temp_lemmas = " ".join(w.get('lemma', '') for w in doc_tokens).strip()
        pred_lemmas.append(temp_lemmas)
        temp_msd = " ".join(w.get('xpos', '') for w in doc_tokens).strip()
        pred_msd.append(temp_msd)
        temp_ner = " ".join(w.get('ner', '') for w in doc_tokens).strip()
        pred_ner.append(temp_ner)

        gold_lemmas.append(gold_map[sentence_id]['lemma'])
        gold_msd.append(gold_map[sentence_id]['msd'])
        gold_ner.append(gold_map[sentence_id]['ner'])

        if (i + 1) % 500 == 0:
            print(f"Processed {i + 1} sentences")

    wer_lemmas = load("wer")    
    wer_score_lemmas = wer_lemmas.compute(predictions=pred_lemmas, references=gold_lemmas)
    wer_msd = load("wer")
    wer_score_msd = wer_msd.compute(predictions=pred_msd, references=gold_msd)
    wer_ner = load("wer")
    wer_score_ner = wer_ner.compute(predictions=pred_ner, references=gold_ner)

    print(f"TRANKIT UNTOKENIZED RESULTS")
    print(f"{"ekavica" if is_ekavica else "ijekavica"} , trankit_variant: {"serbian" if use_serbian_trankit else "croatian"}")
    print(f"Lemma WER: {str(wer_score_lemmas)}")
    print(f"MSD WER: {str(wer_score_msd)}")
    print(f"NER WER: {str(wer_score_ner)}")
