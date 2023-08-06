import random

import pandas as pd
import openprompt
import os
import torch
import wandb
import yaml

from argparse import ArgumentParser
from sklearn.metrics import accuracy_score
from openprompt.prompts import ManualTemplate, ManualVerbalizer
from openprompt import PromptForClassification, PromptDataLoader
from openprompt.plms import load_plm
from openprompt.data_utils import InputExample
from pathlib import Path
from sklearn.metrics import accuracy_score, f1_score
from transformers import AdamW, get_linear_schedule_with_warmup, GPTJForCausalLM
from transformers import BertTokenizer, BertModel, T5Tokenizer, T5Model, AutoTokenizer, AutoModelForCausalLM
from transformers import DebertaModel, DebertaTokenizer, GPT2Tokenizer, GPT2Model, GPT2LMHeadModel, DebertaForSequenceClassification
from transformers import OPTConfig, OPTModel, BertForSequenceClassification, AutoModelWithLMHead, LlamaTokenizer
from torch.nn import CrossEntropyLoss

use_cuda = torch.cuda.is_available()
root_path = Path(__file__).parent
if use_cuda:
    print("-.-.-.- using cuda -.-.-.-.-")
else:
    print("-.-..-. using cpu -.-.-.-.-..")
def load_config():
    """
    Load the configuration of the experiment and the model
    :return: a dictionary containing the configuration of the experiments
    """

    conf_path = Path(root_path, "conf.yaml")
    with open(conf_path) as file:
        config = yaml.safe_load(file)
        return config

def parse_args():
    """
    Parse the arguments of the scripts
    :return:
    """
    parser = ArgumentParser()
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--test", action="store_true")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--wandb", action="store_true")
    parser.add_argument("--fine-tune", action="store_true")
    return parser.parse_args()

def init_wandb(offline=False, params=None):
    if offline:
        os.environ['WANDB_MODE'] = 'offline'

    wandb.login(relogin=True)
    if "few-shot-size" in params:
        wandb.init(project=f"few-shot-stance-cls-{params['few-shot-size']}", config=params, name=f"{params['model-name']}-batch-size-{params['batch-size']}-learning-rate-{params['learning-rate']}")
    else:
        wandb.init(project=f"few-shot-stance-cls", config=params, name=f"{params['model-name']}-batch-size-{params['batch-size']}-learning-rate-{params['learning-rate']}")

def save_splits():
    """
    Save the splits of the experiments by sampling a validation set from the training set with exclusive topic sets
    :return:
    """
    conf = load_config()

    path_source = Path(root_path, conf["dataset"]["path-root"])
    path_training = Path(root_path, conf["experiment"]["path-training"])
    path_validation = Path(root_path, conf["experiment"]["path-validation"])
    path_test = Path(root_path, conf["experiment"]["path-test"])

    df_arguments = pd.read_csv(path_source, sep=",", encoding="utf-8")
    df_training = df_arguments[df_arguments["split"] == "train"]
    df_test = df_arguments[df_arguments["split"] == "test"]
    training_topics = df_training["topicTarget"].sample(12).unique()
    training_topics = training_topics[:10]
    df_sampled_training = df_training[df_training["topicTarget"].isin(training_topics)]

    df_validation = df_training[~df_training["topicTarget"].isin(training_topics)]
    print(df_validation.shape[0])
    df_sampled_training.to_csv(path_training, sep=",", encoding="utf-8", index=False)
    df_validation.to_csv(path_validation, sep=",", encoding="utf-8", index=False)
    df_test.to_csv(path_test, sep=",", encoding="utf-8", index=False)


def oversample_dataset(df):
    pro_claims = df[df["claims.stance"]=="PRO"]
    con_claims = df[df["claims.stance"]=="CON"]
    count_of_con_to_sample = pro_claims.shape[0] - con_claims.shape[0]

    con_claims_to_add = con_claims.sample(count_of_con_to_sample)
    return pd.concat([df, con_claims_to_add])

def load_splits(oversample=True):
    """
    Load the splits of the experiments and return it in a dictionary of pandas dataframes
    :return: a dictionary containing the training, validation, and test splits
    """

    conf = load_config()
    path_training = Path(root_path, conf["experiment"]["path-training"]).resolve()
    path_validation = Path(root_path, conf["experiment"]["path-validation"]).resolve()
    path_test = Path(root_path, conf["experiment"]["path-test"])
    if not os.path.exists(path_validation):
        save_splits()
    df_training = pd.read_csv(path_training, sep=",", encoding="utf-8")
    df_validation = pd.read_csv(path_validation, sep=",", encoding="utf-8")
    df_test = pd.read_csv(path_test, sep=",", encoding="utf-8")
    dataset = {"training": df_training, "validation": df_validation, "test": df_test}
    if oversample:
        dataset["training"] = oversample_dataset(dataset["training"])
    print(dataset["validation"]["claims.stance"].value_counts())
    return dataset




def convert_to_prompt_splits(dataset, params, sample=True):
    """
    Conver the pandas dataframes to splits as specified by the openprompt api
    :param dataset: a dictionary containing the trianing, validation, and test dataframes
    :return: a dictionary containing lists of input examples as specified by the openprompt api
    """
    labels_map = {"PRO": 1, "CON": 0}
    prompt_splits = {}

    prompt_splits["test"] = []
    prompt_splits["training"] = []
    prompt_splits["validation"] = []
    for key in dataset.keys():
        if key == "training" and sample:
                dataset["training"] = sample_few_shots(dataset["training"], params["few-shot-size"])
        for i,record in dataset[key].iterrows():
            prompt_splits[key].append(InputExample(guid= i , text_a = record["claims.claimCorrectedText"], text_b = record["topicTarget"], label = labels_map[record["claims.stance"]]))
    return prompt_splits

def sample_few_shots(df_training, size, filter = None, sort_criterion = None):
    """
    Sample few shots from the training dataframe. The few shots can be filtered by using a specific boolean functions and sorted
    :param df_training: a dataframe containing the whole training split
    :param size: the size of the few shots to use for training
    :param filter: a boolean function that takes a record of the trianing split and decided whether to include or not
    :param sort_criteria: a dicionary specifing the name of the column and the sorting order used to sort the few shot examples
    :return: a dataframe containing the sampled few shots
    """
    df_sample = df_training.sample(n=size)
    return df_sample


def get_few_shot_params():
    """
    Load the few shot params to train  the model
    :return: a dictionary containing the params for the few shot model
    """
    config = load_config()
    return config["few-shot-params"]


def get_baseline_params():
    pass

def save_pre_trained_model():
    """
    Saving pretrained model to use huggingface transformers without internet
    """
    config = load_config()
    config = config["pre-trained-models"]
    path = Path(config["path"])
    bert_path = os.path.join(path,"bert-base-uncased")
    if not os.path.exists(bert_path):
        bert = BertForSequenceClassification.from_pretrained('bert-base-uncased')
        berttokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        bert.save_pretrained(bert_path)
        berttokenizer.save_pretrained(bert_path)

    t5_path = os.path.join(path, "t5-base")
    if not os.path.exists(t5_path):
        t5tokenizer = T5Tokenizer.from_pretrained("t5-base")
        t5model = T5Model.from_pretrained("t5-base")
        t5model.save_pretrained(t5_path)
        t5tokenizer.save_pretrained(t5_path)

    gpt_2_path = os.path.join(path, "gpt2-xl")
    if not os.path.exists(gpt_2_path):
        gpt_2_tokenizer = GPT2Tokenizer.from_pretrained('gpt2-xl')
        gpt_2_model = GPT2Model.from_pretrained('gpt2-xl')
        gpt_2_model.save_pretrained(gpt_2_path)
        gpt_2_tokenizer.save_pretrained(gpt_2_path)

    opt_path = os.path.join(path, "opt")
    if not os.path.exists(opt_path):
        opt_tokenizer = AutoTokenizer.from_pretrained('facebook/opt-350m')
        opt_model = OPTModel.from_pretrained('facebook/opt-350m')
        opt_model.save_pretrained(opt_path)
        opt_tokenizer.save_pretrained(opt_path)

    deberta_path = os.path.join(path, "microsoft/deberta-base")
    if not os.path.exists(deberta_path):
        deberta_tokenizer = DebertaTokenizer.from_pretrained("microsoft/deberta-base")
        deberta_model = DebertaForSequenceClassification.from_pretrained("microsoft/deberta-base")
        deberta_tokenizer.save_pretrained(deberta_path)
        deberta_model.save_pretrained(deberta_path)
    alpaca_path  = os.path.join(path, "wxjiao/alpaca-7b")

    if not os.path.exists(alpaca_path):
        alpaca_tokenizer = LlamaTokenizer.from_pretrained("wxjiao/alpaca-7b")
        alpaca_model = AutoModelForCausalLM.from_pretrained("wxjiao/alpaca-7b")
        alpaca_tokenizer.save_pretrained(alpaca_path)
        alpaca_model.save_pretrained(alpaca_path)

def create_few_shot_model(params, offline=True):
    """
    Prepare an openprompt model based on the configuration
    :param config: a dictionary specifing the name and type of the model
    :return: an openprompt modle, a wrapper class, a tokenizer, and a template
    """
    model_name = params["model-name"]

    if offline:
        model_type = Path( params["model-path"])
    else:
        model_type = params["model-type"]

    classes = ["CON", "PRO"]
    plm, tokenizer, model_config, WrapperClass = load_plm(model_name, model_type)

    promptTemplate = ManualTemplate(
        text = '{"placeholder":"text_a"} is {"mask"} the topic {"placeholder":"text_b"}',
        tokenizer = tokenizer,
    )
    promptVerbalizer = ManualVerbalizer(
        classes = classes,
        label_words = {
            "CON": ["against", "contra"],
            "PRO": ["for", "pro"],
        },
        tokenizer = tokenizer,
    )
    promptModel = PromptForClassification(template = promptTemplate, plm=plm, verbalizer=promptVerbalizer, freeze_plm=False)
    if use_cuda:
        promptModel = promptModel.cuda()
    return promptModel, WrapperClass, tokenizer, promptTemplate


def run_experiment_no_fune_tuning(params=None, offline=False, validate=True, splits=None):


    save_pre_trained_model()
    few_shot_size = params["few-shot-size"]
    labels_text_map = {"PRO": ["supports", "is pro", "is positive to"], "CON": ["attacks", "is con", "is negative to", "is against", "is contra to"]}
    labels_map = {"PRO": 1, "CON":0}

    if offline:
        model_name = params["model-path"]
    else:
        model_name = params["model-name"]
    print(f"loading from {model_name}")

    tokenizer = AutoTokenizer.from_pretrained(model_name)

    model = AutoModelWithLMHead.from_pretrained(model_name)


    if not splits:
        splits = load_splits()
        training_dataset = splits["training"].sample(few_shot_size)
    else:
        training_dataset = splits["training"]

    if validate:
        test_dataset = splits["validation"]
    else:
        test_dataset = splits["test"]

    prompt = "Given are the following examples:\n"

    for i, record in training_dataset.iterrows():
        sentence = record["claims.claimCorrectedText"]
        topic = record["topicText"]
        stance = record["claims.stance"]
        label = labels_text_map[stance]
        idx = random.randint(0,len(label)-1)
        stance_text = label[idx]
        print(f"{stance} --> {stance_text}")
        template = f"While debating the topic {topic} the argument {sentence} was raised which {stance} the topic.\n"
        prompt = prompt + template
    predictions = []
    #test_dataset = test_dataset.sample(10)
    labels = []
    for i, record in test_dataset.iterrows():
        sentence = record["claims.claimCorrectedText"]
        topic = record["topicText"]
        label = record["claims.stance"]
        template_no_stance = f"While debating the topic {topic} the argument {sentence} was raised which."
        prompt_to_predict = prompt + template_no_stance
        seq = tokenizer.encode(prompt_to_predict, return_tensors="pt")
        generated = model.generate(seq, max_new_tokens=3, do_sample=True)

        resulting_string = tokenizer.decode(generated.tolist()[0])

        if "pro" in resulting_string[-15:].lower() or "supports" in resulting_string[-15:].lower() or "positive" in resulting_string[-15:].lower():
            predictions.append(1)
        else:
            predictions.append(0)

        labels.append(labels_map[label])
    print("labels")
    print(labels)
    print("predictions")
    print(predictions)
    accuracy = accuracy_score(labels, predictions)
    pro_f1 = f1_score(labels, predictions,average='binary', pos_label=1)
    con_f1 = f1_score(labels, predictions,average='binary', pos_label=0)
    macro_f1 = f1_score(labels, predictions, average="macro")

    return accuracy, pro_f1, con_f1, macro_f1



def run_experiment_fewshot(params=None, offline=False, validate=True, splits=None):
    """
    Run a validation experiment or a test experiment
    :param validate: a boolean flag specifying whether to run a validation or  test experiment
    :return:
    """
    if offline:
        save_pre_trained_model()
    batch_size = params["batch-size"]
    lr = params["learning-rate"]
    epochs_num = params["epochs"]
    if not splits:
        splits = load_splits()
        prompt_dataset = convert_to_prompt_splits(splits, params)
    else:
        prompt_dataset = convert_to_prompt_splits(splits, params, sample=False)

    promptModel, WrapperClass, tokenizer, promptTemplate = create_few_shot_model(params, offline)


    train_data_loader = PromptDataLoader(dataset = prompt_dataset["training"], tokenizer=tokenizer, template=promptTemplate,
        tokenizer_wrapper_class=WrapperClass, batch_size=batch_size, truncate_method="head", max_seq_length=256, decoder_max_length=3)
    if validate:
        experiment_type = "validate"
        test_data_loader = PromptDataLoader(dataset = prompt_dataset["validation"], tokenizer = tokenizer, template = promptTemplate,
            tokenizer_wrapper_class=WrapperClass, batch_size=batch_size, truncate_method="head", max_seq_length=256, decoder_max_length=3)
    else:
        experiment_type = "test"
        test_data_loader = PromptDataLoader(dataset = prompt_dataset["test"], tokenizer = tokenizer, template = promptTemplate,
            tokenizer_wrapper_class=WrapperClass, batch_size=batch_size, truncate_method="head", max_seq_length=256, decoder_max_length=3)

    loss_func = CrossEntropyLoss()
    no_decay = ['bias', 'LayerNorm.weight']
    optimizer_grouped_parameters = [
        {'params': [p for n, p in promptModel.named_parameters() if not any(nd in n for nd in no_decay)]},
        {'params': [p for n, p in promptModel.named_parameters() if any(nd in n for nd in no_decay)]}
    ]

    optimizer = AdamW(optimizer_grouped_parameters, lr=float(lr))
    metrics = {}
    for epoch in range(epochs_num):
        tot_loss = 0
        for step, inputs in enumerate(train_data_loader):
            if use_cuda:
                inputs = inputs.cuda()
            promptModel.train()
            logits = promptModel(inputs)
            labels = inputs["label"]
            loss = loss_func(logits, labels)
            loss.backward()
            tot_loss += loss.item()
            optimizer.step()
            optimizer.zero_grad()
            if step % 100 == 1:
                print("Epoch {}, average loss: {}".format(epoch, tot_loss/(step+1)), flush=True)
            metrics["train/loss"] = tot_loss/(step+1)

            wandb.log(metrics)

        promptModel.eval()
        test_loss = 0
        all_test_labels = []
        all_test_preds = []
        for step, test_inputs in enumerate(test_data_loader):
            if use_cuda:
                test_inputs = test_inputs.cuda()
            test_logits = promptModel(test_inputs)
            test_labels = test_inputs["label"]
            all_test_labels.extend(test_labels.cpu().tolist())
            all_test_preds.extend(torch.argmax(test_logits, dim = -1).cpu().tolist())
            loss = loss_func(test_logits, test_labels)
            test_loss += loss.item()
            metrics[f"{experiment_type}/loss"] = test_loss/(step+1)
            wandb.log(metrics)
        metrics[f"{experiment_type}/accuracy"] = accuracy_score(all_test_labels, all_test_preds)
        wandb.log(metrics)
    metrics["score"] = metrics[f"{experiment_type}/accuracy"]
    wandb.log(metrics)
    return metrics["score"]

if __name__ == "__main__":
    args = parse_args()
    fine_tune = args.fine_tune
    if args.offline:
        offline = True
    else:
        offline = False
    params = get_few_shot_params()
    wandb = args.wandb
    if wandb:
        if offline:
            init_wandb(offline=True, params=params)
        else:
            init_wandb(offline=False, params=params)

    if args.validate:
        if fine_tune:
            run_experiment_fewshot(params=params, offline=offline, validate=True)
        else:
            run_experiment_no_fune_tuning(params=params, offline=offline, validate=True)

    if args.test:
        if fine_tune:
            run_experiment_fewshot(params=params, offline=offline, validate=False)
        else:
            run_experiment_no_fune_tuning(params=params, offline=offline, validate=False)
