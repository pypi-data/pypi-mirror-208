"""
Light GBM wrapper to simplify early stopping

@author: Francesco Baldisserri
@creation date: 24/9/2021
"""

from math import log10
import lightgbm as lgb
from sklearn.model_selection import train_test_split


class LGBMRegressorWrapper(lgb.LGBMRegressor):
    def fit(self, x, y, sample_weight=None):
        rounds = int(log10(self.n_estimators))
        callbacks = [lgb.early_stopping(rounds), lgb.log_evaluation(period=0)]
        if sample_weight is None:
            x_train, x_val, y_train, y_val = train_test_split(x, y, test_size=0.2)
            return super().fit(x_train, y_train, eval_set=[(x_val, y_val)],
                               callbacks=callbacks)
        else:
            x_train, x_val, y_train, y_val, w_train, w_val = train_test_split(x, y,
                                                                              sample_weight,
                                                                              test_size=0.2)
            return super().fit(x_train, y_train, sample_weight=w_train, callbacks=callbacks,
                               eval_set=[(x_val, y_val)], eval_sample_weight=[w_val])


class LGBMClassifierWrapper(lgb.LGBMClassifier):
    def fit(self, x, y, sample_weight=None):
        rounds = int(log10(self.n_estimators))
        callbacks = [lgb.early_stopping(rounds), lgb.log_evaluation(period=0)]
        if sample_weight is None:
            x_train, x_val, y_train, y_val = train_test_split(x, y, test_size=0.2)
            return super().fit(x_train, y_train, eval_set=[(x_val, y_val)],
                               callbacks=callbacks)
        else:
            x_train, x_val, y_train, y_val, w_train, w_val = train_test_split(x, y,
                                                                              sample_weight,
                                                                              test_size=0.2)
            return super().fit(x_train, y_train, sample_weight=w_train, callbacks=callbacks,
                               eval_set=[(x_val, y_val)], eval_sample_weight=[w_val])