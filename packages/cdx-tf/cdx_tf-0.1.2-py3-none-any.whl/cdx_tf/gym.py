"""
Keras Model base class for Gym models
-------------------------------------
* Cachable
* Keeps best state
* Optimized for async training


Implementation pattern:

    * Create a new gym by deriving from Gym.
      Make use of layers.DenseAgent, layers.RecurrentAgent and monetary_utility.MonetartyUtility to generate the actual networks
      with their flexible design pattern.

    * Derive a "ProgressData" class
      which is used to collect progress information durinbg training.
      This ProgressData will be serialized as part of chaching and when updating the central GUI server during multi-process/multi-machine
      training. Therefore it is imparative that
          1) The data set is kept concise
          2) It can easily be pickled

Feb 25, 2023
@author: hansbuehler
"""

from cdxbasics.verbose import Context, quiet
from cdxbasics.config import Config, Int, Float#NOQA
from cdxbasics.logger import Logger
from cdxbasics.prettydict import PrettyDict
from cdxbasics.util import fmt_now, fmt_seconds, fmt_datetime, fmt_big_number, _fmt, fmt_list
from cdxbasics.subdir import SubDir, uniqueFileName48, CacheMode
from cdxbasics.np import mean, err
from .util import npCast, tfCast, def_dtype, TF_VERSION, default_loss, get_sample_size
from .optimizer import create_optimizer
from collections.abc import Mapping
import tensorflow as tf
from enum import Enum
import numpy as np
import time as time
import psutil as psutil
import sys as sys
from datetime import datetime, timedelta

_log = Logger(__file__)

dtype = def_dtype

def to_config(kwargs):
    """ Convert to Config if not already a Config """
    return kwargs if isinstance(kwargs,Config) else Config(kwargs,config_name="kwargs")

def name(model):#NOQA
    return model.name if not model.name is None else type(model).__name__

# ==========================================================================
# Why training stopped/
# ==========================================================================

class Status(Enum):
    """
    Status indicator for training.
    This flag is used in ProgessData.on_epoch_update_prep() to control continuation of training,
    and is returned as 'status' by train()
    """

    CONTINUE         = 0
    STOP_ABORTED     = -1
    STOP_CONVERGED   = -2
    STOP_INTERRUPTED = -10
    STOP_EXCEPTION   = -11
    FINISHED_EPOCHS  = 1
    ALREADY_TRAINED  = 2

    @staticmethod
    def status(reason) -> str:
        """ Text string translation """
        status = ""
        if reason == Status.CONTINUE:
            status = "training in progress"
        if reason == Status.STOP_ABORTED:
            status = "training aborted"
        elif reason == Status.STOP_CONVERGED:
            status = "desired convergence achieved"
        elif reason == Status.STOP_INTERRUPTED:
            status = "user abort"
        elif reason == Status.STOP_EXCEPTION:
            status = "exception caught"
        elif reason == Status.FINISHED_EPOCHS:
            status = "trained all epochs"
        elif reason == Status.ALREADY_TRAINED:
            status = "model is sufficiently trained"
        else:
            _log.throw("Unknown stopping reason %s", str(reason))
        return status

# ==========================================================================
# Model
# Cachable gym
# ==========================================================================

class Gym(tf.keras.Model):
    """
    Base class for a keras gym model with
    * Automatic caching
    * Default tracking of progress, with support for asynchronous training

    This gym assumes that the loss of the gym is "linear", e.g. an expectation of a returned variable (usually 'loss')

    Implementation comments
    -----------------------
    In order to implement your own gym,
        1) derive from gym
        2) implement build/call.
           The data passed to each will be of the form of the dictionaries in environment.trn.tf_data.
        3) Set the class variable CACHE_VERSION to a string version
        4) Provide a static LOSS_NAME member if the primary loss objective is not called 'loss' (e.g. the data in your returned dictionary)
    """

    CACHE_VERSION = "0.0.1"
    LOSS_NAME     = "loss"

    def __init__(self, config          : Config,
                       name            : str = None,
                       dtype           : tf.DType = None,
                       trainable       : bool = True,
                       cache_uid       : str = None ):
        """
        Initializes the cachable gym
        ------------------------------
            config : Config
                Configuration for the model.
                Unless cache_uid is provided, this determines the unique ID of the gym.
            name : str
                Name of the object
            dtype : tf.DType
                Type of the gym
            trainable : bool
                Whether the gym is trainable.
            cache_uid : int
                Unique ID for this model setup. If not provided, config.unique_id will be used.
        """
        tf.keras.Model.__init__(self, name=name, dtype=dtype, trainable=trainable )

        _log.verify( isinstance(config, Config), "'config' must be of type '%s' but appears to be of type '%s'", Config.__name__, type(config).__name__ )
        self._cache_unique_id = config.unique_id() if cache_uid is None else str(cache_uid)
        self._cache_config    = config.copy()
        self._user_version    = config("user_version", "0.0.1", str, "User-defined version of a gym. Changing this string will change the cache ID, and therefore will trigger a new calculation")

    # -------------------
    # syntatic sugar
    # -------------------

    @property
    def display_name(self) -> str:
        """ Display name for this Gym """
        return name(self)

    @property
    def description(self) -> str:
        """ Returns a description of the gym to be printed to the user. Return None to supress """
        return None

    @property
    def num_trainable_weights(self) -> int:
        """ Returns the number of weights. The gym must have been call()ed once """
        weights = self.trainable_weights
        return np.sum( [ np.prod( w.get_shape() ) for w in weights ] ) if not weights is None else 0.

    @property
    def cache_uid( self ):
        """ Return the unique ID for this gym. """
        return self._cache_unique_id

    @property
    def cache_def_directory_name( self ):
        """ Returns a descriptive name for this class which can be used as directory for the caches. No trailing '/' """
        name = str( self.__class__.__name__ )
        return name if self.CACHE_VERSION is None else ( name + "/" + str(self.CACHE_VERSION) )

    # -------------------
    # Keras serialization
    # -------------------

    @staticmethod
    def from_config( tf_config : dict ):
        """
        You will have to implement this for all derived classes.
        Default pattern is written below
        """
        raise NotImplementedError("Please implement Gym.from_config")

    @staticmethod
    def from_config_default( Class : type, tf_config : dict ):
        """
        Default 'from_config' code.
        Meant to be used as

        class MyGyum(Gym):

            @staticmethod
            def from_config( tf_config : dict ):
                return Gym.from_config_default( MyGym, tf_config )
        """
        _log.verify( tf_config['cache_version'] == Class.CACHE_VERSION, "Error reading configuration from cache for '%s'': version mismatch. Found version %s, but current code is version %s", Class.__name__, tf_config['cache_version'], Class.CACHE_VERSION )
        return Class( config        = tf_config['config'],
                      name          = tf_config['name'],
                      dtype         = tf_config['dtype'],
                      trainable     = tf_config['trainable'],
                      cache_uid     = tf_config['cache_uid']
                )

    def get_config( self ):
        """ You will need to overwrite this if your __init__ signature changes """
        return dict(
            config        = self._cache_config,
            cache_uid     = self._cache_unique_id,
            name          = self.name,
            dtype         = self.dtype,
            trainable     = self.trainable,
            cache_version = self.CACHE_VERSION
            )

# ==========================================================================
# TrainingInfo
# Information on the current training run
# ==========================================================================

class TrainingInfo(object):
    """
    Information on the current training run for user updates provided by the training loop.
    You do not usually create the class.
    To provide user-specified information during training, use the Environment class.

    Attributes
    ----------
        display_name :
            Display name of this training run
        epochs :
            total epochs to be trained
        batch_size :
            Training batch size, as passed to tf.keras.Model.fit()
        run_eagerly :
            run_eagerly as passed to tf.keras.Model.compile()
        debug_numerics :
            If True, then tensorflow is tracking numerical issues. This is very slow.
        start_time :
            Start datetime. This is the start time of the current run, not of the cached run.
        cache_full_file :
            full cache file name
        cache_mode :
            cache mode used.
        verbose :
            Context object for reporting text updates.

    The object also creates new members:
        progress_data : PrettyDict
            Pretty dict to store data which progess_data wants to preserve from one call to another
    """

    def __init__(self, *, display_name    : str,
                          batch_size,
                          epochs          : int,
                          run_eagerly     : bool,
                          debug_numerics  : bool,
                          cache_full_file : str,
                          cache_mode      : CacheMode,
                          verbose         : Context
                          ):
        """ See class level documentation """
        self.display_name    = display_name
        self.epochs          = epochs       # total epochs requested by the user. Note that the actual epochs will be reduced by the number of epochs already trained in the cached file
        self.batch_size      = batch_size   # batch size: int or None
        self.run_eagerly     = run_eagerly
        self.debug_numerics  = debug_numerics
        self.start_time      = datetime.now()
        self.cache_full_file = cache_full_file
        self.cache_mode      = cache_mode
        self.verbose         = verbose

        # for writing updates
        self._write_line_len = 0

        # for ProgressData
        self._progress_data  = PrettyDict()

    def write_output(self, text : str, *kargs, **kwargs ):
        """
        Write training update to the command window.
        This function will only print something if the current context in self.verbose is active (e.g. not 'is_quiet').
        """
        if self.verbose.is_quiet:
            return

        indent = self.verbose.str_indent()
        text   = _fmt(text, kargs, kwargs)
        lines  = text.split("\n")

        # first line: handle current line.
        line = lines[0]
        i    = line.rfind("\r")
        if i==-1:
            # no \r:
            # append line to current line
            line = ( indent + line ) if self._write_line_len == 0 else line
            sys.stdout.write(line)
            self._write_line_len += len(line)
        elif i==len(line)-1:
            # \r at the end
            # clear line but do not print 'indent'
            if self._write_line_len > 0:
                sys.stdout.write("\r" + (" " * self._write_line_len) + "\r")
                self._write_line_len = 0
        else:
            # \r followed by some residual text
            # clear line and print new text
            line = indent + line[i+1:]
            if self._write_line_len > len(line):
                sys.stdout.write("\r" + (" " * self._write_line_len) + "\r" + line)
            else:
                sys.stdout.write("\r" + line)
            self._write_line_len = len(line)

        if len(lines) == 1:
            sys.stdout.flush()
            return

        # intermediate lines
        for line in lines[1:-1]:
            i    = line.rfind("\r")
            line = line if i==-1 else line[i+1:]
            sys.stdout.write( "\n" + indent + line )

        # final line
        line = lines[-1]
        i    = line.rfind("\r")
        line = line if i==-1 else line[i+1:]
        if line=="":
            self._write_line_len = 0
            sys.stdout.write('\n')
        else:
            line = indent + line
            sys.stdout.write('\n' + line)
            self._write_line_len = len(line)

        sys.stdout.flush()

    @property
    def progress_data(self) -> PrettyDict:
        """
        Returns the handle to a PrettyDict which can be used by ProgressData or derived classes
        to store information from one function call to the next
        """
        return self._progress_data

# ==========================================================================
# Environment
# Contains the top level data available throughout the training process
# ==========================================================================

class Environment( PrettyDict ):
    """
    Represents the static environment data available for the overall training loop: the gym model, its data, sample weights.
    This class is provided to the user in ProgressData.on_epoch_end() and other functions of ProgressData.
    This means this environment can also execute a predict() on the current gym for both its training and validation set.

    Objects of this class are not serialized directly.

    The usual step is create a class of this type and add your own member variables to it to provide additional information
    on the overall environment when processing ProgressData events.
    """

    def __init__(self, *, gym                : Gym,
                          tf_trn_data        : dict,
                          tf_val_data        : dict = None,
                          trn_sample_weights : np.ndarray = None,
                          val_sample_weights : np.ndarray = None,
                          **kwargs ):
        """
        Initialize environment.
        The gym is set as part of training via set_model (e.g. if the gym was restored from a cache).
        This class is passed to various functions of ProgressData.

        Parameters
        ----------
            gym : Gym
                Instance of a gym derived from Gym.
                Note that in case the gym is restored from the cache this object is replaced via set_gym().
            trn_tf_data : dict
                Dictionary of TF data to be passed to the gym during training.
                If the sample path are distributed according to some sample_weights,
                then this dictionary must contain the probabiltiy weights and key_sample_weights must
                be set to the name of this element.
            trn_sample_weights : np.ndarray
                Sample weights for the training data set. None for the uniform distribution.
            val_tf_data : dict
                Dictionary of TF data used for validation. Set to None for no validation
            val_sample_weights : np.ndarray
                Sample weights for the validation data set. None for the uniform distribution.

            **kwargs :
                Other arguments to be passed to 'self', see PrettyDict.
                In particular, this allows assigning member values to the environment as follows:

                    e = Environment(gym, trn_data, user_data = user_data )

                in this case  'user_data' is available in the environment in all subsequent contexts
        """
        _log.verify( not gym is None, "'gym' cannot be None")
        _log.verify( isinstance(gym, Gym), "'gym' must be derived from 'Gym'. Found type '%s'", type(gym).__name__)
        _log.verify( isinstance( tf_trn_data, Mapping), "tf_trn_data must be a Mapping. Found type '%s'", type(tf_trn_data).__name__ if not tf_trn_data is None else "None")
        if not tf_val_data is None: _log.verify( isinstance( tf_val_data, Mapping), "tf_val_data must be a Mapping. Found type '%s'", type(tf_val_data).__name__)

        self.gym                = gym
        self.loss_name          = gym.LOSS_NAME
        self.trn                = PrettyDict()
        self.trn.tf_data        = tfCast( tf_trn_data )
        self.trn.sample_weights = np.asarray( trn_sample_weights ) if not trn_sample_weights is None else None
        self.trn.num_samples    = get_sample_size( self.trn.tf_data )
        if not self.trn.sample_weights is None:
            self.trn.sample_weights = self.trn.sample_weights[:,0] if len(self.trn.sample_weights) == 2 and self.trn.sample_weights.shape[1] == 1 else self.trn.sample_weights
            _log.verify( len(self.trn.sample_weights.shape) == 1, "'trn_sample_weights' must be a vector or of shape (N,) or (N,1), but found tensor of shape %s", trn_sample_weights.shape)

        if tf_val_data is None:
            self.val = None
        else:
            self.val                = PrettyDict()
            self.val.tf_data        = tfCast( tf_val_data )
            self.val.sample_weights = np.asarray( val_sample_weights ) if not val_sample_weights is None else None
            self.val.num_samples    = get_sample_size( self.val.tf_data )
            _log.verify( (self.trn.sample_weights is None) == (self.val.sample_weights is None), "'val_sample_weights' and 'trn_sample_weights' must be specified jointly, or jointly omitted")

            if not self.val.sample_weights is None:
                self.val.sample_weights = self.val.sample_weights[:,0] if len(self.val.sample_weights) == 2 and self.val.sample_weights.shape[1] == 1 else self.val.sample_weights
                _log.verify( len(self.trn.sample_weights.shape) == 1, "'val_sample_weights' must be a vector or of shape (N,) or (N,1), but found tensor of shape %s", val_sample_weights.shape)

        if len(kwargs) > 0:
            self.update(kwargs)

    def set_gym(self, gym : Gym, cached : bool ):
        """
        Called to set the gym of the environment.
        Can be overwritten to detect when a gym is restored from disk.

        Parameters
        ----------
            gym : Model
                The gym
            cached : bool
                Indicates whether the gym has been restored from disk
        """
        _log.verify( isinstance( gym, Gym ), "Cannot call set_model(): gym must be derived from Gym. Found type '%s'", type(gym).__name__ if not gym is None else "None" )
        self.gym = gym

    def predict(self):
        """
        Call current gym on tf_data and tf_val_data to predict the latest results of the gym

        Returns
        -------
            A PrettyDict which contains two sub-directories 'trn' and optionally 'val':
                trn.result    : numpy arrays of the training results from gym(trn.tf_data)
                trn.loss      : float of the training loss for the current gym, e.g. np.mean( trn.result.loss ) if sample_weights are not used, otherwise the corresponding calculation.
                trn.loss_err  : float of the standard error of the training loss (e.g. std/sqrt(n))
            If val is not None:
                val.result    : numpy arrays of the validation results from gym(val.tf_data)
                val.loss      : float of the validation loss for the current gym
                val.loss_err  : float of the standard error of the validation loss (e.g. std/sqrt(n))
        """
        # training set
        pack               = PrettyDict()
        pack.trn           = PrettyDict()
        pack.trn.results   = npCast( self.gym(self.trn.tf_data) )
        _log.verify( isinstance(pack.trn.results, np.ndarray) or ( isinstance(pack.trn.results, Mapping) and self.loss_name in pack.trn.results), "The data returned from the gym must either be the loss tensor, or be a dictionary with '%s' entry as specified by '%s.LOSS_NAME'. Model returned data type %s", self.loss_name, type(self.gym).__name__, str(type(pack.trn.results)))

        pack.trn.loss      = pack.trn.results if isinstance(pack.trn.results, np.ndarray) else pack.trn.results[self.loss_name]
        pack.trn.loss      = pack.trn.loss[:,0] if len(pack.trn.loss.shape) == 2 and pack.trn.loss.shape[1] == 1 else pack.trn.loss
        _log.verify( len(pack.trn.loss.shape) == 1, "'loss' must be a vector or of shape (N,1). Found tensor of shape %s", pack.trn.loss.shape)
        if not self.trn.sample_weights is None:
            _log.verify( len(pack.trn.loss) == len(self.trn.sample_weights), "Invalid training sample weight vector: loss vector returned by gym is of length %ld, while training sample weights are of length %ld", len(pack.trn.loss), len(self.trn.sample_weights))
        pack.trn.loss_err  = err(  P=self.trn.sample_weights, x=pack.trn.loss )
        pack.trn.loss      = mean( P=self.trn.sample_weights, x=pack.trn.loss )

        # validation set
        if self.val is None:
            pack.val = None
        else:
            pack.val          = PrettyDict()
            pack.val.results  = npCast( self.gym(self.val.tf_data) )
            pack.val.loss     = pack.val.results if isinstance(pack.val.results, np.ndarray) else pack.val.results[self.loss_name]
            pack.val.loss     = pack.val.loss[:,0] if len(pack.val.loss.shape) == 2 and pack.val.loss.shape[1] == 1 else pack.val.loss
            pack.val.loss_err = err(  P=self.val.sample_weights, x=pack.val.loss )
            pack.val.loss     = mean( P=self.val.sample_weights, x=pack.val.loss )

        return pack

# ==========================================================================
# ProgressData
# Base class for relevant data to be computed during training for user
# feedback (e.g. history of losses; current state of the gym)
# ==========================================================================

class ProgressData(object):
    """
    Base class for relevant data to be computed during training for user
    feedback (e.g. history of losses; current state of the gym).

    This class is intended to be derived from, and that you overwrite on_epoch_end.
    Note that you typically pass the class to train() below, rather than an instance.
    It may also be restored from a cache.

    For being used in Ray, this class needs to be pickle'able.
    """

    def __init__(self, environment        : Environment,        # gym, tf_data, etc
                       predicted_data0    : PrettyDict,         # results from environment.predict()
                       training_info      : TrainingInfo,       # total number of epochs requested etc
                       config             : Config,             # configuration, if any,
                       best_by_training   : bool = True,        # use training results to determine best fit
                       store_epoch_results: bool = True,        # store results for the current epoch in val.results and trn.results
                       store_best_results : bool = True,        # store best results in val.best_results and trn.best_results
                       ):
        """
        Initialize the cachable progress data store
        ** Do not store the gym or any training data into this object **

        Parameters
        ----------
            environment : Environment,
                provides access to various non-serializable objects in the training loop
            predicted_data0 : PrettyDict
                Result of environment.predict().
            training_info :
                Contains information such as total number of epochs, batch_size etc
            config :
                Can be used by derived classes to initialize the object
            best_by_training   : bool = True
                use training results to determine best fit
            store_epoch_results: bool = True
                store results for the current epoch in val.results and trn.results
                Turn off to reduce memory usage for very large results data sets
            store_best_results : bool = True
                store best results in val.best_results and trn.best_results
                Turn off to reduce memory usage for very large results data sets
        """
        # config
        self.best_by_training    = best_by_training
        self.store_epoch_results = store_epoch_results
        self.store_best_results  = store_best_results
        _log.verify( best_by_training or not predicted_data0.val is None, "Cannot use best_by_training=False as no validation set was specified" )

        # timings
        self.epochs              = training_info.epochs
        self.display_name        = training_info.display_name
        self.times_per_epoch     = []
        self.last_cached_epoch   = -1

        # losses
        self.trn                 = PrettyDict()
        self.val                 = PrettyDict() if not predicted_data0.val is None else None
        self.trn.results         = predicted_data0.trn.results if self.store_epoch_results else None
        self.trn.losses          = [ predicted_data0.trn.loss ]
        self.trn.loss_errs       = [ predicted_data0.trn.loss_err ]

        if not self.val is None:
            self.val.results     = predicted_data0.val.results if self.store_epoch_results else None
            self.val.losses      = [ predicted_data0.val.loss ]
            self.val.loss_errs   = [ predicted_data0.val.loss_err ]

        # best epoch
        self.best_epoch       = -1
        self.best_weights     = environment.gym.get_weights()
        self.best_loss        = predicted_data0.trn.loss
        self.trn.best_results = predicted_data0.trn.results if self.store_best_results else None
        if not self.val is None:
            self.val.best_results = predicted_data0.val.results if self.store_best_results else None

        # memory use
        p = psutil.Process()
        with p.oneshot():
            self.process            = PrettyDict()
            self.process.memory_rss = [ p.memory_info().rss / (1024.*1024.) ]
            self.process.memory_vms = [ p.memory_info().vms / (1024.*1024.) ]

    # --------------------
    # Status information
    # --------------------
    
    @property
    def current_epoch(self) -> int:
        """ Returns the current epoch. Returns -1 if no epoch was yet recorded """
        return len(self.times_per_epoch)-1

    @property
    def remaining_epochs(self) -> int:
        """ Returns epochs remaining. Will floor at zero if there nothing to train """
        return max(0, self.epochs - (self.current_epoch + 1))

    @property
    def time_seconds_passed(self) -> float:
        """ Returns total seconds passed training so far """
        return sum( self.times_per_epoch )

    @property
    def time_seconds_per_epoch(self) -> float:
        """ Returns average seconds used per epoch, or None of training has not yet started """
        return self.time_seconds_passed / len(self.times_per_epoch) if len(self.times_per_epoch) > 0 else None

    @property
    def time_remaining_seconds(self) -> float:
        """ Returns the expected reamining time in seconds, or None if training has not started yet """
        time_seconds_per_epoch = self.time_seconds_per_epoch
        return float(self.remaining_epochs) * time_seconds_per_epoch if not time_seconds_per_epoch is None else None

    @property
    def time_end_time(self) -> datetime:
        """ Estimated end time of training, or None if training has not started yet """
        remaining = self.time_remaining_seconds
        return datetime.now() + timedelta(seconds=remaining) if not remaining is None else None

    # --------------------
    # Utilities
    # --------------------

    def write_output(self, training_info : TrainingInfo, text : str, *kargs, **kwargs):
        r"""
        Write training update to the command window.
        This function will only print something if the current context in self.verbose is active (e.g. not 'is_quiet').
        Uses cdxbasics.util.WriteLine for clean use of \r (e.g. it will clear previous lines properly)
        """
        training_info.write_output(text,*kargs,**kwargs)

    # --------------------
    # Events
    # --------------------

    def on_restore(self,    environment    : Environment,  # gym, tf_data, etc
                            predicted_data : PrettyDict,   # results from environment.predict(): current predicted training and validation data; current loss.
                            training_info  : TrainingInfo):# number of epochs to be computed etc
        """
        Called when the training data set was restored from cache.

        Parameters
        ----------
            environment :
                environment as passed to train()
            predicted_data :
                training and, if used, validation information for the current status of the model as returned by environment.predict()
                This is not the status of the 'best' epoch.
                See self.trn.best_results and self.val.best_results, respectively.
            training_info :
                Static information on the current training run
        """
        pass

    def on_first_epoch_begin( self, environment    : Environment,  # gym, tf_data, etc
                                    training_info  : TrainingInfo ):
        """ Called before the first epoch is run. This typically means the main model is compiled """
        r = self.status_info(environment, training_info)
        training_info.write_output("\rCompiling %(display_name)s for %(str_num_weights)s weights..." % r )

    def on_epoch_end_prep(self,  environment    : Environment,  # gym, tf_data, etc
                                 predicted_data : PrettyDict,   # current predicted training and validation data; current loss.
                                 training_info  : TrainingInfo, # number of epochs to be computed etc
                                 logs           : dict          # logs c.f. keras Callback
                          ) -> Status:
        """
        Callback at the end of an epoch.
        Intended to update all calculation for this ProgressData object.
        
        All native data such as current_epoch, timing, results etc are updated at this point, except information on caching because
        this  unction is called before a decision to cache the current object is made.
        Therefore any data computed in a derived on_epoch_end_prep() and stored in 'self' will be cached, too.

        Use on_epoch_end_update() to update the user after caching (e.g. self.last_cached_epoch is correct)
        Note that on_epoch_end_update() is not called if this function returns a stopping reason other than Status.CONTINUE.
        Instead, on_done() is called.

        Parameters
        ----------
            environment :
                environment as passed to train()
            predicted_data :
                training and, if used, validation information for the current status of the model as returned by environment.predict()
                This is not the status of the 'best' epoch. See self.trn.best_results and self.val.best_results,
                respectively
            training_info :
                Static information on the current training run
            logs :
                See tf.keras.Callback.on_epoch_end. Not usually needed here.

        Returns
        -------
            Return Status.STOP_CONVERGED or Status.STOP_ABORTED to abort training or Status.CONTINUE to continue
        """
        return Status.CONTINUE

    def on_epoch_end_update(self,  environment    : Environment,    # gym, tf_data, etc
                                   training_info  : TrainingInfo ): # number of epochs to be computed etc
        """
        Called after on_epoch_end_prep() and potentially caching the traing status to disk.
        This function is intended to update the user about traing progress.

        The default implementation prints self.status_message() to training_info.verbose

        Parameters
        ----------
            environment :
                environment as passed to train()
            training_info :
                Static information on the current training run
        """
        status_message = self.status_message( environment=environment, training_info=training_info )
        training_info.write_output("\r" + status_message)

    def on_done(self,       environment    : Environment,  # gym, tf_data, etc
                            predicted_data : PrettyDict,   # current predicted training and validation data; current loss.
                            training_info  : TrainingInfo, # number of epochs to be computed etc
                            best_epoch     : int,          # best epoch
                            stop_reason    : Status        # why training stopped
                        ):
        """
        Called when training is finished and the gym was set to the best weights.
        Typically used to update any visualization and print a summary.

        The default implementation prints self.done_message() to training_info.verbose

        Parameters
        ----------
            environment :
                environment as passed to train()
            predicted_data :
                training and, if used, validation information for the *best* status of the model, returned by environment.predict()
            training_info :
                Static information on the current training run
            stop_reason :
                Reason for stopping training.
        """
        done_message = self.done_message( environment=environment, training_info=training_info, stop_reason=stop_reason )
        training_info.write_output("\r" + done_message + "\n")

    # --------------------
    # Status utilities
    # --------------------

    def status_info( self, environment    : Environment,
                           training_info  : TrainingInfo) -> PrettyDict:
        """ Returns status information as a pretty dictionary """
        r = PrettyDict()

        r.display_name       = training_info.display_name
        r.epochs             = self.epochs
        r.current_epoch      = self.current_epoch # -1 if not started training yet
        r.best_epoch         = self.best_epoch
        r.last_cached_epoch  = self.last_cached_epoch
        r.current_epoch1     = self.current_epoch+1
        r.best_epoch1        = self.best_epoch+1
        r.last_cached_epoch1 = self.last_cached_epoch+1
        r.batch_size         = training_info.batch_size if not training_info.batch_size is None else 32
        r.num_weights        = environment.gym.num_trainable_weights
        r.str_num_weights    = fmt_big_number( r.num_weights )

        r.trn_samples        = environment.trn.num_samples
        r.trn_init_loss      = self.trn.losses[0]
        r.trn_last_loss      = self.trn.losses[-1]
        r.trn_best_loss      = self.trn.losses[self.best_epoch+1]

        r.val_samples        = environment.val.num_samples if not self.val is None else None
        r.val_init_loss      = self.val.losses[0] if not self.val is None else None
        r.val_last_loss      = self.val.losses[-1] if not self.val is None else None
        r.val_best_loss      = self.val.losses[self.best_epoch+1] if not self.val is None else None

        r.memory_rss         = self.process.memory_rss[-1]
        r.memory_vms         = self.process.memory_vms[-1]
        r.str_memory_rss     = fmt_big_number(r.memory_rss)
        r.str_memory_vms     = fmt_big_number(r.memory_vms)

        r.seconds_elapsed    = self.time_seconds_passed
        r.seconds_per_epoch  = self.time_seconds_per_epoch
        r.remaining_seconds  = self.time_remaining_seconds
        r.current_time       = datetime.now()
        r.end_time           = self.time_end_time

        r.str_seconds_elapsed   = fmt_seconds( self.time_seconds_passed )
        r.str_seconds_per_epoch = fmt_seconds( self.time_seconds_per_epoch ) if not self.time_seconds_per_epoch is None else "n/a"
        r.str_remaining_seconds = fmt_seconds( self.time_remaining_seconds ) if not self.time_remaining_seconds is None else "n/a"
        r.str_current_time      = fmt_datetime( datetime.now() )
        r.str_end_time          = fmt_datetime( self.time_end_time ) if not self.time_end_time is None else "not available yet"

        return r

    def status_message(self, environment    : Environment,
                             training_info  : TrainingInfo) -> str:
        """ Returns a standard status message """
        r     = self.status_info( environment, training_info )

        r.str_val_samples_text  = ( " %ld validation samples," % r.val_samples ) if not r.val_samples is None else ""
        text = "Training %(display_name)s epoch %(current_epoch1)ld/%(epochs)ld for %(str_num_weights)s weights using %(trn_samples)ld samples,%(str_val_samples_text)s batch size %(batch_size)ld | " % r

        if not self.val is None:
            text += "initial loss: %(trn_init_loss)g (%(val_init_loss)g), current loss: %(trn_last_loss)g (%(val_last_loss)g), best loss: %(trn_best_loss)g (%(val_best_loss)g). Best epoch %(best_epoch1)ld. Last cached epoch %(last_cached_epoch1)ld | " % r
        else:
            text += "initial loss: %(trn_init_loss)g, current loss: %(trn_last_loss)g, best loss: %(trn_best_loss)g. Best epoch %(best_epoch1)ld. Last cached epoch %(last_cached_epoch1)ld | " % r

        text += "memory used: rss %(str_memory_rss)s, vms %(str_memory_vms)s | " \
                "time elapsed %(str_seconds_elapsed)s; time per epoch %(str_seconds_per_epoch)s; estimated time remaining %(str_remaining_seconds)s | " \
                "current time: %(str_current_time)s, estimated end time: %(str_end_time)s" % r

        return text

    def done_message(self, environment    : Environment,
                           training_info  : TrainingInfo,
                           stop_reason    : Status ) -> str:
        """ Returns a standard status message """
        r     = self.status_info( environment, training_info )

        r.str_val_samples_text  = ( " %ld validation samples," % r.val_samples ) if not r.val_samples is None else ""
        r.str_stop_reason       = Status.status(stop_reason)

        text = "Trained %(display_name)s until epoch %(current_epoch1)ld/%(epochs)ld for %(str_num_weights)s weights using %(trn_samples)ld samples,%(str_val_samples_text)s batch size %(batch_size)ld: %(str_stop_reason)s | " % r

        if not self.val is None:
            text += "initial loss: %(trn_init_loss)g (%(val_init_loss)g), best loss: %(trn_best_loss)g (%(val_best_loss)g). Best epoch %(best_epoch1)ld. Last cached epoch %(last_cached_epoch1)ld | " % r
        else:
            text += "initial loss: %(trn_init_loss)g, best loss: %(trn_best_loss)g. Best epoch %(best_epoch1)ld. Last cached epoch %(last_cached_epoch1)ld | " % r

        text += "memory used: rss %(str_memory_rss)s, vms %(str_memory_vms)s | "\
                "time elapsed %(str_seconds_elapsed)s; time per epoch %(str_seconds_per_epoch)s; estimated time remaining %(str_remaining_seconds)s | "\
                "current time: %(str_current_time)s" % r

        return text

    # --------------------
    # Internal
    # --------------------

    def _on_restore(self,   environment    : Environment,  # gym, tf_data, etc
                            predicted_data : PrettyDict,   # current predicted training and validation data; current loss.
                            training_info  : TrainingInfo):# number of epochs to be computed etc
        """ Called when a model was restored from the cache. """
        self.epochs            = training_info.epochs
        self.last_cached_epoch = self.current_epoch
        self.on_restore( environment, predicted_data, training_info )

    def _on_epoch_end_prep(self, environment    : Environment,  # gym, tf_data, etc
                                 training_info  : TrainingInfo, # number of epochs to be computed etc
                                 time_epoch     : float,        # time required for
                                 logs           : dict          # logs c.f. keras Callback
                        ):
        """
        Called at the end of an epoch by Callback()
        Will store the time for the epoch in 'times_per_epoch'

        This function is called by the training loop.
        Do not overwrite this function; instead overwrite on_epoch_end()
        """
        assert len(self.times_per_epoch)+1 == len(self.trn.losses), "Internal error: %ld+1 != %ld" % (len(self.times_per_epoch), len(self.trn.losses))
        assert self.epochs == training_info.epochs, "Internal error: %ld != %ld" % (self.epochs, training_info.epochs )

        predicted_data = environment.predict()

        # times, losses
        self.epochs = training_info.epochs
        self.times_per_epoch.append( time_epoch )
        self.trn.losses.append( predicted_data.trn.loss )
        self.trn.loss_errs.append( predicted_data.trn.loss_err )
        self.trn.results = predicted_data.trn.results if self.store_epoch_results else None
        if not self.val is None:
            self.val.losses.append( predicted_data.val.loss )
            self.val.loss_errs.append( predicted_data.val.loss_err )
            self.val.results = predicted_data.val.results if self.store_epoch_results else None

        # best
        is_best = (self.best_loss > predicted_data.trn.loss) if self.best_by_training else (self.best_loss > predicted_data.val.loss)
        if is_best:
            self.best_epoch       = self.current_epoch
            self.best_weights     = environment.gym.get_weights()
            self.best_loss        = predicted_data.trn.loss if self.best_by_training else predicted_data.val.loss
            self.trn.best_results = predicted_data.trn.results if self.store_best_results else None
            if not self.val is None:
                self.val.best_results = predicted_data.val.results if self.store_best_results else None

        # memory uses
        p = psutil.Process()
        with p.oneshot():
            self.process.memory_rss.append( p.memory_info().rss / (1024.*1024.))
            self.process.memory_vms.append( p.memory_info().vms / (1024.*1024.) )

        r = self.on_epoch_end_prep( environment=environment, predicted_data=predicted_data, training_info=training_info, logs=logs )
        assert r in [Status.CONTINUE, Status.STOP_CONVERGED, Status.STOP_ABORTED], "Invalid status return from on_epoch_end: %s" % str(r)
        return r

    def _on_cache_written( self, environment    : Environment,  # gym, tf_data, etc
                                 training_info  : TrainingInfo, # number of epochs to be computed etc
                                 time_seconds_used
                        ):
        """
        Called when the cache was written to disk.
        The new 'last_cached_epoch' will be set to the current epoch
        """
        self.last_cached_epoch = self.current_epoch

    def _on_done(self,      environment    : Environment,  # gym, tf_data, etc
                            training_info  : TrainingInfo, # number of epochs to be computed etc
                            stop_reason    : Status    # why training stopped
                        ):
        """
        Called by the Callback() when training is done, after the best weights have been written to the gym.
        Do not overwrite this function; overwrite on_done()
        """
        predicted_data    = environment.predict()
        self.on_done( environment=environment, predicted_data=predicted_data, training_info=training_info, best_epoch=self.best_epoch, stop_reason=stop_reason )

    def _write_best( self,  gym : Gym ):
        """ Write best weights to the gym, if any """
        if self.best_epoch >= 0:
            gym.set_weights( self.best_weights )

# ==========================================================================
# Callback
# This is called during training to handle caching and user updates
# ==========================================================================

class Callback(tf.keras.callbacks.Callback):
    """
    Manages training of our gym
    -- Keeps track of training data in TrainingProgressData including best fit
    -- Implements caching
    -- Implements dyanmic visual updates
    """

    def __init__(self, *, environment    : Environment,
                          training_info  : TrainingInfo,
                          progress_data  : ProgressData,
                          cache_config   : PrettyDict,
                          verbose        : Context = quiet ):
        """
        Initialize the call back
        The object will attempt to restore a previous training state from disk if found.

        Parameters
        ----------
            model_cachable
                Model derived from Model.
            epochs : int
                Total number of epochs for this training. If the cached object has been trained beyond that point, no further training will commence.
            default_cache_directory : str
                Default caching directory for
        """
        tf.keras.callbacks.Callback.__init__(self)

        gym                  = environment.gym
        _log.verify( isinstance(gym, Gym), "'gym' must be derived from 'Gym'")

        # basics
        self.environment      = environment
        self.training_info    = training_info
        self.progress_data    = progress_data
        self.cache_last_epoch = progress_data.current_epoch # -1 for not cached
        self.verbose          = verbose
        self.time_start_epoch = time.time()
        self.stop_reason      = Status.CONTINUE
        _log.verify( self.training_info.epochs > 0, "'epochs' must be positive. Found %ld", self.training_info.epochs )
        assert not self.is_done, "Internal error: nothing to train?"

        # caching
        self.cache_mode       = cache_config.cache_mode
        self.cache_freq       = cache_config.cache_freq
        self.cache_dir        = cache_config.cache_dir
        self.cache_file       = cache_config.cache_file
        self.time0            = time.time()

    def write_cache(self):
        """ Write cache to disk """
        if self.cache_last_epoch >= self.progress_data.current_epoch:
            assert self.cache_last_epoch == self.progress_data.current_epoch, "Interal error: %ld > %ld ?" % (self.cache_last_epoch, self.progress_data.current_epoch)
            return
        assert self.progress_data.current_epoch >= 0, "Internal error: current epoch is -1"

        t0     = time.time()
        gym    = self.environment.gym
        opt_w  = gym.optimizer.get_weights() if TF_VERSION <= 210 else [ w.value() for w in gym.optimizer.variables() ]
        cache  = dict( name        = gym.__class__.__name__,
                       version     = str(gym.CACHE_VERSION),
                       progress    = self.progress_data,
                       gym_weights = gym.get_weights(),
                       opt_config  = tf.keras.optimizers.serialize(gym.optimizer),
                       opt_weights = opt_w
                      )

        self.cache_dir.write( self.cache_file, cache )
        self.cache_last_epoch = self.progress_data.current_epoch

        self.progress_data._on_cache_written( environment       = self.environment,
                                              training_info     = self.training_info,
                                              time_seconds_used = time.time() - t0 )

    @staticmethod
    def restore_from_cache( gym : Gym, tf_data : dict, cache_config : dict, verbose : Context ):
        """
        Restore the gym, its optimizer, and the associated 'progress_data' from disk.
        This function follows the cdxbasics.utill.CacheMode pattern

        Returns deserialized 'progress_data' or None
        """
        fullFileName = cache_config.cache_dir.fullKeyName( cache_config.cache_file )

        if not cache_config.cache_dir.exists( cache_config.cache_file ):
            return None

        if cache_config.cache_mode.delete:
            cache_config.cache_dir.delete( cache_config.cache_file, None )
            verbose.report(0,"Deleted existing cache '%s'", fullFileName)
            return None

        if not cache_config.cache_mode.read:
            verbose.report(0,"Ignored existing cache '%s' since cache mode was '%s'", fullFileName, cache_config.cache_mode )
            return None

        cache = cache_config.cache_dir.read( cache_config.cache_file, None )
        err   = ""
        if cache is None:
            err = "Failed to read existing cache file '%s': disk read error" % fullFileName

        _ = cache.get('name',"<Undefined>")
        if len(err) == 0 and _ != gym.__class__.__name__:
            err = "Failed to read existing cache file %s: cache refers to a gym of type '%s', not '%s' as expected" % (fullFileName, _, gym.__class__.__name_ )

        _ = cache.get('version',"<Undefined>")
        if len(err) == 0 and _ != str(gym.CACHE_VERSION):
            err = "Failed to read existing cache file %s: cache version is %s, not the current %s" % (fullFileName, _, str(gym.CACHE_VERSION))

        if len(err) == 0:
            try:
                backup_w = gym.get_weights()
            except ValueError:
                _ = gym(tf_data)
                backup_w = gym.get_weights()

            backup_o = gym.optimizer
            try:
                progress_data = cache['progress']
                gym_weights   = cache['gym_weights']
                opt_weights   = cache['opt_weights']
                opt_config    = cache['opt_config']

                optimizer     = tf.keras.optimizers.deserialize(opt_config)

                # we attempt to set the optimizer weights before calling compile()
                # this really needs to be done after compile() which is why we are
                # doing it again below. The reason for the duplication is that
                # this way we will raise an exception before the model was compiled.
                grad_vars     = gym.trainable_weights
                zero_grads    = [tf.zeros_like(w) for w in grad_vars]
                optimizer.apply_gradients(zip(zero_grads, grad_vars))
                optimizer.set_weights(opt_weights)

                # actually set model weights and compile optimizer
                gym.set_weights( gym_weights )
            except Exception as e:
                err = "Failed to read existing cache file %s: %s" % (fullFileName, str(e))
                gym.set_weights(backup_w)
                if not backup_o is None:
                    gym.compile( backup_o, loss={ 'loss' : default_loss } )

        if err != "":
            # handle errors
            # delete file if requested
            if cache_config.cache_mode.del_incomp:
                cache_config.cache_dir.delete( cache_config.cache_file, None )
            add = ("; file has been deleted since cache mode was '%s'" % str(cache_config.cache_mode)) if cache_config.cache_mode.del_incomp else ""
            verbose.report(0,err+add)
            _log.warn(err+add)
            return None

        """ Should experience no more errors from here on """
        gym.compile( optimizer, loss={ 'loss' : default_loss } )

        # trick from https://stackoverflow.com/questions/49503748/save-and-load-model-optimizer-state
        grad_vars     = gym.trainable_weights
        zero_grads    = [tf.zeros_like(w) for w in grad_vars]
        optimizer.apply_gradients(zip(zero_grads, grad_vars))
        optimizer.set_weights(opt_weights)
        verbose.report(0,"Successully loaded model trained until epoch %ld from '%s'", progress_data.current_epoch+1, fullFileName)
        return progress_data

    @property
    def is_done(self):
        """ Checks whether training has finished. This can happen at inception if a cache is restored which was trained for as many epochs as requested """
        return self.progress_data.current_epoch+1 >= self.training_info.epochs

    @property
    def current_epoch(self):
        """ Returns the current epoch. -1 if no epoch was run """
        return self.progress_data.current_epoch

    @property
    def epochs(self):
        """ Returns total number of requested epochs. Note that this can be /less/ than the current epoch if a gym was restored from disk """
        return self.training_info.epochs

    def on_epoch_begin( self, loop_epoch, logs = None ):#NOQA
        if loop_epoch != 0:
            return
        # this event is followed by compilation of the model
        self.progress_data.on_first_epoch_begin(environment       = self.environment,
                                                training_info     = self.training_info )

    def on_epoch_end( self, loop_epoch, logs = None ):
        """
        Called when an epoch ends
        Will call prorgress_data.on_epoch_end()

        Note that 'loop_epoch' is the epoch of the current training run.
        If the state was recovered from a cache, it won't be the logical epoch
        """
        time_now = time.time()
        _current = self.progress_data.current_epoch
        r = self.progress_data._on_epoch_end_prep( environment       = self.environment,
                                                   training_info     = self.training_info,
                                                   time_epoch        = time_now - self.time_start_epoch,
                                                   logs              = logs )
        assert self.progress_data.current_epoch >= 0, "Internal error: progress_data must update its epoch count"
        assert self.progress_data.current_epoch > _current, ("Internal error: progress_data must update its epoch count", self.progress_data.current_epoch, _current)

        # allow calling progress data to abort training
        if r in [Status.STOP_ABORTED, Status.STOP_CONVERGED]:
            self.write_cache()
            self.stop_reason       = r
            self.gym.stop_training = True
        else:
            assert r == Status.CONTINUE, "Invalid stopping reason: %s" % str(r)
            if (self.current_epoch == 0 or (self.current_epoch+1) % self.cache_freq == 0) \
               and self.cache_mode.write\
               and self.progress_data.current_epoch > self.cache_last_epoch:
                self.write_cache()
            self.progress_data.on_epoch_end_update( environment       = self.environment,
                                                    training_info     = self.training_info )
        self.time_start_epoch = time_now

    def finalize( self ):
        """
        Close training. Call this even if training was aborted
        -- Cache the current state
        -- Apply best weight
        """
        # cache current state /before/ we reset gym to its best weights
        # this way we can continue to train from where we left it
        cached_msg = ""
        if self.progress_data.current_epoch >= 0 and self.cache_mode.write:
            fullFileName = self.cache_dir.fullKeyName( self.cache_file )
            self.write_cache()
            cached_msg = " State until epoch %ld cached into %s\n" % (self.cache_last_epoch+1, fullFileName)

        status = Status.status( self.stop_reason )

        # restore best weights & tell user
        self.progress_data._write_best( self.environment.gym )
        self.progress_data._on_done(  environment       = self.environment,
                                      training_info     = self.training_info,
                                      stop_reason       = self.stop_reason )

        self.verbose.report(0, "%(display_name)s status: %(status)s. Current epoch: %(current_epoch)ld.\n"\
                               " Weights set to best epoch: %(best_epoch)ld\n"\
                               "%(cached_msg)s Time: %(time)s",\
                               display_name=self.training_info.display_name,
                               status=status,
                               current_epoch=self.current_epoch+1,
                               best_epoch=self.progress_data.best_epoch+1,
                               cached_msg=cached_msg,
                               time=fmt_now())

# ==========================================================================
# Main training loop
# ==========================================================================

def train(   environment      : Environment = None,
             create_progress  : type = ProgressData,
             config           : Config  = Config(),
             verbose          : Context = Context("all"),
             display_name     : str = None,
             catch_exceptions : bool = False,
             **create_environment ):
    """
    Main training loop

    Parameters
    ----------
        environment : Environment
        **create_environment
            Contains the (initial) gym, training and validation data sets. Also contains sample weights.
            The 'gym' member of the environment can be an object, or a class in which case a new gym is created by calling gym(config.gym).
            If a gym is loaded back from disk, then environment.set_gym() is called.

            If environment is None, then a new environment is created using Environment(**create_environment).
            Combined this means you can write:

                train( gym         = MyGymClass,
                       tf_trn_data = tf_trn_data,
                       tf_val_data = tf_val_data,
                       config      = config
                     )

            Note that 'gym' and 'tf_trn_data' are mandatory arguments for Environment() and must be provided.

        progress_data : ProgressData
            Main callback: the function on_epoch_end() is called at the end of each epoch.
            This function is then intended to compute all other summary statistics required for user feedback doing training.
            The object needs to be pickle'abel if it is intended to be used a multiprocessing environment such as Ray

        config : Config
            Standard config

        verbose : Context
            Controls level of output.
            Set to Context.quiet to surpress all output.

        display_name : str
            Name to display in status messages. If not specified, a name is generated.

        catch_exceptions : bool
            Whether or not to catch exceptions during training, and gracefully recover.
            If this is False, then exceptions will be thrown.
                This is the recommended method when working in an interactive environment.
            If this is True, and if an exception is thrown during training, then the function will return a result with with
                        status    = Status.STOP_EXCEPTION
                        exception = the exception which was caught
                This is the recommended method if train() is run in multiple processes to ensure that termination of the process
                is executed cleanly.

    Returns
    -------
        A PrettyDict which contains, computed at the best weights:
            display_name  : the display name of the environment
            gym           : trained gym, set to best weights (according to training data)
                            Note that this object may differ from the original environment.gym if it was restored from a cache.
            progress_data : progress data, e.g. a version of ProgressData which contains at the very least the time series of losses, and the best weights
            start_time    : datetime of when the process started
            end_time      : datetime of when the process finished
            epochs_trained: number if effective epochs trained. Will be zero if model was fully restored from cache
            status        : reason for stopping, see Status
            exception     : exception if status is Status.STOP_EXCEPTION, None otherwise. Note that this may only happen if catch_exceptions is True

        Values returned from environment.predict():
            trn.result    : numpy arrays of the training results from gym(trn.tf_data)
            trn.loss      : float of the training loss for the current gym
        If val is not None:
            val.result    : numpy arrays of the validation results from gym(val.tf_data)
            val.loss      : float of the validation loss for the current gym
    """
    # --------------------
    # Prep & Caching
    # --------------------

    # how much to print
    debug_numerics   = config.debug("check_numerics", False, bool, "Whether to check TF numerics.")
    tf_verbose       = config.debug("tf_verbose", 0, Int>=0, "Verbosity for TensorFlow fit()")

    # training parameters
    batch_size       = config.train("batch_size",  None, help="Batch size")
    epochs           = config.train("epochs",      100, Int>0, help="Epochs")
    run_eagerly      = config.train("run_eagerly", False, help="Keras gym run_eagerly. Turn to True for debugging. This slows down training. Use None for default.")
    tboard_log_dir   = config.train.tensor_board(   "log_dir", "", str, "Specify tensor board log directory. See https://www.tensorflow.org/guide/profiler")
    tboard_freq      = config.train.tensor_board(   "hist_freq", 1, Int>0, "Specify tensor board log frequency. See https://www.tensorflow.org/guide/profiler")
    tboard_prf_batch = config.train.tensor_board(   "profile_batch", 0, help="Batch used for profiling. Set to non-zero to activate profiling. See https://www.tensorflow.org/guide/profiler")

    # environment & gym
    if environment is None:
        _log.verify( 'gym' in create_environment and 'tf_trn_data' in create_environment, "If 'environment' is not specified, then you need to specify 'gym' and 'tf_trn_data'")
        gym           = create_environment['gym']
        del create_environment['gym']
        gym           = gym if not isinstance(gym,type) else gym(config.gym)
        environment   = Environment(gym=gym, **create_environment )
    else:
        _log.verify( len(create_environment) == 0,  "If 'environment' is specified, then you cannot specify additional keywords. Found %s", fmt_list( list(create_environment.keys())))

    config.gym.mark_done()
    gym                      = environment.gym
    optimizer_uid            = config.train.optimizer.unique_id()
    train_uid                = uniqueFileName48( [ gym.cache_uid, optimizer_uid, gym.CACHE_VERSION ] )
    display_name             = display_name if not display_name is None else gym.display_name
    display_name             = config.train("display_name", display_name, str, "Display name for this training run" )
    verbose.report(0,"Initializing training for %(display_name)s", display_name = display_name )

    # caching
    def_directory_name       = gym.cache_def_directory_name + "/batch_" + (str(batch_size) if not batch_size is None else "default")
    cache_config             = PrettyDict()
    cache_mode               = config.caching("mode", CacheMode.ON, CacheMode.MODES, "Caching strategy: %s" % CacheMode.HELP)
    cache_config.cache_freq  = config.caching("epoch_freq", 10, Int>0, "How often to cache results, in number of epochs")
    cache_dir                = config.caching("directory", "./.cache", str, "Caching parent directory")
    cache_file               = config.caching("overwrite_file_name", "", str, "Allows overwriting the full qualified filename of the object")

    cache_config.cache_dir   = SubDir( cache_dir, "!" )( def_directory_name )
    cache_config.cache_mode  = CacheMode( cache_mode )
    cache_config.cache_file  = train_uid if len(cache_file) == 0 else cache_file

    training_info = TrainingInfo( display_name    = display_name,
                                  batch_size      = batch_size,
                                  epochs          = epochs,
                                  run_eagerly     = run_eagerly,
                                  debug_numerics  = debug_numerics,
                                  cache_full_file = cache_config.cache_dir.fullKeyName( cache_config.cache_file ),
                                  cache_mode      = cache_config.cache_mode,
                                  verbose         = verbose.sub(2) )

    # --------------------
    # Restore cache
    # --------------------

    progress_data = Callback.restore_from_cache( gym, environment.trn.tf_data, cache_config, verbose(1) )
    if not progress_data is None:
        """ Handle cached gym """
        predicted_data0  = environment.predict()
        config.train.optimizer.mark_done()
        config.progress.done()

        progress_data._on_restore( environment    = environment,
                                   predicted_data = predicted_data0,
                                   training_info  = training_info )
        assert progress_data.last_cached_epoch == progress_data.current_epoch, "Internal error: %ld != %ld"  % (progress_data.last_cached_epoch, progress_data.current_epoch)
        if progress_data.remaining_epochs > 0:
            verbose.report(1, "%s: model loaded. Preparing training for the remaining %ld epochs. Model has %ld trainable weights.", display_name, progress_data.remaining_epochs, gym.num_trainable_weights)
    else:
        """ No gym cached yet, or cache ignored """
        gym.compile(    optimizer        = create_optimizer(config.train.optimizer),
                        loss             = { environment.loss_name : default_loss },
                        weighted_metrics = { environment.loss_name : default_loss },
                        run_eagerly      = run_eagerly)
        environment.set_gym( gym, cached=False )

        predicted_data0  = environment.predict()
        progress_data    = create_progress( environment=environment,
                                            predicted_data0=predicted_data0,
                                            training_info=training_info,
                                            config=config.progress )
        verbose.report(1, "%s: model generated. Preparing training for %ld epochs. Model has %ld trainable weights.", display_name, progress_data.remaining_epochs, gym.num_trainable_weights)

    config.done()

    description = gym.description
    if not description is None:
        verbose.report(2, description)

    # --------------------
    # Training
    # --------------------

    remaining_epochs = progress_data.remaining_epochs
    stop_reason      = Status.ALREADY_TRAINED
    stop_exception   = None

    if remaining_epochs <= 0:
        # nothing to do - write 'best' to model
        progress_data._write_best(  environment.gym )
        progress_data._on_done(     environment       = environment,
                                    training_info     = training_info,
                                    stop_reason       = stop_reason )
    else:
        # run training loop
        t0             = time.time()
        callback       = Callback(    environment     = environment,
                                      training_info   = training_info,
                                      progress_data   = progress_data,
                                      cache_config    = cache_config,
                                      verbose         = verbose.sub(1) )
        assert not callback.is_done, "Internal error"

        if debug_numerics:
            tf.debugging.enable_check_numerics()
            verbose.report(1, "Enabled automated checking for numerical errors. This will slow down training. Use config.debug.check_numerics = False to turn this off")
        else:
            tf.debugging.disable_check_numerics()

        # tensorboard
        # See https://docs.aws.amazon.com/sagemaker/latest/dg/studio-tensorboard.html
        tboard = None
        if tboard_log_dir != "":
            t0             = time.time()
            tboard_log_dir = SubDir(tboard_log_dir).path
            tboard         = tf.keras.callbacks.TensorBoard(log_dir=tboard_log_dir, histogram_freq=tboard_freq, profile_batch=tboard_prf_batch )
            verbose.report(1,"TensorBoard log directory set to '%s'. Took %s" % (tboard_log_dir, fmt_seconds(time.time()-t0)))

        try:
            gym.fit(        x              = environment.trn.tf_data,
                            y              = tf.zeros((environment.trn.num_samples,), dtype=gym.dtype),
                            batch_size     = batch_size,
                            sample_weight  = environment.trn.sample_weights * float(len(environment.trn.sample_weights)) if not environment.trn.sample_weights is None else None,  # sample_weights are poorly handled in TF
                            epochs         = remaining_epochs,
                            callbacks      = callback if tboard is None else [ callback, tboard ],
                            verbose        = tf_verbose )
            callback.stop_reason = Status.FINISHED_EPOCHS
        except KeyboardInterrupt:
            callback.stop_reason = Status.STOP_INTERRUPTED
        except Exception as e:
            if not catch_exceptions:
                raise e
            callback.stop_reason = Status.STOP_EXCEPTION
            stop_exception       = e
            _log.critical( "*** %s: exception of type '%s' during model training: %s", display_name, type(e).__name__, str(e) )
        callback.finalize()  # copy best data
        stop_reason      = callback.stop_reason

    # --------------------
    # Results
    # --------------------

    result                = environment.predict()
    result.display_name   = display_name
    result.progress_data  = progress_data
    result.gym            = gym
    result.start_time     = training_info.start_time
    result.end_time       = datetime.now()
    result.epochs_trained = remaining_epochs
    result.status         = stop_reason
    result.exception      = stop_exception

    if remaining_epochs > 0:
        verbose.report(0, "Training %s completed %s. Total training took %s.", display_name, fmt_datetime(result.end_time), fmt_seconds(time.time()-t0))
    else:
        verbose.report(0,"No training required as cached gym for %s is sufficiently trained. Weights set to best epoch: %ld. Training complete %s", display_name, progress_data.best_epoch+1, fmt_datetime(result.end_time))
    return result




