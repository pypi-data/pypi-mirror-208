import tensorflow as tf
import optuna.visualization as vis
from sklearn.metrics import log_loss
from ...classification.metrics import Metrics
from transformers import TFAutoModel
import optuna

class TransformerModel(Metrics):
    def __init__(self,seq_len=128) -> None:
        self.input_ids = tf.keras.layers.Input(shape=(seq_len,), name='input_ids', dtype='int64')
        self.mask = tf.keras.layers.Input(shape=(seq_len,), name='attention_mask', dtype='int64')
        self.model = tf.keras.Sequential()

    def add_layer(self, dimensions=128, activation='relu'):
        self.model.add(tf.keras.layers.Dense(dimensions, activation=activation))

    def add_LSTM(self, dimensions=128, return_sequence=False):
        self.model.add(tf.keras.layers.LSTM(dimensions, return_sequences=return_sequence))

    def add_GRU(self, dimensions=128, return_sequence=False):
        self.model.add(tf.keras.layers.GRU(dimensions, return_sequences=return_sequence))

    def embedding(self, model_name, return_embedding=False):        
        model_extract = TFAutoModel.from_pretrained(model_name)
        
        if 'gpt' in model_name or 'roberta' in model_name:
            outputs = model_extract(self.input_ids)
            embeddings = outputs.last_hidden_state
        else:
            outputs = model_extract(self.input_ids, attention_mask=self.mask)
            embeddings = outputs.last_hidden_state
        self.model.add(embeddings)

        if return_embedding:
            return embeddings

    def output(self, dimension=1, activation="sigmoid"):
        self.model.add(tf.keras.layers.Dense(dimension, activation=activation))
    
    def compile(self, loss, optimizer, metrics):
        self.model.compile(loss=loss, optimizer=optimizer, metrics=metrics)

    def fit(self, train, val, epochs=3, layer_untrained=0):
        self.model.layers[layer_untrained].trainable = False
        self.model.fit(train, validation_data=val, epochs=epochs)

    def fit_optuna_layers(self, train ,val, test_data,test_labels, output_dim=1, output_activ="sigmoid",
                        params=None, model_name="bert-base-cased",n_trials=10, show_plot=False):
        embed = self.embedding(model_name,return_embedding=True)

        params_columns = ["layers", "lstm_layers", "layers_dimensions", "lsmt_layers_dimensions"]
        params_basic ={
            "layers": [2, 10],
            "layers_dimensions": [32, 1024],
            "lsmt_layers": [1, 3],
            "lsmt_layers_dimensions": [32, 1024]
        }
        if params == None:
            params = params_basic
        else:
            for parameter in params_columns:
                if parameter not in params.keys():
                    params[parameter] = params_basic[parameter]

        def objective(trial):
            self.model = tf.keras.Sequential()
            self.model.add(embed)
            layers = trial.suggest_int("layers", params["layers"][0], params["layers"][0])
            lstm_layers = trial.suggest_int("lstm_layers", params["lstm_layers"][0], params["lstm_layers"][1])
            for i in range(lstm_layers-1):
                self.add_LSTM(
                    trial.suggest_int(
                    f"Layer_LSTM_{i}", params["lstm_layers_dimensions"][0], params["lstm_layers_dimensions"][1]),
                    return_sequence=True
                    )
            self.add_LSTM(trial.suggest_int(
                f"Layer_LSTM_end", params["lstm_layers_dimensions"][0], params["lstm_layers_dimensions"][1])
                )
            for i in range(layers):
                self.add_layer(trial.suggest_int(f"Layer_{i}", params["layers_dimensions"][0], params["layers_dimensions"][1]))
            self.output(output_dim, activation=output_activ)
            self.fit(train, val)
            y = self.predict(test_data)
            loss = log_loss(test_labels, y)
            return loss
        
        study = optuna.create_study(direction='minimize', pruner=optuna.pruners.MedianPruner())
        study.optimize(objective, n_trials=n_trials)
        if show_plot:
            optimization_history_plot = vis.plot_optimization_history(study)
            optimization_history_plot.show()
        
        best_params = study.best_params
        self.model = tf.keras.Sequential()
        self.model.add(embed)
        for layer in range(best_params["lstm_layers"]-1):
            self.model.add_LSTM(best_params[f"Layer_LSTM_{layer}"], return_sequence=True)
        self.model.add_LSTM(best_params["Layer_LSTM_end"])
        for layer in range(best_params["layers"]):
            self.model.add_layer(best_params[f"Layer_{layer}"])
        self.model.fit(train, val)

    def evaluate(self, X, y):
        preds = self.model.predict(X)
        return self.metric.calculate_metrics(y, preds)

    def predict(self, X):
        return self.model.predict(X)
    

    def show_layer(self):
        print(self.model.describe())





    