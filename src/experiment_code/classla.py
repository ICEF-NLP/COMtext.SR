import classla

from seqeval.metrics import accuracy_score
from evaluate import load

from src.load_data import load_corpus, load_untokenized_corpus


#TODO ALEKSANDRA: check if the labels for NER need to be adjusted/converted

def load_classla(use_serbian_classla = True, use_gpu = True, tokenize_pretokenized = False):
    if use_serbian_classla:
        lang = "sr"
    else:
        lang = "hr"
    classla.download(lang, processors='tokenize, pos, lemma, ner')
    nlp = classla.Pipeline(lang, processors="tokenize, pos, lemma, ner", use_gpu=use_gpu, tokenize_pretokenized=tokenize_pretokenized)
    return nlp


def run_classla_pretokenized(is_ekavica, use_serbian_classla, use_gpu=True):
    df = load_corpus(is_ekavica=is_ekavica, columns=['sentence_order', 'token', 'lemma', 'msd', 'ner'])
    classla_pipeline = load_classla(use_serbian_classla=use_serbian_classla, use_gpu=use_gpu, tokenize_pretokenized=True)

    sentences = df.groupby('sentence_order')['token'].apply(list).tolist()
    gold_lemmas = df.groupby('sentence_order')['lemma'].apply(list).tolist()
    gold_msd = df.groupby('sentence_order')['msd'].apply(list).tolist()
    gold_ner = df.groupby('sentence_order')['ner'].apply(list).tolist()

    document = classla_pipeline(sentences)

    pred_lemmas = []
    pred_msd = []
    pred_ner = []
    for sentence in document.sentences:
        sent_lemmas = [word.lemma if word.lemma!=None else '' for word in sentence.words]
        pred_lemmas.append(sent_lemmas)
        sent_msd = [word.xpos for word in sentence.words] 
        pred_msd.append(sent_msd)
        sent_ner = [token.ner for token in sentence.tokens]
        pred_ner.append(sent_ner)

    acc_lemmas = accuracy_score(gold_lemmas, pred_lemmas)
    acc_msd = accuracy_score(gold_msd, pred_msd)
    acc_ner = accuracy_score(gold_ner, pred_ner)

    print(f"CLASSLA PRETOKENIZED RESULTS")
    print(f"{"ekavica" if is_ekavica else "ijekavica"} , classla_variant {"serbian" if use_serbian_classla else "croatian"}")
    print(f"Lemma Accuracy: {acc_lemmas}")
    print(f"MSD Accuracy: {acc_msd}")
    print(f"NER Accuracy: {acc_ner}")

def run_classla_untokenized(is_ekavica, use_serbian_classla, use_gpu=True):
    
    df_token_msd = load_corpus(is_ekavica=is_ekavica, columns=['sentence_id','token', 'msd', 'lemma', 'ner'])
    gold_map = df_token_msd.groupby('sentence_id').agg({
        'msd': lambda x: " ".join(x.astype(str)).strip(),
        'lemma': lambda x: " ".join(x.astype(str)).strip(),
        'ner': lambda x: " ".join(x.astype(str)).strip()
    }).to_dict('index')

    df = load_untokenized_corpus(is_ekavica=is_ekavica, columns=["sentence_id", "text"])

    classla_pipeline = load_classla(use_serbian_classla=use_serbian_classla, use_gpu=use_gpu, tokenize_pretokenized=False)

    gold_lemmas = []
    gold_msd = []
    gold_ner = []
    pred_lemmas = []
    pred_msd = []
    pred_ner = []

    for i, row in df.iterrows():
        sentence_id = row['sentence_id']
        document = classla_pipeline(row['text'])

        pred_lemmas.append(" ".join(w.lemma for w in document.iter_words()))
        pred_msd.append(" ".join(w.xpos for w in document.iter_words()))
        pred_ner.append(" ".join(t.ner for t in document.iter_tokens()))

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

    print(f"CLASSLA UNTOKENIZED RESULTS")
    print(f"{"ekavica" if is_ekavica else "ijekavica"} , classla_variant: {"serbian" if use_serbian_classla else "croatian"}")
    print(f"Lemma WER: {str(wer_score_lemmas)}")
    print(f"MSD WER: {str(wer_score_msd)}")
    print(f"NER WER: {str(wer_score_ner)}")

