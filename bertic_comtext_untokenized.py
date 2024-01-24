from simpletransformers.ner import ner_model
import pandas as pd
import random
import torch
import numpy as np
from sklearn.model_selection import KFold
import json
from load_data import load_corpus_tokens, load_untokenized
from helpers.lemmatizer import get_lemma, load_dictionary, DIALECT_INDEX_EKAVICA, DIALECT_INDEX_IJEKAVICA
import classla

from evaluate import load
wer = load("wer")

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

    classla.download('sr', processors='tokenize')
    nlp = classla.Pipeline('sr', processors='tokenize')

    X_tokens, wordlist = load_corpus_tokens(DATA_PATHS[DIALECT], model_name=MODEL_NAME[MODEL_INDEX])
    untokenized = load_untokenized(DATA_PATHS[DIALECT], model_name=MODEL_NAME[MODEL_INDEX])


    if DIALECT == DIALECT_INDEX_EKAVICA:
        load_dictionary(DICTIONARY_PATHS[DIALECT_INDEX_EKAVICA], wordlist, DIALECT_INDEX_EKAVICA, model_name=MODEL_NAME[MODEL_INDEX])
    elif DIALECT == DIALECT_INDEX_IJEKAVICA:
        load_dictionary(DICTIONARY_PATHS[DIALECT_INDEX_EKAVICA], wordlist, DIALECT_INDEX_EKAVICA, model_name=MODEL_NAME[MODEL_INDEX])
        load_dictionary(DICTIONARY_PATHS[DIALECT_INDEX_IJEKAVICA], wordlist, DIALECT_INDEX_IJEKAVICA, model_name=MODEL_NAME[MODEL_INDEX])

    labels_list = get_labels(X_tokens)
    results = {}

    kf = KFold(n_splits=10)

    for i in [1]: #[1, 2, 3, 4, 5, 10, 15]:
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

            for elem in train_index:
                id_train.append(X_tokens[elem][0])
                X_train.append(X_tokens[elem][1])
                y_train.append(X_tokens[elem][2])
                conllu_id_train.append(X_tokens[elem][4])

            gold_lemmas = []
            gold_tags = []
            sentence_data = {}
            lemma_sentence = ''
            tag_sentence = ''
            for elem in test_index:
                conllu_id = X_tokens[elem][4]
                if conllu_id not in sentence_data:
                    sentence_data[conllu_id] = untokenized[conllu_id]

                if (X_tokens[elem][0] > X_tokens[elem - 1][0]) and lemma_sentence.strip() != '':
                    gold_lemmas.append(lemma_sentence.strip())
                    gold_tags.append(tag_sentence.strip())
                    lemma_sentence = X_tokens[elem][3] + ' '
                    tag_sentence = X_tokens[elem][2] + ' '
                else:
                    lemma_sentence += X_tokens[elem][3] + ' '
                    tag_sentence += X_tokens[elem][2] + ' '

            gold_lemmas.append(lemma_sentence.strip())
            gold_tags.append(tag_sentence.strip())

            train_df = pd.DataFrame(list(zip(id_train, X_train, y_train)), columns=["sentence_id", "words", "labels"])

            classla_tokenized = []

            if not list(sentence_data.values())[0].startswith(X_tokens[test_index[0]][1]):
                split_seq = X_tokens[test_index[0]][1]
                for index in range(1,4):
                    if X_tokens[test_index[index]][2] == 'Z':
                        split_seq += X_tokens[test_index[index]][1]
                        if list(sentence_data.values())[0].endswith(split_seq):
                            break
                    else:
                        split_seq += ' ' + X_tokens[test_index[index]][1]
                        if list(sentence_data.values())[0].endswith(split_seq):
                            break
                sentence_data[list(sentence_data.keys())[0]] = (split_seq + list(sentence_data.values())[0].split(split_seq)[1]).strip()

            if not list(sentence_data.values())[-1].endswith(X_tokens[test_index[-1]][1]):
                split_seq = X_tokens[test_index[-1]][1]
                for index in range(1,4):
                    if X_tokens[test_index[-index]][2] == 'Z' or X_tokens[test_index[-index]][2].startswith('M'):
                        split_seq = X_tokens[test_index[-1-index]][1] + split_seq
                        if list(sentence_data.values())[-1].startswith(split_seq):
                            break
                    else:
                        split_seq = X_tokens[test_index[-1-index]][1] + ' ' + split_seq
                        if list(sentence_data.values())[-1].startswith(split_seq):
                            break
                sentence_data[list(sentence_data.keys())[-1]] = (list(sentence_data.values())[-1].split(split_seq)[0] + split_seq).strip()

            for sentence in sentence_data.values():
                doc = nlp(sentence)
                tokenized_sentence = []
                for word in doc.iter_words():
                    tokenized_sentence.append(word.text)
                classla_tokenized.append(tokenized_sentence)

            model = ner_model.NERModel(MODEL_TYPE[MODEL_INDEX],
                                MODEL_NAME[MODEL_INDEX],
                                use_cuda=True,
                                labels=labels_list,
                                args=args
                                )

            print('Model training for ' + str(i) + ' epochs, fold ' + str (fold_index))
            model.train_model(train_df)
            print('Model evaluation, fold ' + str(fold_index))
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
            print('MSD WER after fine-tuning for ' + str(i) + ' epochs, fold ' + str(fold_index) + ':')
            print(wer_score_msd)

            lemma_results = []
            for j in range(len(predicted_lemmas)):
                wer_score_lemma = wer.compute(predictions=predicted_lemmas[j], references=gold_lemmas)
                print(DICTIONARY_NAME[j] + ' lemmatization WER after fine-tuning for ' + str(i) + ' epochs, fold ' + str(fold_index) + ':')
                print(wer_score_lemma)
                lemma_results.append(wer_score_lemma)

            results[i].append((wer_score_msd, lemma_results))

    with open('results_untokenized_CV_' + MODEL_NAME[MODEL_INDEX].split('/')[1] + '_' + DIALECT_NAME[DIALECT]
              + '.json', 'w') as outfile:
        json.dump(results, outfile)