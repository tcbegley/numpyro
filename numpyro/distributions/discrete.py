# Source code modified from scipy.stats._discrete_distns.py
#
# Copyright (c) 2001, 2002 Enthought, Inc.
# All rights reserved.
#
# Copyright (c) 2003-2019 SciPy Developers.
# All rights reserved.

import jax.numpy as np
from jax.lax import lgamma

from numpyro.distributions.distribution import jax_discrete
from numpyro.distributions.util import entr, xlogy, xlog1py


class binom_gen(jax_discrete):
    def _rvs(self, n, p):
        return self._random_state.binomial(n, p, self._size)

    def _argcheck(self, n, p):
        self.b = n
        return (n >= 0) & (p >= 0) & (p <= 1)

    def _logpmf(self, x, n, p):
        k = np.floor(x)
        combiln = (lgamma(n + 1) - (lgamma(k + 1) + lgamma(n - k + 1)))
        return combiln + xlogy(k, p) + xlog1py(n - k, -p)

    def _pmf(self, x, n, p):
        # binom.pmf(k) = choose(n, k) * p**k * (1-p)**(n-k)
        return np.exp(self._logpmf(x, n, p))

    def _stats(self, n, p, moments='mv'):
        q = 1.0 - p
        mu = n * p
        var = n * p * q
        g1, g2 = None, None
        if 's' in moments:
            g1 = (q - p) / np.sqrt(var)
        if 'k' in moments:
            g2 = (1.0 - 6 * p * q) / var
        return mu, var, g1, g2

    def _entropy(self, n, p):
        k = np.r_[0:n + 1]
        vals = self._pmf(k, n, p)
        return np.sum(entr(vals), axis=0)


class bernoulli_gen(binom_gen):
    def _rvs(self, p):
        return binom_gen._rvs(self, 1, p)

    def _argcheck(self, p):
        return (p >= 0) & (p <= 1)

    def _logpmf(self, x, p):
        return binom._logpmf(x, 1, p)

    def _pmf(self, x, p):
        # bernoulli.pmf(k) = 1-p  if k = 0
        #                  = p    if k = 1
        return binom._pmf(x, 1, p)

    def _stats(self, p):
        return binom._stats(1, p)

    def _entropy(self, p):
        return entr(p) + entr(1 - p)


bernoulli = bernoulli_gen(b=1, name='bernoulli')
binom = binom_gen(name='binom')
