from transformers import BertTokenizer, GPT2Tokenizer, RobertaTokenizer, DistilBertTokenizer, AlbertTokenizer, ElectraTokenizer
import numpy as np
import tensorflow as tf

class Text2Number():
    def __init__(self):
        self.token = None

    def tokenize_bert(self, data, seq_len=128, model="bert-base-cased"):
        '''
            Computationally expensive due to their large size, and the tokenization process can be slower
        '''
        tokenizer = BertTokenizer.from_pretrained(model)
        token = tokenizer(data.tolist(),
                          max_length=seq_len,
                          truncation=True,
                          padding='max_length',
                          add_special_tokens=True,
                          return_tensors="tf")
        self.token = token

    def tokenize_gpt2(self, data, seq_len=128, model="gpt2-medium"):
        '''
            Unidirectional
        '''
        tokenizer = GPT2Tokenizer.from_pretrained(model)
        token = tokenizer(data.tolist(),
                          max_length=seq_len,
                          truncation=True,
                          padding='max_length',
                          add_special_tokens=True,
                          return_tensors="tf")
        self.token = token

    def tokenize_robert(self, data, seq_len=128, model="roberta-base"):
        '''
            Requiring more computational resources for training and inference.
        '''
        tokenizer = RobertaTokenizer.from_pretrained(model)
        token = tokenizer(data.tolist(),
                          max_length=seq_len,
                          truncation=True,
                          padding='max_length',
                          add_special_tokens=True,
                          return_tensors="tf")
        self.token = token

    def tokenize_distilBERT(self, data, seq_len=128, model="distilbert-base-uncased"):
        '''
            Scenarios where memory and computational resources are limited
        '''
        tokenizer = DistilBertTokenizer.from_pretrained(model)
        token = tokenizer(data.tolist(),
                          max_length=seq_len,
                          truncation=True,
                          padding='max_length',
                          add_special_tokens=True,
                          return_tensors="tf")
        self.token = token

    def tokenize_Albert(self, data, seq_len=128, model="albert-base-v2"):
        '''
            Fewer parameters, making them more memory-efficient and faster during training and inference
        '''
        tokenizer = AlbertTokenizer.from_pretrained(model)
        token = tokenizer(data.tolist(),
                          max_length=seq_len,
                          truncation=True,
                          padding='max_length',
                          add_special_tokens=True,
                          return_tensors="tf")
        self.token = token

    def tokenize_Electra(self, data, seq_len=128, model="google/electra-base-discriminator"):
        '''
            Rely on a discriminator-generator setup, which means they may not capture certain aspects of language semantics
        '''
        tokenizer = ElectraTokenizer.from_pretrained(model)
        token = tokenizer(data.tolist(),
                          max_length=seq_len,
                          truncation=True,
                          padding='max_length',
                          add_special_tokens=True,
                          return_tensors="tf")
        self.token = token

    def create_dataset(self, labels, train_size=0.8, batch_size=32):
        '''
            Creates the train and validation datasets
        '''
        labels = np.array(labels.tolist()).reshape(-1,1)
        size = int(labels.shape[0] / batch_size * train_size)

        dataset = tf.data.Dataset.from_tensor_slices((self.token['input_ids'], self.token['attention_mask'], labels))
        dataset = dataset.map(self.map_func_train)
        dataset = dataset.shuffle(10000).batch(batch_size,drop_remainder=True)

        train_ds = dataset.take(size)
        val_ds = dataset.skip(size)
        return train_ds, val_ds
    
    def create_Xy(self,labels, batch_size=32):
        labels = np.array(labels.tolist()).reshape(-1,1)
        labels = np.array(labels.tolist()).reshape(-1,1)
        dataset = tf.data.Dataset.from_tensor_slices((self.token['input_ids'], self.token['attention_mask']))
        dataset = dataset.map(self.map_func_data)
        dataset = dataset.shuffle(10000).batch(batch_size,drop_remainder=True)
        return dataset, labels
    
    def map_func_train(self, input_ids, masks, labels):
        return {'input_ids':input_ids,
                'attention_mask':masks}, labels
    
    def map_func_data(self, input_ids, masks):
        return {'input_ids':input_ids, 'attention_mask':masks}
    
    def get(self):
        return self.token
    