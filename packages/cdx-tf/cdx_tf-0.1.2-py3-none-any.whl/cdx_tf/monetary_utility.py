"""
Monteary utilities
-------------------
Closely linked to deep hedging http://deephedging.com/
March 1st, 2023
@author: hansbuehler
"""

from cdxbasics.logger import Logger
from cdxbasics.util import fmt_list
from cdxbasics.config import Config, Int, Float#NOQA
from cdxbasics.prettydict import PrettyDict as pdct
from .models import to_config, DenseAgent, VariableModel
from .util import tf, def_dtype, default_loss, npCast, tfCast#NOQA
from collections.abc import Mapping
from scipy.optimize import minimize_scalar
import numpy as np
_log = Logger(__file__)

UTILITIES = ['mean', 'exp', 'exp2', 'vicky', 'cvar', 'quad']

class MonetaryUtility(tf.keras.Model):
    """
    Monetary utility function as standard objective for deep hedging.
    The objective for a claim X is defined as

        sup_y E[ u(X+y)-y ]

    The variable 'y' needs to be learned.
    The standard implementation is to learn the variable for the intial payoff and the overall hedging gains in the same
    training loop (see loss definition for the gym).

    By default 'y' is a plain real variable. That assumes that the initial state of the world is constant, and does not
    differ by path. An example to the contrary is if we wanted to learn a hedging strategy accross products (e.g. different strikes for calls).
    In this case, 'y' would have to be a network which depends on such `per_path` features.
    The list of available per path features for a given world in a given gym can be obtained using gym.available_features_per_path()

    Attributes
    ----------
        y_model : bool
            Whether the intercept 'y' is a model which requires features
        features : list
            List of features required; possibly [] if 'y' is a variable or 0.

    Members
    -------
        __call__()
            Tensor flow call to evaluate the utility for a given environment
        compute()
            Computes utility and its derivative after training.

    Hans Buehler, June 2022
    """

    UTILITIES = ['mean', 'exp', 'exp2', 'vicky', 'cvar', 'quad']

    def __init__(self, config : Config = None, *, kwargs_cfg : dict = None, **kwargs):
        """
        Parameters
        ----------
            config : Config
                configuration, most notably
                utility  - which utility to use e.g. mean, exp, vicky, quad
                lmbda    - risk aversion
                features - features to use for time 0 y.
                           Leave empty for a determinstic y amount

            name : str, optional
                Name of the tenosrflow model
            dtype : tf.DType, optional
                dtype
        """
        assert kwargs_cfg is None or len(kwargs) == 0, "Cannot specify 'kwargs_cfg' and **kwargs"
        kwargs            = to_config(kwargs_cfg if not kwargs_cfg is None else kwargs, config_name="kwargs_MonetaryUtility")
        config            = config if not config is None else Config()

        dtype             = kwargs('dtype', def_dtype )
        name              = kwargs('name', None, (str, None))
        trainable         = kwargs('trainable', True, bool)
        tf.keras.Model.__init__(self, name=name, dtype=dtype, trainable=trainable )

        self.utility      = kwargs("utility", None, (None,UTILITIES) )
        self.lmbda        = kwargs("lmbda", None, (None,Float>=0.) )
        eps_lmbda         = kwargs("eps_lmbda", 1E-8, Float>0. )

        def_utility       = kwargs("def_utility", "exp2", UTILITIES )
        def_lmbda         = kwargs("def_lmbda", 1., Float>=0 )

        self.utility      = config("utility",def_utility, UTILITIES, help="Type of monetary utility") if self.utility is None else self.utility
        self.lmbda        = config("lmbda", def_lmbda, Float>=0., help="Risk aversion") if self.lmbda is None else self.lmbda
        self.display_name = self.utility + "@%g" % self.lmbda

        self.y            = DenseAgent( nOutput = 1, config = config, kwargs_cfg = kwargs )

        if self.utility in ["mean"] or self.lmbda < eps_lmbda:
            self.y       = VariableModel( 0., trainable=False, name="y", dtype=dtype )

        config.done() # all config read
        kwargs.done() # catch typos

    def __call__( self, X : tf.Tensor, features : dict = None, training : bool = False, return_derivative : bool = False  ) -> tf.Tensor:
        """
        Compute the monetary utility for a Deep Hedging problem,
            u(X+y) - y
        and its derivative in X for random variable X and y=self.y

        Parameters
        ----------
        X: tf.Tensor
            Random variable, typically total gains on the path
        features : dict
            features required for 'y' if so specified.
            Check self.features
        training : bool, optional
            Whether we are in training model

        Returns
        -------
            dict:
                The OCE utility value. If 'return_derivative' then this function returns the tuple of the value and its derivative.
        """
        features = features if not features is None else dict()
        _log.verify( isinstance(features, Mapping), "'features_time_0' must be a dictionary type. Found type %s", type(features).__name__)
        y      = self.y( features, training=training )
        assert len(y.shape) == 2 and y.shape[1] == 1, "Internal error: expected variable to return a vector of shape [None,1]. Found %s" % y.shape.as_list()
        y      = y[:,0]
        return tf_utility( utility=self.utility, lmbda=self.lmbda, X=X, y=y, return_derivative=return_derivative )

    @property
    def features(self):
        """ Features used by the utility """
        return self.y.features
    @property
    def available_features(self):
        """ Features available to the utility. """
        return self.y.available_features
    @property
    def has_features(self):
        """ Number of features used """
        return self.y.has_features
    @property
    def has_state(self):
        """ Number of features used """
        return self.y.has_state
    @property
    def num_trainable_weights(self) -> int:
        """ Returns the number of weights. The model must have been call()ed once """
        weights = self.trainable_weights
        return np.sum( [ np.prod( w.get_shape() ) for w in weights ] )

    def compute_stateless_utility(self, X : np.ndarray, sample_weights : np.ndarray = None, **minimize_scalar_kwargs ) -> float:
        """
        Computes the utility of a payoff with classic optimization, assuming a stateless/featurless intercept 'y'.

        Parameters
        ----------
            payoff : the terminal value to compute a utility for
            sample_weights: from the world. If None, set to 1/N

        Returns
        -------
            The utility value as a float.
        """
        return oce_utility( self.utility, self.lmbda, X=X, sample_weights=sample_weights )

# -------------------------------------------------
# utilities for managing layers
# -------------------------------------------------

@tf.function(reduce_retracing=True)
def tf_utility( utility : str, lmbda : float, X : tf.Tensor, y : tf.Tensor = 0., return_derivative : bool = False, dtype : tf.DType = def_dtype ) -> dict:
    """
    Computes
        u(X+y) - y
    and its derivative in X for random variable X and OCE variable y.
    Read the material on http://deephedging.com/ for more details.

    Parameters
    ----------
    utility: str
        Which utility function 'u' to use
    lmbda : flost
        risk aversion
    X: tf.Tensor
        Random variable, typically total gains on the path
    y: tf.Tensor, None, or 0
        OCE intercept y.

    Returns
    -------
        dict if return_derivative is True
            with menbers 'u' and 'd'
        the utility value if return_derivative is False
    """
    X = tf.convert_to_tensor( X, dtype=dtype )
    y = tf.convert_to_tensor( y, dtype=dtype )
#    if not y is None and not isinstance(y, float):
#        print(type(X),X.shape, type(y),y.shape, y)
#        _log.verify( X.shape == y.shape, "'X' and 'y' must have the same shape. Found %s and %s, respectively", X.shape.as_list(), y.shape.as_list() )

    utility  = str(utility)
    lmbda    = float(lmbda)
    y        = y if not y is None else 0.
    gains    = X + y

    _log.verify( lmbda >= 0., "Risk aversion 'lmbda' cannot be negative. Found %g", lmbda )
    if lmbda < 1E-12:
        # Zero lambda => mean
        utility = "mean"
        lmbda   = 1.

    if utility in ["mean", "expectation"]:
        # Expectation
        #
        u = gains
        d = tf.ones_like(gains)

    elif utility == "cvar":
        # CVaR risk measure
        #   u(x) = (1+lambda) min(0, x)
        # The resulting OCE measure U computes the expected value under the condition that X is below the p's percentile.
        #   U(X) = E[ X | X <= P^{-1}[ X<=* ](p)
        # Here p is small to reflect risk-aversion, e.g p=5% means we are computing the mean over the five worst percentiles.
        # Note that CVaR is often quoted with a survival percentile, e.g. q = 1-p e.g. 95%
        #
        # Conversion from percentile p (e.g. 5%)
        #   1+lambda = 1/p
        # =>
        #   lambda = 1/p - 1
        #
        # Conversion from lambda to percentile
        #   p = 1/(1+lambda)
        #
        # In other words, for p=50% use 1. (as in https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3120710)
        #                 for p=5%  use 19.

        u = (1.+lmbda) * tf.math.minimum( 0., gains ) - y
        d = tf.where( gains < 0., -(1.+lmbda), 0. )

    elif utility == "quad":
        # quadratic penalty; flat extrapolation
        #
        # u(x)  = -0.5 lambda * ( x - x0 )^2 + 0.5 * lmbda * x0^2;   u(0)  = 0
        # u'(x) = - lambda (x-x0);                                   u'(0) = 1 = lambda x0 => x0 = 1/lmbda

        x0 = 1./lmbda
        xx = tf.minimum( 0., gains-x0 )
        u  = - 0.5 * lmbda * (xx**2) + 0.5 * lmbda * (x0**2) - y
        d  = - lmbda * xx

    elif utility in ["exp", "entropy"]:
        # Entropy
        #   u(x) = { 1 - exp(- lambda x ) } / lambda
        #
        # The OCE measure for this utility has the closed form
        #   U(X) = - 1/lambda log E[ exp(-\lambda X) ]
        #
        # However, this tends to be numerically challenging.
        # we introcue a robust version less likely to explode
        inf = tf.stop_gradient( tf.reduce_min( X ) )
        u = (1. - tf.math.exp( - lmbda * (gains-inf)) ) / lmbda - y + inf
        d = tf.math.exp(- lmbda * gains )

    elif utility == "exp2":
        # Exponential for the positive axis, quadratic for the negative axis.
        # A non-exploding version of the entropy
        #
        # u1(x)  = { 1-exp(-lambda x) } / lambda; u1(0)  = 0
        # u1'(x) = exp(-lambda x);                u1'(0) = 1
        # u2(x)  = x - 0.5 lambda x^2;            u2(0)  = 0
        # u2'(x) = 1 - lambda x;                  u2'(0) = 1
        g1  = tf.maximum(gains,0.)
        g2  = tf.minimum(gains,0.)
        eg1 = tf.math.exp( - lmbda * g1)
        u1  = (1. - eg1 ) / lmbda - y
        u2  = g2 - 0.5 * lmbda * g2 * g2 - y
        d1  = eg1
        d2  = 1. - lmbda * g2
        u   = tf.where( gains > 0., u1, u2 )
        d   = tf.where( gains > 0., d1, d2 )

    elif utility == "vicky":
        # Vicky Handerson & Mark Rodgers
        # https://warwick.ac.uk/fac/sci/statistics/staff/academic-research/henderson/publications/indifference_survey.pdf
        #
        # u(x)  = { 1 + lambda * x - sqrt{ 1+lambda^2*x^2 } } / lmbda
        # u'(x) = 1 - lambda x / sqrt{1+lambda^2*x^2}
        u = (1. + lmbda * gains - tf.math.sqrt( 1. + (lmbda * gains) ** 2 )) / lmbda  - y
        d = 1 - lmbda * gains / tf.math.sqrt( 1. + (lmbda * gains) ** 2)

    _log.verify( not u is None, "Unknown utility function '%s'. Use one of %s", utility, fmt_list( UTILITIES )  )

    u = tf.debugging.check_numerics(u, "Numerical error computing u in %s. Turn on tf.enable_check_numerics to find the root cause.\nX: %s\ny : %s" % (__file__, str(X), str(y)) )
    d = tf.debugging.check_numerics(d, "Numerical error computing d in %s. Turn on tf.enable_check_numerics to find the root cause.\nX: %s\ny : %s" % (__file__, str(X), str(y)) )

    return pdct(
            u = u,
            d = d
        ) if return_derivative else u



# -------------------------------------------------------------------------
# Mini OCE solver using scalar optimization
# -------------------------------------------------------------------------

class _Objective( tf.keras.Model ):

    def __init__(self, utility, lmbda, init = 0. ):
        tf.keras.Model.__init__(self)
        self.utility = utility
        self.lmbda   = lmbda
        self.y       = tf.Variable(init, dtype=def_dtype)

    def call(self, data, training=False):
        assert len(data.shape) == 1, "'data' must be a vector, found shape %s" % (data.shape.as_list())
        return -tf_utility( self.utility, self.lmbda, X=data, y=self.y ).u

def oce_utility( utility : str,
                 lmbda : float,
                 X : np.ndarray,
                 sample_weights : np.ndarray = None,
                 method : str = None,
                 epochs : int = 100,
                 batch_size : int = 'all',
                 **minimize_scalar_kwargs ) -> float:
    """
    Stand-alone OCE utility calculation, using analytical solutions where possible or a numerical.
    This function computes the OCE utility for a real intercept 'y'.
    Statefull intercepts are supported by the

    Parameters
    ----------
        utility:
            Name of the utility function, see MonetaryUtility.UTILITIES
        lmbda:
            Risk aversion
        X:
            Variable to compute utility for
        sample_weights:
            Sammple weights or None for 1/n
        method:
            None for best,
            'analytical' for numerical where possible
            'minscalar' for numerical minimization
            'tf' for tensorflow
        epochs, batch_size:
            For tensorflow mode.
            Use batch_size='all' for full batch size, None for 32 or a specific number
        minimize_scalar_kwargs:
            Arguments for 'minscalar'

    Returns
    -------
        Result
    """
    utility        = str(utility)
    lmbda          = float(lmbda)
    X              = np.asarray(X)
    sample_weights = np.asarray(sample_weights) if not sample_weights is None else None

    _log.verify( len(X.shape) == 1, "'X' must be a vector, found shape %s", X.shape)
    _log.verify( utility in UTILITIES, "Unknown utility '%s': must be one of %s", utility, fmt_list(UTILITIES) )

    if not sample_weights is None:
        _log.verify( sample_weights.shape[0] == len(X), "'sample_weights' first dimension must be %ld, not %ld", len(X), sample_weights.shape[0] )
        if len(sample_weights.shape) == 2:
            _log.verify( sample_weights.shape[1] == 1, "'sample_weights' second dimension must be 1, not %ld", sample_weights.shape[1] )
        else:
            _log.verify( len(sample_weights.shape) == 1, "'sample_weights' must be vector of length %ld. Found shape %ld", len(X), sample_weights.shape )
            sample_weights = sample_weights[:,np.newaxis]
        w = np.sum( sample_weights )
        _log.verify( w > 1E-10, "'sample_weights' add up to approximately zero: %g", w )
        sample_weights /= w

    # analytical?
    # -----------

    if method is None or method =="analytical":
        P = sample_weights[:,0] if not sample_weights is None else None

        if utility in ["mean", "expectation"] or lmbda == 0.:
            return np.sum(P * X) if not P is None else np.mean(X)

        if utility in ["exp", "entropy"]:
            expX = np.exp( - lmbda * X )
            eexp = np.sum( P * expX ) if not P is None else np.mean( expX )
            return - np.log( eexp ) / lmbda

        if utility == "cvar":
            p         = 1./(1. + lmbda)
            assert p>0. and p<=1., "Invalid percentile %g" % p
            if abs(1.-p)<1E-8:
                return np.sum(P * X) if not P is None else np.mean(X)

            if sample_weights is None:
                pcnt     = np.percentile( X, p*100. )
                ixs      = X <= pcnt
                return np.mean( X[ixs] )

            ixs       = np.argsort(X)
            X         = X[ixs]
            P         = P[ixs]
            cumP      = np.cumsum(P)
            assert abs(cumP[-1]-1.)<1E-4, "Internal error: cumsum(P)[-1]-1 = %g" % (cumP[-1]-1.)
            cumP[-1]  = 1.
            if p <= cumP[0]:
                return X[0]
            ix        = np.searchsorted( cumP, p )
            ix        = max( 0., min( len(X)-1, ix ))
            return np.sum( (P * X)[:ix+1] ) / np.sum( P[:ix+1] )

        _log.verify( method is None, "Cannot solve utility '%s' analytically", utility )

    # minimize_scalar
    # ---------------

    if method is None or method == 'minscalar':
        X = tfCast(X, dtype=def_dtype)
        def objective(y):
            y = np.asarray(y)
            y = tfCast(y, dtype=def_dtype)
            u = tf_utility(utility, lmbda, X, y=y )
            u = np.asarray( u )
            u = np.sum( sample_weights[:,0] * u ) if not sample_weights is None else np.mean(u)
            return -u

        _  = objective(0.)   # triggers errors if any
        r  = minimize_scalar( objective, tol=1E-6, **minimize_scalar_kwargs )
        if not r.success: _log.error( "Failed to find optimal intercept 'y' for utility %s with risk aversion %g: %s", utility, lmbda, r.message )
        return -objective(r.x)

    # tensorflow
    # ----------

    _log.verify( method == 'tf', "'method' must be None, 'minscalar', or 'tf'. Found %s", method )

    batch_size     = len(X) if batch_size == 'all' else batch_size
    epochs         = int(epochs)
    X              = tfCast(X, dtype=def_dtype)
    sample_weights = tfCast(sample_weights, dtype=def_dtype) if not sample_weights is None else None

    model = _Objective( utility, lmbda, np.mean(X) )
    model.compile( optimizer = "adam", loss=default_loss )
    model.fit(  x              = X,
                y              = X*0.,
                batch_size     = batch_size,
                sample_weight  = sample_weights * float(len(X)) if not sample_weights is None else None,  # sample_weights are poorly handled in TF
                epochs         = epochs,
                verbose = 0)

    return -np.mean(model(X))
