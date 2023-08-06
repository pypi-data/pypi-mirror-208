import tensorflow as tf
from transformers import TFAutoModel

class NLPModel():
    def __init__(self) -> None:
        self.layers = []
        self.loss = None
        self.optimizer = None
        self.metrics = None

        self.model = None

    def add_layer(self, dimensions=128, activation=None):
        self.layers.append(tf.keras.layers.Dense(dimensions, activation=activation))

    def embedding(self, model_name, layer_extract=0,seq_len=128):
        if len(self.layers):
            print("Trying to add embedding not in first layer")
            return
        
        input_ids = tf.keras.layers.Input(shape=(seq_len,), name='input_ids', dtype='int64')
        mask = tf.keras.layers.Input(shape=(seq_len,), name='attention_mask', dtype='int64')
        model_extract = TFAutoModel.from_pretrained(model_name)
        
        if 'gpt' in model_name or 'roberta' in model_name:
            outputs = model_extract(input_ids)
            embedding_layers = outputs.last_hidden_state[layer_extract]
        else:
            outputs = model_extract(input_ids, attention_mask=mask)
            embedding_layers = outputs.last_hidden_state[layer_extract]
        self.layers.append(embedding_layers)
    
    def compile(self, loss, optimizer, metrics):
        self.loss = loss
        self.optimizer = optimizer
        self.metrics = metrics

    def fit(self, train, val, epochs=10, seq_len=128):
        input_ids = tf.keras.layers.Input(shape=(seq_len,), name='input_ids', dtype='int64')
        mask = tf.keras.layers.Input(shape=(seq_len,), name='attention_mask', dtype='int64')

        embed = self.layers[0]
        x = self.layers[1](embed)
        for layer in range(2,len(self.layers)-1):
            x = self.layers[layer](x)
        y = self.layers[-1](x)
        model = tf.keras.Model(inputs=[input_ids, mask], outputs=y)

        model.compile(loss=self.loss,
             optimizer=self.optimizer,
             metrics=self.metrics)
        
        model.fit(train, validation_data=val, epochs=2)
        self.model = model





    