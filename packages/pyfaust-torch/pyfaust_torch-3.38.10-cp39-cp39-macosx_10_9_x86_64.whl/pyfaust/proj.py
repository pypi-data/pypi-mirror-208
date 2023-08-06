# -*- coding: utf-8 -*-
# ##########################################################################################
# Copyright (c) 2021, INRIA                                                              #
# All rights reserved.                                                                   #
#                                                                                        #
# BSD License 2.0                                                                        #
#                                                                                        #
# Redistribution and use in source and binary forms, with or without                     #
# modification, are permitted provided that the following conditions are met:            #
# * Redistributions of source code must retain the above copyright notice,               #
# this list of conditions and the following disclaimer.                                  #
# * Redistributions in binary form must reproduce the above copyright notice,            #
# this list of conditions and the following disclaimer in the documentation              #
# and/or other materials provided with the distribution.                                 #
# * Neither the name of the <copyright holder> nor the names of its contributors         #
# may be used to endorse or promote products derived from this software without          #
# specific prior written permission.                                                     #
#                                                                                        #
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND        #
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED          #
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.     #
# IN NO EVENT SHALL INRIA BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,       #
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF     #
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) #
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,  #
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS  #
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.                           #
#                                                                                        #
# Contacts:                                                                              #
# 	Remi Gribonval  : remi.gribonval@inria.fr                                        #
# 	Hakim Hadj-dji. : hakim.hadj-djilani@inria.fr                                    #
#                                                                                        #
# Authors:                                                                               #
# 	Software Engineers:                                                              #
# 		Nicolas Bellot                                                           #
# 		Thomas Gautrais,                                                         #
# 		Hakim Hadj-Djilani,                                                      #
# 		Adrien Leman,                                                            #
#                                                                                        #
# 	Researchers:                                                                     #
# 		Luc Le Magoarou,                                                         #
# 		Remi Gribonval                                                           #
#                                                                                        #
# 	INRIA, France                                                             #
# 	http://www.inria.fr/                                                             #
##########################################################################################

## @package pyfaust.proj @brief This module provides matrix projectors.
import _FaustCorePy
from pyfaust.factparams import *
from abc import ABC, abstractmethod

from pyfaust.fact import _check_fact_mat

class proj_gen(ABC):
    """
    The parent abstract class to represent projectors (as functors).
    """
    @abstractmethod
    def __init__(self, shape):
        self.shape = shape

    def __call__(self, M):
        return self.constraint.project(M)

class proj_id(proj_gen):
    """
    Functor for the identity projector.

    This projector simply returns the same array as the one passed as argument.

    It's not useless for example in PALM4MSA (pyfaust.fact.palm4msa,
    pyfaust.fact.hierarchical) it might serve to avoid any
    constraint on a factor.

    Example:
    >>> from pyfaust.proj import proj_id
    >>> from numpy import allclose
    >>> from numpy.random import rand
    >>> M = rand(5,5)
    >>> p = proj_id(M.shape)
    >>> allclose(p(M), M)
    True
    """

    def __init__(self, shape):
        super(proj_id, self).__init__(shape)
        self.constraint = ConstraintMat('id', shape=shape)
        self.constraint._num_rows = shape[0]
        self.constraint._num_cols = shape[1]

class toeplitz(proj_gen):
    """
    Functor for the TOEPLITZ projector.

    Example:
        >>> from pyfaust.proj import toeplitz
        >>> from numpy.random import rand, seed
        >>> import numpy as np
        >>> seed(42) # just for reproducibility
        >>> M = np.round(rand(5,5), decimals=2)
        >>> M
        array([[0.37, 0.95, 0.73, 0.6 , 0.16],
               [0.16, 0.06, 0.87, 0.6 , 0.71],
               [0.02, 0.97, 0.83, 0.21, 0.18],
               [0.18, 0.3 , 0.52, 0.43, 0.29],
               [0.61, 0.14, 0.29, 0.37, 0.46]])
        >>> p = toeplitz(M.shape)
        >>> p(M)
        array([[0.18366651, 0.24773622, 0.21498948, 0.27977108, 0.06834103],
               [0.21570136, 0.18366651, 0.24773622, 0.21498948, 0.27977108],
               [0.08685005, 0.21570136, 0.18366651, 0.24773622, 0.21498948],
               [0.06834103, 0.08685005, 0.21570136, 0.18366651, 0.24773622],
               [0.26055016, 0.06834103, 0.08685005, 0.21570136, 0.18366651]])

    """
    def __init__(self, shape, normalized=True, pos=False):
        """
        Args:
            shape: the size of the input matrix.
            normalized: True to normalize the projection image according to its Frobenius norm.
            pos: True to skip negative values (replaced by zero) of the matrix to project.
        """
        super(toeplitz, self).__init__(shape)
        self.constraint = ConstraintMat('toeplitz', shape=shape,
                                        normalized=normalized, pos=pos)

class circ(proj_gen):
    """
    Functor for the CIRC(ulant) projector.


    Example:
        >>> from pyfaust.proj import circ
        >>> import numpy as np
        >>> from numpy.random import rand, seed
        >>> seed(43) # for reproducibility
        >>> M = (rand(5, 5)*10).astype('int').astype('double')
        >>> M
        array([[1., 6., 1., 2., 3.],
               [8., 6., 5., 0., 7.],
               [3., 8., 2., 0., 8.],
               [2., 4., 3., 0., 8.],
               [8., 9., 3., 9., 4.]])
        >>> p = circ(M.shape, normalized=False)
        >>> p(M)
        array([[2.6, 5.4, 4. , 3.8, 6.2],
               [6.2, 2.6, 5.4, 4. , 3.8],
               [3.8, 6.2, 2.6, 5.4, 4. ],
               [4. , 3.8, 6.2, 2.6, 5.4],
               [5.4, 4. , 3.8, 6.2, 2.6]])


    """
    def __init__(self, shape, normalized=True, pos=False):
        """
        Args:
            shape: the size of the input matrix.
            normalized: True to normalize the projection image according to its Frobenius norm.
            pos: True to skip negative values (replaced by zero) of the matrix to project.


        """
        super(circ, self).__init__(shape)
        self.constraint = ConstraintMat('circ', shape=shape,
                                        normalized=normalized, pos=pos)


class anticirc(proj_gen):
    """
    Functor for the anticirculant projector.


    Example:
        >>> from pyfaust.proj import circ
        >>> import numpy as np
        >>> from numpy.random import rand, seed
        >>> seed(43) # for reproducibility
        >>> M = (rand(5, 5)*10).astype('int').astype('double')
        >>> M
        array([[1., 6., 1., 2., 3.],
               [8., 6., 5., 0., 7.],
               [3., 8., 2., 0., 8.],
               [2., 4., 3., 0., 8.],
               [8., 9., 3., 9., 4.]])
        >>> p = anticirc(M.shape, normalized=False)
        >>> p(M)
        array([[4. , 5. , 5.4, 4.2, 3.4],
               [5. , 5.4, 4.2, 3.4, 4. ],
               [5.4, 4.2, 3.4, 4. , 5. ],
               [4.2, 3.4, 4. , 5. , 5.4],
               [3.4, 4. , 5. , 5.4, 4.2]])


    """
    def __init__(self, shape, normalized=True, pos=False):
        """
        Args:
            shape: the size of the input matrix.
            normalized: True to normalize the projection image according to its Frobenius norm.
            pos: True to skip negative values (replaced by zero) of the matrix to project.


        """
        super(anticirc, self).__init__(shape)
        self.constraint = ConstraintMat('anticirc', shape=shape,
                                        normalized=normalized, pos=pos)

class hankel(proj_gen):
    """
    Functor for the HANKEL projector.

    Example:
        >>> from pyfaust.proj import hankel
        >>> from numpy.random import rand, seed
        >>> import numpy as np
        >>> seed(42) # just for reproducibility
        >>> M = np.round(rand(5,5), decimals=2)
        >>> M
        array([[0.37, 0.95, 0.73, 0.6 , 0.16],
               [0.16, 0.06, 0.87, 0.6 , 0.71],
               [0.02, 0.97, 0.83, 0.21, 0.18],
               [0.18, 0.3 , 0.52, 0.43, 0.29],
               [0.61, 0.14, 0.29, 0.37, 0.46]])
        >>> p = hankel(M.shape)
        >>> p(M)
        array([[0.1613085 , 0.24196275, 0.11771161, 0.28555964, 0.21798446],
               [0.24196275, 0.11771161, 0.28555964, 0.21798446, 0.17220772],
               [0.11771161, 0.28555964, 0.21798446, 0.17220772, 0.13079068],
               [0.28555964, 0.21798446, 0.17220772, 0.13079068, 0.14386974],
               [0.21798446, 0.17220772, 0.13079068, 0.14386974, 0.2005457 ]])


    """
    def __init__(self, shape, normalized=True, pos=False):
        """
        Args:
            shape: the size of the input matrix.
            normalized: True to normalize the projection image according to its Frobenius norm.
            pos: True to skip negative values (replaced by zero) of the matrix to project.
        """
        super(hankel, self).__init__(shape)
        self.constraint = ConstraintMat('hankel', shape=shape,
                                        normalized=normalized, pos=pos)


class sp(proj_gen):
    """
    Functor for the SP projector.

    A, the image matrix, is such that \f$ \| A \|_0 = k,  \| A\|_F = 1 \f$ (if normalized == True).


    Example:
        >>> from pyfaust.proj import sp
        >>> from numpy.random import rand, seed
        >>> import numpy as np
        >>> seed(42) # just for reproducibility
        >>> M = np.round(rand(5,5), decimals=2)
        >>> M
        array([[0.37, 0.95, 0.73, 0.6 , 0.16],
               [0.16, 0.06, 0.87, 0.6 , 0.71],
               [0.02, 0.97, 0.83, 0.21, 0.18],
               [0.18, 0.3 , 0.52, 0.43, 0.29],
               [0.61, 0.14, 0.29, 0.37, 0.46]])
        >>> p = sp(M.shape, 3, normalized=False)
        >>> p(M)
        array([[0.  , 0.95, 0.  , 0.  , 0.  ],
               [0.  , 0.  , 0.87, 0.  , 0.  ],
               [0.  , 0.97, 0.  , 0.  , 0.  ],
               [0.  , 0.  , 0.  , 0.  , 0.  ],
               [0.  , 0.  , 0.  , 0.  , 0.  ]])
    """

    def __init__(self, shape, k, normalized=True, pos=False):
        """

        Args:
            shape: shape of the input array.
            k: the number of nonzeros of the projection image.
            normalized: True to normalize the projection image according to its Frobenius norm.
            pos: True to skip negative values (replaced by zero) of the matrix to project.

        """
        super(sp, self).__init__(shape)
        self.constraint = ConstraintInt('sp', shape[0], shape[1], k, normalized, pos)

class splin(proj_gen):
    """
    Functor for the SPLIN projector.

    A, the image matrix, is defined by \f$
    \forall i \in \{0,...,shape[0]-1\} \| \f$ the i-th row \f$ A_{i,*}\f$ is
    such that \f$ \| A_{i,*}\|_0 = k,  \| A\|_F = 1\f$ (if normalized == True).


    Example:
        >>> from pyfaust.proj import splin
        >>> from numpy.random import rand, seed
        >>> import numpy as np
        >>> seed(42) # just for reproducibility
        >>> M = np.round(rand(5,5), decimals=2)
        >>> M
        array([[0.37, 0.95, 0.73, 0.6 , 0.16],
               [0.16, 0.06, 0.87, 0.6 , 0.71],
               [0.02, 0.97, 0.83, 0.21, 0.18],
               [0.18, 0.3 , 0.52, 0.43, 0.29],
               [0.61, 0.14, 0.29, 0.37, 0.46]])
        >>> p = splin(M.shape, 3, normalized=False)
        >>> p(M)
        array([[0.  , 0.95, 0.73, 0.6 , 0.  ],
               [0.  , 0.  , 0.87, 0.6 , 0.71],
               [0.  , 0.97, 0.83, 0.21, 0.  ],
               [0.  , 0.3 , 0.52, 0.43, 0.  ],
               [0.61, 0.  , 0.  , 0.37, 0.46]])

    """
    def __init__(self, shape, k, normalized=True, pos=False):
        """
        Args:
            shape: shape of the input array.
            k: the number of nonzeros of the projection image.
            normalized: True to normalize the projection image according to its Frobenius norm.
            pos: True to skip negative values (replaced by zero) of the matrix to project.

        """
        super(splin, self).__init__(shape)
        self.constraint = ConstraintInt('splin', shape[0], shape[1], k, normalized, pos)

class spcol(proj_gen):
    """
    Functor for the SPCOL projector.

    A, the image matrix, is defined by \f$
    \forall j \in \{0,...,shape[1]-1\} \f$ the j-th column \f$ A_{*,j}\f$ is
    such that \f$ \| A_{*,j}\|_0 = k,  \| A\|_F = 1\f$ (if normalized == True)

    Example:
        >>> from numpy.random import rand, seed
        >>> from pyfaust.proj import spcol
        >>> import numpy as np
        >>> seed(42) # just for reproducibility
        >>> M = np.round(rand(5,5), decimals=2)
        >>> M
        array([[0.37, 0.95, 0.73, 0.6 , 0.16],
               [0.16, 0.06, 0.87, 0.6 , 0.71],
               [0.02, 0.97, 0.83, 0.21, 0.18],
               [0.18, 0.3 , 0.52, 0.43, 0.29],
               [0.61, 0.14, 0.29, 0.37, 0.46]])
        >>> p = spcol(M.shape, 3, normalized=False)
        >>> p(M)
        array([[0.37, 0.95, 0.73, 0.6 , 0.  ],
               [0.  , 0.  , 0.87, 0.6 , 0.71],
               [0.  , 0.97, 0.83, 0.  , 0.  ],
               [0.18, 0.3 , 0.  , 0.43, 0.29],
               [0.61, 0.  , 0.  , 0.  , 0.46]])

    """
    def __init__(self, shape, k, normalized=True, pos=False):
        """

        Args:
            shape: shape of the input array.
            S: the support matrix.
            normalized: True to normalize the projection image according to its Frobenius norm.
            pos: True to skip negative values (replaced by zero) of the matrix to project.

        """
        super(spcol, self).__init__(shape)
        self.constraint = ConstraintInt('spcol', shape[0], shape[1], k, normalized, pos)

class splincol(proj_gen):
    """
    Functor for the SPLINCOL projector.

    It's the union of SPLIN and SPCOL projectors.

    Example:
        >>> from pyfaust.proj import splincol, splin, spcol
        >>> from numpy.random import rand, seed
        >>> import numpy as np
        >>> seed(42) # just for reproducibility
        >>> M = np.round(rand(5,5), decimals=2)
        >>> M
        array([[0.37, 0.95, 0.73, 0.6 , 0.16],
               [0.16, 0.06, 0.87, 0.6 , 0.71],
               [0.02, 0.97, 0.83, 0.21, 0.18],
               [0.18, 0.3 , 0.52, 0.43, 0.29],
               [0.61, 0.14, 0.29, 0.37, 0.46]])
        >>> p1 = splin(M.shape, 3, normalized=False)
        >>> p2 = spcol(M.shape, 3, normalized=False)
        >>> p = splincol(M.shape, 3, normalized=False)
        >>> p1(M)
        array([[0.  , 0.95, 0.73, 0.6 , 0.  ],
               [0.  , 0.  , 0.87, 0.6 , 0.71],
               [0.  , 0.97, 0.83, 0.21, 0.  ],
               [0.  , 0.3 , 0.52, 0.43, 0.  ],
               [0.61, 0.  , 0.  , 0.37, 0.46]])
        >>> p2(M)
        array([[0.37, 0.95, 0.73, 0.6 , 0.  ],
               [0.  , 0.  , 0.87, 0.6 , 0.71],
               [0.  , 0.97, 0.83, 0.  , 0.  ],
               [0.18, 0.3 , 0.  , 0.43, 0.29],
               [0.61, 0.  , 0.  , 0.  , 0.46]])
        >>> p(M)
        array([[0.37, 0.95, 0.73, 0.6 , 0.  ],
               [0.  , 0.  , 0.87, 0.6 , 0.71],
               [0.  , 0.97, 0.83, 0.21, 0.  ],
               [0.18, 0.3 , 0.52, 0.43, 0.29],
               [0.61, 0.  , 0.  , 0.37, 0.46]])
        >>> p1M = p1(M)
        >>> p2M = p2(M)
        >>> p1M[p1M == p2M] = 0
        >>> p1M+p2M
        array([[0.37, 0.95, 0.73, 0.6 , 0.  ],
               [0.  , 0.  , 0.87, 0.6 , 0.71],
               [0.  , 0.97, 0.83, 0.21, 0.  ],
               [0.18, 0.3 , 0.52, 0.43, 0.29],
               [0.61, 0.  , 0.  , 0.37, 0.46]])
        >>> (p1M+p2M == p(M)).all()
        True

    """
    def __init__(self, shape, k, normalized=True, pos=False):
        """

        Args:
            shape: shape of the input array.
            k: the integer sparsity (number of nonzeros) targeted per-row and
            per-column.
            normalized: True to normalize the projection image according to its Frobenius norm.
            pos: True to skip negative values (replaced by zero) of the matrix to project.

        """
        super(splincol, self).__init__(shape)
        self.constraint = ConstraintInt('splincol', shape[0], shape[1], k, normalized, pos)

class supp(proj_gen):
    """
        Functor for the SUPP projector. A, the image matrix, is such that np.nonzero(A) == np.nonzero(S).

        Example:
            >>> from pyfaust.proj import supp
            >>> from numpy.random import rand, seed
            >>> from numpy import zeros
            >>> import numpy as np
            >>> seed(42) # just for reproducibility
            >>> M = np.round(rand(5,5), decimals=2)
            >>> M
            array([[0.37, 0.95, 0.73, 0.6 , 0.16],
                   [0.16, 0.06, 0.87, 0.6 , 0.71],
                   [0.02, 0.97, 0.83, 0.21, 0.18],
                   [0.18, 0.3 , 0.52, 0.43, 0.29],
                   [0.61, 0.14, 0.29, 0.37, 0.46]])
            >>> S = zeros((5,5))
            >>> S[M>.5] = 1 # the support of values > .5 in M
            >>> p = supp(S, normalized=False)
            >>> p(M)
            array([[0.  , 0.95, 0.73, 0.6 , 0.  ],
                   [0.  , 0.  , 0.87, 0.6 , 0.71],
                   [0.  , 0.97, 0.83, 0.  , 0.  ],
                   [0.  , 0.  , 0.52, 0.  , 0.  ],
                   [0.61, 0.  , 0.  , 0.  , 0.  ]])

    """
    def __init__(self, S, normalized=True, pos=False):
        """

        Args:
            S: the support matrix.
            normalized: True to normalize the projection image according to its Frobenius norm.
            pos: True to skip negative values (replaced by zero) of the matrix to project.
        """
        super(supp, self).__init__(S.shape)
        self.constraint = ConstraintMat('supp', cons_value=S,
                                        normalized=normalized, pos=pos)

class const(proj_gen):
    """
        Functor for the CONST projector. A, the image matrix, is such that A == C.

        Example:
            >>> from pyfaust.proj import const
            >>> from numpy.random import rand, seed
            >>> import numpy as np
            >>> seed(42) # just for reproducibility
            >>> M = np.round(rand(5,5), decimals=2)
            >>> C = np.round(rand(5,5), decimals=2)
            >>> p = const(C)
            >>> C
            array([[0.79, 0.2 , 0.51, 0.59, 0.05],
                   [0.61, 0.17, 0.07, 0.95, 0.97],
                   [0.81, 0.3 , 0.1 , 0.68, 0.44],
                   [0.12, 0.5 , 0.03, 0.91, 0.26],
                   [0.66, 0.31, 0.52, 0.55, 0.18]])
            >>> M
            array([[0.37, 0.95, 0.73, 0.6 , 0.16],
                   [0.16, 0.06, 0.87, 0.6 , 0.71],
                   [0.02, 0.97, 0.83, 0.21, 0.18],
                   [0.18, 0.3 , 0.52, 0.43, 0.29],
                   [0.61, 0.14, 0.29, 0.37, 0.46]])
            >>> p(M)
            array([[0.79, 0.2 , 0.51, 0.59, 0.05],
                   [0.61, 0.17, 0.07, 0.95, 0.97],
                   [0.81, 0.3 , 0.1 , 0.68, 0.44],
                   [0.12, 0.5 , 0.03, 0.91, 0.26],
                   [0.66, 0.31, 0.52, 0.55, 0.18]])

    """
    def __init__(self, C, normalized=False):
        """

        Args:
            C: the constant matrix.
            normalized: True to normalize the projection image according to its Frobenius norm.
            pos: True to skip negative values (replaced by zero) of the matrix to project.

        """
        super(const, self).__init__(C.shape)
        self.constraint = ConstraintMat('const', cons_value=C, normalized=normalized, pos=False)

class normcol(proj_gen):
    """
        Functor for the NORMCOL projector. A, the image matrix, is defined by \f$ \forall j \in \{0,...,shape[1]-1\} \f$ the j-th column \f$ A_{*,j} \f$ is such that \f$\| A_{*,j}\|_2 = s  \f$.

        Example:
            >>> from pyfaust.proj import normcol
            >>> from numpy.random import rand, seed
            >>> from numpy.linalg import norm
            >>> import numpy as np
            >>> seed(42) # just for reproducibility
            >>> M = np.round(rand(5,5), decimals=2)
            >>> M
            array([[0.37, 0.95, 0.73, 0.6 , 0.16],
                   [0.16, 0.06, 0.87, 0.6 , 0.71],
                   [0.02, 0.97, 0.83, 0.21, 0.18],
                   [0.18, 0.3 , 0.52, 0.43, 0.29],
                   [0.61, 0.14, 0.29, 0.37, 0.46]])
            >>> p = normcol(M.shape, .01)
            >>> norm(p(M)[:,0], 2)
            0.009999999999999998

   """
    def __init__(self, shape, s=1):
        """
        Args:
            shape: the input matrix shape.
            s: the column 2-norm (default to 1).

        """
        super(normcol, self).__init__(shape)
        if(s < 0):
            raise ValueError('A norm can\'t be negative')
        normalized=False
        pos=False
        self.constraint = ConstraintReal('normcol', shape[0], shape[1], s, normalized, pos)

class normlin(proj_gen):
    """
        Functor for the NORMLIN projector. A, the image matrix, is defined by \f$ \forall i \in \{0,...,shape[0]-1\}\f$ the i-th row \f$ A_{i,*} \f$ is such that \f$ \| A_{i,*} \|_2 = s \f$.

        Example:
            >>> from pyfaust.proj import normlin
            >>> from numpy.random import rand, seed
            >>> from numpy.linalg import norm
            >>> import numpy as np
            >>> seed(42) # just for reproducibility
            >>> M = np.round(rand(5,5), decimals=2)
            >>> M
            array([[0.37, 0.95, 0.73, 0.6 , 0.16],
                   [0.16, 0.06, 0.87, 0.6 , 0.71],
                   [0.02, 0.97, 0.83, 0.21, 0.18],
                   [0.18, 0.3 , 0.52, 0.43, 0.29],
                   [0.61, 0.14, 0.29, 0.37, 0.46]])
            >>> p = normlin(M.shape, .01)
            >>> p(M)
            array([[0.00264427, 0.00678935, 0.00521708, 0.00428801, 0.00114347],
                   [0.00124552, 0.00046707, 0.00677253, 0.00467071, 0.00552701],
                   [0.00015309, 0.00742494, 0.0063533 , 0.00160746, 0.00137782],
                   [0.00221263, 0.00368772, 0.00639205, 0.00528573, 0.0035648 ],
                   [0.00671873, 0.001542  , 0.00319415, 0.0040753 , 0.00506658]])

    """

    def __init__(self, shape, s=1):
        """
        Args:
            shape: the input matrix shape.
            s: the row 2-norm (default to 1).

        """
        super(normlin, self).__init__(shape)
        if(s < 0):
            raise ValueError('A norm can\'t be negative')
        normalized=False
        pos=False
        self.constraint = ConstraintReal('normlin', shape[0], shape[1], s, normalized, pos)

class blockdiag(proj_gen):
    """
	Functor for the BLOCKDIAG projector. It sets all values to zero except for the diagonal blocks of the support defined by block_shapes. The i-th diagonal block starts at the row and column indices (block_shapes[i-1][0], block_shapes[i-1][1]) or (0,0) if i == 0 and ends at the row and columns indices (block_shapes[i][0]-1, block_shapes[i][1]-1) or (shape[0], shape[1]) if i == len(block_shapes)-1.

        Example:
            >>> from pyfaust.proj import blockdiag
            >>> import numpy as np
            >>> M = np.ones((12,12))
            >>> p = blockdiag(M.shape, [(1, 1), (4, 4), (7, 7)], normalized=False)
            >>> M_ = p(M)
            >>> M_
            array([[1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                   [0., 1., 1., 1., 1., 0., 0., 0., 0., 0., 0., 0.],
                   [0., 1., 1., 1., 1., 0., 0., 0., 0., 0., 0., 0.],
                   [0., 1., 1., 1., 1., 0., 0., 0., 0., 0., 0., 0.],
                   [0., 1., 1., 1., 1., 0., 0., 0., 0., 0., 0., 0.],
                   [0., 0., 0., 0., 0., 1., 1., 1., 1., 1., 1., 1.],
                   [0., 0., 0., 0., 0., 1., 1., 1., 1., 1., 1., 1.],
                   [0., 0., 0., 0., 0., 1., 1., 1., 1., 1., 1., 1.],
                   [0., 0., 0., 0., 0., 1., 1., 1., 1., 1., 1., 1.],
                   [0., 0., 0., 0., 0., 1., 1., 1., 1., 1., 1., 1.],
                   [0., 0., 0., 0., 0., 1., 1., 1., 1., 1., 1., 1.],
                   [0., 0., 0., 0., 0., 1., 1., 1., 1., 1., 1., 1.]])


    """

    def __init__(self, shape, block_shapes, normalized=True, pos=False):
        """
        Constructor.

        Args:
            shape: the size of the input matrix.
            block_shapes: the list of tuples defining the lower right corner of
            successive diagonal blocks (see class description and example).
            normalized: True to normalize the projection image matrix.
            pos: True to ignore negative values (replaced by 0).
        """
        super(blockdiag, self).__init__(shape)
        self._m_vec = [ sh[0] for sh in block_shapes ]
        self._n_vec = [ sh[1] for sh in block_shapes ]
        self._shape = shape
        self._block_shapes = block_shapes
        self.normalized = normalized
        self.pos = pos
#        if(self._m_vec[-1] != shape[0]): raise ValueError("The last index of (row"
#                                                    " offsets) _m_vec"
#                                                    " must be equal to"
#                                                    " shape[0]")
#        if(self._n_vec[-1] != shape[1]): raise ValueError("The last index of (column"
#                                                    " offsets) _n_vec"
#                                                    " must be equal to"
#                                                    " shape[1]")
        cons_value = np.asfortranarray(np.array(block_shapes, dtype=float))
        self.constraint = ConstraintMat('blockdiag', cons_value=cons_value,
                                        normalized=normalized, pos=pos,
                                        cons_value_sz=cons_value.size)

    def __call__(self, M):
        """
        Implements the functor.
        """
        if(M.shape != self._shape): raise ValueError('The dimension of the '
                                                   'projector and matrix must '
                                                   'agree.')

        is_real = np.empty((1,))
        M = _check_fact_mat('prox_blockdiag.__call__', M, is_real)
        if is_real:
            is_float = M.dtype == 'float32'
            if is_float:
                return _FaustCorePy.ConstraintMatCoreFlt.prox_blockdiag(M, self._block_shapes, self.normalized,
                                                                        self.pos)
            else:
                return _FaustCorePy.ConstraintMatCoreDbl.prox_blockdiag(M, self._block_shapes, self.normalized,
                                                                        self.pos)

        else:
            return _FaustCorePy.ConstraintMatCoreCplxDbl.prox_blockdiag(M, self._block_shapes, self.normalized,
                                                             self.pos)

#        M_ = np.zeros(M.shape)
#        m_ = 0
#        n_ = 0
#        for i,(m,n) in enumerate(zip(self.m_vec, self.n_vec)):
#            print("i=", i, "m=", m, "n=", n)
#            M_[m_:m,n_:n] = M[m_:m,n_:n]
#            m_ = m
#            n_ = n
#        return M_

class skperm(proj_gen):
    """
    Functor for the SKPERM projector.

    Example:
        >>> from pyfaust.proj import skperm
        >>> import numpy as np
        >>> from numpy import array
        >>> k = 2
        >>> M = array([[-0.04440802, -0.17569296, -0.02557815, -0.15559154], \
                       [-0.0083095,  -3.38725936, -0.78484126, -0.4883618 ], \
                       [-1.48942563, -1.71787215, -0.84000212, -3.71752454], \
                       [-0.88957883, -0.19107863, -5.92900636, -6.51064175]])
        >>> p = skperm(M.shape, k, normalized=False)
        >>> p(M)
        array([[-0.04440802,  0.        , -0.02557815,  0.        ],
               [-0.0083095 , -3.38725936,  0.        ,  0.        ],
               [ 0.        , -1.71787215,  0.        , -3.71752454],
               [ 0.        ,  0.        , -5.92900636, -6.51064175]])

    Reference:
        [1] Quoc-Tung Le, Rémi Gribonval. Structured Support Exploration For
        Multilayer Sparse Matrix Fac- torization. ICASSP 2021 - IEEE International
        Conference on Acoustics, Speech and Signal Processing, Jun 2021, Toronto,
        Ontario, Canada. pp.1-5 <a href="https://hal.inria.fr/hal-03132013/document">hal-03132013</a>.

    """
    def __init__(self, shape, k, normalized=True, pos=False):
        """
        Projector constructor.

        Args:
            shape: shape of the input array.
            k: the integer sparsity (number of nonzeros) targeted per-row and
            per-column.
            normalized: True to normalize the projection image according to its Frobenius norm.
            pos: True to skip negative values (replaced by zero) of the matrix to project.

        """
        super(skperm, self).__init__(shape)
        self.constraint = ConstraintInt('skperm', shape[0], shape[1], k, normalized, pos)

class sptriu(proj_gen):
    """
    Functor for the SPTRIU projector.

    A, the image matrix, is such that the lower triangular part is 0 and \f$ \| A \|_0 = k,  \| A\|_F = 1 \f$ (if normalized == True).


    Example:
        >>> from pyfaust.proj import sptriu
        >>> from numpy.random import rand, seed
        >>> import numpy as np
        >>> seed(42) # just for reproducibility
        >>> M = np.round(rand(5,5), decimals=2)
        >>> M
        array([[0.37, 0.95, 0.73, 0.6 , 0.16],
               [0.16, 0.06, 0.87, 0.6 , 0.71],
               [0.02, 0.97, 0.83, 0.21, 0.18],
               [0.18, 0.3 , 0.52, 0.43, 0.29],
               [0.61, 0.14, 0.29, 0.37, 0.46]])
        >>> p = sptriu(M.shape, 3, normalized=False)
        >>> p(M)
        array([[0.  , 0.95, 0.  , 0.  , 0.  ],
               [0.  , 0.  , 0.87, 0.  , 0.  ],
               [0.  , 0.  , 0.83, 0.  , 0.  ],
               [0.  , 0.  , 0.  , 0.  , 0.  ],
               [0.  , 0.  , 0.  , 0.  , 0.  ]])
        >>> np.linalg.norm(np.tril(p(M), -1)) == 0
        True
        >>> np.count_nonzero(p(M)) == 3
        True


    <b>See also:</b> pyfaust.proj.sptril
    """

    def __init__(self, shape, k, normalized=True, pos=False):
        """

        Args:
            shape: shape of the input array.
            k: the number of nonzeros of the projection image.
            normalized: True to normalize the projection image according to its Frobenius norm.
            pos: True to skip negative values (replaced by zero) of the matrix to project.

        """
        super(sptriu, self).__init__(shape)
        self.constraint = ConstraintInt('sptriu', shape[0], shape[1], k, normalized, pos)

class sptril(proj_gen):
    """
    Functor for the SPTRIL projector.

    A, the image matrix, is such that the upper triangular part is 0 and \f$ \| A \|_0 = k,  \| A\|_F = 1 \f$ (if normalized == True).


    Example:
        >>> from pyfaust.proj import sptril
        >>> from numpy.random import rand, seed
        >>> import numpy as np
        >>> seed(42) # just for reproducibility
        >>> M = np.round(rand(5,5), decimals=2)
        >>> M
        array([[0.37, 0.95, 0.73, 0.6 , 0.16],
               [0.16, 0.06, 0.87, 0.6 , 0.71],
               [0.02, 0.97, 0.83, 0.21, 0.18],
               [0.18, 0.3 , 0.52, 0.43, 0.29],
               [0.61, 0.14, 0.29, 0.37, 0.46]])
        >>> p = sptril(M.shape, 3, normalized=False)
        >>> p(M)
        array([[0.  , 0.  , 0.  , 0.  , 0.  ],
               [0.  , 0.  , 0.  , 0.  , 0.  ],
               [0.  , 0.97, 0.83, 0.  , 0.  ],
               [0.  , 0.  , 0.  , 0.  , 0.  ],
               [0.61, 0.  , 0.  , 0.  , 0.  ]])
        >>> np.linalg.norm(np.triu(p(M), 1)) == 0
        True
        >>> np.count_nonzero(p(M)) == 3
        True


    <b>See also:</b> pyfaust.proj.sptriu
    """

    def __init__(self, shape, k, normalized=True, pos=False):
        """

        Args:
            shape: shape of the input array.
            k: the number of nonzeros of the projection image.
            normalized: True to normalize the projection image according to its Frobenius norm.
            pos: True to skip negative values (replaced by zero) of the matrix to project.

        """
        super(sptril, self).__init__(shape)
        self.constraint = ConstraintInt('sptril', shape[0], shape[1], k, normalized, pos)

class spsymm(proj_gen):
    """
    Functor for the SYMM SP projector.

    A, the image matrix, is such that A is symmetric and \f$ \| A \|_0 = k + k \mod{2},  \| A\|_F = 1 \f$ (if normalized == True).


    Example:
        >>> from pyfaust.proj import spsymm
        >>> from numpy.random import rand, seed
        >>> import numpy as np
        >>> seed(42) # just for reproducibility
        >>> M = np.round(rand(5,5), decimals=2)
        >>> M
        array([[0.37, 0.95, 0.73, 0.6 , 0.16],
               [0.16, 0.06, 0.87, 0.6 , 0.71],
               [0.02, 0.97, 0.83, 0.21, 0.18],
               [0.18, 0.3 , 0.52, 0.43, 0.29],
               [0.61, 0.14, 0.29, 0.37, 0.46]])
        >>> p = spsymm(M.shape, 3, normalized=False)
        >>> p(M)
        array([[0.  , 0.95, 0.  , 0.  , 0.  ],
               [0.95, 0.  , 0.97, 0.  , 0.  ],
               [0.  , 0.97, 0.  , 0.  , 0.  ],
               [0.  , 0.  , 0.  , 0.  , 0.  ],
               [0.  , 0.  , 0.  , 0.  , 0.  ]])
        >>> np.linalg.norm(p(M) - p(M).T) == 0
        True
        >>> np.count_nonzero(p(M)) == 4
        True

    """

    def __init__(self, shape, k, normalized=True, pos=False):
        """

        Args:
            shape: shape of the input array.
            k: the number of nonzeros of the projection image.
            normalized: True to normalize the projection image according to its Frobenius norm.
            pos: True to skip negative values (replaced by zero) of the matrix to project.

        """
        super(spsymm, self).__init__(shape)
        self.constraint = ConstraintInt('spsymm', shape[0], shape[1], k, normalized, pos)
