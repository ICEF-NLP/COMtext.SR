from simpletransformers.ner import ner_model
import pandas as pd
import random
import torch
import numpy as np
from sklearn.model_selection import KFold
from seqeval.metrics import accuracy_score
import json
from load_data import load_corpus_tokens
from helpers.lemmatizer import get_lemma, load_dictionary, DIALECT_INDEX_EKAVICA, DIALECT_INDEX_IJEKAVICA

import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='seqeval')

RANDOM_SEED = 64

MODEL_INDEX = 0 # 0: BERTic, 1: SrBERTa
MODEL_TYPE = ["electra", "roberta"]
MODEL_NAME = ["classla/bcms-bertic", "nemanjaPetrovic/SrBERTa"]
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

    X_tokens, wordlist = load_corpus_tokens(DATA_PATHS[DIALECT], model_name=MODEL_NAME[MODEL_INDEX])
    if DIALECT == DIALECT_INDEX_EKAVICA:
        load_dictionary(DICTIONARY_PATHS[DIALECT_INDEX_EKAVICA], wordlist, DIALECT_INDEX_EKAVICA,
                        model_name=MODEL_NAME[MODEL_INDEX])
    elif DIALECT == DIALECT_INDEX_IJEKAVICA:
        load_dictionary(DICTIONARY_PATHS[DIALECT_INDEX_EKAVICA], wordlist, DIALECT_INDEX_EKAVICA,
                        model_name=MODEL_NAME[MODEL_INDEX])
        load_dictionary(DICTIONARY_PATHS[DIALECT_INDEX_IJEKAVICA], wordlist, DIALECT_INDEX_IJEKAVICA,
                        model_name=MODEL_NAME[MODEL_INDEX])

    labels_list = get_labels(X_tokens)
    results = {}

    kf = KFold(n_splits=10)

    for i in [1, 2, 3, 4, 5, 10, 15]:
        args = {}
        args["num_train_epochs"] =  i
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
        results[i] = []

        fold_index = 0
        for train_index, test_index in kf.split(X_tokens, X_tokens):
            fold_index += 1
            conllu_id_train = []
            id_train = []
            X_train = []
            y_train = []
            conllu_id_test = []
            id_test = []
            X_test = []
            y_test = []

            for elem in train_index:
                id_train.append(X_tokens[elem][0])
                X_train.append(X_tokens[elem][1])
                y_train.append(X_tokens[elem][2])
                conllu_id_train.append(X_tokens[elem][4])
            gold_lemmas = []
            for elem in test_index:
                id_test.append(X_tokens[elem][0])
                X_test.append(X_tokens[elem][1])
                y_test.append(X_tokens[elem][2])
                gold_lemmas.append(X_tokens[elem][3])
                conllu_id_test.append(X_tokens[elem][4])

            train_df = pd.DataFrame(list(zip(id_train, X_train, y_train)), columns=["sentence_id", "words", "labels"])
            test_df = pd.DataFrame(list(zip(id_test, X_test, y_test)), columns=["sentence_id", "words", "labels"])

            model = ner_model.NERModel(MODEL_TYPE[MODEL_INDEX],
                                MODEL_NAME[MODEL_INDEX],
                                use_cuda=True,
                                labels=labels_list,
                                args=args
                                )

            print('Model training for ' + str(i) + ' epochs, fold ' + str (fold_index))
            model.train_model(train_df, acc=accuracy_score)

            print('Model evaluation, fold ' + str(fold_index))
            msd_result, model_outputs, preds_list = model.eval_model(test_df, acc=accuracy_score)
            print('MSD tagging accuracy after fine-tuning for ' + str(i) + ' epochs, fold ' + str(fold_index) + ':')
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
                print(DICTIONARY_NAME[j] + ' lemmatization accuracy after fine-tuning for ' + str(i) + ' epochs, fold ' + str(fold_index) + ':')
                print(lemma_acc)
                lemma_results.append(lemma_acc)

            results[i].append((msd_result, lemma_results))

    with open('results_pretokenized_CV_' + MODEL_NAME[MODEL_INDEX].split('/')[1] + '_' + DIALECT_NAME[DIALECT]
              + '.json', 'w') as outfile:
        json.dump(results, outfile)
