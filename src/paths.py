from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
CODE_DIR = PROJECT_ROOT / "src"
RESULTS_DIR = PROJECT_ROOT / "results"
DATA_DIR = PROJECT_ROOT / "data"

srlex_path = DATA_DIR / "srLex_v1.3"
hrlex_path = DATA_DIR / "hrLex_v1.3"

setimes_path = DATA_DIR / "set.sr.plus.conllup"
ekavica_path = DATA_DIR / "comtext.sr.legal.ekavica.conllu"
ijekavica_path = DATA_DIR / "omtext.sr.legal.ekavica.conllu"

def get_dataset_filepath (dataset = "comtext", is_ekavica:bool=True):
    filepath = None
    if dataset == "comtext":
        if is_ekavica:
            filepath = ekavica_path
        else:
            filepath = ijekavica_path
    elif dataset == "setimes":
        filepath = setimes_path
    return filepath