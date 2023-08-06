import rpy2.robjects as robjects
from rpy2.robjects import pandas2ri
from tensorflow.python.keras import backend as K
from tensorflow.python.keras import initializers, regularizers, constraints
from tensorflow.python.keras.layers import *


def trans(str1):
    a = []
    dic = {'A': 1, 'B': 0, 'U': 0, 'J': 0, 'Z': 0, 'O': 0, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7, 'I': 8,
           'K': 9, 'L': 10, 'M': 11, 'N': 12, 'P': 13, 'Q': 14, 'R': 15, 'S': 16, 'T': 17, 'V': 18, 'W': 19, 'Y': 20,
           'X': 0}
    for i in range(len(str1)):
        a.append(dic.get(str1[i]))
    return a


def zero_or_one(x):
    return 1 if x > 0.5 else 0


def r2py(text):
    s = r"""
library('protr')
library('DT')
extractCTD = function (x) c(extractCTDC(x), extractCTDT(x), extractCTDD(x))

funcdict   = c(
'aac'    = 'extractAAC',
'dc'     = 'extractDC',
'ctd'    = 'extractCTD',
'qso'    = 'extractQSO',
'paac'   = 'extractPAAC',
'apaac'  = 'extractAPAAC'
)


fs = function(path){

 seq <- scan(textConnection(path), what = 'complex', blank.lines.skip = TRUE)

 aaa <- c("aac","dc","ctd","qso","paac","apaac")

 exec = paste0('t(sapply(seq, ', funcdict[as.character(aaa)], '))')
 outlist = vector('list', length(exec))
 n = length(exec)
 for (i in 1L:n) {
   outlist[[i]] = eval(parse(text = exec[i]))
 }

 out = do.call(cbind, outlist)
 return(out)
}
"""
    robjects.r(s)

    r = robjects.r["fs"](text)

    # print(r)
    # print(type(r))
    rr = pandas2ri.rpy2py_floatvector(r)
    # print(type(rr))
    return rr


def merge_all(text):
    ret = r2py(text)
    ret1 = ret.flatten()

    return ret1


def trans_6(str1):
    a = []
    dic = {'A': 6, 'C': 1, 'D': 2, 'E': 2, 'F': 1, 'G': 4, 'H': 3, 'I': 1, 'K': 3, 'L': 1, 'M': 1, 'N': 5, 'P': 4,
           'Q': 5, 'R': 3, 'S': 5, 'T': 6, 'V': 1, 'W': 1, 'Y': 1, 'X': 0, 'B': 0, 'U': 0, 'J': 0, 'Z': 0, 'O': 0, }
    for i in range(len(str1)):
        a.append(dic.get(str1[i]))
    return a


def get_feature_from_profeat_replace(name, sequence, is_non_redundancy=False):
    result = merge_all(sequence)
    result = result.tolist()
    # print("result", result)
    return list(range(len(result))), result


class Attention(Layer):
    def __init__(self, step_dim,
                 W_regularizer=None, b_regularizer=None,
                 W_constraint=None, b_constraint=None,
                 bias=True, **kwargs):
        """
        Keras Layer that implements an Attention mechanism for temporal data.
        Supports Masking.
        Follows the work of Raffel et al. [https://arxiv.org/abs/1512.08756]
        # Input shape
            3D tensor with shape: `(samples, steps, features)`.
        # Output shape
            2D tensor with shape: `(samples, features)`.
        :param kwargs:
        Just put it on top of an RNN Layer (GRU/LSTM/SimpleRNN) with return_sequences=True.
        The dimensions are inferred based on the output shape of the RNN.
        Example:
            # 1
            model.add(LSTM(64, return_sequences=True))
            model.add(Attention())
            # next add a Dense layer (for classification/regression) or whatever...
            # 2
            hidden = LSTM(64, return_sequences=True)(words)
            sentence = Attention()(hidden)
            # next add a Dense layer (for classification/regression) or whatever...
        """
        self.supports_masking = True
        self.init = initializers.get('glorot_uniform')

        self.W_regularizer = regularizers.get(W_regularizer)
        self.b_regularizer = regularizers.get(b_regularizer)

        self.W_constraint = constraints.get(W_constraint)
        self.b_constraint = constraints.get(b_constraint)

        self.bias = bias
        self.step_dim = step_dim
        self.features_dim = 0

        super(Attention, self).__init__(**kwargs)

    def build(self, input_shape):
        assert len(input_shape) == 3

        self.W = self.add_weight(shape=(input_shape[-1],),
                                 initializer=self.init,
                                 name='{}_W'.format(self.name),
                                 regularizer=self.W_regularizer,
                                 constraint=self.W_constraint)
        self.features_dim = input_shape[-1]

        if self.bias:
            self.b = self.add_weight(shape=(input_shape[1],),
                                     initializer='zero',
                                     name='{}_b'.format(self.name),
                                     regularizer=self.b_regularizer,
                                     constraint=self.b_constraint)
        else:
            self.b = None

        self.built = True

    def compute_mask(self, input, input_mask=None):
        # do not pass the mask to the next layers
        return None

    def call(self, x, mask=None):
        features_dim = self.features_dim
        step_dim = self.step_dim

        e = K.reshape(K.dot(K.reshape(x, (-1, features_dim)), K.reshape(self.W, (features_dim, 1))),
                      (-1, step_dim))  # e = K.dot(x, self.W)
        if self.bias:
            e += self.b
        e = K.tanh(e)

        a = K.exp(e)
        # apply mask after the exp. will be re-normalized next
        if mask is not None:
            # cast the mask to floatX to avoid float64 upcasting in theano
            a *= K.cast(mask, K.floatx())
        # in some cases especially in the early stages of training the sum may be almost zero
        # and this results in NaN's. A workaround is to add a very small positive number ε to the sum.
        a /= K.cast(K.sum(a, axis=1, keepdims=True) + K.epsilon(), K.floatx())
        a = K.expand_dims(a)

        c = K.sum(a * x, axis=1)
        return c

    def compute_output_shape(self, input_shape):
        return input_shape[0], self.features_dim

    def get_config(self):

        config = {"step_dim": self.step_dim, "W_regularizer": self.W_regularizer, "b_regularizer": self.b_regularizer,
                  "W_constraint": self.W_constraint, "b_constraint": self.b_constraint, "bias": self.bias}

        base_config = super(Attention, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))
