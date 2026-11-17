from evaluate import load
import pathlib
import pandas as pd

def eval_lemma_transform(results_file, results, model, test_data, gold_transform):
    if results["pretokenized"]  == True:
        test_data = test_data.groupby("sentence_id", sort=False)["words"].apply(list).tolist()

    predictions, _ = model.predict(test_data, split_on_space=False)
    transform_pred_list = [list(d.values())[0] for sentence in predictions for d in sentence]
    wer_transform = load("wer")
    predictions_str = " ".join(transform_pred_list)
    gold_str = " ".join(gold_transform)
    lemma_transform_wer = wer_transform.compute(predictions=[predictions_str], references=[gold_str])
    results['lemma_trans_wer'] = lemma_transform_wer
    df_row = pd.DataFrame.from_dict([results])
    if pathlib.Path(results_file).exists():
        df_row.to_csv(results_file, mode='a', header=False, index=False, sep='\t', encoding='utf-8')
    else:
        df_row.to_csv(results_file, mode='w', header=True, index=False, sep='\t', encoding='utf-8')



def eval_msd_and_lex_lemmas(results_file, results, model, test_data, gold_msd, gold_lemmas, lex_ekavica, lex_ijekavica):
    if results['pretokenized'] == True:
        test_data = test_data.groupby("sentence_id", sort=False)["words"].apply(list).tolist()

    predictions, _ = model.predict(test_data, split_on_space=False)
    msd_preds_list = [list(d.values())[0] for sent in predictions for d in sent]
    word_list = [w for sentence in test_data for w in sentence]

    msd_wer = load("wer").compute(predictions=[" ".join(msd_preds_list)], references=[" ".join(gold_msd)])
    results['msd_wer'] = msd_wer

    is_ekavica = True if results['dialect'] == "ekavica" else False
    pred_lemma_eka = []
    pred_lemma_ije = []
    for msd_pred, word in zip(msd_preds_list, word_list):
        lemma_eka = lex_ekavica.get_lemma(word, msd_pred)
        pred_lemma_eka.append(lemma_eka)
        if not is_ekavica:
            lemma_ije = lex_ijekavica.get_lemma(word, msd_pred)
            pred_lemma_ije.append(lemma_ije)

    eval_lex_lemmas(results_file, pred_lemma_eka, gold_lemmas, results, is_srlex=True)
    if not is_ekavica:
        eval_lex_lemmas(results_file, pred_lemma_ije, gold_lemmas, results, is_srlex=False)


def eval_lex_lemmas(results_file, pred_lemmas, gold_lemmas, results, is_srlex= True):
    lemma_wer = load("wer")
    prediction_string = " ".join(pred_lemmas)
    gold_string = " ".join(gold_lemmas)
    lemma_results = lemma_wer.compute(predictions=[prediction_string], references=[gold_string])
    results['dictionary'] = "srLex" if is_srlex else "hrLex"
    results['lemma_wer'] = lemma_results
    df_row = pd.DataFrame.from_dict([results])
    if pathlib.Path(results_file).exists():
        df_row.to_csv(results_file, mode='a', header=False, index=False, sep='\t', encoding='utf-8')
    else:
        df_row.to_csv(results_file, mode='w', header=True, index=False, sep='\t', encoding='utf-8')



def create_results_dict(dataset, pretokenized, model_variant, is_ekavica, num_train_epochs, fold_index, start_time, end_time):
    results = {
        "dataset": dataset,
        "pretokenized": pretokenized,
        "model": model_variant,
        "dialect": "ekavica" if is_ekavica else "ijekavica",
        "epoch": num_train_epochs,
        "fold": fold_index,
        'start_time': start_time,
        'end_time': end_time
    }
    return results