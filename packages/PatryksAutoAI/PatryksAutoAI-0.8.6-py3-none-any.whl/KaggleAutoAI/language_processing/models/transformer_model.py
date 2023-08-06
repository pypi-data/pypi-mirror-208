import tensorflow as tf
from sklearn.metrics import log_loss
import optuna.visualization as vis
from ...classification.metrics import Metrics
from transformers import TFAutoModel
import optuna
optuna.logging.disable_default_handler()

class TransformerModel(Metrics):
    def __init__(self,seq_len=128) -> None:
        self.input_ids = tf.keras.layers.Input(shape=(seq_len,), name='input_ids', dtype='int64')
        self.mask = tf.keras.layers.Input(shape=(seq_len,), name='attention_mask', dtype='int64')

        self.embedding_layer = None
        self.layers = []
        self.output_layer = None
        self.compile_inst = {}
        self.model = None

    def add_layer(self, dimensions=128, activation=None):
        self.layers.append(tf.keras.layers.Dense(dimensions, activation=activation))

    def add_LSTM(self, dimensions=128, return_sequence=False):
        self.layers.append(tf.keras.layers.LSTM(dimensions, return_sequences=return_sequence))

    def add_GRU(self, dimensions=128, return_sequence=False):
        self.layers.append(tf.keras.layers.GRU(dimensions, return_sequences=return_sequence))

    def embedding(self, model_name):        
        model_extract = TFAutoModel.from_pretrained(model_name)
        
        if 'gpt' in model_name or 'roberta' in model_name:
            outputs = model_extract(self.input_ids)
            embeddings = outputs.last_hidden_state
        else:
            outputs = model_extract(self.input_ids, attention_mask=self.mask)
            embeddings = outputs.last_hidden_state
        self.embedding_layer = embeddings

    def output(self, dimension=1, activation="sigmoid"):
        self.output_layer = tf.keras.layers.Dense(dimension, activation=activation)
    
    def compile(self, loss, optimizer, metrics):
        self.compile_inst = {"loss": loss,
                            "optimizer": optimizer,
                            "metrics":metrics}

    def fit(self, train, val, epochs=3, layer_untrained=0):
        embed = self.embedding_layer
        x = self.layers[0](embed)
        for i in range(1, len(self.layers)):
            x = self.layers[i](x)
        y = self.output_layer(x)
        if self.mask is not None:
            model = tf.keras.Model(inputs=[self.input_ids, self.mask], outputs=y)
        else:
            model = tf.keras.Model(inputs=self.input_ids, outputs=y)
        model.compile(loss=self.compile_inst["loss"],
                           optimizer=self.compile_inst["optimizer"],
                           metrics=self.compile_inst["metrics"])
        model.layers[layer_untrained].trainable = False
        model.fit(train, validation_data=val, epochs=epochs)
        self.model = model

    def fit_optuna_layers(self, train ,val, test_data,test_labels, params=None, n_trials=10, show_plot=False):
        params_columns = ["layers", "lstm_layers", "layers_dimensions", "lstm_dimensions"]
        params_basic ={
            "layers": [2, 10],
            "layers_dimensions": [32, 1024],
            "lstm_layers": [1, 3],
            "lstm_dimensions": [32, 1024]
        }
        if params == None:
            params = params_basic
        else:
            for parameter in params_columns:
                if parameter not in params.keys():
                    params[parameter] = params_basic[parameter]

        def objective(trial):
            layers = trial.suggest_int("num_layers", params["layers"][0], params["layers"][1])
            lstm_layers = trial.suggest_int("num_layers_lstm", params["lstm_layers"][0], params["lstm_layers"][1])
            embed = self.embedding_layer
            x = tf.keras.layers.LSTM(
                trial.suggest_int("Llayer_0", params["lstm_dimensions"][0], params["lstm_dimensions"][1]),
                                return_sequences=True
                                  )(embed)
            for i in range(1, lstm_layers-1):
                x = tf.keras.layers.LSTM(
                    trial.suggest_int(f"Llayer_{i}", params["lstm_dimensions"][0], params["lstm_dimensions"][1]),
                    return_sequences=True)(x)
            x = tf.keras.layers.LSTM(trial.suggest_int("Llayer_end", params["lstm_dimensions"][0], params["lstm_dimensions"][1]))(x)
            for i in range(layers):
                x = tf.keras.layers.Dense(
                    trial.suggest_int(f"Layer_{i}", params["layers_dimensions"][0], params["layers_dimensions"][1]),
                    activation="relu"
                    )(x)

            y = self.output_layer(x)
            model = tf.keras.Model(inputs=[self.input_ids, self.mask], outputs=y)
            model.fit(train, val,epochs=2)
            y = model.predict(test_data)
            loss = log_loss(test_labels, y)
            return loss
        
        study = optuna.create_study(direction='minimize', pruner=optuna.pruners.MedianPruner())
        study.optimize(objective, n_trials=n_trials)
        if show_plot:
            optimization_history_plot = vis.plot_optimization_history(study)
            optimization_history_plot.show()
        
        best_params = study.best_params
        for layer in range(best_params["lstm_layers"]-1):
            self.model.add_LSTM(best_params[f"Layer_LSTM_{layer}"], return_sequence=True)
        self.model.add_LSTM(best_params["Layer_LSTM_end"])
        for layer in range(best_params["layers"]):
            self.model.add_layer(best_params[f"Layer_{layer}"])
        self.fit(train, val)
            
    def evaluate(self, X, y):
        preds = self.model.predict(X)
        return self.metric.calculate_metrics(y, preds)

    def predict(self, X):
        return self.model.predict(X)
    
    def reset_layers(self):
        self.layers = None

    def show_layer(self):
        print(self.model.describe())





    