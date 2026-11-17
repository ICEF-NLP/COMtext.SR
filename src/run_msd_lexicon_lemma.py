import argparse

from src.environment import set_seed
from src.helpers.model_helper import MODELS
from src.experiment_code.msd_lexicon_lemmas import run_comtext, run_setimes

def parse_cmd_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset", "-d", 
        required=False, 
        choices=["comtext", "setimes"], 
        help="Select the dataset to use: 'comtext' or 'setimes'.",
        default = "comtext"
    )
    parser.add_argument(
        "--is_ekavica", "-e", 
        required=False, 
        choices=["true", "false"], 
        help="Select the dialect: 'true' for ekavica, 'false' for ijekavica.",
        default= "true"
    )
    parser.add_argument(
        "--model_variant", "-m", 
        required=True, 
        choices=MODELS.keys(), 
        help=f"Select the model variant: {', '.join(MODELS.keys())}.",
        default= "bertic"
    )
    args = parser.parse_args()
    if args.is_ekavica == "true":
        args.is_ekavica = True
    else:
        args.is_ekavica = False
    return args

def main(args):
    if args.dataset == "comtext":
        run_comtext(is_ekavica=args.is_ekavica, model_variant=args.model_variant)
    else:
        run_setimes(is_ekavica=args.is_ekavica, model_variant=args.model_variant)

if __name__ == "__main__":
    set_seed()
    args = parse_cmd_line_args()
    main(args)

    ##alternate way to run the script without command line arguments:
    #set_seed()
    #run_comtext(is_ekavica=True, model_variant="bertic")
    #or
    #run_setimes(is_ekavica=False, model_variant="pripravnik")