from simpletransformers.ner import ner_model
import pandas as pd
import random
import torch
import numpy as np
import json
from load_data import load_corpus, load_corpus_tokens, load_untokenized
from helpers.lemmatizer import get_lemma, load_dictionary, DIALECT_INDEX_EKAVICA, DIALECT_INDEX_IJEKAVICA
import classla

from evaluate import load
wer = load("wer")

RANDOM_SEED = 64
DIALECT = DIALECT_INDEX_EKAVICA # EKAVICA / IJEKAVICA
DIALECT_NAME = ['Ekavica', 'Ijekavica']
DICTIONARY_NAME = ['srLex', 'hrLex']
DICTIONARY_PATHS = ['srLex_v1.3', 'hrLex_v1.3']
DATA_PATHS = (['data/comtext.sr.legal.ekavica.conllu'], ['data/comtext.sr.legal.ijekavica.conllu'])


def get_labels(all_data):
    labels = []
    for item in all_data:
        tag = item[2]
        if tag not in labels:
            labels.append(tag)

    return labels


if __name__ == '__main__':

    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)
    torch.manual_seed(RANDOM_SEED)

    classla.download('sr', processors='tokenize')
    nlp = classla.Pipeline('sr', processors='tokenize')

    train_data, _ = load_corpus_tokens(['data/set.sr.plus.conllup'], conllup=True)
    test_data, wordlist = load_corpus_tokens(DATA_PATHS[DIALECT])
    all_data = train_data.copy()
    all_data.extend(test_data)
    labels_list = get_labels(all_data)

    if DIALECT == DIALECT_INDEX_EKAVICA:
        load_dictionary(DICTIONARY_PATHS[DIALECT_INDEX_EKAVICA], wordlist, DIALECT_INDEX_EKAVICA)
    elif DIALECT == DIALECT_INDEX_IJEKAVICA:
        load_dictionary(DICTIONARY_PATHS[DIALECT_INDEX_EKAVICA], wordlist, DIALECT_INDEX_EKAVICA)
        load_dictionary(DICTIONARY_PATHS[DIALECT_INDEX_IJEKAVICA], wordlist, DIALECT_INDEX_IJEKAVICA)

    untokenized_test_data = load_untokenized(DATA_PATHS[DIALECT])
    sentence_tokenized_test_data = load_corpus(DATA_PATHS[DIALECT])

    results = []

    for i in [1,2,3,4,5,10,15]:
        args = {}
        args["num_train_epochs"] = i
        args['fp16'] = False
        args["manual_seed"] = RANDOM_SEED
        args["max_seq_length"] = 512
        args["silent"] = True
        args['overwrite_output_dir'] = True
        args['reprocess_input_data'] = True
        args['no_cache'] = True
        args['save_eval_checkpoints'] = False
        args['save_model_every_epoch'] = False
        args['use_cached_eval_features'] = False
        args['do_lower_case'] = False

        id_train = []
        X_train = []
        y_train = []
        conllu_id_train = []

        X_test = []
        gold_tags = []
        gold_lemmas = []
        conllu_id_test = []

        for elem in train_data:
            id_train.append(elem[0])
            X_train.append(elem[1])
            y_train.append(elem[2])
            conllu_id_train.append(elem[4])

        for sent_id in sentence_tokenized_test_data.keys():
            X_sent = []
            y_sent = []
            gold_lemmas_sent = []
            for item in sentence_tokenized_test_data[sent_id]:
                X_sent.append(item[1])
                y_sent.append(item[2])
                gold_lemmas_sent.append(item[3])
            X_test.append(X_sent)
            gold_tags.append(' '.join(y_sent))
            gold_lemmas.append(' '.join(gold_lemmas_sent))
            conllu_id_test.append(sent_id)

        train_df = pd.DataFrame(list(zip(id_train, X_train, y_train)), columns=["sentence_id", "words", "labels"])

        classla_tokenized = []
        for index in range(len(X_test)):
            sentence = untokenized_test_data[conllu_id_test[index]]
            doc = nlp(sentence)
            tokenized_sentence = []
            for word in doc.iter_words():
                tokenized_sentence.append(word.text)
            classla_tokenized.append(tokenized_sentence)

        model = ner_model.NERModel("electra", "classla/bcms-bertic", use_cuda=True, labels=labels_list, args=args)

        print('Model training for ' + str(i) + ' epochs')
        model.train_model(train_df)
        print('Model evaluation')
        preds_list, model_outputs = model.predict(classla_tokenized, split_on_space=False)

        predicted_tags = []
        predicted_lemmas = [[]]
        if DIALECT == DIALECT_INDEX_IJEKAVICA:
            predicted_lemmas.append([])

        for sentence in preds_list:
            tag_sen = ''
            lemma_sen = ['']
            if DIALECT == DIALECT_INDEX_IJEKAVICA:
                lemma_sen.append('')
            for prediction in sentence:
                tag_sen += list(prediction.values())[0] + ' '
                if DIALECT == DIALECT_INDEX_EKAVICA:
                    lemma = get_lemma(list(prediction.values())[0], list(prediction.keys())[0], DIALECT_INDEX_EKAVICA)['text']
                    lemma_sen[DIALECT_INDEX_EKAVICA] += lemma + ' '
                elif DIALECT == DIALECT_INDEX_IJEKAVICA:
                    lemma = get_lemma(list(prediction.values())[0], list(prediction.keys())[0], DIALECT_INDEX_EKAVICA)['text']
                    lemma_sen[DIALECT_INDEX_EKAVICA] += lemma + ' '
                    lemma = get_lemma(list(prediction.values())[0], list(prediction.keys())[0], DIALECT_INDEX_IJEKAVICA)['text']
                    lemma_sen[DIALECT_INDEX_IJEKAVICA] += lemma + ' '
            if DIALECT == DIALECT_INDEX_EKAVICA:
                predicted_lemmas[DIALECT_INDEX_EKAVICA].append(lemma_sen[DIALECT_INDEX_EKAVICA].strip())
                predicted_tags.append(tag_sen.strip())
            elif DIALECT == DIALECT_INDEX_IJEKAVICA:
                predicted_lemmas[DIALECT_INDEX_EKAVICA].append(lemma_sen[DIALECT_INDEX_EKAVICA].strip())
                predicted_lemmas[DIALECT_INDEX_IJEKAVICA].append(lemma_sen[DIALECT_INDEX_IJEKAVICA].strip())
                predicted_tags.append(tag_sen.strip())

        wer_score_msd = wer.compute(predictions=predicted_tags, references=gold_tags)
        print('MSD WER after fine-tuning for ' + str(i) + ' epochs:')
        print(wer_score_msd)

        lemma_results = []
        for j in range(len(predicted_lemmas)):
            wer_score_lemma = wer.compute(predictions=predicted_lemmas[j], references=gold_lemmas)
            print(DICTIONARY_NAME[j] + ' lemmatization WER after fine-tuning for ' + str(i) + ' epochs:')
            print(wer_score_lemma)
            lemma_results.append(wer_score_lemma)

        results.append((wer_score_msd, lemma_results))

    with open('results_bertic_setimes_untokenized' + DIALECT_NAME[DIALECT] + '.json', 'w') as outfile:
        json.dump(results, outfile)
