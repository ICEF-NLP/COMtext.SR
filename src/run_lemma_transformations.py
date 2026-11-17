import argparse

from src.environment import set_seed
from src.experiment_code.lemma_transformations import run_comtext
from src.helpers.model_helper import MODELS

def parse_cmd_line_args():
    parser = argparse.ArgumentParser()
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

if __name__ == "__main__":
    set_seed()
    args = parse_cmd_line_args()
    run_comtext(is_ekavica=args.is_ekavica, model_variant=args.model_variant)
