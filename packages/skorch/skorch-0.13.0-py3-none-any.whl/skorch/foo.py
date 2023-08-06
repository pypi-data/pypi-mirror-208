#!/usr/bin/env python3

from sklearn.base import BaseEstimator, TransformerMixin


class MyTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, foo=3):
        self.foo = foo

    def fit(self, X, y=None, **fit_params):
        self.param_ = len(X) + self.foo
        return self

    def transform(self, X):
        return X + self.param_

    def __getstate__(self):
        print("called __getstate__")
        state = self.__dict__.copy()
        state['param_'] = str(state['param_'])
        return state

    def __setstate__(self, state):
        print("called __setstate__")
        state['param_'] = int(state['param_'])
        self.__dict__.update(state)


if __name__ == '__main__':
    import numpy as np
    import skops.io as sio

    X = np.arange(10)
    t = MyTransformer()
    t.fit(X)
    print(t.transform(X))

    loaded = sio.loads(sio.dumps(t), trusted=['__main__.MyTransformer'])
    print(loaded.transform(X))
