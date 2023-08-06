"""
TF basic utilities
------------------
Import this file in all deep hedging files.
June 30, 2022
@author: hansbuehler
"""

from cdxbasics.logger import Logger
from cdxbasics.util import isAtomic
import numpy as np
import tensorflow as tf
import math as math
import inspect as inspect
import datetime as datetime
from collections.abc import Mapping, Collection

_log = Logger(__file__)

# -------------------------------------------------
# Manage tensor flow
# -------------------------------------------------

TF_VERSION = [ int(x) for x in tf.__version__.split(".") ]
TF_VERSION = TF_VERSION[0]*100+TF_VERSION[1]
_log.verify( TF_VERSION >= 210, "Tensor Flow version 2.10 required. Found %s", tf.__version__)

TF_NUM_GPU = len(tf.config.list_physical_devices('GPU'))
TF_NUM_CPU = len(tf.config.list_physical_devices('CPU'))

def_dtype = tf.float32  # this is the default srttpe
tf.keras.backend.set_floatx(def_dtype.name)

"""
DIM_DUMMY
Each world data dictionary must have an element with this name, whcih needs to be of dimension (None,1)
This is used in layers.VariableLayer in order to scale the variable up to the number of samples

The reason the dimension is (None,1) and not (None,) is that older Tensorflow versions auto-upscale data
of dimension (None,) to (None,1) anyway.

It's not a pretty construction but there seems to be no other nice way in TF to find our current sample size.
"""

DIM_DUMMY = "_dimension_dummy"

# -------------------------------------------------
# TF <--> NP
# -------------------------------------------------

def tfCast( x, native = True, dtype=def_dtype ):
    """
    Casts an object or a collection of objecyts iteratively into tensors.
    Turns all custom dictionaries (such as PrettyDict) into dictionaries unless 'native' is False.

    Parameters
    ----------
        x
            object. Can be list of lists of dicts of numpys etc
                - numpy arrays become tenors
                - tensors will be cast to dtype, if required
                - atomic variables become tensor constants
                - None is None
        native : bool, optional
            True
                - lists-types of x's becomes lists of tensors
                - dicts-types of x's becomes dicts of tensors
            False:
                - lists-types of x's stay list-types
                - dicts-types of x's stay dict-types

        dtype : tf.DType, optional
            Overwrite dtype

    Returns
    -------
        tensors.
    """
    if x is None:
        return None
    if isinstance(x, tf.Tensor):
        return x if ( dtype is None or x.dtype == dtype ) else tf.convert_to_tensor( x, dtype=dtype )
    if isinstance(x, np.ndarray):
        return tf.convert_to_tensor( x, dtype=dtype )
    if isAtomic(x):
        return tf.constant( x, dtype=dtype )
    if isinstance(x, dict):
        d = { _ : tfCast(x[_], dtype=dtype) for _ in x }
        return d if native or (type(x) == 'dict') else x.__class__(d)
    if isinstance(x, list):
        l = [ tfCast(_, dtype=dtype) for _ in x ]
        return l if native or (type(l) == 'list') else x.__class__(l)

    _log.verify( False, "Cannot convert object of type '%s' to tensor", x.__class__.__name__)
    return None

def npCast( x, dtype=None ):
    """
    Casts an object or a collection of objecyts iteratively into numpy arrays.

    Parameters
    ----------
        x
            object. Can be list of lists of dicts of tensors etc
                - tensors become numpy arrays (copies !)
                - numpy arrays will be cast into dtype if necessaryt
                - atomic variables become arrays with shape ()
                - lists of x's becomes lists of npCast(x)'s
                - dicts of x's becomes dicts of npCast(x)'s
                - None returns None

        dtype : tf.DType, optional
            Overwrite dtype

    Returns
    -------
        numpys.
    """
    if x is None:
        return None
    if isinstance(x, tf.Tensor):
        return np.asarray( x, dtype=dtype )
    if isinstance(x, np.ndarray):
        return np.asarray( x, dtype=dtype )
    if isAtomic(x):
        return np.array(x, dtype=dtype )
    if isinstance(x, dict):
        d  = { _ : npCast(x[_], dtype=dtype) for _ in x }
        return d if type(x) == 'dict' else x.__class__(d)
    if isinstance(x, list):
        l = [ npCast(_, dtype=dtype) for _ in x ]
        return l if type(l) == 'list' else x.__class__(l)

    return  np.asarray( x, dtype=dtype )

def tf_dict( dtype=None, **kwargs ):
    """ Return a (standard) dictionary of tensors """
    return tfCast(kwargs, dtype=dtype)

# -------------------------------------------------
# Loss
# -------------------------------------------------

def get_sample_size( data : dict, raise_error : bool = True ) -> tf.Tensor:
    """
    Extract the current sample size from a 'data' dictionary as it is usually passed to
    tf.keras.layers.Layer.__call__ or tf.kersas.Model.__call__

    Parameters
    ----------
        data : dict or tensor
            Read batch sample size from this object
        raise_error : bool
            If True, an exception is rasied in case no tensor could be found
    Returns
    -------
        Returns first dimension of the first tensor this function finds a tensor, or 0.
        Note that this function may return None if the current sample size is not set yet, for example
        in
    """
    if isinstance(data, tf.Tensor):
        assert data.shape[0] is None or int(data.shape[0])>0, data.shape
        return int(data.shape[0]) if not data.shape[0] is None else None
    if isinstance(data, Mapping):
        for x in data.values():
            l = get_sample_size(x)
            if l>0:
                return l
    else:
        _log.verify( isinstance(data, Collection), "Cannot determine data sample size for type %s", str(type(x)))
        for x in data:
            l = get_sample_size(x)
            if l>0:
                return l
    _log.verify( not raise_error, "Cannot determine sample size: no tensors found in 'data'")
    return 0

# -------------------------------------------------
# Loss
# -------------------------------------------------

@tf.function(reduce_retracing=True)
def default_loss( y_true,y_pred ):
    """ Default loss: ignore y_true """
    return y_pred

# -------------------------------------------------
# TF flattening
# -------------------------------------------------

if False:
    # below code seems more natural, but does not work with None dimensions
    def tf_make_dim( tensor : tf.Tensor, target_dim : int = 2, name : str = None ) -> tf.Tensor:
        """
        Ensure a tensor as a given dimension by either flattening at the end to
        reduce diemnsions, or adding tf.newaxis to increase them.

        x = tf.Tensor( np.array((16,8,4,2)) )
        tf_back_flatten( x, dim = 1)   --> shape [16*8*4*2]
        tf_back_flatten( x, dim = 2)   --> shape [16,8*4*2]
        x = tf.Tensor( np.array((16,)) )
        tf_back_flatten( x, dim = 2)   --> shape [16,1]

        Parameters
        ----------
            tensor : tf.Tensor
                A tensor
            target_dim : int
                target dimension of the flattened tensor.
            name : str
                Name or None. Name will not be set if the current shape of the tensor matches 'target_dim'

        Returns
        -------
            Tensor of dimension 'target_dim'
        """
        target_dim = int(target_dim)
        _log.verify( target_dim > 0, "'target_dim' most be positive")
        dim        = len(tensor.shape)

        if dim > target_dim:
            target_shape = [ int(tensor.shape[i]) if tensor.shape[i] is None else None for i in range(target_dim) ]
            target_shape[target_dim-1] = np.prod( [ int(i) for i in tensor.shape[target_dim-1:] ] )
            tensor       = tf.reshape( tensor, tuple(target_shape), name=name )
        elif dim < target_dim:
            target_shape = [ int(i) if not i is None else None for i in tensor.shape ]
            target_shape += [1] * ( target_dim - len(tensor.shape) )
            tensor       = tf.reshape( tensor, tuple(target_shape), name=name )

        return tensor

def tf_back_flatten( tensor : tf.Tensor, target_dim : int = 2) -> tf.Tensor:
    """
    Flattens a tensor while keeping the first 'dim'-1 axis the same.

    x = tf.Tensor( np.array((16,8,4,2)) )
    tf_back_flatten( x, dim = 1)   --> shape [16*8*4*2]
    tf_back_flatten( x, dim = 2)   --> shape [16,8*4*2]
    ...

    Use case: assume we are given features for an ML model.
    First dimension is number of Samples. Subsequent dimensions might be present, but are not relevant for network construction.
    This function allows flattening it such that the first dimension remains the number of samples, while the rest is flattened.

    Use tf_make_dim to also handles whose existing dimension is less than target_dim

    Parameters
    ----------
        tensor : tf.Tensor
            A tensor
        target_dim : int
            max dimension of the flattened tensor.

    Returns
    -------
        Flat tensor.
    """
    _log.verify( target_dim > 0 and target_dim <= len(tensor.shape), "'target_dim' most be positive and not exceed dimension of tensor, %ld. Found target_dim %ld. If this intended, use 'tf_make_dim' instead", len(tensor.shape), target_dim)
    if len(tensor.shape) > target_dim:
        splits = [ tf_back_flatten( tensor[...,_], target_dim=target_dim ) for _ in range(tensor.shape[-1]) ]
        tensor = tf.concat( splits, axis=-1 )
    return tensor

def tf_make_dim( tensor : tf.Tensor, target_dim : int = 2) -> tf.Tensor:
    """
    Ensure a tensor as a given dimension by either flattening at the end to
    reduce diemnsions, or adding tf.newaxis to increase them.

    x = tf.Tensor( np.array((16,8,4,2)) )
    tf_back_flatten( x, dim = 1)   --> shape [16*8*4*2]
    tf_back_flatten( x, dim = 2)   --> shape [16,8*4*2]
    x = tf.Tensor( np.array((16,)) )
    tf_back_flatten( x, dim = 2)   --> shape [16,1]

    Parameters
    ----------
        tensor : tf.Tensor
            A tensor
        target_dim : int
            target dimension of the flattened tensor.

    Returns
    -------
        Flat tensor.
    """
    try:
        if len(tensor.shape) > target_dim:
            return tf_back_flatten(tensor,target_dim)
        while len(tensor.shape) < target_dim:
            tensor = tensor[...,tf.newaxis]
        return tensor
    except AttributeError as e:
        _log.throw( "Error converting tensor to dimension %ld: %s\nTensor is %s of type %s", target_dim, e, str(tensor), type(tensor) )

