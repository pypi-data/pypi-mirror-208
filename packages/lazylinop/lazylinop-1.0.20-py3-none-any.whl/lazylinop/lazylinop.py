"""
Module to implement lazy linear operators.
"""

import numpy as np
from scipy.sparse.linalg import LinearOperator

HANDLED_FUNCTIONS = {'ndim'}

class LazyLinearOp(LinearOperator):
    """
    This class implements a lazy linear operator. A LazyLinearOp is a
    specialization of a scipy.linalg.LinearOperator
    (https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.linalg.LinearOperator.html).

    The evaluation of any defined operation is delayed until a multiplication
    by a dense matrix/vector, a call of LazyLinearOp.toarray.

    To instantiate a LazyLinearOp look at
    lazylinop.aslazylinearoperator or
    lazylinop.LazyLinearOp to instantiate from matmat/matvec
    functions.

    **Note: This code is in a beta status.**
    """

    def __init__(self, shape, **kwargs):
        """
        Returns a LazyLinearOp defined by shape and at least a matvec or a matmat function.

        Args:
            shape: (tuple)
                 dimensions (M, N).
            matvec: (callable)
                 returns A * v (v a vector).
            rmatvec: (callable)
                 returns A^H * v (v a vector of size N).
            matmat: (callable)
                 returns A * V (V a dense matrix of dimensions (N, K)).
            rmatmat: (callable)
                 returns A^H * V (V a dense matrix of dimensions (M, K)).
            dtype:
                 data type of the matrix (can be None).

        Return:
            LazyLinearOp

        Example:
            >>> # In this example we create a LazyLinearOp for the DFT using the fft from scipy
            >>> import numpy as np
            >>> from scipy.fft import fft, ifft
            >>> from lazylinop import LazyLinearOp
            >>> lfft = LazyLinearOp((8, 8), matmat=lambda x: fft(x, axis=0), rmatmat=lambda x: 8 * ifft(x, axis=0))
            >>> x = np.random.rand(8)
            >>> np.allclose(lfft * x, fft(x))
            True

        """
        if 'internal_call' in kwargs and kwargs['internal_call']:
            self.shape = shape
            if 'dtype' in kwargs:
                self.dtype = kwargs['dtype']
            else:
                self.dtype = None
                super(LazyLinearOp, self).__init__(self.dtype, self.shape)
            return
        matvec, rmatvec, matmat, rmatmat = [None for i in range(4)]
        def callable_err(k):
            return TypeError(k+' in kwargs must be a callable/function')

        for k in kwargs.keys():
            if k != 'dtype' and not callable(kwargs[k]):
                raise callable_err(k)
        if 'matvec' in kwargs.keys():
            matvec = kwargs['matvec']
        if 'rmatvec' in kwargs.keys():
            rmatvec = kwargs['rmatvec']
        if 'matmat' in kwargs.keys():
            matmat = kwargs['matmat']
        if 'rmatmat' in kwargs.keys():
            rmatmat = kwargs['rmatmat']
        if 'dtype' in kwargs.keys():
            dtype = kwargs['dtype']
        else:
            dtype = None

        if matvec is None and matmat is None:
            raise ValueError('At least a matvec or a matmat function must be'
                             ' passed in kwargs.')

        def _matmat(M, _matvec):
            nonlocal dtype
            if len(M.shape) == 1:
                return _matvec(M)
            first_col = _matvec(M[:, 0])
            dtype = first_col.dtype
            out = np.empty((shape[0], M.shape[1]), dtype=dtype)
            out[:, 0] = first_col
            for i in range(1, M.shape[1]):
                out[:, i] = _matvec(M[:,i])
            return out

        if matmat is None:
            matmat = lambda M: _matmat(M, matvec)

        if rmatmat is None and rmatvec is not None:
            rmatmat = lambda M: _matmat(M, rmatvec)

        #MX = lambda X: matmat(np.eye(shape[1])) @ X
        MX = lambda X: matmat(X)
        #MTX = lambda X: rmatmat(X.T).T
        MHX = lambda X: rmatmat(X)

        lambdas = {'@': MX}
        lambdasT = {'@': lambda op: rmatmat(op.real).conj() -
                    rmatmat(1j * op.imag).conj()}
        lambdasH = {'@': MHX}
        lambdasC = {'@': lambda op: (matmat(op.real).conj() -
                    matmat(1j * op.imag)) if 'complex' in str(dtype) or \
                    dtype is None else MX(op)}
        # set lambdas temporarily to None (to satisfy the ctor)
        # they'll be initialized later
        for l in [lambdas, lambdasT, lambdasH, lambdasC]:
            l['T'] = None
            l['H'] = None
            l['slice'] = None

        lop = LazyLinearOp._create_LazyLinOp(lambdas, shape, dtype=dtype,
                                             self=self)
        super(LazyLinearOp, lop).__init__(lop.dtype, lop.shape)
        lopT = LazyLinearOp._create_LazyLinOp(lambdasT, (shape[1], shape[0]), dtype=dtype)
        lopH = LazyLinearOp._create_LazyLinOp(lambdasH, (shape[1], shape[0]), dtype=dtype)
        lopC = LazyLinearOp._create_LazyLinOp(lambdasC, shape, dtype=dtype)

        lambdas['T'] = lambda: lopT
        lambdas['H'] = lambda: lopH
        lambdas['slice'] = lambda indices: LazyLinearOp._index_lambda(lop,
                                                                       indices)()
        lambdasT['T'] = lambda: lop
        lambdasT['H'] = lambda: lopC
        lambdasT['slice'] = lambda indices: LazyLinearOp._index_lambda(lopT,
                                                                        indices)()
        lambdasH['T'] = lambda: lopC
        lambdasH['H'] = lambda: lop
        lambdasH['slice'] = lambda indices: LazyLinearOp._index_lambda(lopH,
                                                                        indices)()
        lambdasC['T'] = lambda: lopH
        lambdasC['H'] = lambda: lopT
        lambdasC['slice'] = lambda indices: LazyLinearOp._index_lambda(lopC,
                                                                        indices)()
        self = lop


    @staticmethod
    def _create_LazyLinOp(lambdas, shape, root_obj=None, dtype=None, self=None):
        """
        Low-level constructor. Not meant to be used directly.

        Args:
            lambdas: starting operations.
            shape: the initial shape of the operator.
            root_obj: the initial object the operator is based on.

        <b>See also:</b> lazylinop.aslazylinearoperator.
        """
        if root_obj is not None:
            if not hasattr(root_obj, 'shape'):
                raise TypeError('The starting object to initialize a'
                                ' LazyLinearOp must possess a shape'
                                ' attribute.')
            if len(root_obj.shape) != 2:
                raise ValueError('The starting object to initialize a LazyLinearOp '
                                 'must have two dimensions, not: '+str(len(root_obj.shape)))

        if self is None:
            self = LazyLinearOp(shape, dtype=dtype, internal_call=True)
        else:
            self.shape = shape
            self.dtype = dtype
        self.lambdas = lambdas
        self._check_lambdas()
        self._root_obj = root_obj
        return self

    def _check_lambdas(self):
        if not isinstance(self.lambdas, dict):
            raise TypeError('lambdas must be a dict')
        keys = self.lambdas.keys()
        for k in ['@', 'H', 'T', 'slice']:
            if k not in keys:
                raise ValueError(k+' is a mandatory lambda, it must be set in'
                                 ' self.lambdas')

    @staticmethod
    def create_from_op(obj, shape=None):
        """
        Alias of lazylinop.aslazylinearoperator.
        """
        if shape is None:
            oshape = obj.shape
        else:
            oshape = shape
        lambdas = {'@': lambda op: obj @ op}
        lambdasT = {'@': lambda op: obj.T @ op}
        lambdasH = {'@': lambda op: obj.T.conj() @ op}
        lambdasC = {'@': lambda op: \
                    obj.conj() @ op if 'complex' in str(obj.dtype) \
                    or obj.dtype is None \
                    else obj @ op}
        # set lambdas temporarily to None (to satisfy the ctor)
        # they'll be initialized later
        for l in [lambdas, lambdasT, lambdasH, lambdasC]:
            l['T'] = None
            l['H'] = None
            l['slice'] = None #TODO: rename slice to index
        lop = LazyLinearOp._create_LazyLinOp(lambdas, oshape, obj, dtype=obj.dtype)
        lopT = LazyLinearOp._create_LazyLinOp(lambdasT, (oshape[1], oshape[0]), obj, dtype=obj.dtype)
        lopH = LazyLinearOp._create_LazyLinOp(lambdasH, (oshape[1], oshape[0]), obj, dtype=obj.dtype)
        lopC = LazyLinearOp._create_LazyLinOp(lambdasC, oshape, obj, dtype=obj.dtype)

        # TODO: refactor with create_from_funcs (in ctor)
        lambdas['T'] = lambda: lopT
        lambdas['H'] = lambda: lopH
        lambdas['slice'] = lambda indices: LazyLinearOp._index_lambda(lop,
                                                                       indices)()
        lambdasT['T'] = lambda: lop
        lambdasT['H'] = lambda: lopC
        lambdasT['slice'] = lambda indices: LazyLinearOp._index_lambda(lopT,
                                                                        indices)()
        lambdasH['T'] = lambda: lopC
        lambdasH['H'] = lambda: lop
        lambdasH['slice'] = lambda indices: LazyLinearOp._index_lambda(lopH,
                                                                        indices)()
        lambdasC['T'] = lambda: lopH
        lambdasC['H'] = lambda: lopT
        lambdasC['slice'] = lambda indices: LazyLinearOp._index_lambda(lopC,
                                                                        indices)()

        return lop

    #TODO: function not used anywhere, delete it?
    @staticmethod
    def create_from_scalar(s, shape=None):
        """
        Returns a LazyLinearOp L created from the scalar s, such as each L[i, i] == s.
        """
        if shape is None:
            shape = (1, 1)
        a = np.ones(shape) * s
        return create_from_op(a)

    @staticmethod
    def create_from_funcs(matmat, rmatmat, shape, dtype=None):
        """
        Alias of ctor lazylinop.LazyLinearOp.
        """
        pass

    def _checkattr(self, attr):
        if self._root_obj is not None and not hasattr(self._root_obj, attr):
            raise TypeError(attr+' is not supported by the root object of this'
                            ' LazyLinearOp')

    def _index_lambda(lop, indices):
        from scipy.sparse import eye as seye
        s = lambda: \
                LazyLinearOp.create_from_op(seye(lop.shape[0],
                                                  format='csr')[indices[0]]) \
                @ lop @ LazyLinearOp.create_from_op(seye(lop.shape[1], format='csr')[:, indices[1]])
        return s

    @property
    def ndim(self):
        """
        Returns the number of dimensions of the LazyLinearOp (it is always 2).
        """
        return 2

    def transpose(self):
        """
        Returns the LazyLinearOp transpose.
        """
        self._checkattr('transpose')
        return self.lambdas['T']()

    @property
    def T(self):
        """
        Returns the LazyLinearOp transpose.
        """
        return self.transpose()

    def conj(self):
        """
        Returns the LazyLinearOp conjugate.
        """
        self._checkattr('conj')
        return self.H.T

    def conjugate(self):
        """
        Returns the LazyLinearOp conjugate.
        """
        return self.conj()

    def getH(self):
        """
        Returns the LazyLinearOp adjoint/transconjugate.
        """
        #self._checkattr('getH')
        return self.lambdas['H']()

    @property
    def H(self):
        """
        The LazyLinearOp adjoint/transconjugate.
        """
        return self.getH()

    def _adjoint(self):
        """
        Returns the LazyLinearOp adjoint/transconjugate.
        """
        return self.H

    def _slice(self, indices):
        return self.lambdas['slice'](indices)

    def __add__(self, op):
        """
        Returns the LazyLinearOp for self + op.

        Args:
            op: an object compatible with self for this binary operation.

        """
        self._checkattr('__add__')
        if not LazyLinearOp.isLazyLinearOp(op):
            op = LazyLinearOp.create_from_op(op)
        if op.shape != self.shape:
            raise ValueError('Dimensions must agree')
        lambdas = {'@': lambda o: self @ o + op @ o,
                   'H': lambda: self.H + op.H,
                   'T': lambda: self.T + op.T,
                   'slice': lambda indices: self._slice(indices) + op._slice(indices)
                  }
        new_op = LazyLinearOp._create_LazyLinOp(lambdas=lambdas,
                              shape=tuple(self.shape),
                              root_obj=None)
        return new_op

    def __radd__(self, op):
        """
        Returns the LazyLinearOp for op + self.

        Args:
            op: an object compatible with self for this binary operation.

        """
        return self.__add__(op)

    def __iadd__(self, op):
        """
        Not Implemented self += op.
        """
        raise NotImplementedError(LazyLinearOp.__name__+".__iadd__")
# can't do as follows, it recurses indefinitely because of self.eval
#        self._checkattr('__iadd__')
#        self = LazyLinearOp._create_LazyLinOp(init_lambda=lambda:
#                              (self.eval()).\
#                              __iadd__(LazyLinearOp._eval_if_lazy(op)),
#                              shape=(tuple(self.shape)),
#                              root_obj=self._root_obj)
#        return self


    def __sub__(self, op):
        """
        Returns the LazyLinearOp for self - op.

        Args:
            op: an object compatible with self for this binary operation.

        """
        self._checkattr('__sub__')
        if not LazyLinearOp.isLazyLinearOp(op):
            op = LazyLinearOp.create_from_op(op)
        lambdas = {'@': lambda o: self @ o - op @ o,
                   'H': lambda: self.H - op.H,
                   'T': lambda: self.T - op.T,
                   'slice': lambda indices: self._slice(indices) - op._slice(indices)
                  }
        new_op = LazyLinearOp._create_LazyLinOp(lambdas=lambdas,
                              shape=tuple(self.shape),
                              root_obj=None)
        return new_op


    def __rsub__(self, op):
        """
        Returns the LazyLinearOp for op - self.

        Args:
            op: an object compatible with self for this binary operation.

        """
        self._checkattr('__rsub__')
        if not LazyLinearOp.isLazyLinearOp(op):
            op = LazyLinearOp.create_from_op(op)
        lambdas = {'@': lambda o: op @ o - self @ o,
                   'H': lambda: op.H - self.H,
                   'T': lambda: op.T - self.T,
                   'slice': lambda indices: op._slice(indices) - self._slice(indices)
                  }
        new_op = LazyLinearOp._create_LazyLinOp(lambdas=lambdas,
                              shape=self.shape,
                              root_obj=None)
        return new_op

    def __isub__(self, op):
        """
        Not implemented self -= op.
        """
        raise NotImplementedError(LazyLinearOp.__name__+".__isub__")
# can't do as follows, it recurses indefinitely because of self.eval
#        self._checkattr('__isub__')
#        self = LazyLinearOp._create_LazyLinOp(init_lambda=lambda:
#                              (self.eval()).\
#                              __isub__(LazyLinearOp._eval_if_lazy(op)),
#                              shape=(tuple(self.shape)),
#                              root_obj=self._root_obj)
#        return self


    def __truediv__(self, s):
        """
        Returns the LazyLinearOp for self / s.

        Args:
            s: a scalar.

        """
        new_op = self * 1/s
        return new_op

    def __itruediv__(self, op):
        """
        Not implemented self /= op.
        """
        raise NotImplementedError(LazyLinearOp.__name__+".__itruediv__")
# can't do as follows, it recurses indefinitely because of self.eval
#
#        self._checkattr('__itruediv__')
#        self = LazyLinearOp._create_LazyLinOp(init_lambda=lambda:
#                              (self.eval()).\
#                              __itruediv__(LazyLinearOp._eval_if_lazy(op)),
#                              shape=(tuple(self.shape)),
#                              root_obj=self._root_obj)
#        return self

    def _sanitize_matmul(self, op, swap=False):
        self._checkattr('__matmul__')
        if not hasattr(op, 'shape'):
            raise TypeError('op must have a shape attribute')
        if len(op.shape) == 1 and (self.shape[0] if swap else self.shape[1]) != \
           op.size or len(op.shape) >= 2 and (swap and
                                        op.shape[-1]
                                        !=
                                        self.shape[0]
                                        or not
                                        swap and
                                        self.shape[1]
                                        !=
                                        op.shape[-2]):
            raise ValueError('dimensions must agree')

    def __matmul__(self, op):
        """
        Computes self @ op as a sparse matrix / dense array or as a LazyLinearOp depending on the type of op.

        Args:
            op: an object compatible with self for this binary operation.

        Returns:
            If op is an numpy array or a scipy matrix the function returns (self @
            op) as a numpy array or a scipy matrix. Otherwise it returns the
            LazyLinearOp for the multiplication self @ op.

        """
        from scipy.sparse import issparse
        self._sanitize_matmul(op)
        if isinstance(op, np.ndarray) or issparse(op):
            if op.ndim == 1 and self._root_obj is not None:
                res = self.lambdas['@'](op.reshape(op.size, 1)).ravel()
            elif op.ndim > 2:
                from itertools import product
                # op.ndim > 2
                dtype = _binary_dtype(self.dtype, op.dtype)
                res = np.empty((*op.shape[:-2], self.shape[0], op.shape[-1]),
                               dtype=dtype)
                idl = [ list(range(op.shape[i])) for i in range(op.ndim-2) ]
                for t in product(*idl):
                    tr = (*t, slice(0, res.shape[-2]), slice(0, res.shape[-1]))
                    to = (*t, slice(0, op.shape[-2]), slice(0, op.shape[-1]))
                    R = self.lambdas['@'](op.__getitem__(to))
                    res.__setitem__(tr, R)
                # TODO: try to parallelize
            else:
                res = self.lambdas['@'](op)
        else:
            if not LazyLinearOp.isLazyLinearOp(op):
                op = LazyLinearOp.create_from_op(op)
            lambdas = {'@': lambda o: self @ (op @ o),
                       'H': lambda: op.H @ self.H,
                       'T': lambda: op.T @ self.T,
                       'slice': lambda indices: self._slice((indices[0],
                                                            slice(0,
                                                                  self.shape[1])))\
                       @ op._slice((slice(0, op.shape[0]), indices[1]))
                      }
            res = LazyLinearOp._create_LazyLinOp(lambdas=lambdas,
                               shape=(self.shape[0], op.shape[1]),
                               root_obj=None)
#            res = LazyLinearOp.create_from_op(super(LazyLinearOp,
#                                                     self).__matmul__(op))
        return res

    def dot(self, op):
        """
        Alias of LazyLinearOp.__matmul__.
        """
        return self.__matmul__(op)

    def matvec(self, op):
        """
        This function is an alias of self @ op, where the multiplication might
        be specialized for op a vector (depending on how self has been defined
        ; upon on a operator object or through a matvec/matmat function).


        <b>See also:</b> lazylinop.LazyLinearOp.
        """
        if not hasattr(op, 'shape') or not hasattr(op, 'ndim'):
            raise TypeError('op must have shape and ndim attributes')
        if op.ndim > 2 or op.ndim == 0:
            raise ValueError('op.ndim must be 1 or 2')
        if op.ndim != 1 and op.shape[0] != 1 and op.shape[1] != 1:
            raise ValueError('op must be a vector -- attribute ndim to 1 or'
                             ' shape[0] or shape[1] to 1')
        return self.__matmul__(op)

    def _rmatvec(self, op):
        """
        Returns self^H @ op, where self^H is the conjugate transpose of A.

        Returns:
            It might be a LazyLinearOp or an array depending on the op type
            (cf. lazylinop.LazyLinearOp.__matmul__).
        """
        # LinearOperator need.
        return self.T.conj() @ op

    def _matmat(self, op):
        """
        Alias of LazyLinearOp.__matmul__.
        """
        # LinearOperator need.
        if not hasattr(op, 'shape') or not hasattr(op, 'ndim'):
            raise TypeError('op must have shape and ndim attributes')
        if op.ndim > 2 or op.ndim == 0:
            raise ValueError('op.ndim must be 1 or 2')
        return self.__matmul__(op)

    def _rmatmat(self, op):
        """
        Returns self^H @ op, where self^H is the conjugate transpose of A.

        Returns:
            It might be a LazyLinearOp or an array depending on the op type
            (cf. lazylinop.LazyLinearOp.__matmul__).
        """
        # LinearOperator need.
        return self.T.conj() @ op

    def __imatmul__(self, op):
        """
        Not implemented self @= op.
        """
        raise NotImplementedError(LazyLinearOp.__name__+".__imatmul__")

    def __rmatmul__(self, op):
        """
        Returns op @ self which can be a LazyLinearOp or an array depending on op type.

        Args:
            op: an object compatible with self for this binary operation.

        <b>See also:</b> lazylinop.LazyLinearOp.__matmul__)
        """
        self._checkattr('__rmatmul__')
        from scipy.sparse import issparse
        self._sanitize_matmul(op, swap=True)
        if isinstance(op, np.ndarray) or issparse(op):
            res = op @ self.toarray()
        else:
            if not LazyLinearOp.isLazyLinearOp(op):
                op = LazyLinearOp.create_from_op(op)
            lambdas = {'@': lambda o: (op @ self) @ o,
                       'H': lambda: self.H @ op.H,
                       'T': lambda: self.T @ op.T,
                       'slice': lambda indices: (op @ self)._slice(indices)
                      }
            res = LazyLinearOp._create_LazyLinOp(lambdas=lambdas,
                               shape=(op.shape[0], self.shape[1]),
                               root_obj=None)
        return res

    def __mul__(self, other):
        """
        Returns the LazyLinearOp for self * other if other is a scalar
        otherwise returns self @ other.

        Args:
            other: a scalar or a vector/array.

        <b>See also:</b> lazylinop.LazyLinearOp.__matmul__)
        """
        self._checkattr('__mul__')
        if np.isscalar(other):
            Dshape = (self.shape[1], self.shape[1])
            matmat = lambda M: M * other
            D = LazyLinearOp(Dshape, matmat=matmat, rmatmat=matmat)
            new_op = self @ D
        else:
            new_op = self @ other
        return new_op

    def __rmul__(self, other):
        """
        Returns other * self.

        Args:
            other: a scalar or a vector/array.

        """
        if np.isscalar(other):
            return self * other
        else:
            return other @ self


    def __imul__(self, op):
        """
        Not implemented self *= op.
        """
        raise NotImplementedError(LazyLinearOp.__name__+".__imul__")

    def toarray(self):
        """
        Returns self as a numpy array.
        """
        #from scipy.sparse import eye
        #return self @ eye(self.shape[1], self.shape[1], format='csr')
        # don't use csr because of function based LazyLinearOp
        # (e.g. scipy fft receives only numpy array)
        return self @ np.eye(self.shape[1], order='F')

    def __getitem__(self, indices):
        """
        Returns the LazyLinearOp for slicing/indexing.

        Args:
            indices: array of length 1 or 2 which elements must be slice, integer or
            Ellipsis (...). Note that using Ellipsis for more than two indices
            is normally forbidden.

        """
        self._checkattr('__getitem__')
        if isinstance(indices, int):
            indices = (indices, slice(0, self.shape[1]))
        if isinstance(indices, tuple) and len(indices) == 2 and isinstance(indices[0], int) and isinstance(indices[1], int):
            return self.toarray().__getitem__(indices)
        elif isinstance(indices, slice) or isinstance(indices[0], slice) and \
                isinstance(indices[0], slice):
            return self._slice(indices)
        else:
            return self._slice(indices)

    def _newshape_getitem(self, indices):
        empty_lop_except = Exception("Cannot create an empty LazyLinearOp.")
        if isinstance(indices, (np.ndarray, list)):
            return (len(indices), self.shape[1])
        elif indices == Ellipsis:
            return self.shape
        elif isinstance(indices,int):
            # self[i] is a row
            return (1, self.shape[1])
        elif isinstance(indices, slice):
            #self[i:j] a group of contiguous rows
            start, stop, step = indices.start, indices.stop, indices.step
            if stop is None:
                stop = self.shape[0]
            if start is None:
                start = 0
            if step is None:
                step = 1
            return ((stop - start) // step, self.shape[1])
        elif isinstance(indices, tuple):
            if len(indices) == 1:
                return self._newshape_getitem(indices[0])
            elif len(indices) == 2:
                if(isinstance(indices[0], int) and isinstance(indices[1],int)):
                    # item
                    return (1, 1)
            else:
                raise IndexError('Too many indices.')

            if indices[0] == Ellipsis:
                if indices[1] == Ellipsis:
                    raise IndexError('an index can only have a single ellipsis '
                                     '(\'...\')')
                else:
                    # all rows
                    new_shape = self.shape
            elif isinstance(indices[0], int):
                # line F[i]
                new_shape = (1, self.shape[1])
            elif isinstance(indices[0], slice):
                start, stop, step = indices[0].start, indices[0].stop, indices[0].step
                if stop is None:
                    stop = self.shape[0]
                if start is None:
                    start = 0
                if step is None:
                    step = 1
                new_shape = ((stop - start) // step, self.shape[1])
            elif isinstance(indices[0], (list, np.ndarray)):
                if len(indices[0]) == 0: raise empty_lop_except
                new_shape = (len(indices[0]), self.shape[1])
            else:
                 raise idx_error_exception

            if indices[1] == Ellipsis:
                # all columns
                new_shape = self.shape
            elif isinstance(indices[1], int):
                # col F[:, i]
                new_shape = (new_shape[0], 1)
            elif isinstance(indices[1], slice):
                start, stop, step = indices[1].start, indices[1].stop, indices[1].step
                if stop is None:
                    stop = self.shape[1]
                if start is None:
                    start = 0
                if step is None:
                    step = 1
                new_shape = (new_shape[0], (stop - start) // step)
            elif isinstance(indices[1], (list, np.ndarray)):
                if len(indices[1]) == 0: raise empty_lop_except
                new_shape = (new_shape[0], len(indices[1]))
            else:
                 raise idx_error_exception
            return new_shape

    def concatenate(self, *ops, axis=0):
        """
        Returns the LazyLinearOp for the concatenation of self and op.

        Args:
            axis: axis of concatenation (0 for rows, 1 for columns).
        """
        from pyfaust import concatenate as cat
        nrows = self.shape[0]
        ncols = self.shape[1]
        out = self
        for op in ops:
            if axis == 0:
                out = out.vstack(op)
            elif axis == 1:
                out = out.hstack(op)
            else:
                raise ValueError('axis must be 0 or 1')
        return out

    def _vstack_slice(self, op, indices):
        rslice = indices[0]
        if isinstance(rslice, int):
            rslice = slice(rslice, rslice+1, 1)
        if rslice.step is not None and rslice.step != 1:
            raise ValueError('Can\'t handle non-contiguous slice -- step > 1')
        if rslice.start == None:
            rslice = slice(0, rslice.stop, rslice.step)
        if rslice.stop == None:
            rslice = slice(rslice.start, self.shape[0] + op.shape[0], rslice.step)
        if rslice.stop > self.shape[0] + op.shape[0]:
            raise ValueError('Slice overflows the row dimension')
        if rslice.start >= 0 and rslice.stop <= self.shape[0]:
            # the slice is completly in self
            return lambda: self._slice(indices)
        elif rslice.start >= self.shape[0]:
            # the slice is completly in op
            return lambda: op._slice((slice(rslice.start - self.shape[0],
                                            rslice.stop - self.shape[0]) ,indices[1]))
        else:
            # the slice is overlapping self and op
            self_slice = self._slice((slice(rslice.start, self.shape[0]), indices[1]))
            op_slice = self._slice((slice(0, rslice.stop - self.shape[0]), indices[1]))
            return lambda: self_slice.vstack(op_slice)

    def _vstack_mul_lambda(self, op, o):
        from scipy.sparse import issparse
        mul_mat = lambda o: np.vstack((self @ o, op @ o))
        mul_vec = lambda o: mul_mat(o.reshape(self.shape[1], 1)).ravel()
        mul_mat_vec = lambda : mul_vec(o) if len(o.shape) == 1 else mul_mat(o)
        mul = lambda: mul_mat_vec() if isinstance(o, np.ndarray) \
                or issparse(o) else self.vstack(op) @ o
        return mul


    def vstack(self, op):
        """
        See lazylinop.vstack.
        """
        if self.shape[1] != op.shape[1]:
            raise ValueError('self and op numbers of columns must be the'
                             ' same')
        if not LazyLinearOp.isLazyLinearOp(op):
            op = LazyLinearOp.create_from_op(op)
        lambdas = {'@': lambda o: self._vstack_mul_lambda(op, o)(),
                   'H': lambda: self.H.hstack(op.H),
                   'T': lambda: self.T.hstack(op.T),
                   'slice': lambda indices: self._vstack_slice(op, indices)()
                  }
        new_op = LazyLinearOp._create_LazyLinOp(lambdas=lambdas,
                              shape=(self.shape[0] + op.shape[0], self.shape[1]),
                              root_obj=None)
        return new_op

    def _hstack_slice(self, op, indices):
        cslice = indices[1]
        if isinstance(cslice, int):
            cslice = slice(cslice, cslice+1, 1)
        if cslice.step is not None and cslice.step != 1:
            raise ValueError('Can\'t handle non-contiguous slice -- step > 1')
        if cslice.stop > self.shape[1] + op.shape[1]:
            raise ValueError('Slice overflows the row dimension')
        if cslice.start >= 0 and cslice.stop <= self.shape[1]:
            # the slice is completly in self
            return lambda: self._slice(indices)
        elif cslice.start >= self.shape[1]:
            # the slice is completly in op
            return lambda: op._slice((indices[0], slice(cslice.start - self.shape[1],
                                            cslice.stop - self.shape[1])))
        else:
            # the slice is overlapping self and op
            self_slice = self._slice((indices[0], slice(cslice.start, self.shape[1])))
            op_slice = self._slice((indices[0], slice(0, cslice.stop - self.shape[1])))
            return lambda: self_slice.vstack(op_slice)

    def _hstack_mul_lambda(self, op, o):
        from scipy.sparse import issparse
        if isinstance(o, np.ndarray) or issparse(o):
            if len(o.shape) == 1:
                return lambda: self @ o[:self.shape[1]] + op @ o[self.shape[1]:]
            else:
                return lambda: self @ o[:self.shape[1],:] + op @ o[self.shape[1]:, :]
        else:
            return lambda: \
                self @ o._slice((slice(0, self.shape[1]), slice(0,
                                                                o.shape[1]))) \
                    + op @ o._slice((slice(self.shape[1], o.shape[0]), slice(0, o.shape[1])))

    def hstack(self, op):
        """
        See lazylinop.hstack.
        """
        if self.shape[0] != op.shape[0]:
            raise ValueError('self and op numbers of rows must be the'
                             ' same')
        if not LazyLinearOp.isLazyLinearOp(op):
            op = LazyLinearOp.create_from_op(op)
        lambdas = {'@': lambda o: self._hstack_mul_lambda(op, o)(),
               'H': lambda: self.H.vstack(op.H),
               'T': lambda: self.T.vstack(op.T),
               'slice': lambda indices: self._hstack_slice(op, indices)()
              }
        new_op = LazyLinearOp._create_LazyLinOp(lambdas=lambdas,
                              shape=(self.shape[0], self.shape[1]
                                    + op.shape[1]),
                              root_obj=None)
        return new_op

    @property
    def real(self):
        """
        Returns the LazyLinearOp for real.
        """
        from scipy.sparse import issparse
        lambdas = {'@': lambda o: (self @ o.real).real + \
                   (self @ o.imag * 1j).real if isinstance(o, np.ndarray) \
                   or issparse(o) else real(self @ o),
                   'H': lambda: self.T.real,
                   'T': lambda: self.T.real,
                   'slice': lambda indices: self._slice(indices).real
                  }
        new_op = LazyLinearOp._create_LazyLinOp(lambdas=lambdas,
                           shape=tuple(self.shape),
                           root_obj=None)
        return new_op

    @property
    def imag(self):
        """
        Returns the LazyLinearOp for imag.
        """
        from scipy.sparse import issparse
        lambdas = {'@': lambda o: (self @ o.real).imag + \
                   (self @ (1j * o.imag)).imag if isinstance(o, np.ndarray) \
                   or issparse(o) else imag(self @ o),
                   'H': lambda: self.T.imag,
                   'T': lambda: self.T.imag,
                   'slice': lambda indices: self._slice(indices).imag
                  }
        new_op = LazyLinearOp._create_LazyLinOp(lambdas=lambdas,
                           shape=tuple(self.shape),
                           root_obj=None)
        return new_op


    @staticmethod
    def isLazyLinearOp(obj):
        """
        Returns True if obj is a LazyLinearOp, False otherwise.
        """
        return isinstance(obj, LazyLinearOp)

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        if method == '__call__':
            if str(ufunc) == "<ufunc 'matmul'>" and len(inputs) >= 2 and \
               LazyLinearOp.isLazyLinearOp(inputs[1]):
                return inputs[1].__rmatmul__(inputs[0])
            elif str(ufunc) == "<ufunc 'multiply'>" and len(inputs) >= 2 and \
               LazyLinearOp.isLazyLinearOp(inputs[1]):
                return inputs[1].__rmul__(inputs[0])
            elif str(ufunc) == "<ufunc 'add'>" and len(inputs) >= 2 and \
                    LazyLinearOp.isLazyLinearOp(inputs[1]):
                return inputs[1].__radd__(inputs[0])
            elif str(ufunc) == "<ufunc 'subtract'>" and len(inputs) >= 2 and \
                    LazyLinearOp.isLazyLinearOp(inputs[1]):
                return inputs[1].__rsub__(inputs[0])
        elif method == 'reduce':
#            # not necessary numpy calls Faust.sum
#            if ufunc == "<ufunc 'add'>":
#                if len(inputs) == 1 and pyfaust.isLazyLinearOp(inputs[0]):
#                    #return inputs[0].sum(*inputs[1:], **kwargs)
#                else:
            return NotImplemented

    def __array__(self, *args, **kwargs):
        return self

    def __array_function__(self, func, types, args, kwargs):
        # Note: this allows subclasses that don't override
        # __array_function__ to handle self.__class__ objects
        if not all(issubclass(t, LazyLinearOp) for t in types):
            return NotImplemented
        if func.__name__ == 'ndim':
            return self.ndim
        return NotImplemented

def kron(A, B, use_pylops=True):
    """
    Returns the LazyLinearOp(Kron) for the Kronecker product A x B.

    Note: this specialization is particularly optimized for multiplying the
    operator by a vector.

    Args:
        A: LinearOperator
            scaling factor,
        B: LinearOperator
            block factor.
        use_pylops: bool
            if True (default) use the Kronecker implementation of pylops.

    Returns:
        The diagonal LazyLinearOp.

    Example:
        >>> from lazylinop import kron as lkron
        >>> import numpy as np
        >>> from pyfaust import rand
        >>> A = np.random.rand(100, 100)
        >>> B = np.random.rand(100, 100)
        >>> AxB = np.kron(A,B)
        >>> lAxB = lkron(A, B)
        >>> x = np.random.rand(AxB.shape[1], 1)
        >>> print(np.allclose(AxB@x, lAxB@x))
        True
        >>> from timeit import timeit
        >>> timeit(lambda: AxB @ x, number=10) # doctest:+ELLIPSIS
        0...
        >>> # example: 0.4692082800902426
        >>> timeit(lambda: lAxB @ x, number=10) # doctest:+ELLIPSIS
        0...
        >>> # example 0.03464869409799576

    **See also:** numpy.kron.
    """
    if use_pylops:
        from pylops import Kronecker
        k = Kronecker(aslazylinearoperator(A),
                      aslazylinearoperator(B))
        return LazyLinearOp(shape=(k.shape), matmat=lambda X:k @ X, rmatmat=lambda X: k.H
                                  @ X, matvec=lambda x: k @ x, rmatvec= lambda
                                  x: k.H @ x)
    def _kron(A, B, shape, op):
        from threading import Thread
        from multiprocessing import cpu_count
        from os import environ
        from pyfaust import isFaust
        #LazyLinearOp._sanitize_matmul(op) # TODO
        if hasattr(op, 'reshape') and hasattr(op, '__matmul__') and hasattr(op,
                                                                            '__getitem__'):
            if isFaust(A) or isFaust(B):
                parallel = False # e.g. for A, B Fausts in R^100x100 and op 128 columns
                # it was found that the sequential computation is faster
            else:
                parallel = True
            if 'KRON_PARALLEL' in environ:
                parallel = environ['KRON_PARALLEL'] == '1'
            nthreads = cpu_count() // 2
            if len(op.shape) == 1:
                op = op.reshape((op.size, 1))
                one_dim = True
            else:
                one_dim = False
            dtype = _binary_dtype(A.dtype, B.dtype)
            res = np.empty((shape[0], op.shape[1]), dtype=dtype)
            def out_col(j, ncols):
                for j in range(j, min(j + ncols, op.shape[1])):
                    op_mat = op[:, j].reshape((A.shape[1], B.shape[1]))
                    res[:, j] = (A @ op_mat @ B.T).reshape(shape[0])
            ncols = op.shape[1]
            if parallel:
                t = []
                cols_per_thread = ncols // nthreads
                if cols_per_thread * nthreads < ncols:
                    cols_per_thread += 1
                while len(t) < nthreads:
                    t.append(Thread(target=out_col, args=(cols_per_thread *
                                                          len(t),
                                                          cols_per_thread)))
                    t[-1].start()

                for j in range(nthreads):
                    t[j].join()
            else:
                out_col(0, ncols)
            if one_dim:
                res = res.ravel()
        else:
            raise TypeError('op must possess reshape, __matmul__ and'
                            ' __getitem__ attributes to be multiplied by a'
                            ' Kronecker LazyLinearOp (use toarray on the'
                            ' latter to multiply by the former)')
        return res
    shape = (A.shape[0] * B.shape[0], A.shape[1] * B.shape[1])
    return LazyLinearOp(shape, matmat=lambda x: _kron(A, B, shape, x),
                              rmatmat=lambda x : _kron(A.T.conj(), B.T.conj(),
                                                       (shape[1], shape[0]), x))

def eye(m, n=None, k=0, dtype='float'):
    """
    Returns the LazyLinearOp for eye.

    Args:
        m: (int)
             Number of rows of the LazyLinearOp.
        n: (int)
             Number of columns. Default is m.
        k: (int)
             Diagonal to place ones on. Default is 0 (main diagonal). Negative integer for a diagonal below the main diagonal, strictly positive integer for a diagonal above.
        dtype: (str)
             data type of the LazyLinearOp.

    Example:
        >>> from lazylinop import eye
        >>> le1 = eye(5)
        >>> le1
        <5x5 LazyLinearOp with dtype=float64>
        >>> le1.toarray()
        array([[1., 0., 0., 0., 0.],
               [0., 1., 0., 0., 0.],
               [0., 0., 1., 0., 0.],
               [0., 0., 0., 1., 0.],
               [0., 0., 0., 0., 1.]])
        >>> le2 = eye(5, 2)
        >>> le2
        <5x2 LazyLinearOp with dtype=float64>
        >>> le2.toarray()
        array([[1., 0.],
               [0., 1.],
               [0., 0.],
               [0., 0.],
               [0., 0.]])
        >>> le3 = eye(5, 3, 1)
        >>> le3
        <5x3 LazyLinearOp with dtype=float64>
        >>> le3.toarray()
        array([[0., 1., 0.],
               [0., 0., 1.],
               [0., 0., 0.],
               [0., 0., 0.],
               [0., 0., 0.]])
        >>> le4 = eye(5, 3, -1)
        >>> le4
        <5x3 LazyLinearOp with dtype=float64>
        >>> le4.toarray()
        array([[0., 0., 0.],
               [1., 0., 0.],
               [0., 1., 0.],
               [0., 0., 1.],
               [0., 0., 0.]])

    **See also:** scipy.sparse.eye.
    """
    def matmat(x, m, n, k):
        nonlocal dtype # TODO: take dtype into account
        if n != x.shape[0]:
            raise ValueError('Dimensions must agree')
        if len(x.shape) == 1:
             x = x.reshape(x.size, 1)
             x_1dim = True
        else:
             x_1dim = False
        minmn = min(m, n)
        x_islop = isLazyLinearOp(x)
        if k < 0:
            neg_k = True
            nz = np.zeros((abs(k), x.shape[1]))
            if x_islop:
                nz = aslazylinearoperator(nz)
            limk = min(minmn, m - abs(k))
            k = 0
        else:
            limk = min(minmn, n - k)
            neg_k = False
        mul = x[k: k + limk, :]
        if neg_k:
            if x_islop:
                mul = vstack((nz, mul))
            else:
                mul = np.vstack((nz, mul))
        if mul.shape[0] < m:
            z = np.zeros((m -
                      mul.shape[0],
                      mul.shape[1]))
            if x_islop:
                    z = aslazylinearoperator(z)
            t = (mul, z)
            if x_islop:
                mul = vstack(t)
            else:
                mul = np.vstack(t)
        if x_1dim:
            mul = mul.reshape(-1)
        return mul
    n = n if n is not None else m
    return LazyLinearOp((m, n), matmat=lambda x: matmat(x, m, n, k),
                              rmatmat=lambda x: matmat(x, n, m, -k),
                              dtype='float')

def diag(v, k=0):
    """
    Constructs a diagonal LazyLinearOp.

    Args:
        v:
             a 1-D numpy array for the diagonal.
        k: (int)
             the index of digonal, 0 for the main diagonal, k>0 for diagonals above, k<0 for diagonals below.

    Returns:
        The diagonal LazyLinearOp.

    Example:
        >>> from lazylinop import diag
        >>> import numpy as np
        >>> v = np.arange(1, 6)
        >>> v
        array([1, 2, 3, 4, 5])
        >>> ld1 = diag(v)
        >>> ld1
        <5x5 LazyLinearOp with unspecified dtype>
        >>> ld1.toarray()
        array([[1., 0., 0., 0., 0.],
               [0., 2., 0., 0., 0.],
               [0., 0., 3., 0., 0.],
               [0., 0., 0., 4., 0.],
               [0., 0., 0., 0., 5.]])
        >>> ld2 = diag(v, -2)
        >>> ld2
        <7x7 LazyLinearOp with unspecified dtype>
        >>> ld2.toarray()
        array([[0., 0., 0., 0., 0., 0., 0.],
               [0., 0., 0., 0., 0., 0., 0.],
               [1., 0., 0., 0., 0., 0., 0.],
               [0., 2., 0., 0., 0., 0., 0.],
               [0., 0., 3., 0., 0., 0., 0.],
               [0., 0., 0., 4., 0., 0., 0.],
               [0., 0., 0., 0., 5., 0., 0.]])
        >>> ld3 = diag(v, 2)
        >>> ld3
        <7x7 LazyLinearOp with unspecified dtype>
        >>> ld3.toarray()
        array([[0., 0., 1., 0., 0., 0., 0.],
               [0., 0., 0., 2., 0., 0., 0.],
               [0., 0., 0., 0., 3., 0., 0.],
               [0., 0., 0., 0., 0., 4., 0.],
               [0., 0., 0., 0., 0., 0., 5.],
               [0., 0., 0., 0., 0., 0., 0.],
               [0., 0., 0., 0., 0., 0., 0.]])
    """
    if len(v.shape) > 1 or len(v.shape) == 0:
        raise ValueError("v must be a 1-dim vector.")
    m = v.size + abs(k)
    def matmat(x, v, k):
        v = v.reshape(v.size, 1)
        if len(x.shape) == 1:
            x_is_1d = True
            x = x.reshape(x.size, 1)
        else:
            x_is_1d = False
        if isLazyLinearOp(x):
            y = np.diag(v, k) @ x
        else:
            if k > 0:
                y = v * x[k:k+v.size]
                y = np.vstack((y, np.zeros((k, x.shape[1]))))
            elif k < 0:
                y = v * x[:v.size]
                y = np.vstack((np.zeros((abs(k), x.shape[1])), y))
            else: # k == 0
                y = v * x[:v.size]
            if x_is_1d:
                y = y.ravel()
        return y
    return LazyLinearOp((m, m), matmat=lambda x: matmat(x, v, k),
                              rmatmat=lambda x: matmat(x, v, -k))

def sum(*lops, mt=False, af=False):
    """
    Sums (lazily) all linear operators in lops.

    Args:
        lops:
             the objects to add up as a list of LazyLinearOp-s or other compatible linear operator.
        mt:
             True to active the multithread experimental mode (not advisable, so far it's not faster than sequential execution).
        af:
             this argument defines how to compute L @ M = sum(lops) @ M, with M a numpy array. If True, the function adds the lops[i] into s before computing s @ M. Otherwise, by default, each lops[i] @ M are computed and then summed.

    Returns:
        The LazyLinearOp for the sum of lops.

    Example:
        >>> import numpy as np
        >>> from lazylinop import sum, aslazylinearoperator
        >>> from pyfaust import dft, Faust
        >>> from scipy.sparse import diags
        >>> nt = 10
        >>> d = 64
        >>> v = np.random.rand(d)
        >>> terms = [dft(d) @ Faust(diags(v, format='csr')) @ dft(d) for _ in range(nt)]
        >>> ls = sum(*terms) # ls is the LazyLinearOp sum of terms
    """
    lAx = lambda A, x: A @ x
    lAHx = lambda A, x: A.T.conj() @ x
    for l in lops[1:]:
        if l.shape != lops[0].shape:
            raise ValueError('Dimensions must agree')
    def matmat(x, lmul):
        if af:
            S = lops[0]
            for T in lops[1:]:
                S = S + T
            return S @ x
        from threading import Thread
        from multiprocessing import cpu_count
        Ps = [None for _ in range(len(lops))]
        n = len(lops)
        class Mul(Thread):
            def __init__(self, As, x, out, i):
                self.As = As
                self.x = x
                self.out = out
                self.i = i
                super(Mul, self).__init__(target=self.run)

            def run(self):
                for i, A in enumerate(self.As):
                    self.out[self.i + i] = lmul(A, self.x)

        if mt:
            ths = []
            nths = min(cpu_count(), n)
            share = n // nths
            #print("nths:", nths, "share:", share)
            rem = n - share * nths
            for i in range(nths):
                start = i*share
                if i == nths - 1:
                    end = n
                else:
                    end = (i+1) * share
                #print("i:", i, "start:", start, "end:", end)
                ths += [Mul(lops[start:end], x, Ps, start)]
                ths[-1].start()
            for i in range(nths):
                ths[i].join()
        else:
            for i, A in enumerate(lops):
                Ps[i] = lmul(A, x)
        S = Ps[-1]
        for i in range(n-2, -1, -1):
            S = S + Ps[i]
        return S
    return LazyLinearOp(lops[0].shape, matmat=lambda x: matmat(x, lAx),
                              rmatmat=lambda x: matmat(x, lAHx))

def block_diag(*lops, mt=False):
    """
    Returns the block diagonal LazyLinearOp formed of operators in lops.

    Args:
        lops:
             the objects defining the diagonal blocks as a list of LazyLinearOp-s or other compatible linear operator.
        mt:
             True to active the multithread experimental mode (not advisable, so far it's not faster than sequential execution).

    Returns:
        The diagonal block LazyLinearOp.

    Example:
        >>> import numpy as np
        >>> from lazylinop import block_diag, aslazylinearoperator
        >>> from scipy.sparse import diags
        >>> nt = 10
        >>> d = 64
        >>> v = np.random.rand(d)
        >>> terms = [np.random.rand(64, 64) for _ in range(10)]
        >>> ls = block_diag(*terms) # ls is the block diagonal LazyLinearOp


    <b>See also:</b> scipy.linalg.block_diag
    """
    lAx = lambda A, x: A @ x
    lAHx = lambda A, x: A.T.conj() @ x
    roffsets =  [0]
    coffsets =  [0] # needed for transpose case
    for i in range(len(lops)):
        roffsets += [roffsets[i] + lops[i].shape[1]]
        coffsets += [coffsets[i] + lops[i].shape[0]]
    def matmat(x, lmul, offsets):
        from threading import Thread
        from multiprocessing import cpu_count
        if len(x.shape) == 1:
            x_is_1d = True
            x = x.reshape(x.size, 1)
        else:
            x_is_1d = False
        Ps = [None for _ in range(len(lops))]
        n = len(lops)
        class Mul(Thread):
            def __init__(self, As, x, out, i):
                self.As = As
                self.x = x
                self.out = out
                self.i = i
                super(Mul, self).__init__(target=self.run)

            def run(self):
                for i, A in enumerate(self.As):
                    ipi = self.i + i
                    self.out[ipi] = lmul(A,
                                         self.x[offsets[ipi]:offsets[ipi+1]])

        if mt:
            ths = []
            nths = min(cpu_count(), n)
            share = [n // nths for _ in range(nths)]
            rem = n - share[0] * nths
            if rem > 0:
                while rem > 0:
                    share[rem-1] += 1
                    rem -= 1
            for i in range(1, len(share)):
                share[i] += share[i-1]
            share = [0] + share
            for i in range(nths):
                start = share[i]
                end = share[i+1]
                ths += [Mul(lops[start:end], x, Ps, start)]
                ths[-1].start()
            for i in range(nths):
                ths[i].join()
        else:
            for i, A in enumerate(lops):
                Ps[i] = lmul(A, x[offsets[i]:offsets[i+1]])
        S = Ps[0]
        conv_to_lop = isLazyLinearOp(S)
        vcat = vstack if conv_to_lop else np.vstack
        for i in range(1, n):
            if conv_to_lop:
                Ps[i] = aslazylinearoperator(Ps[i])
            elif isLazyLinearOp(Ps[i]):
                S = aslazylinearoperator(S)
                conv_to_lop = True
                vcat = vstack
            S = vcat((S, Ps[i]))
        if x_is_1d:
            S = S.ravel()
        return S
    return LazyLinearOp((coffsets[-1], roffsets[-1]), matmat=lambda x:
                              matmat(x, lAx, roffsets),
                              rmatmat=lambda x: matmat(x, lAHx, coffsets))

def zeros(shape):
    """
    Returns a zero LazyLinearOp.

    Args:
        shape:
             the shape of the operator.

    Example:
        >>> from lazylinop import zeros
        >>> import numpy as np
        >>> Lz = zeros((10, 12))
        >>> x = np.random.rand(12)
        >>> Lz @ x
        array([0., 0., 0., 0., 0., 0., 0., 0., 0., 0.])

    """
    def _matmat(op, shape):
        _sanitize_op(op)
        op_m = op.shape[0] if op.ndim == 1 else op.shape[-2]
        if op_m != shape[1]:
            raise ValueError('Dimensions must agree')
        if LazyLinearOp.isLazyLinearOp(op):
            return zeros((shape[0], op.shape[1]))
        # TODO: another output type than numpy array?
        elif op.ndim == 2:
            return np.zeros((shape[0], op.shape[1]), dtype=op.dtype)
        elif op.ndim > 2:
            return np.zeros((*op.shape[:-2], shape[0], op.shape[-1]),
                            dtype=op.dtype)
        else:
            # op.ndim == 1
            return np.zeros((shape[0],))
    return LazyLinearOp(shape, matmat=lambda x:
                              _matmat(x, shape),
                              rmatmat=lambda x: _matmat(x, (shape[1],
                                                             shape[0])))

def zpad(z_sizes, x_shape, ret_unpad=False, use_pylops=True):
    """
    Returns a LazyLinearOp to pad any compatible object x of shape x_shape with zeros on one or two dimensions.

    Args:
        z_sizes:
             a tuple/list of tuples/pairs of integers. It can be one tuple only if x is one-dimensional or a tuple two tuples if x two-dimensional.
        x_shape:
             shape of x to apply the zero padding to.
        ret_unpad:
             by default (False) the function returns only the zero-padding LazyLinearOp. If True it returns a tuple of the zero-padding operator and its inverse (the operator which undoes the padding on a padded x).
        use_pylops:
             if True (default) use the pylops.Pad implementation.

    Example:
        >>> from lazylinop import zpad
        >>> from numpy import arange
        >>> A = arange(18*2).reshape((18, 2))
        >>> A
        array([[ 0,  1],
               [ 2,  3],
               [ 4,  5],
               [ 6,  7],
               [ 8,  9],
               [10, 11],
               [12, 13],
               [14, 15],
               [16, 17],
               [18, 19],
               [20, 21],
               [22, 23],
               [24, 25],
               [26, 27],
               [28, 29],
               [30, 31],
               [32, 33],
               [34, 35]])
        >>> lz = zpad(((2, 3), (4, 1)), A.shape)
        >>> lz
        <23x18 LazyLinearOp with unspecified dtype>
        >>> np.round(lz @ A, decimals=2).astype('double')
        array([[ 0.,  0.,  0.,  0.,  0.,  0.,  0.],
               [ 0.,  0.,  0.,  0.,  0.,  0.,  0.],
               [ 0.,  0.,  0.,  0.,  0.,  1.,  0.],
               [ 0.,  0.,  0.,  0.,  2.,  3.,  0.],
               [ 0.,  0.,  0.,  0.,  4.,  5.,  0.],
               [ 0.,  0.,  0.,  0.,  6.,  7.,  0.],
               [ 0.,  0.,  0.,  0.,  8.,  9.,  0.],
               [ 0.,  0.,  0.,  0., 10., 11.,  0.],
               [ 0.,  0.,  0.,  0., 12., 13.,  0.],
               [ 0.,  0.,  0.,  0., 14., 15.,  0.],
               [ 0.,  0.,  0.,  0., 16., 17.,  0.],
               [ 0.,  0.,  0.,  0., 18., 19.,  0.],
               [ 0.,  0.,  0.,  0., 20., 21.,  0.],
               [ 0.,  0.,  0.,  0., 22., 23.,  0.],
               [ 0.,  0.,  0.,  0., 24., 25.,  0.],
               [ 0.,  0.,  0.,  0., 26., 27.,  0.],
               [ 0.,  0.,  0.,  0., 28., 29.,  0.],
               [ 0.,  0.,  0.,  0., 30., 31.,  0.],
               [ 0.,  0.,  0.,  0., 32., 33.,  0.],
               [ 0.,  0.,  0.,  0., 34., 35.,  0.],
               [ 0.,  0.,  0.,  0.,  0.,  0.,  0.],
               [ 0.,  0.,  0.,  0.,  0.,  0.,  0.],
               [ 0.,  0.,  0.,  0.,  0.,  0.,  0.]])
        >>> # padding for a vector
        >>> x = np.full(3, 1)
        >>> zpad(((2, 3)), x.shape) @ x
        array([0, 0, 1, 1, 1, 0, 0, 0])

    """
    z_sizes = np.array(z_sizes).astype('int')
    if z_sizes.shape[0] > 2 or z_sizes.ndim > 1 and z_sizes.shape[1] > 2:
        raise ValueError('Cannot pad zeros on more than two dimensions')
    if len(x_shape) != z_sizes.ndim:
        raise ValueError('z_sizes number of tuples must be len(x_shape).')
    if z_sizes.ndim == 1:
        z_sizes = np.vstack((z_sizes, (0, 0)))
    def mul(op):
        _sanitize_op(op, 'op')
        if op.ndim == 1:
            # op can't be a LazyLinearOp
            return np.hstack((np.zeros((z_sizes[0,0])), op, np.zeros((z_sizes[0, 1]))))
        out = op
        for i in range(z_sizes.shape[0]):
            bz = z_sizes[i][0]
            az = z_sizes[i][1]
            if bz > 0:
                if i == 0:
                    out = vstack((zeros((bz, out.shape[1])), out))
                else: #i == 1:
                    out = hstack((zeros((out.shape[0], bz)), out))
            if az > 0:
                if i == 0:
                    out = vstack((out, zeros((az, out.shape[1]))))
                else: #i == 1:
                    out = hstack((out, zeros((out.shape[0], az))))
        if isinstance(op, np.ndarray) or issparse(op):
            return out.toarray()
        else:
            return out
    def rmul(op):
        if op.ndim == 1:
            # op can't be a LazyLinearOp
            return op[z_sizes[0, 0]: z_sizes[0, 0] + x_shape[0]]
        r_offset = z_sizes[0][0]
        c_offset = z_sizes[1][0]
        return op[r_offset:r_offset + x_shape[0],
                  c_offset:c_offset + x_shape[1]]
    if len(x_shape) == 1:
        out_nrows = np.sum(z_sizes[0]) + x_shape[0]
    else:
        out_nrows = np.sum(z_sizes[0]) + x_shape[0]
    if use_pylops:
        from pylops import Pad
        pad = Pad(dims=x_shape, pad=z_sizes[0] if len(x_shape) == 1 else z_sizes)
        ret = LazyLinearOp((out_nrows, x_shape[0]), matmat=lambda op: pad @ op)
        if ret_unpad:
            ret2 = LazyLinearOp((x_shape[0], out_nrows),
                                      matmat=lambda op: pad.H @ op)
            return ret, ret2
        else:
            return ret
    else:
        ret = LazyLinearOp((out_nrows, x_shape[0]), matmat=lambda op: mul(op))
        if ret_unpad:
            ret2 = LazyLinearOp((x_shape[0], out_nrows), matmat=lambda op: rmul(op))
            ret = (ret, ret2)
    return ret

def _sanitize_op(op, op_name='op'):
    if not hasattr(op, 'shape') or not hasattr(op, 'ndim'):
        raise TypeError(op_name+' must have shape and ndim attributes')

def check_op(op):
    """
    Verifies validity assertions on any LazyLinearOp.

    Let op a LazyLinearOp, u a vector of size op.shape[1], v a vector of size
    op.shape[0], X an array such that X.shape[0] == op.shape[1],
    Y an array such that Y.shape[0] == op.shape[0],
    the function verifies that:

        - (op @ u).size == op.shape[0],
        - (op.H @ v).size == op.shape[1],
        - (op @ u).conj().T @ v == u.conj().T @ op.H @ v,
        - op @ X is equal to the horizontal concatenation of all op @ X[:, j] for j in {0, ..., X.shape[1]-1}.
        - op.H @ Y is equal to the horizontal concatenation of all op.H @ Y[:, j] for j in {0, ..., X.shape[1]-1}.
        - op @ X @ Y.H == (Y @ (X.H @ op.H)).H

    **Note**: this function has a computational cost (at least similar to the
    cost of op@x), it shouldn't be used into an efficient implementation but
    only to test a LazyLinearOp works properly.

    Example:
        >>> from numpy.random import rand
        >>> from lazylinop import aslazylinearoperator, check_op
        >>> M = rand(12, 14)
        >>> check_op(aslazylinearoperator(M))

    """
    u = np.random.randn(op.shape[1])
    v = np.random.randn(op.shape[0])
    X = np.random.randn(op.shape[1], 5)
    Y = np.random.randn(op.shape[0], 5)
    # Check operator - vector product dimension
    if (op @ u).shape != (op.shape[0],):
        raise Exception("Wrong operator dimension")
    # Check operator adjoint - vector product dimension
    if (op.H @ v).shape != (op.shape[1],):
        raise Exception("Wrong operator adjoint dimension")
    # Check operator - matrix product consistency
    if not np.allclose(op @ X, np.hstack([(op @ X[:, i]).reshape(-1, 1) for i in range(X.shape[1])])):
        raise Exception("Wrong operator matrix product")
    # Dot test to check forward - adjoint consistency
    if not np.allclose((op @ u).conj().T @ v, u.conj().T @ (op.H @ v)):
        raise Exception("Operator and its adjoint do not match")
    if (op.T @ Y).shape[0] != op.shape[1]:
        raise Exception("Wrong operator transpose dimension (when multiplying"
                        " an array)")
    if not np.allclose(op.H @ Y, np.hstack([(op.H @ Y[:, i]).reshape(-1, 1) for i in range(X.shape[1])])):
        raise Exception("Wrong operator adjoint on matrix product")
    if not np.allclose(op.dot(X) @ Y.T.conj(), (Y @ (X.T.conj() @ op.H)).T.conj()):
        raise Exception("Wrong operator on (Y @ X.H @ op.H).H")

def isLazyLinearOp(obj):
    """
    Returns True if obj is a LazyLinearOp, False otherwise.
    """
    return LazyLinearOp.isLazyLinearOp(obj)

def aslazylinearoperator(obj, shape=None) -> LazyLinearOp:
    """
    Creates a LazyLinearOp based on the object obj which must be of a linear operator compatible type.

    **Note**: obj must support operations and attributes defined in the
    LazyLinearOp class.
    Any operation not supported would raise an exception at the evaluation
    time.

    Args:
        obj:
            the root object on which the LazyLinearOp is based
            (it could be a numpy array, a scipy matrix, a Faust object or
            almost any object that supports the same kind of functions).
        shape:
            defines the shape of the resulting LazyLinearOp. In most cases
            this argument shouldn't be used because we can rely on obj.shape but
            if for any reason obj.shape is not well defined the user can explicitly
            define the shape of the LazyLinearOp (cf. example of pylops.Symmetrize defective shape).


    Returns: LazyLinearOp
        a LazyLinearOp instance based on obj.

    Example:
        >>> from lazylinop import aslazylinearoperator
        >>> import numpy as np
        >>> M = np.random.rand(10, 12)
        >>> lM = aslazylinearoperator(M)
        >>> twolM = lM + lM
        >>> twolM
        <10x12 LazyLinearOp with unspecified dtype>
        >>> import pyfaust as pf
        >>> F = pf.rand(10, 12)
        >>> lF = aslazylinearoperator(F)
        >>> twolF = lF + lF
        >>> twolF
        <10x12 LazyLinearOp with unspecified dtype>

		>>> # To illustrate the use of the optional “shape” parameter, let us consider implementing a lazylinearoperator associated with the pylops.Symmetrize linear operator,
		>>> # https://pylops.readthedocs.io/en/latest/api/generated/pylops.Symmetrize.html
		>>> # which is designed to symmetrize a vector, or a matrix, along some coordinate axis
		>>> from pylops import Symmetrize
		>>> M = np.random.rand(22, 2)
		>>> # Here the matrix M is of shape(22, 2) and we want to symmetrize it vertically (axis == 0), so we build the corresponding symmetrizing operator Sop
		>>> Sop = Symmetrize(M.shape, axis=0)
		>>> # Applying the operator to M works, and the symmetrized matrix has 43 = 2*22-1 rows, and 2 columns (as many as M) as expected
		>>> (Sop @ M).shape
		(43, 2)
		>>> # Since it maps matrices with 22 rows to matrices with 43 rows, the “shape” of Sop should be (43,22) however, the “shape” as provided by pylops is inconsistent

        >>> Sop.shape
        (86, 44)

		>>> # To exploit Sop as a LazyLinearOp we cannot rely on the “shape” given by pylops (otherwise the LazyLinearOp-matrix product wouldn't be properly defined, and would fail on a "dimensions must agree" exception)
		>>> # Thanks to the optional “shape” parameter of aslazylinearoperator, this can be fixed
		>>> lSop = aslazylinearoperator(Sop, shape=(43, 22))
		>>> # now lSop.shape is consistent 
		>>> lSop.shape
		(43, 22)
		>>> (lSop @ M).shape
		(43, 2)
		>>> # Besides, Sop @ M is equal to lSop @ M, so all is fine !
		>>> np.allclose(lSop @ M, Sop @ M)
		True


    **See also:** pyfaust.rand, pylops.Symmetrize
    (https://pylops.readthedocs.io/en/latest/api/generated/pylops.Symmetrize.html)

    """
    if isLazyLinearOp(obj):
        return obj
    return LazyLinearOp.create_from_op(obj, shape)

def hstack(tup):
    """
    Concatenates tup objects horizontally.

    Args:
        tup:
            a tuple whose first argument is a LazyLinearOp and other must
            be compatible objects (numpy array, matrix, LazyLinearOp).

    Return:
        A LazyLinearOp resulting of the concatenation.

    """
    lop = tup[0]
    if isLazyLinearOp(lop):
        return lop.concatenate(*tup[1:], axis=1)
    else:
        raise TypeError('lop must be a LazyLinearOp')

def vstack(tup):
    """
    Concatenates tup objects vertically.

    Args:
        tup:
            a tuple whose first argument is a LazyLinearOp and other must be
            compatible objects (numpy array, matrix, LazyLinearOp).

    Return:
        A LazyLinearOp resulting of the concatenation.

    """
    lop = tup[0]
    if isLazyLinearOp(lop):
        return lop.concatenate(*tup[1:], axis=0)
    else:
        raise TypeError('lop must be a LazyLinearOp')
