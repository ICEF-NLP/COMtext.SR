from simpletransformers.ner import ner_model
import pandas as pd
import random
import torch
import numpy as np
from seqeval.metrics import accuracy_score
import json
from load_data import load_corpus_tokens
from helpers.lemmatizer import get_lemma, load_dictionary, DIALECT_INDEX_EKAVICA, DIALECT_INDEX_IJEKAVICA

import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='seqeval')

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
        id_test = []
        X_test = []
        y_test = []
        gold_lemmas = []
        conllu_id_test = []

        for elem in train_data:
            id_train.append(elem[0])
            X_train.append(elem[1])
            y_train.append(elem[2])
            conllu_id_train.append(elem[4])

        for elem in test_data:
            id_test.append(elem[0])
            X_test.append(elem[1])
            y_test.append(elem[2])
            gold_lemmas.append(elem[3])
            conllu_id_test.append(elem[4])

        train_df = pd.DataFrame(list(zip(id_train, X_train, y_train)), columns=["sentence_id", "words", "labels"])
        test_df = pd.DataFrame(list(zip(id_test, X_test, y_test)), columns=["sentence_id", "words", "labels"])

        model = ner_model.NERModel("electra", "classla/bcms-bertic", use_cuda=True, labels=labels_list, args=args)

        print('Model training for ' + str(i) + ' epochs')
        model.train_model(train_df, show_running_loss=False, acc=accuracy_score)

        print('Model evaluation')
        msd_result, model_outputs, preds_list = model.eval_model(test_df, acc=accuracy_score)
        print('MSD tagging evaluation results after fine-tuning for ' + str(i) + ' epochs:')
        print(msd_result)

        predicted_lemmas = [[]]
        if DIALECT == DIALECT_INDEX_IJEKAVICA:
            predicted_lemmas.append([])
        t = 0
        for sentence in preds_list:
            for prediction in sentence:
                if DIALECT == DIALECT_INDEX_EKAVICA:
                    lemma = get_lemma(prediction, X_test[t], DIALECT_INDEX_EKAVICA)['text']
                    predicted_lemmas[DIALECT_INDEX_EKAVICA].append(lemma)
                elif DIALECT == DIALECT_INDEX_IJEKAVICA:
                    lemma = get_lemma(prediction, X_test[t], DIALECT_INDEX_EKAVICA)['text']
                    predicted_lemmas[DIALECT_INDEX_EKAVICA].append(lemma)
                    lemma = get_lemma(prediction, X_test[t], DIALECT_INDEX_IJEKAVICA)['text']
                    predicted_lemmas[DIALECT_INDEX_IJEKAVICA].append(lemma)
                t += 1

        lemma_results = []
        for j in range(len(predicted_lemmas)):
            lemma_acc = accuracy_score(gold_lemmas, predicted_lemmas[j])
            print(DICTIONARY_NAME[j] + ' lemmatization evaluation results after fine-tuning for ' + str(i) + ' epochs:')
            print(lemma_acc)
            lemma_results.append(lemma_acc)

        results.append((msd_result, lemma_results))

    with open('results_bertic_setimes_pretokenized' + DIALECT_NAME[DIALECT] + '.json', 'w') as outfile:
        json.dump(results, outfile)
