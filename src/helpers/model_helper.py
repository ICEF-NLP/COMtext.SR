from simpletransformers.ner import NERModel

from src.constants import RANDOM_SEED

MODELS = {
    "bertic" : {
        "model_name": "classla/bcms-bertic",
        "model_type": "electra",
    },
    "srberta": {
        "model_name": "jelenaTosic/SrBERTa",
        "model_type": "roberta",
    },
    "pripravnik":{
        "model_name": "procesaur/pripravnik157",
        "model_type": "auto"
    },
    "mBerticLarge": {
        "model_name": "permitt/galton-modernbertic-large",
        "model_type": "auto",
    },
    "mBerticBase": {
        "model_name": "permitt/galton-modernbertic-base",
        "model_type": "auto",
    }
}

def get_model_name_and_type(model = "bertic"):
    model_dict = MODELS.get(model, {})
    if model_dict == {}:
        print(f"Model doesnt exist, model name input: {model}, returning bertic as default ")
        model_dict = MODELS.get("bertic", {})
    model_name = model_dict.get("model_name", "None")
    model_type = model_dict.get("model_type", "None")
    return model_name, model_type

def get_args(model_variant = "bertic"):
    args = {}
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
    args['train_batch_size'] = 8
    args['no_save'] = True
    if model_variant == "mBerticLarge":
        args['fp16'] = True
    return args

def fix_pripravnik_tokenizer(model, model_variant):
    if model_variant == "pripravnik":
        model.tokenizer.cls_token = "<s>"
        model.tokenizer.sep_token = "</s>"
        model.tokenizer.unk_token = "<unk>"
        model.tokenizer.bos_token = "<s>"
        model.tokenizer.eos_token = "</s>"
        model.tokenizer.pad_token = "<pad>"


def train_model(model_variant:str = "bertic", labels_list:list = [], train_df= None, use_cuda:bool = True, epochs:int=1):
    model_name, model_type = get_model_name_and_type(model_variant)
    args = get_args(model_variant=model_variant)
    args["num_train_epochs"] = epochs

    model = NERModel(model_type, model_name, labels_list, use_cuda = use_cuda, args = args)
    fix_pripravnik_tokenizer(model, model_variant)
    model.train_model(train_df)
    return model