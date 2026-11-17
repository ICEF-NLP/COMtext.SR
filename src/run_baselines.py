import argparse

from src.environment import set_seed, fix_certifi_ssl_context

def run_specific_classla(is_ekavica, use_serbian_classla, tokenization, use_gpu=True):
    if tokenization == "pretokenized":
        from src.experiment_code.classla import run_classla_pretokenized
        run_classla_pretokenized(is_ekavica=is_ekavica, use_serbian_classla=use_serbian_classla, use_gpu=use_gpu)
    elif tokenization == "untokenized":
        from src.experiment_code.classla import run_classla_untokenized
        run_classla_untokenized(is_ekavica=is_ekavica, use_serbian_classla=use_serbian_classla, use_gpu=use_gpu)

def run_specific_trankit(is_ekavica, use_serbian_trankit, tokenization, use_gpu=True):
    if tokenization == "pretokenized":
        from src.experiment_code.trankit import run_trankit_pretokenized
        run_trankit_pretokenized(is_ekavica=is_ekavica, use_serbian_trankit=use_serbian_trankit, use_gpu=use_gpu)
    elif tokenization == "untokenized":
        from src.experiment_code.trankit import run_trankit_untokenized
        run_trankit_untokenized(is_ekavica=is_ekavica, use_serbian_trankit=use_serbian_trankit, use_gpu=use_gpu)

def parse_cmd_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--baseline", "-b", 
        required=True, 
        choices=["classla", "trankit", "all"], 
        help="Select the baseline model to use: 'classla' or 'trankit'.",
        default = "classla"
    )
    parser.add_argument(
        "--is_ekavica", "-e", 
        required=False, 
        choices=["true", "false", "all"], 
        help="Select the dialect: 'true' for ekavica, 'false' for ijekavica.",
        default= "all"
    )
    parser.add_argument(
        "--tokenization", "-t", 
        required=False, 
        choices=["pretokenized", "untokenized", "all"], 
        help="Select the tokenization method: 'pretokenized' or 'untokenized'.",
        default= "all"
    )
    parser.add_argument(
        "--baseline_language", "-l", 
        required=False, 
        choices=["sr", "hr", "all"], 
        help="Select the language: 'sr' for Serbian, 'hr' for Croatian.",
        default= "sr"
    )
    args = parser.parse_args()
    if args.baseline == "all":
        args.baseline = ["classla", "trankit"]
    else:
        args.baseline = [args.baseline]

    if args.is_ekavica == "all":
        args.is_ekavica = [True, False]
    elif args.is_ekavica == "true":
        args.is_ekavica = [True]
    else:
        args.is_ekavica = [False]

    if args.tokenization == "all":
        args.tokenization = ["pretokenized", "untokenized"]
    else:
        args.tokenization = [args.tokenization]

    if args.baseline_language == "all":
        args.baseline_language = [True, False]
    elif args.baseline_language == "sr":
        args.baseline_language = [True]
    else:
        args.baseline_language = [False]

    return args

def main(args):
    for is_ekavica in args.is_ekavica:
        for use_serbian_classla in args.baseline_language:
            if not use_serbian_classla and is_ekavica:
                print("Skipping Croatian baseline for ekavica, as it is not applicable.")
                continue
            for tokenization in args.tokenization:
                for baseline in args.baseline:
                    if baseline == "classla":
                        run_specific_classla(is_ekavica, use_serbian_classla, tokenization, use_gpu=True)
                    elif baseline == "trankit":
                        run_specific_trankit(is_ekavica, use_serbian_classla, tokenization, use_gpu=True)

if __name__ == "__main__":
    #fix_certifi_ssl_context()
    set_seed()
    args = parse_cmd_line_args()
    main(args)

    #alternate way to run the script without command line arguments:
    #fix_certifi_ssl_context()
    #set_seed()
    #run_specific_classla(is_ekavica=True, use_serbian_classla=True, tokenization="pretokenized", use_gpu=True)
    #run_specific_trankit(is_ekavica=False, use_serbian_trankit=False, tokenization="untokenized", use_gpu=True)