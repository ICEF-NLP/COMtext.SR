
import classla
from datetime import datetime
from sklearn.model_selection import KFold

from src.data_helpers.utils import get_id_to_system_info, get_untokenized_data_split
from src.helpers.eval_helper import create_results_dict, eval_msd_and_lex_lemmas
from src.helpers.lemmatizer import Lemmatizer
from src.helpers.model_helper import get_args, train_model
from src.load_data import load_corpus, load_untokenized_corpus
from src.paths import RESULTS_DIR

def load_classla( use_gpu = True):
    classla.download("sr", processors='tokenize')
    nlp = classla.Pipeline("sr", processors="tokenize", use_gpu=use_gpu)
    return nlp

def run_comtext(is_ekavica = True, model_variant = "bertic", epoch_list = [1, 2, 3, 4, 5, 10, 15, 20], num_of_splits = 10, use_cuda = True, dataset = "comtext"):
    if model_variant == "srberta" or model_variant == "pripravnik":
        is_latin = False
    else:
        is_latin = True

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    metrics_results_file = RESULTS_DIR / f'comtext_msd_metrics.tsv'
    
    df_untok = load_untokenized_corpus(dataset="comtext", is_ekavica=is_ekavica, is_latin=is_latin, columns=['sentence_order', 'text'])
    df = load_corpus(dataset="comtext", is_ekavica=is_ekavica, is_latin=is_latin, columns=['sentence_order','token', 'msd','lemma'] )
    df = df.rename(columns={
        "sentence_order": "sentence_id",
        "token": "words",
        "msd": "labels"
    })
    nlp = load_classla(use_cuda)
    id_to_system_info = get_id_to_system_info(nlp, df_untok)
    labels_list = sorted(list(set(df["labels"].unique())))

    lex_ekavica = Lemmatizer(dataset,is_ekavica=True, is_latin=is_latin)
    if not is_ekavica:
        lex_ijekavica = Lemmatizer(dataset, is_ekavica=False, is_latin=is_latin)

    args = get_args(model_variant=model_variant)

    kf = KFold(n_splits=num_of_splits)
    for num_train_epochs in epoch_list:
        args["num_train_epochs"] =  num_train_epochs
        fold_index = 0
        for train_idx, test_idx in kf.split(df):
            fold_index += 1
            train_df = df.loc[train_idx, ["sentence_id", "words", "labels"]].reset_index(drop=True)
            test_df = df.loc[test_idx, ["sentence_id", "words", "labels"]].reset_index(drop=True)
            gold_lemmas = df.loc[test_idx, "lemma"].to_list()
            gold_msd = df.loc[test_idx, "labels"].to_list()
            
            start_time = datetime.now().strftime("%d.%m.%Y___%H:%M:%S")
            print(f'****   MODEL TRAINING epoch {num_train_epochs} fold {fold_index} ****')
            trained_model = train_model(model_variant=model_variant, labels_list=labels_list, train_df=train_df, use_cuda=use_cuda, epochs=num_train_epochs)
            end_time = datetime.now().strftime("%d.%m.%Y___%H:%M:%S")
            
            untokenized_test = get_untokenized_data_split(test_df, train_df, id_to_system_info)
            
            print(f'****   MODEL EVALUATION UNTOKENIZED, fold {fold_index}   ****')
            results = create_results_dict(dataset, False, model_variant, is_ekavica, num_train_epochs, fold_index, start_time, end_time)
            eval_msd_and_lex_lemmas(metrics_results_file, results, trained_model, untokenized_test, gold_msd, gold_lemmas, lex_ekavica, lex_ijekavica if not is_ekavica else None)
        
            print(f'****   MODEL EVALUATION PRETOKENIZED, fold {fold_index}   ****')
            results = create_results_dict(dataset, True, model_variant, is_ekavica, num_train_epochs, fold_index, start_time, end_time)
            eval_msd_and_lex_lemmas(metrics_results_file, results, trained_model, test_df, gold_msd, gold_lemmas, lex_ekavica, lex_ijekavica if not is_ekavica else None)

def run_setimes(is_ekavica=True, model_variant = "bertic", epoch_list = [1, 2, 3, 4, 5, 10, 15, 20], num_of_splits = 10, use_cuda = True):
    if model_variant == "srberta" or model_variant == "pripravnik":
        is_latin = False
    else:
        is_latin = True

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    metrics_results_file = RESULTS_DIR / f'setimes_msd_metrics.tsv'

    train_df = load_corpus(dataset="setimes", is_ekavica=is_ekavica, is_latin=is_latin, columns=['sentence_order', 'token', 'lemma', 'msd'])
    train_df = train_df.rename(columns={
        "sentence_order": "sentence_id",
        "token": "words",
        "msd": "labels"
    })

    test_df_untok = load_untokenized_corpus(dataset="comtext", is_ekavica=is_ekavica, is_latin=is_latin, columns=['sentence_order', 'text'])
    test_df = load_corpus(dataset="comtext", is_ekavica=is_ekavica, is_latin=is_latin, columns=['token', 'msd','lemma'] )
    test_df = test_df.rename(columns={
        "sentence_order": "sentence_id",
        "token": "words",
        "msd": "labels"
    })
    nlp = load_classla(is_ekavica, use_cuda)
    untokenized_test_data = []
    for _, row in test_df_untok.iterrows():
        doc = nlp(row['text'])
        for sentence in doc.sentences:
            tokens = [word.text for word in sentence.words]
            untokenized_test_data.append(tokens)

    labels_list = sorted(list(set(train_df["labels"].unique()) | set(test_df["labels"].unique())))
    lex_ekavica = Lemmatizer(dataset = "comtext",is_ekavica=True, is_latin=is_latin)
    if not is_ekavica:
        lex_ijekavica = Lemmatizer(dataset = "comtext", is_ekavica=False, is_latin=is_latin)

    args = get_args(model_variant=model_variant)
    for num_train_epochs in epoch_list:
        args["num_train_epochs"] =  num_train_epochs
        
        start_time = datetime.now().strftime("%d.%m.%Y___%H:%M:%S")
        print(f'****   MODEL TRAINING epoch {num_train_epochs}  ****')
        trained_model = train_model(model_variant=model_variant, labels_list=labels_list, train_df=train_df, use_cuda=use_cuda, epochs=num_train_epochs)
        end_time = datetime.now().strftime("%d.%m.%Y___%H:%M:%S")

        gold_lemmas = test_df['lemma'].to_list()
        gold_msd = test_df['labels'].to_list()

        print(f'****   MODEL EVALUATION UNTOKENIZED   ****')
        results = create_results_dict("setimes", False, model_variant, is_ekavica, num_train_epochs, -1, start_time, end_time)
        eval_msd_and_lex_lemmas(metrics_results_file, results, trained_model, untokenized_test_data, gold_msd, gold_lemmas, lex_ekavica, lex_ijekavica if not is_ekavica else None)

        print(f'****   MODEL EVALUATION PRETOKENIZED   ****')
        results = create_results_dict("setimes", True, model_variant, is_ekavica, num_train_epochs, -1, start_time, end_time)
        eval_msd_and_lex_lemmas(metrics_results_file, results, trained_model, test_df, gold_msd, gold_lemmas, lex_ekavica, lex_ijekavica if not is_ekavica else None)


if __name__ == "__main__":
    run_comtext()