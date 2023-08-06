import numpy as np
import torch
import random

from debater_python_api.api.debater_api import DebaterApi
from random import randint

from sklearn.metrics import f1_score
from torch import nn
from torch.utils.data import DataLoader
from transformers import BertTokenizer, DebertaForSequenceClassification, AutoModelForSequenceClassification,\
    BertForSequenceClassification, DebertaTokenizer
from few_shot_priming.few_shot_stance import *

class Dataset(torch.utils.data.Dataset):
    def __init__(self,df, labels, path=None, model='bert-base-cased'):
        if path:
            tokenizer= AutoTokenizer.from_pretrained(path)
        else:
            tokenizer = AutoTokenizer.from_pretrained(model)
        self.labels = [labels[label] for label in df["claims.stance"]]
        self.texts = tokenizer(list(df["topicText"].values), list(df['claims.claimCorrectedText'].values), padding=True
                               , truncation=True, return_tensors="pt")
        print(f"size of labels {len(self.labels)} and size of texts is {len(self.texts)}")

    def classes(self):
        return self.labels

    def __len__(self):
        return len(self.labels)

    def get_batch_labels(self, idx):
        return np.array(self.labels[idx])

    def get_batch_texts(self, idx):
        return {"input_ids":self.texts["input_ids"][idx],"attention_mask": self.texts["attention_mask"][idx]}

    def __getitem__(self, idx):
        batch_texts = self.get_batch_texts(idx)
        batch_y = self.get_batch_labels(idx)
        return batch_texts, batch_y


class DeBERTaClassifier(nn.Module):
    def __init__(self, hyperparameters, path=None):
        super(DeBERTaClassifier, self).__init__()
        self.lr = hyperparameters["learning-rate"]
        self.batch_size = hyperparameters["batch-size"]
        if path:
            self.deberta = AutoModelForSequenceClassification.from_pretrained(path)
        else:
            self.deberta = AutoModelForSequenceClassification.from_pretrained('microsoft/deberta-base')
        self.labels = {"CON": 0, "PRO":1}

    def forward(self, input_ids, mask):
        pooled_output = self.deberta(input_ids=input_ids,  return_dict=False)

        return pooled_output

class BertClassifier(nn.Module):
    def __init__(self, hyperparameters, path=None):
        super(BertClassifier, self).__init__()
        self.lr = hyperparameters["learning-rate"]
        self.batch_size = hyperparameters["batch-size"]
        if path:
            self.bert = AutoModelForSequenceClassification.from_pretrained(path)
        else:
            self.bert = AutoModelForSequenceClassification.from_pretrained('bert-base-cased')
        self.labels = {"CON": 0, "PRO":1}


    def forward(self, input_ids, mask):
        pooled_output = self.bert(input_ids=input_ids, attention_mask=mask, return_dict=False)
        return pooled_output


def get_baseline_params():
    config = load_config()
    print(config)
    return config["baseline-params"]


def parse_args():
    """
    Parse the arguments of the scripts
    :return:
    """
    parser = ArgumentParser()
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--test", action="store_true")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--random", action="store_true")
    parser.add_argument("--majority", action="store_true")
    parser.add_argument("--ibm-api", action="store_true")
    return parser.parse_args()

def run_finetuning_experiment_baseline(params=None, offline=True, validate=False):
    splits = load_splits()
    use_cuda = torch.cuda.is_available()

    if use_cuda:
        print("-.-.-.- using cuda -.-.-.-.-")
    else:
        print("-.-..-. using cpu -.-.-.-.-..")

    path = None
    if offline:
        save_pre_trained_model()
        path = params["model-path"]
    model_name = params["model-name"]

    if not params:
        params = get_baseline_params()
    else:
        print("params are input online")

    train_dataset = Dataset(splits["training"], {"PRO": 1, "CON": 0}, path=path, model=model_name)
    if validate:
        experiment_type = "validate"
        test_dataset = Dataset(splits["validation"], {"PRO": 1, "CON": 0}, path=path, model=model_name)
    else:
        experiment_type = "test"
        test_dataset = Dataset(splits["test"], {"PRO": 1, "CON": 0}, path=path, model=model_name)

    train_dataloader = DataLoader(train_dataset, batch_size=params["batch-size"], shuffle=True)
    test_dataloader = DataLoader(test_dataset, batch_size=params["batch-size"], shuffle=True)
    eval_dataloader = DataLoader(test_dataset, batch_size=1, shuffle=False)

    device = torch.device("cuda" if use_cuda else "cpu")

    if model_name.startswith("bert"):
        model = BertClassifier(params, path=path)
    else:
        model = DeBERTaClassifier(params, path=path)

    if use_cuda:
        model = model.cuda()
        print(f"{model_name} is on cuda")
    optimizer = AdamW(model.parameters(), lr=float(params["learning-rate"]))
    epochs = params["epochs"]
    criterion = nn.CrossEntropyLoss().cuda()


    model.train()
    metrics = {}
    for epoch in range(epochs):
        train_loss = 0
        all_test_labels = []
        all_test_preds = []
        model.train()
        for step, (train_input, train_label) in enumerate(train_dataloader):
            train_label = train_label.to(device)
            mask = train_input["attention_mask"].to(device)
            input_ids = train_input["input_ids"].to(device)
            output = model(input_ids, mask)
            batch_loss = criterion(output[0], train_label)
            train_loss += batch_loss.item()
            batch_loss.backward()
            optimizer.step()
            optimizer.zero_grad()
            metrics["train/loss"] = train_loss / (step +1)
            wandb.log(metrics)
        test_loss = 0
        model.eval()
        for step, (test_input, test_labels) in enumerate(test_dataloader):
            test_labels = test_labels.to(device)
            mask = test_input["attention_mask"].to(device)
            input_ids = test_input["input_ids"].to(device)
            output = model(input_ids, mask)
            batch_loss = criterion(output[0], test_labels)
            test_loss += batch_loss.item()
            metrics[f"{experiment_type}/loss"] = test_loss / (step+1)
            wandb.log(metrics)
    for step, (test_input, test_labels) in enumerate(eval_dataloader):
        test_labels = test_labels.to(device)
        mask = test_input["attention_mask"].to(device)
        input_ids = test_input["input_ids"].to(device)
        output = model(input_ids, mask)
        predictions = torch.argmax(output[0],dim=1)
        all_test_preds.extend(predictions.cpu())
        all_test_labels.extend(test_labels.cpu().tolist())

    test_accuracy = accuracy_score(all_test_labels, all_test_preds)
    pro_f1 = f1_score(all_test_labels, all_test_preds,average='binary', pos_label=1)
    con_f1 = f1_score(all_test_labels, all_test_preds,average='binary', pos_label=0)
    macro_f1 = f1_score(all_test_labels, all_test_preds, average="macro")
    metrics[f"{experiment_type}/macro-f1"] = macro_f1
    metrics[f"{experiment_type}/pro-f1"] = pro_f1
    metrics[f"{experiment_type}/con-f1"] = con_f1
    metrics[f"{experiment_type}/accuracy"] = test_accuracy
    metrics["score"] = metrics[f"{experiment_type}/accuracy"]
    wandb.log(metrics)
    print(metrics)
    return metrics["score"]


def baseline(params, offline=True, validate=True, majority=False):
    splits = load_splits()
    if validate:
        test_split = splits["validation"]
    else:
        test_split = splits["test"]

    if offline:
        save_pre_trained_model()
        path = params["model-path"]

    test_dataset = Dataset(test_split, {"PRO": 1, "CON": 0}, path=path)
    test_dataloader = DataLoader(test_dataset, batch_size=8, shuffle=True)
    predictions = []
    labels = []
    for step, (test_input, test_labels) in enumerate(test_dataloader):
        labels.extend(test_labels)
        if majority:
            predictions.extend([1 for _ in test_labels])
        else:
            predictions.extend([randint(0,1) for _ in test_labels])
    print(f"size of test is {test_labels}")
    pro_f1 = f1_score(labels, predictions,average='binary', pos_label=1)
    con_f1 = f1_score(labels, predictions,average='binary', pos_label=0)
    macro_f1 = f1_score(labels, predictions, average="macro")
    accuracy = accuracy_score(labels,predictions)

    return accuracy, pro_f1, con_f1, macro_f1


def run_ibm_baseline(params, validate=True):
    splits = load_splits()
    if validate:
        test_split = splits["validation"]
    else:
        test_split = splits["test"]
    api_key = params["api-key"]
    debater_api = DebaterApi(api_key)
    pro_con_client = debater_api.get_pro_con_client()
    if validate:
        df_test = splits["validation"]
    else:
        df_test = splits["test"]
    list_of_instances = []
    for i, record in df_test.iterrows():
        list_of_instances.append({"sentence" : record['claims.claimCorrectedText'], "topic": record["topicText"]})
    scores = pro_con_client.run(list_of_instances)
    predictions = [score > 0 for score in scores]
    labels_map = {"PRO": 1, "CON": 0}
    labels = [labels_map[label] for label in test_split["claims.stance"]]
    accuracy = accuracy_score(labels, predictions)
    pro_f1 = f1_score(labels, predictions,average='binary', pos_label=1)
    con_f1 = f1_score(labels, predictions,average='binary', pos_label=0)
    macro_f1 = f1_score(labels, predictions, average="macro")
    return accuracy, pro_f1, con_f1, macro_f1

if __name__ == "__main__":
    args = parse_args()
    params = get_baseline_params()
    if args.random:
        accuracy, pro_f1, con_f1, macro_f1  = baseline(params, offline=args.offline, validate=args.validate)
        print(f"random baseline: accuracy {accuracy}, macro-f1 {macro_f1}, pro f1 {pro_f1}, con f1 {con_f1}")
    elif args.majority:
        accuracy, pro_f1, con_f1, macro_f1  = baseline(params, offline=args.offline, validate=args.validate, majority=True)
        print(f"majority baseline: accuracy {accuracy}, macro-f1 {macro_f1}, pro f1 {pro_f1}, con f1 {con_f1}")
    elif args.ibm_api:
        accuracy, pro_f1, con_f1, macro_f1  = run_ibm_baseline(params, args.validate)
        print(f"ibm api: accuracy {accuracy}, macro-f1 {macro_f1}, pro f1 {pro_f1}, con f1 {con_f1}")
    else:
        init_wandb(args.offline, params)
        run_finetuning_experiment_baseline(params, args.offline, args.validate)

