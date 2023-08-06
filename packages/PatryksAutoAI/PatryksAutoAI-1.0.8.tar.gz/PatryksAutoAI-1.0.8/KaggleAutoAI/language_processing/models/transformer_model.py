import tensorflow as tf
from sklearn.metrics import log_loss
import optuna.visualization as vis
from ...classification.metrics import Metrics
from transformers import TFAutoModel
import optuna
import numpy as np
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

    def fit_optuna_layers(self, train, val, test_data, test_labels, params=None, n_trials=10, show_plot=False):
        params_columns = ["layers","layers_dimensions",]
        params_basic = {
            "layers": [2, 10],
            "layers_dimensions": [32, 1024],
        }
        if params is None:
            params = params_basic
        else:
            for parameter in params_columns:
                if parameter not in params.keys():
                    params[parameter] = params_basic[parameter]

        def objective(trial):
            self.reset_layers()
            layers = trial.suggest_int("num_layers", params["layers"][0], params["layers"][1])
            for i in range(layers):
                self.add_layer(
                    trial.suggest_int(f"Layer_{i}", params["layers_dimensions"][0], params["layers_dimensions"][1]),
                    activation="relu"
                )
            self.fit(train, val, epochs=2)
            print("here:", test_data)
            preds = self.model.predict(test_data)
            print("preds", preds)
            loss = log_loss(test_labels, preds)
            return loss

        study = optuna.create_study(direction='minimize', pruner=optuna.pruners.MedianPruner())
        study.optimize(objective, n_trials=n_trials)
        if show_plot:
            optimization_history_plot = optuna.visualization.plot_optimization_history(study)
            optimization_history_plot.show()

        best_params = study.best_params
        self.reset_layers()
        for layer in range(best_params["layers"]):
            self.add_layer(best_params[f"Layer_{layer}"], activation="relu")
        self.fit(train, val, epochs=2)
                
    def evaluate(self, X, y):
        preds = self.model.predict(X)
        return self.metric.calculate_metrics(y, preds)

    def predict(self, X, labels=False):
        predictions = []
        if labels:
            for input_ids, attention_mask, labels in X:
                batch_predictions = self.model.predict([input_ids, attention_mask])
                predictions.append(batch_predictions)
            predictions = np.concatenate(predictions, axis=0)
            return predictions

        for input_ids, attention_mask in X:
            print("here:", input_ids, attention_mask)
            batch_predictions = self.model.predict([input_ids, attention_mask])
            predictions.append(batch_predictions)
        predictions = np.concatenate(predictions, axis=0)
        return predictions
    
    def reset_layers(self):
        self.layers = []

    def show_layer(self):
        for layer in self.layers:
            print(f"{layer}")





    