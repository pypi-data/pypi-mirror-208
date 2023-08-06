# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.5
# ---

# author: evelin amorim
# tries to learn the concept of participant from the result of an SRL output
import os.path
from builtins import zip

import torch

from text2story.annotators import ALLENNLP
from text2story.readers import read_brat
from text2story.core.utils import bsearch_tuplelist

from transformers import BertTokenizer, BertModel
from torch.optim import Adam
from torch.utils.data import TensorDataset, DataLoader,RandomSampler

import os
from pathlib import Path

import spacy
from torch import nn


class ParticipantsModel(nn.Module):
    def __init__(self, bert, hidden_size):
        super(ParticipantsModel, self).__init__()
        self.bert = bert

        # Define your layers
        self.conv1d = nn.Conv1d(in_channels=self.bert.config.hidden_size, out_channels=64, kernel_size=3,
                                stride=1)

    def forward(self, sent):
        sent_embeddings = self.bert(sent)[0]
        #span_embeddings = self.bert(span)[0]

        # Apply the convolutional layer
        sentence_features = self.conv1d(
            sent_embeddings.transpose(1, 2))  # [batch_size, out_channels, sequence_length - kernel_size + 1]


class ParticipantConceptLearning:

    def __init__(self, lang):
        self.lang = lang
        if lang == "en":
            if not (spacy.util.is_package('en_core_web_lg')):
                spacy.cli.download('en_core_web_lg')

            self.language_model = spacy.load('en_core_web_lg')
        if lang == "pt":
            if not (spacy.util.is_package('pt_core_news_lg')):
                spacy.cli.download('pt_core_news_lg')
            self.language_model = spacy.load('pt_core_news_lg')

        # Load the pre-trained BERT tokenizer and model
        self.max_seq_len = 128
        self.tokenizer = BertTokenizer.from_pretrained('neuralmind/bert-base-portuguese-cased',model_max_length=self.max_seq_len)
        self.bert_model = BertModel.from_pretrained('neuralmind/bert-base-portuguese-cased')

        self.hidden_size = 128
        self.nepochs = 5
        self.learning_rate = 0.001

    def read_file_lst(self, file_lst):
        doc_lst = []

        for f in file_lst:
            p = Path(f)
            reader = read_brat.ReadBrat()

            file_name = p.parent.joinpath(p.stem).absolute()
            doc = reader.process_file(str(file_name))
            doc_lst.append((doc, str(p.absolute())))
        return doc_lst

    def load_dataset(self, data_dir, type_data="train", split_data=None):
        if split_data is None:
            file_lst = []
            for dirpath, dirnames, filenames in os.walk(data_dir):
                for f in filenames:
                    if f.endswith(".txt"):
                        file_lst.append(os.path.join(dirpath, f))
        else:
            if type_data == "train":
                split_data_file = os.path.join(split_data, "sampletrain.txt")
            else:
                split_data_file = os.path.join(split_data, "test.txt")

            file_lst = open(split_data_file, "r").readlines()
            file_lst = [os.path.join(data_dir, f.replace("\n", "")) for f in file_lst]

        dataset = self.read_file_lst(file_lst)

        return dataset

    def get_actors(self, doc):

        actor_lst = []

        for tok in doc:
            for ann_type, ann_attr in tok.attr:
                if ann_type == "Participant":
                    actor_lst.append((tok.offset, tok.offset + len(tok.text)))

        return actor_lst

    def get_sent_lst(self, doc_text):
        sent_lst = []
        doc_lm = self.language_model(doc_text)

        for sent in doc_lm.sents:
            sent_lst.append(sent.text)

        return sent_lst

    def get_sent_text(self, span_offset, doc_lm):
        pass

    def get_sents_offset(self, sent_lst):
        sent_offset_lst = []
        offset_start = 0
        for sent in sent_lst:
            offset_end = offset_start + len(sent) - 1
            sent_offset_lst.append((offset_start, offset_end))
            offset_start = offset_end
        return sent_offset_lst

    def get_candidates_class(self, candidate_lst, actor_lst, sent_lst):
        """

        @param sent:
        @return: a list of words
        """
        sent_off_lst = self.get_sents_offset(sent_lst)
        y = []
        sent_id_lst = []

        for candidate in candidate_lst:

            cand_offset = candidate[0]
            sent_id = bsearch_tuplelist(cand_offset[0], sent_off_lst)
            sent_id_lst.append(sent_id)

            pos = bsearch_tuplelist(cand_offset[0], actor_lst)
            if pos == -1:
                pos = bsearch_tuplelist(cand_offset[1], actor_lst)
                if pos == -1:
                    y.append(0)
                else:
                    y.append(1)
            else:
                y.append(1)

        return candidate_lst, y, sent_id_lst

    def build_batch_data(self, dataset):

        sent_text_lst = []
        candidate_text_lst = []

        for doc, file_name in dataset:
            # I need to get the class from the lusa annotations
            with open(file_name, "r") as fd:
                doc_text = fd.read()
                candidate_lst = ALLENNLP.extract_actors(self.lang, doc_text)

            sent_lst = self.get_sent_lst(doc_text)
            actor_lst = self.get_actors(doc)

            # TODO: verificar quantidade de candidatos e quantidade de cada classe
            candidate_lst, y, sent_id_lst = self.get_candidates_class(candidate_lst, actor_lst, sent_lst)

            sent_text_lst += [sent_lst[id] for id in sent_id_lst]

            for ((start, end), _, _) in candidate_lst:
                cand = doc_text[start:end]
                candidate_text_lst.append(cand)


        tokens_sent = self.tokenizer.batch_encode_plus(sent_text_lst,
                                                       max_length=self.max_seq_len,
                                                       pad_to_max_length=True,
                                                       truncation=True,
                                                       return_token_type_ids=False)
        tokens_sent = torch.tensor(tokens_sent['input_ids'])

        data_sent = TensorDataset(tokens_sent)
        dataloader_sent = DataLoader(data_sent, batch_size=16)

        tokens_span = self.tokenizer.batch_encode_plus(candidate_text_lst,
                                                       max_length=self.max_seq_len,
                                                       pad_to_max_length=True,
                                                       truncation=True,
                                                       return_token_type_ids=False)
        tokens_span = torch.tensor(tokens_span['input_ids'])

        data_span = TensorDataset(tokens_span)
        dataloader_span = DataLoader(data_span, batch_size=16)

        return dataloader_sent, dataloader_span

    def process_train(self, data_dir, split_dir=None):

        # load train dataset
        if split_dir is not None:
            dataset = self.load_dataset(data_dir, type_data="train", split_data=split_dir)
        else:
            dataset = self.load_dataset(data_dir)

        # load srl model
        ALLENNLP.load(self.lang)

        # apply srl and get possible candidates as participants
        dataloader_sent, dataloader_span = self.build_batch_data(dataset)

       # model = ParticipantsModel(self.bert_model, self.hidden_size)

        # Define the optimizer
        #optimizer = Adam(model.parameters(), lr=self.learning_rate)

        #for epoch in range(self.nepochs):
        #    model.train()
        #    optimizer.zero_grad()

            # iterate over batches
        #    for step, batch in enumerate(dataloader_sent):

        #        sent_id = batch[0]
                # clear previously calculated gradients
        #        model.zero_grad()

                # get model predictions for the current batch
        #        preds = model(sent_id)
                # Forward pass
               #outputs = model(tokens_train, candidate_text_lst)

