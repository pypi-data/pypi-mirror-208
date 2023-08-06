import tensorflow as tf
from transformers import TFAutoModel

class NLPModel():
    def __init__(self,seq_len=128) -> None:
        self.embed= None
        self.layers = []
        self.output_layer = None

        self.input_ids = tf.keras.layers.Input(shape=(seq_len,), name='input_ids', dtype='int64')
        self.mask = tf.keras.layers.Input(shape=(seq_len,), name='attention_mask', dtype='int64')

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
        
        model_extract = TFAutoModel.from_pretrained(model_name)
        
        if 'gpt' in model_name or 'roberta' in model_name:
            outputs = model_extract(self.input_ids)
            embedding_layers = outputs.last_hidden_state[layer_extract]
        else:
            outputs = model_extract(self.input_ids, attention_mask=self.mask)
            embedding_layers = outputs.last_hidden_state[layer_extract]
        self.embed = embedding_layers

    def output(self, dimension=1, activation="sigmoid"):
        self.output_layer = tf.keras.layers.Dense(dimension, activation=activation)
    
    def compile(self, loss, optimizer, metrics):
        self.loss = loss
        self.optimizer = optimizer
        self.metrics = metrics

    def fit(self, train, val, epochs=10, seq_len=128):
        embed = self.embed
        x = self.layers[1](embed)
        for layer in self.layers:
            x = layer(x)
        y = self.output(x)
        model = tf.keras.Model(inputs=[self.input_ids, self.mask], outputs=y)

        model.compile(loss=self.loss,
             optimizer=self.optimizer,
             metrics=self.metrics)
        
        model.fit(train, validation_data=val, epochs=epochs)
        self.model = model
    
    def show_layer(self):
        print(f"Embed: {self.embed}")
        for i, layer in enumerate(self.layers):
            print(f"{i} layer: {layer}")
        print(f"Output: {self.output}")





    