"""
Utilities to build keras models
-------------------------------

Below defines a number of utility functions to generate keras models.

The most atomic models are
    * VariableModel which represents a variable.
      The added functionality is that its __call__() function will scale the variable to the sample size
      correctly, e.g. if the variable if of size (2,3) then __call__() will return (batch_size, 2, 3).
    * DenseModel which represents a fully conencted neural network
      It also has a zero_mode which initializes the network such that the initial value is zero,
      while derivatives are randomized.

The two atomic models are wrapped up into a function call
    * dense_model()
      This function creates either a DenseModel or a VariableModel, depending on whether the size of the
      input features: if it is zero, a VariableModel will be returned.
      dense_model() implements also defaulting for user variables and configuration handling

The two top level models are
    * DenseAgent()
      A keras model representing a fully connected model which is parameterized by the 'features' it extracts
      from the 'data' feature set.
    * RecurrentAgent()
      A recurrent agent with the same functionality as DenseAgent, which also allows for recurrent nodes.

April 1st, 2023
@author: hansbuehler
"""

from cdxbasics.logger import Logger
from cdxbasics.util import fmt_list
from cdxbasics.config import Config, Float, Int, to_config # NOQA
from collections.abc import Mapping
import numpy as np
from .util import tf, def_dtype, tf_make_dim
_log = Logger(__file__)

def name(self):
    return self.name if not self.name is None else type(self).__name__

# =====================================================================================
# Raw building blocks
# These models will expect tensors of a specified input dimension in __call__()
# =====================================================================================

class VariableModel( tf.keras.Model ):
    """
    Keras Model which represents a variable.

    The complication here is that such a model does not naturally get informed about the batch dimension of the
    data is it supposed to return. The example code hacks this by looking up *any* member of the 'data' provided
    to call(), and scale the variable accordingly.
    """

    def __init__(self,
                 init,
                 dtype     : tf.DType = def_dtype,
                 name      : str = None,
                 trainable : bool = True):
        """
        Initialie the variable model for a given variable. The model does not take any inputs but returns the
        value of the variable, scaled up to the batch size.

        Parameters
        ----------
            init:
                If an int: initialize with a zero vector of length init
                If a shape: initialize with a zero vector of shape init
                If a numpy array: initialize with this array
            dtype, name, trainable: c.f. tf.keras.Model()
        """
        tf.keras.Model.__init__(self, name=name, dtype=dtype, trainable=trainable )
        if isinstance(init, int):
            init = np.zeros(shape=(init,))
        elif isinstance(init, (tuple,list)):
            init = np.zeros(shape=tuple(init))
        else:
            init = np.asarray( init )
        self._init     = init
        self._variable = tf.Variable( init, trainable=trainable, name="var_" + self.name, dtype=self.dtype )

    def call(self, data, training=False):
        """ Returns the variable, scaled to the current batch size. For this to work, 'data' must contain at least one correct data element """
        assert isinstance( data, (Mapping, tf.Tensor) ), "'data' must be a tensor or a dict, not %s" % type(data).__name__
        def zeros_from_data( data ) -> tf.Tensor:
            """ Returns a zero tensor of dimension one, with the first dimension equal to the batch size """
            if isinstance(data, tf.Tensor):
                while len(data.shape) > 1:
                    data = data[:,0]
                return data*0.
            assert isinstance(data, Mapping), "'data' must be a tensor or a dictionary. Found %s" % type(data).__name__
            for t in data:
                t = data[t]
                d = zeros_from_data(t)
                if not d is None:
                    return d
            return None

        zero = zeros_from_data(data)
        _log.verify( not zero is None, "Cannot determine batch sample size from 'data' of type %s", type(data).__name__ )
        zero = tf_make_dim( zero, len(self._variable.shape)+1 )
        return zero + self._variable[None,...]

    @property
    def num_trainable_weights(self) -> int:
        """
        Returns the number of weights. The gym must have been call()ed once
        Agent needs to have been called at least once
        """
        weights = self.trainable_weights
        return np.sum( [ np.prod( w.get_shape() ) for w in weights ] ) if not weights is None else 0.

    @property
    def variable(self) -> tf.Variable:
        """ Return underlying TF variable """
        return self._variable

    def get_config(self) -> dict:#NOQA
        return dict( init = self._init, dtype=self.dtype, name=self.name, trainable=self.trainable )

class DenseModel( tf.keras.Model ):
    """
    Standard dense Sequential keras neural network.

    Represents a dense network with a given 'depth', 'width', 'activation' function and a final layer with activation function 'final_act' (typicall linear).
    The layer maps a tensors of dimension nInput into tensors of dimension nOutput.

    The model can initialize the model with zero initial value, but with non-trivial initial gradients.
    It does this by returning the difference between two networks, with the same initial weights, but where only
    the first is trainable.

    If the number of inputs is zero, then this function uses a VariableModel initialized at zero.
    """

    def __init__(self,  nInput     : int,
                        nOutput    : int,
                        width      : int = 50,
                        depth      : int = 3,
                        activation : str = "relu",
                        final_act  : str = "linear",
                        zero_model : bool = False,
                        regression : bool = False,
                        dtype      : tf.DType = def_dtype,
                        name       : str = None,
                        trainable  : bool = True
                    ):
        """
        Represents a dense network with a given 'depth', 'width', 'activation' function and a final layer with activation function 'final_act' (typicall linear).
        The layer maps a tensors of dimension nInput into tensors of dimension nOutput.

        Parameters
        ----------
            nInput :
                second dimension of the input vector to this model, e.g. it expects tensors of shape [None, nInput]
                If nInput is zero, then this function returns a VariableModel( nOutput )
            nOutput:
                number of output states
            network construction:
                width        : width of the network
                depth        : depth
                activation   : activation function in core network
                final_activation : activation function to compress last 'width' to nOutput. Usually linear.
                zero_model   : whether the model is initialzed to zero initial value (but not zero gradients)
                               Practically, the model constructs both the original model F and a non-trainable
                               model F', then sets the weights of F' to the initial weights of F, and defines
                               the full model as M=F-F'. If 'trainable' is False then this function returnbs a network
                               with zero initial value.
                regression   : hard set the network to a pure regression model.
                               This is equivalent to setting depth = 0, width = nInput, and final_activation = 'linear'.
            dtype, name, trainable :
                see tf.keras.Model()
        """
        tf.keras.Model.__init__(self, name=name, dtype=dtype, trainable=trainable )

        self._nInput      = int(nInput)
        self._nOutput     = int(nOutput)
        assert self._nInput > 0, nInput
        assert self._nOutput > 0, nOutput

        self._get_config = dict( nInput     = self._nInput,
                                 nOutput    = self._nOutput,
                                 width      = width,
                                 depth      = depth,
                                 activation = activation,
                                 final_act  = final_act,
                                 zero_model = zero_model,
                                 regression = regression,
                                 dtype      = dtype,
                                 name       = name,
                                 trainable = trainable)

        if regression:
            depth      = 0
            width      = nInput
            final_act  = 'linear'

        def dense(width,activation, x1, x2 ):
            """ Utility function to construct zero_model layers """
            d1 = tf.keras.layers.Dense(units=width,
                                       activation=activation,
                                       use_bias=True, dtype=dtype,
                                       trainable=trainable )
            if x2 is None:
                return d1(x1), None

            d2 = tf.keras.layers.Dense(units=width,
                                       activation=activation,
                                       use_bias=True, dtype=dtype,
                                       trainable=False )
            x1 = d1(x1)
            x2 = d2(x2)
            return x1, x2

        inp       = tf.keras.layers.Input( shape=(nInput,), dtype=dtype )
        x1, x2    = ( inp, inp if zero_model else None )
        for d in range(depth):
            x1, x2    = dense( width, activation, x1, x2 )
        x1, x2 = dense( nOutput, final_act, x1, x2 )
        x  = tf.keras.layers.Subtract()([x1, x2]) if not x2 is None else x1
        m  = tf.keras.Model( inputs=inp, outputs=x, name=name )
        if zero_model:
            for v1, v2 in zip( m.trainable_weights, m.non_trainable_weights ):
                v2.assign( v1.value() )
        self._model = m

    def __call__(self, features : tf.Tensor, **kwargs ) -> tf.Tensor:
        """ Execute model. """
        assert isinstance( features, tf.Tensor ), "'features' must be a tensor, not %s" % type(features).__name__
        _log.verify( len(features.shape) == 2 and int(features.shape[1]) == self._nInput, "Model '%s' input error: expected features tensor of shape [None, %ld] but found tensor of shape %s", name(self) , self._nInput, features.shape.as_list() )
        return self._model(features,**kwargs)

    def get_config(self) -> dict:#NOQA
        return self._get_config

    @property
    def num_trainable_weights(self) -> int:
        """
        Returns the number of weights. The gym must have been call()ed once
        Agent needs to have been called at least once
        """
        weights = self.trainable_weights
        return np.sum( [ np.prod( w.get_shape() ) for w in weights ] ) if not weights is None else 0.


def dense_model( nInput     : int,
                 nOutput    : int,
                 config     : Config = None,
                 kwargs_cfg : dict = None,
                 **kwargs
                 ) -> tf.keras.Model:
    """
    Create standard dense Sequential keras neural network.

    The function creates a dense network of 'depth' and 'width' with activation function 'activation'.
    The final layer then condenses the last 'width' nodes to 'nOutput' nodes, usually with a linear 'final_act'.
    The model can initialize the model with zero initial value, but with non-trivial initial gradients.
    It does this by returning the difference between two networks, with the same initial weights, but where only
    the first is trainable.

    The function takes in a 'config' which lets a user set the geometry of the network, and default values set
    by the code developer.

    This function expects data to be passed as a tensor of dimension [None, nInput].
    See Agent() for a model which can extract named elements from a feature dictionary on the fly.

    If the number of inputs is zero, then this function returns a VariableModel initialized at zero.

    Parameters
    ----------
        nInput :
            second dimension of the input vector to this model, e.g. it expects tensors of shape [None, nInput]
            If nInput is zero, then this function returns a VariableModel( nOutput )
        nOutput:
            number of output states

        kwargs_cfg, **kwargs :
            Only one of the these two can be non-empty.
            User settings to specify the following:
                width        : width of the network
                depth        : depth
                activation   : activation function in core network
                final_activation : activation function to compress last 'width' to nOutput. Usually linear.
                zero_model   : whether the model is initialzed to zero initial value (but not zero gradients)
                               Practically, the model constructs both the original model F and a non-trainable
                               model F', then sets the weights of F' to the initial weights of F, and defines
                               the full model as M=F-F'. If 'trainable' is False then this function returnbs a network
                               with zero initial value.
                regression   : hard set the network to a pure regression model.
                               This is equivalent to setting depth = 0, width = nInput, and final_activation = 'linear'.

                Each of the above can either be specified directly, or they can be read from a Config dictrionary.
                In that case the function still allows providing default values.

                For example, instead of setting width=50, we may pass a Config object with config=config, and also a default
                value def_width=50.

            dtype, name, trainable :
                see tf.keras.Model()
    Returns
    -------
        Keras model.
    """
    assert kwargs_cfg is None or len(kwargs) == 0, "Cannot specify 'kwargs_cfg' and **kwargs"
    kwargs          = to_config(kwargs_cfg if not kwargs_cfg is None else kwargs, config_name="kwargs_dense_model")

    width           = kwargs('width', None, (None, Int>0))
    depth           = kwargs('depth', None, (None, Int>=0))
    activation      = kwargs('activation', None, (None, str))
    final_act       = kwargs('final_act', None, (None,str))
    zero_model      = kwargs('zero_model', None, (None, bool))
    regression      = kwargs('regression', None, (None, bool))

    dtype           = kwargs('dtype', def_dtype )
    name            = kwargs('name', None, (str, None))
    trainable       = kwargs('trainable', True, bool)

    def_width       = kwargs("def_width", 50, Int>0 )
    def_depth       = kwargs("def_depth", 3, Int>=0 )
    def_activation  = kwargs("def_activation", 'relu', str)
    def_final_act   = kwargs("def_final_act", "linear", str)
    def_zero_model  = kwargs("def_zero_model", True, bool)
    def_regression  = kwargs("def_regression", False, bool)

    kwargs.done() # catch developer typos

    config          = config if not config is None else Config()
    width           = config("width", def_width, Int>0, "Width") if width is None else width
    depth           = config("depth", def_depth, Int>=0, "Depth") if depth is None else depth
    activation      = config("activation", def_activation, str, "Activation function") if activation is None else activation
    final_act       = config("final_activation",def_final_act, str, "Final activation function") if final_act is None else final_act
    zero_model      = config("zero_model", def_zero_model, bool, "Whether to initialze values (but not derivatives) of the model with zero") if zero_model is None else zero_model
    regression      = config("simple_regression", def_regression, bool, "Learn simple regression model only") if regression is None else regression

    config.done() # catch user errors

    if nInput == 0:
        return VariableModel( int(nOutput), name=name, dtype=dtype, trainable=trainable )

    return DenseModel( nInput  = nInput,
                       nOutput = nOutput,
                       width   = width,
                       depth   = depth,
                       activation = activation,
                       final_act  = final_act,
                       zero_model = zero_model,
                       regression = regression,
                       dtype = dtype,
                       name = name,
                       trainable = trainable)

# =====================================================================================
# Agents
# Agents extract named features from the 'data' given to __call__
# =====================================================================================

class DenseAgent(tf.keras.Model):
    """
    Standardized generic agent which will use named features as inputs, and will extract those from the 'data' dictionary provided.
    All features are flattened before passed on to the agent.

    If no features are selected, then this model becomes a VariableModel, e.g. it is a variable of size nOutput.
    """

    def __init__(self, nOutput : int, state_size : int = 0, config : Config = None, *, kwargs_cfg : dict = None, **kwargs ):
        """
        Create standard Agent.

        The model implements a dense network of 'depth' and 'width' with activation function 'activation'.
        The final layer then condenses the last 'width' nodes to 'nOutput' nodes, usually with a linear 'final_act'.
        The model will extract the user-requested features from the 'data' dictionary provided to __call__.
        The user specifies the desired features with the 'features' config keyword. The model can be made to always
        use some features by using 'required_features'.

        The model can initialize the model with zero initial value, but with non-trivial initial gradients.
        It does this by returning the difference between two networks, with the same initial weights, but where only
        the first is trainable.

        If the model is created without features it will represent a VariableModel.

        Parameters
        ----------
            nOutput :
                number of output states
            state_size :
                If non-zero, this specifies the second dimension of an additional state vector which is to be passed
                to the agent when calling() it.
                This allows the calling user to add a fixed state to the otherwise dynamic features extracted during
                runtime

            kwargs_cfg, **kwargs:
                Only one of these can be non-empty.
                They are both used to drive the configuration of the underlying network.
                The general principle for each parameter is the same, and allows the developer to (a) set a default value for each
                setting, and (b) either fix the setting or let the user set it using a 'config' object.
                Example: 'depth'

                    def_depth       : defines the default depth for the network to be created. This default is set by the developer.
                    depth           : if set, then depth is fixed by the developer to this number. The user cannot overwrite this.
                    config('depth') : if kwargs contains a 'config' element, and if 'depth' is not set, then the function will
                                      read 'depth' from the config as specified to the user.

                The settings thus controlled are:
                    width        : width of the network. Default is 50
                    depth        : depth, default 3
                    activation   : activation function in core network, default 'relu'
                    final_activation : activation function to compress last 'width' to nOutput. Usually left to its default 'linear'.
                    zero_model   : whether the model is initialzed to zero initial value (but not zero gradients), default True.
                                   Practically, the model constructs both the original model F and a non-trainable
                                   model F', then sets the weights of F' to the initial weights of F, and defines
                                   the full model as M=F-F'. If 'trainable' is False then this function returnbs a network
                                   with zero initial value.
                    regression   : hard set the network to a pure regression model. This is a debugging option with default False.
                                   This is equivalent to setting depth = 0, width = nInput, and final_activation = 'linear'.

                A more complex example is that of selecting features for the underlying agent.
                Those are specified by name. The agent will then drive extraction of the relevant data from the data universe automatically.

                    def_features     : just as in the above example, these are the default features for the agent.
                    required_features: features which the agent always needs to use
                    allow_no_features: whether or not to allow an empty list fo features. This is set to False if required_features

                    features         : if specified by the developer, then these features are always used.
                                       Note that if required_features are defined, then the two lists are merged.

                    config('features') : if 'features' is not specified, then the user may choose her own features.

                Finally, both kwargs_cfg and kwargs may also contain standard keyword parameters for tf.keras.Model() such as dtype, name, trainable.
        """
        assert kwargs_cfg is None or len(kwargs) == 0, "Cannot specify 'kwargs_cfg' and **kwargs"

        kwargs                   = to_config(kwargs_cfg if not kwargs_cfg is None else kwargs, config_name="kwargs_DenseAgent")
        nOutput                  = int(nOutput)
        state_size               = int(state_size)
        _log.verify( nOutput > 0, "'nOutput' must be positive. Found %ld", nOutput )
        _log.verify( state_size >= 0, "'state_size' must not be negative. Found %ld", state_size )

        dtype                    = kwargs('dtype', def_dtype )
        name                     = kwargs('name', None, (str, None))
        trainable                = kwargs('trainable', True, bool)
        tf.keras.Model.__init__(self, name=name, dtype=dtype, trainable=trainable )

        self._model              = None
        self._available_features = None
        self._size_features      = None
        self._nOutput            = nOutput
        self._state_size         = state_size

        self._features           = kwargs('features', None, (None, list))
        def_features             = kwargs("def_features", [], list)
        req_features             = kwargs("required_features", [], list)
        allow_no_features        = kwargs("allow_no_features", True, bool) if len(req_features)==0 else False
        self._kwargs             = kwargs.detach() # store kwargs for a subsequent call to dense_model()

        config                   = config if not config is None else Config()
        self._features           = config("features", def_features, list, "Names of features to be used by this agent") if self._features is None else self._features
        self._features           = list(set( self._features + req_features ))
        self._config             = config.detach() # store config for a subsequent call to dense_model()
        self._features.sort()
        _log.verify( len(self._features) > 0 or allow_no_features, "'features' cannot be left empty")
        config.done() # catch user errors
        kwargs.done() # catch dev errors

    # ----------------------------
    # keras build/call
    # ----------------------------

    def build(self, shapes_data_and_state : dict ):
        """ Extract the requested features from the shapes provided """
        assert self._model is None, "'build' called twice?"

        state_shape = shapes_data_and_state.get('state', None)
        shapes      = shapes_data_and_state['data']

        self._available_features = list(shapes.keys())
        self._available_features.sort()

        self._size_features = 0
        missing         = []
        for f in self._features:
            fs = shapes.get(f,None)
            if fs is None:
                missing.append(f)
                continue
            # we will flatten all features
            if len(fs) > 2:
                fs = [ fs[0], np.product( fs.as_list()[1:] ) ]
            self._size_features += fs[1] if len(fs) > 0 else 1

        if len(missing) > 0:
            missing   = fmt_list(missing)
            available = fmt_list(self._available_features, "(none)")
            _log.throw("Could not extract the following features: %s. Available features are: %s", missing, available)

        self._model = dense_model(
                nInput      = self._size_features + self._state_size,
                nOutput     = self._nOutput,
                config      = self._config,
                kwargs_cfg  = self._kwargs
                )

    def call(self, data_with_state : dict, training : bool = False) ->  tf.Tensor:
        """
        Return action based on data provied
        This construction here is a bit convoluted. Would prefer to just use __call__ TODO
        """
        assert not self._model is None, "build() was not called...?"
        data     = data_with_state['data']
        state    = data_with_state['state'] if self._state_size > 0 else None
        features = None
        if len(self._features) > 0:
            features  = [ data[f] for f in self._features ]
            features  = [ tf_make_dim( f, target_dim=2 ) for f in features ]
            features  = tf.concat( features, axis=1 ) if len(features) > 1 else features[0]
            assert features.shape[1] == self._size_features, "Internal error: %ld != %ld" % ( features.shape[1], self._size_features)

        if self._state_size > 0:
            _log.verify( not state is None, "Error calling '%s': state_size was set to %ld, hence you need to provide a state. Found 'None'")
            _log.verify( len(state.shape) == 2 and int(state.shape[1]) == self._state_size, "Error calling '%s': state_size was set to %ld, hence you need to provide a state of shape [None, %ld]. Found tensor of shape %s", self._state_size, self._state_size, state.shape.as_list())
            features = tf.concat( [features, state], axis=1) if not features is None else state
        else:
            _log.verify( state is None, "Error calling '%s': model is not recurrent, but a state was provided. Set state to 'None'.", name(self) )

        assert features is None or isinstance( features, tf.Tensor ), "'features' must be a tensor, not %s" % type(features).__name__
        return self._model( features if not features is None else data, training=training )

    def __call__(self, data : dict, state : tf.Tensor = None, **kwargs ):
        """
        Compute agent result.


        Parameters
        ----------
            data : dict
                Dictionary containing the models' named features for this model. Does not include 'state'
            state : tf.Tensor or None
                If the model has a state, then 'state' must be set to a matrix tensor with second dimension equal to self.size_recurrent_state.
                For the first call, this is the initial state. For subsequent calls, provide the 'new_state' of the previous __call__()
                If the model does not have a state, then 'state' must be None
            **kwargs:
                see tf.keras.Model.__call__()

        Returns
        -------
            A tuple (result, new_state)
            If the model has a state, then 'new_state' is the state to be passed to the next function call.
            If the model does not have a state, then 'state' is None
        """
        assert isinstance( data, Mapping ), "'data' must be dictionary or similar, not '%s'" % type(data).__name__
        if self._state_size > 0:
            _log.verify( isinstance( state, tf.Tensor ), "'state' must be tensor of shape [None, %ld], not a type '%s'", self._state_size, type(state).__name__ )
        else:
            _log.verify( state is None, "'state' must be None, not '%s'", type(state).__name__  )
        return tf.keras.Model.__call__(self, dict( data=data, state=state ) if not state is None else dict(data=data), **kwargs )

    # ----------------------------
    # data access
    # ----------------------------

    @property
    def features(self) -> list:
        """
        Returns the features used by this agent
        Agent needs to have been called at least once
        """
        assert not self._model is None, "agent model needs to be called at least once before calling this function"
        return self._features

    @property
    def size_features(self) -> int:
        """ Returns the size of the featues of this agent """
        return self._size_features

    @property
    def has_features(self) -> bool:
        """ Whether the agent has any features """
        return len(self._features) > 0

    @property
    def available_features(self) -> list:
        """
        Returns the sorted list of available features for this agent.
        Agent needs to have been called at least once
        """
        assert not self._model is None, "agent model needs to be called at least once before calling this function"
        return self._available_features

    @property
    def num_output(self) -> int:
        """ Returns the dimnension of the action output tensor """
        return self._nOutput

    @property
    def num_trainable_weights(self) -> int:
        """
        Returns the number of weights. The gym must have been call()ed once
        Agent needs to have been called at least once
        """
        assert not self._model is None, "agent model needs to be called at least once before calling this function"
        weights = self.trainable_weights
        return np.sum( [ np.prod( w.get_shape() ) for w in weights ] ) if not weights is None else 0.

    @property
    def has_state(self):
        """ Whether this agent is recurrent """
        return self._state_size > 0

    @property
    def state_size(self):
        """ Returns the size of the recurrent state """
        return self._state_size

    @property
    def dim_all_features(self) -> int:
        """
        Returns the size of the total features vector after flattening
        Agent needs to have been called at least once
        """
        assert not self._model is None, "agent model needs to be called at least once before calling this function"
        return self._size_features

class RecurrentAgent(tf.keras.Model):
    """
    Recurrent agent

    The recurrence framework for the Deep Hedging pattern is explicit - it requires the user to explicitly handle states as part of the data sets
    used doing training in the 'gym' framework.

    The core pattern is as follows:

    def build(self, shapes):
        self.agent          = RecurrentAgent(...)

    def call(self, data, training=False):

        features_time_0 = data(...)
        state           = agent.initial_state(features_time_0)
        for t in range(nSteps):
            features_t    = data(...)
            action, state = self.agent( features_t, state=state, training=training )
            ....

    See discussion in RecurrentAgent.__init__() for further details.
    """

    def __init__(self, nOutput : int, config : Config = None, init_config : Config = None, *, init_kwargs : dict = None, main_kwargs : dict = None, **kwargs ):
        """
        Create recurrent Agent.

        This model implements a recurrent agent with LSTM-like recurent nodes.

        Let s' be the previous state and N be the network. Let f be the current feature set.
        Then

            a
            r = N( s', f )
            g

        where 'a' is the new action, 'g' is the gate and 'r' is the new candidate state.
        Let

            c = sigmoid(g)

        and set the new state to:

            s' := c * r' + (1-c) s

        The network N itself is constructed with the same method as an Agent, e.g. it is a dense network with specified
        activation function, depth, and width, and a final, usually linear, layer.

        The model will extract the user-requested features from the 'data' dictionary provided to __call__.
        The user specifies the desired features with the 'features' config keyword. The model can be made to always
        use some features by using 'required_features'.

        Important
        ---------
        The model's __call__() function expects that the current state is provided.
        In addition, __call__() returns not a single tensor, but the tuple of the main result and the new state to be used in the next logical call.
        See __call__()

        Parameters
        ----------
            nOutput :
                number of outputs.

            config : Config
                User-driven configuration for this agent.
                Main fields are:
                        'init'          :  network specification for the initial agent
                        'recurrence'    : number of recurrent nodes
                        Rest is sent to DenseAgent()

            kwargs:
                You can only specify kwargs or init_kwargs and main_kwargs.
                If kwargs is specified, then all its keys starting with 'init_' will be moved to init_kwargs, with the remainder copied to main_kwargs.

            init_kwargs:
                Keywords which drive the initialization of the initial state for the recurrent network.
                Typically, the initial state
                    - has a less deep network, e.g. with smaller depths and width.
                    - only uses features which are meaningful at time 0, e.g. exclude keys such as 'time_left' in deep hedging.
                The keywords available are described in DenseAgent.__init__()

            main_kwargs:
                Keywords which drive the configuration of the main agent network.
                Most keywords available are described in DenseAgent.__init__().

                In addition:
                    recurrence       : If specified, sets the number of recurrent states for this network. In this case 'recurrence' cannot be set by the user.
                    def_recurrence   : sets the default number of recurrent states for this network. The default is 5.
        """
        assert (init_kwargs is None and main_kwargs is None) or len(kwargs) == 0, "Cannot specify 'init_kwargs', 'main_kwargs' and **kwargs"

        init_kwargs = to_config( { k[5:] : kwargs[k] for k in kwargs if k[:5] == "init_" } if init_kwargs is None else init_kwargs, config_name="kwargs_Recurrent_init" )
        main_kwargs = to_config( { k     : kwargs[k] for k in kwargs if k[:5] != "init_" } if main_kwargs is None else main_kwargs, config_name="kwargs_Recurrent_main" )

        dtype                    = main_kwargs('dtype', def_dtype )
        name                     = main_kwargs('name', None, (str, None))
        trainable                = main_kwargs('trainable', True, bool)
        init_kwargs['dtype']     = dtype
        init_kwargs['name']      = name if name is None else (name + "_init")
        init_kwargs['trainable'] = trainable

        tf.keras.Model.__init__(self, name=name, dtype=dtype, trainable=trainable )

        self._nOutput     = int(nOutput)
        assert self._nOutput > 0, "Ouput must be positive, not %ld" % nOutput

        recurrence       = main_kwargs('recurrence', None, (None, Int>=0))
        def_recurrence   = main_kwargs('def_recurrence', 5, Int>=0)

        # handle main recurrence
        config           = config if not config is None else Config()
        self._recurrence = config("recurrence", def_recurrence, Int>=0, "Number of recurrent nodes") if recurrence is None else recurrence
        config_init      = init_config if not init_config is None else Config()
        config_main      = config

        self._main_agent  = DenseAgent( nOutput=self._nOutput+2*self._recurrence, state_size=self._recurrence, config=config_main, kwargs_cfg=main_kwargs )
        self._init_agent  = DenseAgent( nOutput=self._nOutput+self._recurrence, config=config_init, kwargs_cfg=init_kwargs )
        init_kwargs.done() # catch misspelled keywords, and catches remaining config() items
        main_kwargs.done() # catch misspelled keywords, and catches remaining config() items

    # ----------------------------
    # Execution
    # ----------------------------

    def initial_action_and_state(self, features : dict, **kwargs ) -> tuple:
        """
        Return the value of the initial action and state.
        """
        assert isinstance( features, Mapping ), "'features' must be dictionary or similar"
        r      = self._init_agent( features, **kwargs )
        if self._recurrence == 0:
            return r, None
        n      = self._recurrence
        state  = r[:,:n]
        action = r[:,n:]
        return action, state

    def __call__(self, features : dict, state : tf.Tensor, **kwargs ) -> tuple:
        """
        Compute recurrent action and state

        This function accepts a dictionary of generic named features, and a dedicated state.
        The state variable should be initialized with the initial state returned by
        self.initial_agent_and_state() at the beginning of the recurrent sequence.

        Parameters
        ----------
            features :
                Dictionary of features
            state :
                Tensor which represents the current state of the recurrent agent.
                For the first step, initialize the state with initial_state().
            **kwargs:
                passed to the underlying model call

        Returns
        -------
            This function returns (action, state)
        """
        assert isinstance( features, Mapping ), "'features' must be dictionary or similar"
        if self._recurrence == 0:
            _log.verify( state is None, "Model '%s' is not recurrent, hence 'state' must None", name(self))
            return self._main_agent( features, **kwargs ), None

        _log.verify( not state is None, "Model '%s': 'state' cannot be 'None'. Use initial_state()", name(self))
        _log.verify( len(state.shape) == 2 and int(state.shape[1]) == self._recurrence, "Model '%s': state is expected to be of shape [None, %ld]. Found shape %s", name(self), self._recurrence, state.shape.as_list())
        result    = self._main_agent( features, state=state, **kwargs )
        n         = self._recurrence
        new_state = result[:,0*n:1*n]
        gate      = result[:,1*n:2*n]
        action    = result[:,2*n:]
        assert action.shape[1] == self._nOutput, "Internal error: %ld != %ld" % (action.shape[1], self._nOutput)
        gate      = tf.math.sigmoid( gate )
        state     = state * gate + (1. - gate) * new_state
        return action, state

    # ----------------------------
    # syntatic sugar
    # ----------------------------

    @property
    def has_features(self) -> bool:
        """ Whether the agent has any features """
        return self._init_agent.has_features

    @property
    def has_state(self) -> bool:
        """ Whether this agent has an initial state """
        return self._recurrence > 0

    @property
    def num_trainable_weights(self) -> int:
        """
        Returns the number of weights. The gym must have been call()ed once
        Agent needs to have been called at least once
        """
        weights = self.trainable_weights
        return np.sum( [ np.prod( w.get_shape() ) for w in weights ] ) if not weights is None else 0.

    @property
    def is_recurrent(self) -> bool:
        """ Whether the agent is recurrent """
        return self._recurrence > 0

    @property
    def recurrence(self) -> int:
        """ Number of recurrent states. """
        return self._recurrence

    @property
    def init_agent(self) -> DenseAgent:
        """ Returns the DenseAgent used for the initial state. Returns None if agent is not recurrent"""
        return self._init_agent

    @property
    def main_agent(self) -> DenseAgent:
        """ Returns the DenseAgent used for the main (loop) action """
        return self._main_agent

