from simpletransformers.ner import ner_model
import pandas as pd
import random
import torch
import numpy as np
from load_data import load_corpus_tokens
from helpers.lemmatizer import DIALECT_INDEX_EKAVICA, DIALECT_INDEX_IJEKAVICA

RANDOM_SEED = 64
DIALECT = DIALECT_INDEX_EKAVICA # EKAVICA / IJEKAVICA
DIALECT_NAME = ['Ekavica', 'Ijekavica']
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

    train_data, wordlist = load_corpus_tokens(DATA_PATHS[DIALECT])
    labels_list = get_labels(train_data)

    i = 15
    args = {}
    args["num_train_epochs"] = i
    args['fp16'] = False
    args["manual_seed"] = RANDOM_SEED
    args["max_seq_length"] = 512
    args["silent"] = False
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

    for elem in train_data:
        id_train.append(elem[0])
        X_train.append(elem[1])
        y_train.append(elem[2])

    train_df = pd.DataFrame(list(zip(id_train, X_train, y_train)), columns=["sentence_id", "words", "labels"])

    model = ner_model.NERModel("electra", "classla/bcms-bertic", use_cuda=True, labels=labels_list, args=args)

    print('Model training for ' + str(i) + ' epochs')
    model.train_model(train_df)
