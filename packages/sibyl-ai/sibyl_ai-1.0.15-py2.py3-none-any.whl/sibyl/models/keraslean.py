"""
Generic regression model for machine learning problems based on Keras

@author: Francesco Baldisserri
@creation date: 06/03/2020
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tempfile
import keras
import keras.layers as klrs
from keras.callbacks import EarlyStopping
from sklearn.model_selection._split import indexable
from sklearn.base import BaseEstimator, ClassifierMixin, RegressorMixin


# TODO: Consolidate Regressor and Classifier?
class KerasDenseRegressor(BaseEstimator, RegressorMixin):
    def __init__(self, units=(64, 64), dropout=0, activation="relu",
                 batch_norm=False, batch_size=None, optimizer="nadam",
                 kernel_init="glorot_normal", val_split=0.2, epochs=10,
                 loss="mean_squared_error", n_iter_no_change=None,
                 custom_objects=None, _estimator_type="regressor",
                 out_act="linear", metrics=None):
        self.units = units
        self.dropout = dropout
        self.activation = activation
        self.batch_norm = batch_norm
        self.batch_size = batch_size
        self.optimizer = optimizer
        self.kernel_init = kernel_init
        self.val_split = val_split
        self.epochs = epochs
        self.loss = loss
        self.n_iter_no_change = n_iter_no_change
        self.out_act = out_act
        self.metrics = metrics
        self.custom_objects = custom_objects
        self._estimator_type = _estimator_type
        self.model = None

    def fit(self, X, y):
        X_val, y_val = indexable(X, y)
        if self.model is None: self.model = self._build_model(X_val, y_val)
        calls = [] if self.n_iter_no_change is None else\
            [EarlyStopping(monitor="val_loss" if self.val_split > 0 else "loss",
                           patience=self.n_iter_no_change,
                           restore_best_weights=True)]
        return self.model.fit(X_val, y_val, epochs=self.epochs, verbose=0,
                              callbacks=calls, validation_split=self.val_split)

    def predict(self, X):
        return self.model.predict(indexable(X))

    def _build_model(self, X, y):
        """ Build Keras model according to input parameters """
        model = keras.models.Sequential()
        for units in self.units:
            if self.dropout > 0: model.add(klrs.Dropout(self.dropout))
            model.add(klrs.Dense(units, activation=self.activation,
                                 kernel_initializer=self.kernel_init))
            if self.batch_norm: model.add(klrs.BatchNormalization())
        out_shape = y.shape[1] if len(y.shape) > 1 else 1
        model.add(klrs.Dense(out_shape, activation=self.out_act))
        model.compile(loss=self.loss, metrics=self.metrics,
                      optimizer=self.optimizer)

    def __getstate__(self):
        state = self.__dict__.copy()
        if self.model:
            temp = tempfile.NamedTemporaryFile(delete=False, suffix=".h5")
            keras.models.save_model(self.model, temp.name)
            with temp:
                state["model"] = temp.read()
            os.remove(temp.name)
        return state

    def __setstate__(self, state):
        self.__dict__ = state
        if self.model:
            temp = tempfile.NamedTemporaryFile(delete=False, suffix=".h5")
            with temp:
                temp.write(state["model"])
            self.model = keras.models.load_model(temp.name,
                                                 custom_objects=self.custom_objects)
            os.remove(temp.name)


class KerasDenseClassifier(KerasDenseRegressor, ClassifierMixin):
    def __init__(self, units=(64, 64), dropout=0, activation="relu",
                 batch_norm=False, batch_size=None, optimizer="nadam",
                 kernel_init="glorot_normal", val_split=0.2, epochs=10,
                 loss="categorical_crossentropy", n_iter_no_change=None,
                 custom_objects=None, out_act="softmax"):
        super().__init__(units=units, dropout=dropout,
                         activation=activation, batch_norm=batch_norm,
                         batch_size=batch_size,  optimizer=optimizer,
                         kernel_init=kernel_init, val_split=val_split,
                         epochs=epochs, loss=loss, out_act=out_act,
                         metrics=["accuracy", "precision", "f1"],
                         n_iter_no_change=n_iter_no_change,
                         custom_objects=custom_objects)
        self._estimator_type = "classifier"

    def predict_proba(self, X):
        return self.model.predict_proba(X)


class KerasCNNRegressor(KerasDenseRegressor):
    def __init__(self, cnn_units=(64, 64), dense_units=(64, 64), dropout=0,
                 activation="relu", batch_norm=False, batch_size=None,
                 optimizer="nadam", kernel_init="glorot_normal", val_split=0.2,
                 epochs=10, loss="mean_squared_error", out_act="linear",
                 n_iter_no_change=None, custom_objects=None):
        super().__init__(dropout = dropout,
                         activation = activation,
                         batch_norm = batch_norm,
                         batch_size = batch_size,
                         optimizer = optimizer,
                         kernel_init = kernel_init,
                         val_split = val_split,
                         epochs = epochs,
                         loss = loss,
                         out_act= out_act,
                         n_iter_no_change = n_iter_no_change,
                         custom_objects = custom_objects)
        self.cnn_units = cnn_units
        self.dense_units = dense_units

    def _build_model(self, X, y):
        """ Build Keras model according to input parameters """
        model = keras.models.Sequential()
        for units in self.cnn_units:
            if self.dropout > 0: model.add(klrs.Dropout(self.dropout))
            model.add(klrs.Conv1D(filters=units, kernel_size=2,
                                  dilation_rate=2, padding="causal",
                                  activation=self.activation))
            if self.batch_norm: model.add(klrs.BatchNormalization())
        model.add(klrs.Flatten())
        for units in self.dense_units:
            if self.dropout > 0: model.add(klrs.Dropout(dropout))
            model.add(klrs.Dense(units, activation=self.activation,
                                 kernel_initializer=self.kernel_init))
            if self.batch_norm: model.add(klrs.BatchNormalization())
        out_shape = y.shape[1] if len(y.shape) > 1 else 1
        model.add(klrs.Dense(out_shape, activation=self.out_act))
        model.compile(loss=self.loss, metrics=self.metrics,
                      optimizer=self.optimizer)
        return model


class KerasCNNClassifier(KerasCNNRegressor):
    def __init__(self, cnn_units=(64, 64), dense_units=(64, 64), dropout=0,
                 activation="relu", batch_norm=False, batch_size=None,
                 optimizer="nadam", kernel_init="glorot_normal", val_split=0.2,
                 epochs=10, loss="categorical_crossentropy", out_act="softmax",
                 n_iter_no_change=None, custom_objects=None):
        super().__init__(
            cnn_units = cnn_units,
            dense_units= dense_units,
            dropout = dropout,
            activation = activation,
            batch_norm = batch_norm,
            batch_size = batch_size,
            optimizer = optimizer,
            kernel_init = kernel_init,
            val_split = val_split,
            epochs = epochs,
            loss = loss,
            out_act= out_act,
            n_iter_no_change = n_iter_no_change,
            custom_objects = custom_objects)
        self._estimator_type = "classifier"

    def predict_proba(self, X):
        return self.model.predict_proba(X)
