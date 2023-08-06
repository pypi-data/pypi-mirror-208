"""
Module for signal processing related LazyLinearOps (work in progress).
"""
import numpy as np
import scipy as sp
from lazylinop import *


_disable_numba = True


def fft(n, backend='scipy', **kwargs):
    """
    Returns a LazyLinearOp for the DFT of size n.

    Args:
        backend:
             'scipy' (default) or 'pyfaust' for the underlying computation of the DFT.
        kwargs:
            any key-value pair arguments to pass to the scipy of pyfaust dft backend
            (https://docs.scipy.org/doc/scipy/reference/generated/scipy.fft.fft.html,
            https://faustgrp.gitlabpages.inria.fr/faust/last-doc/html/namespacepyfaust.html#a2695e35f9c270e8cb6b28b9b40458600).

    Example:
        >>> #from lazylinop.wip.signal import fft
        >>> import numpy as np
        >>> F1 = fft(32, norm='ortho')
        >>> F2 = fft(32, backend='pyfaust')
        >>> x = np.random.rand(32)
        >>> np.allclose(F1 @ x, F2 @ x)
        True
        >>> y = F1 @ x
        >>> np.allclose(F1.H @ y, x)
        True
        >>> np.allclose(F2.H @ y, x)
        True

    """
    from scipy.fft import fft, ifft

    if backend == 'scipy':
        def scipy_scaling(kwargs):
            if 'norm' in kwargs:
                if kwargs['norm'] == 'ortho':
                    return 1
                elif kwargs['norm'] == 'forward':
                    return 1 / n
                elif kwargs['norm'] == 'backward':
                    return n
                else:
                    raise ValueError('Invalid norm value for scipy backend')
            else: # default is backward
                return n
        lfft = LazyLinearOp(matmat=lambda x: fft(x, axis=0, **kwargs),
                                  rmatmat=lambda x: ifft(x, axis=0, **kwargs) *
                                  scipy_scaling(kwargs), shape=(n, n))
    elif backend == 'pyfaust':
        from pyfaust import dft
        lfft = aslazylinearoperator(dft(n, **kwargs))
    else:
        raise ValueError('backend '+str(backend)+' is unknown')
    return lfft


def fft2(shape, backend='scipy', **kwargs):
    """Returns a LazyLinearOp for the 2D DFT of size n.

    Args:
        shape:
             the signal shape to apply the fft2 to.
        backend:
             'scipy' (default) or 'pyfaust' for the underlying computation of the 2D DFT.
        kwargs:
             any key-value pair arguments to pass to the scipy or pyfaust dft backend
                (https://docs.scipy.org/doc/scipy/reference/generated/scipy.fft.fft2.html,
                https://faustgrp.gitlabpages.inria.fr/faust/last-doc/html/namespacepyfaust.html#a2695e35f9c270e8cb6b28b9b40458600).

    Example:

        >>> #from lazylinop.wip.signal import fft2
        >>> import numpy as np
        >>> F_scipy = fft2((32, 32), norm='ortho')
        >>> F_pyfaust = fft2((32, 32), backend='pyfaust')
        >>> x = np.random.rand(32, 32)
        >>> np.allclose(F_scipy @ x.ravel(), F_pyfaust @ x.ravel())
        True
        >>> y = F_scipy @ x.ravel()
        >>> np.allclose(F_scipy.H @ y, x.ravel())
        True
        >>> np.allclose(F_pyfaust.H @ y, x.ravel())
        True
    """
    s = shape[0] * shape[1]
    if backend == 'scipy':
        from scipy.fft import fft2, ifft2
        return LazyLinearOp(
            (s, s),
            matvec=lambda x: fft2(x.reshape(shape), **kwargs).ravel(),
            rmatvec=lambda x: ifft2(x.reshape(shape), **kwargs).ravel()
        )
    elif backend == 'pyfaust':
        from pyfaust import dft
        K = kron(dft(shape[0], **kwargs), dft(shape[1], **kwargs))
        return LazyLinearOp((s, s), matvec=lambda x: K @ x,
                                  rmatvec=lambda x: K.H @ x)
    else:
        raise ValueError('backend '+str(backend)+' is unknown')


def _binary_dtype(A_dtype, B_dtype):
    if isinstance(A_dtype, str):
        A_dtype = np.dtype(A_dtype)
    if isinstance(B_dtype, str):
        B_dtype = np.dtype(B_dtype)
    if A_dtype is None:
        return B_dtype
    if B_dtype is None:
        return A_dtype
    if A_dtype is None and B_dtype is None:
        return None
    kinds = [A_dtype.kind, B_dtype.kind]
    if A_dtype.kind == B_dtype.kind:
        dtype = A_dtype if A_dtype.itemsize > B_dtype.itemsize else B_dtype
    elif 'c' in [A_dtype.kind, B_dtype.kind]:
        dtype = 'complex'
    elif 'f' in kinds:
        dtype = 'double'
    else:
        dtype = A_dtype
    return dtype

def _is_power_of_two(n: int) -> bool:
    """return True if integer 'n' is a power of two.

    Args:
        n: int

    Returns:
        bool
    """
    return ((n & (n - 1)) == 0) and n > 0


def flip(shape: tuple, start: int = 0, end: int = None, axis: int = 0):
    """Constructs a flip lazy linear operator.

    Args:
        shape: tuple
        shape of the input
        start: int, optional
        flip from start (default is 0)
        end: int, optional
        stop flip (not included, default is None)
        axis: int, optional
        if axis=0 (default) flip per column, if axis=1 flip per row
        it does not apply if shape[1] is None.

    Returns:
        The flip LazyLinearOp

    Raises:
        ValueError
            start is < 0.
        ValueError
            start is > number of elements along axis.
        ValueError
            end is < 1.
        ValueError
            end is > number of elements along axis.
        ValueError
            end is <= start.
        ValueError
            axis is either 0 or 1.
    Examples:
        >>> #from lazylinop.wip.signal import flip
        >>> import numpy as np
        >>> x = np.arange(6)
        >>> x
        array([0, 1, 2, 3, 4, 5])
        >>> y = flip(x.shape, 0, 5) @ x
        >>> y
        array([4, 3, 2, 1, 0, 5])
        >>> y = flip(x.shape, 2, 7) @ x # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ValueError: end is > number of elements along axis.
        >>> X = np.eye(5, M=5, k=0)
        >>> X
        array([[1., 0., 0., 0., 0.],
               [0., 1., 0., 0., 0.],
               [0., 0., 1., 0., 0.],
               [0., 0., 0., 1., 0.],
               [0., 0., 0., 0., 1.]])
        >>> flip(X.shape, 1, 4) @ X
        array([[1., 0., 0., 0., 0.],
               [0., 0., 0., 1., 0.],
               [0., 0., 1., 0., 0.],
               [0., 1., 0., 0., 0.],
               [0., 0., 0., 0., 1.]])
    """
    N = shape[0]
    A = N
    if len(shape) == 2:
        M = shape[1]
        if axis == 1:
            A = M

    if start < 0:
        raise ValueError("start is < 0.")
    if start > A:
        raise ValueError("start is > number of elements along axis.")
    if not end is None and end < 1:
        raise ValueError("end is < 1.")
    if not end is None and end > A:
        raise ValueError("end is > number of elements along axis.")
    if not end is None and end <= start:
        raise ValueError("end is <= start.")
    if axis != 0 and axis != 1:
        raise ValueError("axis is either 0 or 1.")

    def _matvec(x, start, end, axis):
        if x.ndim == 1:
            y = np.copy(x.reshape(x.shape[0], 1))
            x_is_1d = True
            y[start:end, 0] = x[end - 1 - (np.arange(start, end, 1) - start)]
            return y.ravel()
        else:
            y = np.copy(x)
            x_is_1d = False
            if axis == 0:
                y[start:end, :] = x[end - 1 - (np.arange(start, end, 1) - start), :]
            else:
                y[:, start:end] = x[:, end - 1 - (np.arange(start, end, 1) - start)]
            return y

    return LazyLinearOp(
        (N, N),
        matmat=lambda x: _matvec(x, start, N if end is None else end, axis),
        rmatmat=lambda x: _matvec(x, start, N if end is None else end, axis)
    )


def decimate(shape: tuple, start: int = 0, end: int = None, every: int = 2, axis: int = 0):
    """Constructs a decimation lazy linear operator.
    If the shape of the input array is (N, M) and the axis=0 the operator
    has a shape = ((D + D % every) // every, N) where D = end - start.

    Args:
        shape: tuple
        shape (N, M) of the input
        start: int, optional
        first element to keep, default is 0
        end: int, optional
        stop decimation (not included), default is None
        every: int, optional
        keep element every this number, default is 2
        axis: int, optional
        if axis=0 (default) decimation per column, if axis=1 decimation per row.
        it does not apply if shape[1] is None.

    Returns:
        The decimation LazyLinearOp

    Raises:
        ValueError
            every is < 1.
        ValueError
            axis expects 0 or 1.
        ValueError
            start is < 0.
        ValueError
            end is <= start.
        ValueError
            start is > number of elements along axis.
        ValueError
            end is > number of elements along axis.

    Examples:
        >>> #from lazylinop.wip.signal import decimate
        >>> import numpy as np
        >>> x = np.arange(10)
        >>> x
        array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        >>> y = decimate(x.shape, 0, 10, every=2) @ x
        >>> y
        array([0, 2, 4, 6, 8])
        >>> X = np.arange(30).reshape((10, 3))
        >>> X
        array([[ 0,  1,  2],
               [ 3,  4,  5],
               [ 6,  7,  8],
               [ 9, 10, 11],
               [12, 13, 14],
               [15, 16, 17],
               [18, 19, 20],
               [21, 22, 23],
               [24, 25, 26],
               [27, 28, 29]])
        >>> decimate(X.shape, 0, 10, every=2) @ X
        array([[ 0,  1,  2],
               [ 6,  7,  8],
               [12, 13, 14],
               [18, 19, 20],
               [24, 25, 26]])
    """
    if every < 1:
        raise ValueError("every is < 1.")
    if axis != 0 and axis != 1:
        raise ValueError("axis expects 0 or 1.")
    N = shape[0]
    if start < 0:
        raise ValueError("start is < 0.")
    M = 1 if len(shape) == 1 else shape[1]
    if start > (N if axis == 0 else M):
        raise ValueError("start is > number of elements along axis.")
    if not end is None:
        if end > (N if axis == 0 else M):
            raise ValueError("end is > number of elements along axis.")
    if not end is None and end <= start:
        raise ValueError("end is <= start.")

    def _matmat(x, start, end, every, axis):
        D = end - start
        # L = (D + D % every) // every
        L = int(np.ceil(D / every))
        if x.ndim == 1:
            y = np.zeros((L, 1), dtype=x.dtype)
            indices = np.arange(y.shape[0])
            y[indices, 0] = x[start + indices * every]
            return y.ravel()
        else:
            if axis == 0:
                # decimation per column
                y = np.zeros((L, x.shape[1]), dtype=x.dtype)
                indices = np.arange(y.shape[0])
                y[indices, :] = x[start + indices * every, :]
            else:
                # decimation per row
                y = np.zeros((x.shape[0], L), dtype=x.dtype)
                indices = np.arange(y.shape[1])
                # print(x.shape, start + indices * every)
                y[:, indices] = x[:, start + indices * every]
            return y

    def _rmatmat(x, start, end, every, axis):
        if x.ndim == 1:
            y = np.zeros(end, dtype=x.dtype)
            indices = np.arange(x.shape[0])
            y[start + indices * every] = x[indices]
            return y
        else:
            D = end - start
            if axis == 0:
                # decimation per column
                y = np.zeros((end, x.shape[1]), dtype=x.dtype)
                indices = np.arange(x.shape[0])
                y[start + indices * every, :] = x[indices, :]
            else:
                # decimation per row
                y = np.zeros((x.shape[0], end), dtype=x.dtype)
                indices = np.arange(y.shape[1])
                y[:, indices] = x[:, start + indices * every]
            return y

    last = (N if axis==0 else M) if end is None else end
    D = last - start
    # L = (D + D % every) // every
    L = int(np.ceil(D / every))
    return LazyLinearOp(
        (L, N),
        matmat=lambda x: _matmat(x, start, last, every, axis),
        rmatmat=lambda x: _rmatmat(x, start, last, every, axis)
    )


def bc(shape: tuple, n: int=1, boundary='periodic'):
    """Constructs a periodic boundary condition lazy linear operator
    xN, ..., x2, x1 | x1, x2, ..., xN | xN, ..., x2, x1
    or constructs a symmetric boundary condition lazy linear operator.
    x1, x2, ..., xN | x1, x2, ..., xN | x1, x2, ..., xN

    Args:
        shape: tuple
        shape of the array
        n: int, optional
        duplicate signal this number of times on both side
        boundary: str, optional
        boundary condition ('periodic' is default)

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            n has to be >= 1.
        ValueError
            boundary is either 'periodic' or 'symmetric'.

    Examples:
        >>> #from lazylinop.wip.signal import bc
        >>> import numpy as np
        >>> x = np.arange(10)
        >>> x
        >>> LOP = bc(x.shape, n=1, boundary='periodic')
        >>> LOP @ x
        >>> X = np.arange(12).reshape(4, 3)
        >>> X
        >>> LOP = bc(X.shape, n=1, boundary='periodic')
        >>> LOP @ X
        >>> x = np.arange(5)
        >>> x
        array([0, 1, 2, 3, 4])
        >>> LOP = bc(x.shape, n=1, boundary='symmetric')
        >>> LOP @ x
        array([4, 3, 2, 1, 0, 0, 1, 2, 3, 4, 4, 3, 2, 1, 0])
        >>> X = np.arange(12).reshape(4, 3)
        >>> X
        array([[0, 1, 2],
               [3, 4, 5]])
        >>> LOP = bc(X.shape, n=1, boundary='symmetric')
        >>> LOP @ X
        array([[3, 4, 5],
               [0, 1, 2],
               [0, 1, 2],
               [3, 4, 5],
               [3, 4, 5],
               [0, 1, 2]])
    """
    if n < 1:
        raise ValueError("n has to be >= 1.")

    if boundary == 'symmetric':
        def _matvec(x, n):
            shape = x.shape
            if len(shape) == 1:
                X, Y = shape[0], 1
                x = x.reshape(X, 1)
            else:
                X, Y = shape[0], shape[1]
            y = np.zeros(((n + 1 + n) * X, Y), dtype=x.dtype)
            y[(n * X):((n + 1) * X), :] = x[:X, :]
            for i in range(0, n, 2):
                y[((n - 1 - i) * X):((n - i) * X), :] = x[X - 1 - np.arange(X), :]
                y[((n + 1 + i) * X):((n + 2 + i) * X), :] = x[X - 1 - np.arange(X), :]
            for i in range(1, n, 2):
                y[((n - 1 - i) * X):((n - i) * X), :] = x[:X, :]
                y[((n + 1 + i) * X):((n + 2 + i) * X), :] = x[:X, :]
            if Y == 1:
                return y.ravel()
            else:
                return y

        def _rmatvec(x, n):
            shape = x.shape
            if len(shape) == 1:
                X, Y = shape[0], 1
                x = x.reshape(X, 1)
            else:
                X, Y = shape[0], shape[1]
            y = np.zeros((Y, (n + 1 + n) * X), dtype=x.dtype)
            y[:, (n * X):((n + 1) * X)] = x[:X, :]
            for i in range(0, n, 2):
                y[:, ((n - 1 - i) * X):((n - i) * X)] = x[X - 1 - np.arange(X), :]
                y[:, ((n + 1 + i) * X):((n + 2 + i) * X)] = x[X - 1 - np.arange(X), :]
            for i in range(1, n, 2):
                y[:, ((n - 1 - i) * X):((n - i) * X)] = x[:X, :]
                y[:, ((n + 1 + i) * X):((n + 2 + i) * X)] = x[:X, :]
            if Y == 1:
                return y.ravel()
            else:
                return y
    elif boundary == 'periodic':
        def _matvec(x, n):
            shape = x.shape
            if len(shape) == 1:
                X, Y = shape[0], 1
                y = np.zeros(((n + 1 + n) * X, 1), dtype=x.dtype)
                for i in range(n + 1 + n):
                    y[(i * X):((i + 1) * X), 0] = x[:X]
                return y.ravel()
            else:
                X, Y = shape[0], shape[1]
                y = np.zeros(((n + 1 + n) * X, X), dtype=x.dtype)
                for i in range(n + 1 + n):
                    y[(i * X):((i + 1) * X), :] = x[:X]
                return y

        def _rmatvec(x, n):
            shape = x.shape
            if len(shape) == 1:
                X, Y = shape[0], 1
                y = np.zeros((1, (n + 1 + n) * X), dtype=x.dtype)
                for i in range(n + 1 + n):
                    y[0, (i * X):((i + 1) * X)] = x[:X]
                return y.ravel()
            else:
                X, Y = shape[0], shape[1]
                y = np.zeros((X, (n + 1 + n) * X), dtype=x.dtype)
                for i in range(n + 1 + n):
                    y[:, (i * X):((i + 1) * X)] = x[:X]
                return y
    else:
        raise ValueError("boundary is either 'periodic' or 'symmetric'.")

    return LazyLinearOp(
        ((n + 1 + n) * shape[0], shape[0]),
        matvec=lambda x: _matvec(x, n),
        rmatvec=lambda x: _rmatvec(x, n)
    )

def _old_dwt(hfilter: np.ndarray, lfilter: np.ndarray, mode: str = 'zero', level: int = -1, **kwargs):
    """Constructs Discrete Wavelet Transform (DWT) as lazy linear operator.
    Because of the decomposition, the size of the data has to be a power of 2.

    Args:
        :hfilter: np.ndarray, quadratic mirror high-pass filter
        :lfilter: np.ndarray, quadratic mirror low-pass filter
        :mode: str, optional, see pywavelet documentation for more details, zero is default
        :level: int, decomposition level, by default (level < 0) return all
        :kwargs:
            :N: int, size of the input signal
            :shape: tuple, shape of the input signal

    Returns:
        The DWT LazyLinearOp.

    Raises:
        ValueError
            size of the input is not a power of two.
    """
    if 'N' in kwargs.keys() and 'shape' in kwargs.keys():
        raise ValueError("function expects N or shape argument but not both.")
    if not ('N' in kwargs.keys() or 'shape' in kwargs.keys()):
        raise ValueError("function expects N or shape argument.")
    use_1d, use_2d = False, False
    for key, value in kwargs.items():
        if key == 'N':
            N = value
            use_1d = True
            if not _is_power_of_two(N):
                raise ValueError("size of the input is not a power of two.")
        elif key == 'shape':
            shape = value
            use_2d = True
            if not (_is_power_of_two(shape[0]) and _is_power_of_two(shape[1])):
                raise ValueError("size of the input is not a power of two.")
        else:
            pass
    if use_1d:
        # because of the decomposition the size
        # of the input has to be a power of 2^k
        K = int(np.log2(N))
        # first iteration of hih-pass and low-pass filters + decimation
        # return vertical stack of high-pass and low-pass filters lazy linear operator
        D = K if level < 1 else min(K, level)
        A = [None] * (D)
        A[0] = _dwt_qmf_decimation(hfilter, lfilter, (N, ))
        M = [N // 2]
        for i in range(1, D, 1):
            # low-pass filter output goes through low-pass and high-pass filters
            A[i] = block_diag(*[_dwt_qmf_decimation(hfilter, lfilter, (M[i - 1], )), eye(N - M[i - 1], n=N - M[i - 1], k=0)], mt=True) @ A[i - 1]
            M.append(M[i - 1] // 2)
        return A[len(A) - 1]
    if use_2d:
        # TODO, does not work.
        print("Work in progress ...")
        # image has been flattened vec = (row1, row2, ..., rowR) with size = R * C
        # number of rows, columns
        R, C = shape[0], shape[1]
        # low and high-pass filter for each row
        # A = kron(eye(R, n=R, k=0), _dwt_qmf_decimation(hfilter, lfilter, (C, )), use_pylops=True)
        G = kron(eye(R, n=R, k=0), _dwt_qmf_decimation(hfilter, lfilter, (C, ), filters = "low"), use_pylops=True)
        # result is vec = (gdrow1, gdrow2, ..., gdrowR)
        H = kron(eye(R, n=R, k=0), _dwt_qmf_decimation(hfilter, lfilter, (C, ), filters = "high"), use_pylops=True)
        print(H)
        # result is vec = (hdrow1, hdrow2, ..., hdrowR)
        # now we work on the columns
        # get first column
        # P[r, r * N / 2] = 1 where r = 0 to R
        
        # result is ((G_1, H_1), (G_2, H_2), ..., (G_R, H_R)) with size = R * C
        B = kron(eye(R, n=R, k=0), _dwt_qmf_decimation(hfilter, lfilter, (R, )), use_pylops=True)
        return H


def _dwt(hfilter: np.ndarray, lfilter: np.ndarray, mode: str = 'zero', level: int = -1, **kwargs):
    """Constructs Discrete Wavelet Transform (DWT) as lazy linear operator.
    Because of the decomposition, the size of the data has to be a power of 2.

    Args:
        hfilter:
            np.ndarray, quadratic mirror high-pass filter
        lfilter:
            np.ndarray, quadratic mirror low-pass filter
        mode:
            str, optional, see pywavelet documentation for more details, zero is default
        level:
            int, decomposition level, by default (level < 0) return all
        kwargs:
            in1:
                np.ndarray, input array
            shape:
                tuple, shape of the input array
            implementation:
                int, 0 or anything


    Returns:
        The DWT LazyLinearOp.

    Raises:
        ValueError
            function expects in1 or shape argument but not both.
        ValueError
            function expects in1 or shape argument.
        ValueError
            first dimension of the input is not a power of two.
        ValueError
            second dimension of the input is not a power of two.
    """
    if 'in1' in kwargs.keys() and 'shape' in kwargs.keys():
        raise ValueError("function expects in1 or shape argument but not both.")
    if not ('in1' in kwargs.keys() or 'shape' in kwargs.keys()):
        raise ValueError("function expects in1 or shape argument.")
    use_1d, use_2d, implementation = False, False, 1
    for key, value in kwargs.items():
        if key == 'in1':
            shape = value.shape
            use_1d = bool(in1.ndim == 1)
            use_2d = bool(in1.ndim == 2)
        elif key == 'shape':
            shape = value
            use_1d = bool(not shape[0] is None and shape[1] is None)
            use_2d = bool(not shape[0] is None and not shape[1] is None)
        elif key == 'implementation':
            implementation = value
        else:
            pass
    N = shape[0]
    if not _is_power_of_two(N):
        raise ValueError("first dimension of the input is not a power of two.")
    if not shape[1] is None:
        if not _is_power_of_two(shape[1]):
            raise ValueError("second dimension of the input is not a power of two.")
    if use_1d:
        # because of the decomposition the size
        # of the input has to be a power of 2^k
        K = int(np.log2(N))
        # first iteration of hih-pass and low-pass filters + decimation
        # return vertical stack of high-pass and low-pass filters lazy linear operator
        D = K if level < 1 else min(K, level)
        A = eye(N, n=N, k = 0)
        M = [N]
        for i in range(D):
            # low-pass filter
            G = convolveND((M[i], ), lfilter, mode='same', boundary='fill', method='lazy.scipy.signal.convolve')
            # high-pass filter
            H = convolveND((M[i], ), hfilter, mode='same', boundary='fill', method='lazy.scipy.signal.convolve')
            # decimation and vertical stack (pywavelet starts from 1)
            if False:
                GH = vstack((G[1::2, :], H[1::2, :]))
            else:
                GH = vstack((decimation(G.shape, 1, None, 2) @ G, decimation(H.shape, 1, None, 2) @ H))
            if i == 0:
                # first level of decomposition
                # apply low and high-pass filters to the signal
                A = GH @ A
            else:
                # second and higher levels of decomposition
                # do not apply to the result of the high-pass filter
                tmp_eye = eye(N - M[i], n=N - M[i], k=0)
                # low-pass filter output goes through low-pass and high-pass filters
                # it corresponds to a lazy linear operator (second level of decomposition):
                # (GH 0) @ (G) @ input
                # (0 Id)   (H)
                A = block_diag(*[GH, tmp_eye], mt=True) @ A
            M.append(M[i] // 2)
        return A
    if use_2d:
        # TODO: does not work for decomposition level > 1.
        if implementation == 0:
            # image has been flattened (with img.flatten(order='C'))
            # the result is vec = (row1, row2, ..., rowR) with size = R * C
            # number of rows, columns
            R, C = shape[0], shape[1]
            # low-pass filter for each row + decimation
            # result is vec = (gdrow1, gdrow2, ..., gdrowR)
            G = kron(eye(R, n=R, k=0), _dwt_qmf_decimation(hfilter, lfilter, (C, ), filters = "low"), use_pylops=True)
            # high-pass filter for each row + decimation
            # result is vec = (hdrow1, hdrow2, ..., hdrowR)
            H = kron(eye(R, n=R, k=0), _dwt_qmf_decimation(hfilter, lfilter, (C, ), filters = "high"), use_pylops=True)
            # now we work on the columns
            # from 'C' order to 'F' order
            G = C_to_F_flatten((R, C // 2)) @ G
            H = C_to_F_flatten((R, C // 2)) @ H
            # low-pass for each column of the result of the previous low-pass filter
            GG = kron(eye(R, n=R, k=0), _dwt_qmf_decimation(hfilter, lfilter, (C // 2, ), filters = "low"), use_pylops=True) @ G
            # high-pass for each column of the result of the previous low-pass filter
            HG = kron(eye(R, n=R, k=0), _dwt_qmf_decimation(hfilter, lfilter, (C // 2, ), filters = "high"), use_pylops=True) @ G
            # low-pass for each column of the result of the previous high-pass filter
            GH = kron(eye(R, n=R, k=0), _dwt_qmf_decimation(hfilter, lfilter, (C // 2, ), filters = "low"), use_pylops=True) @ H
            # high-pass for each column of the result of the previous high-pass filter
            HH = kron(eye(R, n=R, k=0), _dwt_qmf_decimation(hfilter, lfilter, (C // 2, ), filters = "high"), use_pylops=True) @ H
            # from 'F' order to 'C' order
            GG = C_to_F_flatten((C // 2, R // 2)) @ GG
            HG = C_to_F_flatten((C // 2, R // 2)) @ HG
            GH = C_to_F_flatten((C // 2, R // 2)) @ GH
            HH = C_to_F_flatten((C // 2, R // 2)) @ HH
        else:
            # image has been flattened (with img.flatten(order='C'))
            # the result is vec = (row1, row2, ..., rowR) with size = R * C
            # number of rows, columns
            R, C = shape[0], shape[1]
            # low-pass filter for each row + decimation
            # high-pass filter for each row + decimation
            # first work on the row ...
            G = _dwt_qmf_decimation(hfilter, lfilter, (C, ), filters = "low")
            H = _dwt_qmf_decimation(hfilter, lfilter, (C, ), filters = "high")
            GH = vstack((G, H))
            A = kron(GH, GH, use_pylops=True)
            print(A, R, C)
            # ... and then work on the column
            
        # do we need to do from 'F' order to 'C' order ?
        # return -------
        #        |GG|HG|
        #        -------
        #        |GH|HH|
        #        -------
        # return vstack((hstack((GG, HG)), hstack((GH, HH))))
        # return ----
        #        |GG|
        #        |HG|
        #        |GH|
        #        |HH|
        #        ----
        return vstack((vstack((GG, HG)), vstack((GH, HH))))


def dwt(in1, hfilter: np.ndarray, lfilter: np.ndarray, mode: str = 'zero', level: int = 1) -> list:
    """multiple levels DWT, see _dwt function for more details.
    If in1 is a tuple the function returns a lazy linear operator.
    If in1 is a Numpy array the function returns the result of the DWT.

    Args:
        in1:
            tuple or np.ndarray, shape or array of the input
        hfilter:
            np.ndarray, quadratic mirror high-pass filter
        lfilter:
            np.ndarray, quadratic mirror low-pass filter
        mode:
            str, optional, see pywavelet documentation for more details, zero is default
        level:
            int, optional, decomposition level >= 1, 1 is the default value
            consider only decomposition level <= log2(in1.shape[0])

    Returns:
        [cAn, cDn, cDn-1, ..., cD2, cD1]: list, approximation and detail coefficients

    Raises:
        ValueError
            decomposition level must greater or equal to 1.
        Exception
            in1 expects tuple or np.ndarray.
    """
    if level < 1:
        raise ValueError("decomposition level must be greater or equal to 1.")
    if type(in1) is tuple:
        return _dwt(hfilter, lfilter, mode, 1, shape=in1)
    elif type(in1) is np.ndarray:
        if in1.ndim == 1:
            N = in1.shape[0]
            if level == 1:
                cAcD = _dwt(hfilter, lfilter, mode, 1, N=N) @ in1
                return [cAcD[:(N // 2)], cAcD[(N // 2):]]
            else:
                cAD = _dwt(hfilter, lfilter, mode, level, N=N) @ in1
                # max decomposition level
                K = int(np.log2(N))
                # build list of approximaton and details coefficients
                M = N // np.power(2, level)
                list_cAD = [cAD[:M], cAD[M:(2 * M)]]
                start = 2 * M
                for k in range(min(K, level) - 1 - 1, -1, -1):
                    M *= 2
                    list_cAD.append(cAD[start:(start + M)])
                    start += M
                return list_cAD
        if in1.ndim == 2:
            X, Y = in1.shape
            F = X * Y
            result = _dwt(hfilter, lfilter, mode, 1, shape=in1.shape) @ in1.flatten()
            return (result[:(F // 4)], (result[(F // 4):(2 * F // 4)], result[(2 * F // 4):(3 * F // 4)], result[(3 * F // 4):]))
    else:
        raise Exception("in1 expects tuple or np.ndarray.")

def dwt1d(shape: tuple, hfilter: np.ndarray, lfilter: np.ndarray, boundary: str = 'zero', level: int = None):
    """Constructs a Discrete Wavelet Transform (DWT) lazy linear operator.
    Because of the decomposition, the size of the data has to be a multiple of 2.
    If the lazy linear operator is applied to 1d array it returns:
    first level: [cA, cD]
    nth level  : [cAn, cDn, cDn-1, ..., cD2, cD1]
    Of note, the function follows the format returned by Pywavelets module.

    Args:
        shape: tuple
        shape of the input array
        hfilter: np.ndarray
        quadratic mirror high-pass filter
        lfilter: np.ndarray
        quadratic mirror low-pass filter
        boundary: str, optional
        zero, signal is padded with zeros (default)
        symmetric, use mirroring to pad the signal
        periodic, signal is treated as periodic signal
        level: int, optional
        decomposition level, by default (None) return all

    Returns:
        LazyLinearOp

    Raises:
        ValueError
            shape expects tuple.
        ValueError
            first dimension is not a multiple of 2.
        ValueError
            second dimension is not a multiple of 2.
        ValueError
            decomposition level must be greater or equal to 1.
        ValueError
            boundary is either 'zero', 'symmetric' or 'periodic'.
        ValueError
            level is greater than the maximum decomposition level.

    References:
        See also `Pywavelets module <https://pywavelets.readthedocs.io/en/latest/ref/dwt-discrete-wavelet-transform.html#pywt.wavedec>`_
    """
    if not type(shape) is tuple:
        raise ValueError("shape expects tuple.")
    if level < 1:
        raise ValueError("decomposition level must be greater or equal to 1.")
    if not boundary in ['zero', 'symmetric', 'periodic']:
        raise ValueError("boundary is either 'zero', 'symmetric' or 'periodic'.")

    if (shape[0] % 2) != 0:
        raise ValueError("first dimension is not a multiple of 2.")
    if len(shape) == 2:
        if (shape[1] % 2) != 0:
            raise ValueError("second dimension is not a multiple of 2.")

    # maximum decomposition level
    N = shape[0]
    bufferN, K = N, 0
    while (bufferN % 2) == 0:
        bufferN = bufferN // 2
        K += 1
    if level > K:
        raise ValueError("level is greater than the maximum decomposition level.")
    D = K if level is None else level

    # add X signal before and after
    X = 2

    # first iteration of hih-pass and low-pass filters + decimation
    # return vertical stack of high-pass and low-pass filters lazy linear operator
    if boundary == 'symmetric':
        # tmp_eye = eye(N, n=N, k=0)
        # tmp_flip = flip(shape, start=0, end=None)
        # A = vstack((tmp_flip, vstack((tmp_eye, tmp_flip))))
        A = bc((N, ), n=X, boundary='symmetric')
    elif boundary == 'periodic':
        # tmp_eye = eye(N, n=N, k=0)
        # A = vstack((tmp_eye, vstack((tmp_eye, tmp_eye))))
        A = bc((N, ), n=X, boundary='periodic')
    else:
        A = eye(N, n=N, k=0)
    Nm = A.shape[0]
    M = [Nm]
    for i in range(D):
        # low-pass filter
        G = convolve((M[i], ), lfilter, mode='same', method='lazy.scipy.signal.convolve')
        # high-pass filter
        H = convolve((M[i], ), hfilter, mode='same', method='lazy.scipy.signal.convolve')
        # decimation and vertical stack (pywavelet starts from 1)
        if False:
            GH = vstack((G[1::2, :], H[1::2, :]))
        else:
            GH = vstack((decimate(G.shape, 1, None, 2) @ G, decimate(H.shape, 1, None, 2) @ H))
        if i == 0:
            # first level of decomposition
            # apply low and high-pass filters to the signal
            A = GH @ A
        else:
            # second and higher levels of decomposition
            # do not apply to the result of the high-pass filter
            E = eye(Nm - M[i], n=Nm - M[i], k=0)
            # low-pass filter output goes through low-pass and high-pass filters
            # for second level of decomposition it corresponds to a lazy linear operator like:
            # (GH 0) @ (G) @ input
            # (0 Id)   (H)
            A = block_diag(*[GH, E], mt=True) @ A
        M.append(M[i] // 2)
    return A


def dwt1d_coeffs(in1: np.ndarray, boundary: str = 'zero', level: int = None):
    """Returns approximation and details coefficients of Discrete-Wavelet-Transform.
    first level: [cA, cD]
    nth level  : [cAn, cDn, cDn-1, ..., cD2, cD1]
    Of note, the function follows the format returned by Pywavelets module.

    Args:
        in1: np.ndarray
        input array (result of `dwt1d @ signal`)
        mode: str, optional
        zero, signal is padded with zeros (default)
        symmetric, use mirroring to pad the signal
        periodic, signal is treated as periodic signal
        level: int, optional
        decomposition level, by default (None) return all

    Returns:
        first level: list [cA, cD]
        nth level: list [cAn, cDn, cDn-1, ..., cD2, cD1] of approximation and detail coefficients
        TODO in1 is 2d input array:
        it follows Pywavelets format

    Raises:
        ValueError
            in1 expects np.ndarray.
        ValueError
            first dimension is not a multiple of 2.
        ValueError
            second dimension is not a multiple of 2.
        ValueError
            decomposition level must be greater or equal to 1.
        ValueError
            boundary is either 'zero', 'symmetric' or 'periodic'.
        ValueError
            level is greater than the maximum decomposition level.

    References:
        See also `Pywavelets module <https://pywavelets.readthedocs.io/en/latest/ref/dwt-discrete-wavelet-transform.html#pywt.wavedec>`_
    """
    if not type(in1) is np.ndarray:
        raise ValueError("in1 expects np.ndarray.")
    if level < 1:
        raise ValueError("decomposition level must be greater or equal to 1.")
    if not boundary in ['zero', 'symmetric', 'periodic']:
        raise ValueError("mode is either 'zero', 'symmetric' or 'periodic'.")

    shape = in1.shape

    if (shape[0] % 2) != 0:
        raise ValueError("first dimension is not a multiple of 2.")
    if len(shape) == 2:
        if (shape[1] % 2) != 0:
            raise ValueError("second dimension is not a multiple of 2.")

    # add X signal before and after
    if boundary == 'symmetric' or boundary == 'periodic':
        X = 2
        N = shape[0] // (2 * X + 1)
    else:
        X = 1
        N = shape[0]

    # maximum decomposition level
    bufferN, K = N, 0
    while (bufferN % 2) == 0:
        bufferN = bufferN // 2
        K += 1
    if level > K:
        raise ValueError("level is greater than the maximum decomposition level.")
    D = K if level is None else level

    # first iteration of hih-pass and low-pass filters + decimation
    # return vertical stack of high-pass and low-pass filters lazy linear operator
    if boundary == 'symmetric' or boundary == 'periodic':
        Nm = shape[0]
    else:
        Nm = N

    sm = Nm // 2
    if level == 1:
        return [in1[(sm - N // 2):sm], in1[sm:(sm + N // 2)]]
    else:
        # decomposition level > 1
        # list [cAn, cDn, cDn-1, ..., cD2, cD1] of approximaton and details coefficients
        cAD = [None] * (level + 1)
        M = N
        # list [cDn, cDn-1, ..., cD2, cD1] of details coefficients
        for k in range(level):
            cAD[level - k] = in1[sm:(sm + M // 2)]
            M = N // np.power(2, k + 1)
            sm = (Nm // 2) // np.power(2, k + 1)
        # add cAn at the beginning of the cAD list
        cAD[0] = in1[0:(N // np.power(2, level))]
        return cAD


def _ttoeplitz(c1: np.ndarray, r1: np.ndarray, K: int = None):
    """Constructs triangular Toeplitz matrix as lazy linear operator
    that will be used in the computation of the convolution.
    Shape of the lazy linear operator is computed from c1 and r1.

    Args:
        c1: np.ndarray
        first column of the Toeplitz matrix, shape is (R, )
        r1: np.ndarray
        first row of the Toeplitz matrix, shape is (C, )
        if r1 is not zero considers c1 to be zero except first element c1[0] = r1[0]
        K: int, optional
        size of the kernel, if None (default) size is c1.shape[0]

    Returns:
        The triangular Toeplitz LazyLinearOp
    """
    # matrix-vector product
    import numba as nb
    nb.config.DISABLE_JIT = int(_disable_numba)
    @nb.jit(nopython=True)
    def _matvec(x, c1: np.ndarray, r1: np.ndarray) -> np.ndarray:
        # number of rows and columns (shape of Toeplitz matrix)
        R, C = c1.shape[0], r1.shape[0]
        nzr = np.count_nonzero(r1)
        if nzr > int(r1[0] != 0.0):
            # find the index 'sz' such that c1[i >= sz] = 0
            # all the elements with index greater or equal to 'sz' are zero
            if not K is None and K > 0:
                sz = K
            else:
                sz = 0
                for r in range(R):
                    nzr -= int(r1[r] != 0.0)
                    if nzr == 0:
                        sz = r + 1
                        break
            # print(r1[sz - 1], r1[sz], r1[sz + 1])
            mv = np.full(R, 0.0 * r1[0])
            fr1 = r1[:sz]
            rmax = min(R, C - sz)
            if nb.config.DISABLE_JIT == 0:
                mv[:rmax] = x[np.arange(0, rmax, 1)[:, None] + np.arange(0, sz, 1)] @ fr1
                for r in range(rmax, min(R, C), 1):
                    start = 0
                    end = start + sz - min(0, (C - sz) - r)
                    xstart = r
                    xend = min(x.shape[0], xstart + end - start)
                    mv[r] = fr1[start:end] @ x[xstart:xend]
            else:
                for r in range(min(R, C)):
                    start = 0
                    end = start + sz - min(0, (C - sz) - r)
                    xstart = r
                    xend = min(x.shape[0], xstart + end - start)
                    mv[r] = fr1[start:end] @ x[xstart:xend]
        else:
            # find the index 'sz' such that c1[i >= sz] = 0
            # all the elements with index greater or equal to 'sz' are zero
            if not K is None and K > 0:
                sz = K
            else:
                nzc = np.count_nonzero(c1)
                sz = 0
                for r in range(R):
                    nzc -= int(c1[r] != 0.0)
                    if nzc == 0:
                        sz = r + 1
                        break
            # print(R, sz, c1[sz - 1], c1[sz], c1[sz + 1])
            # import time
            # tt = time.time()
            mv = np.full(R, 0.0 * c1[0])
            # txy = tt - time.time()
            fc1 = np.flip(c1[:sz])
            if nb.config.DISABLE_JIT == 0:
                for r in range(R):
                    start = max(0, (sz - 1) - r)
                    end = sz + min(0, C - (r + 1))
                    xend = min(C, r + 1)
                    xstart = max(0, xend - (end - start))
                    # t0 = time.time()
                    mv[r] = np.dot(fc1[start:end], x[xstart:xend])
                    # t0 = time.time() - t0
                    # t1 = time.time()
                    # mv[r] = np.sum(fc1[start:end] * x[xstart:xend])
                    # t1 = time.time() - t1
                    # print(t0, t1)
            else:
                # tt = time.time()
                for r in range(sz):
                    start = max(0, (sz - 1) - r)
                    end = sz + min(0, C - (r + 1))#min(sz, start + C)
                    xend = min(C, r + 1)
                    xstart = max(0, xend - (end - start))
                    mv[r] = np.dot(fc1[start:end], x[xstart:xend])
                # print(sz, time.time() - tt)
                # numpy broadcasting
                step = sz
                middle = (C - sz) - (C - sz) % step
                if True:
                    # tt = time.time()
                    mv[sz:(sz + middle)] = x[np.arange(0, middle, 1)[:, None] + np.arange(1, step + 1, 1)] @ fc1
                    # mv[sz:(sz + middle)] = np.sum(fc1 * x[np.arange(0, middle, 1)[:, None] + np.arange(1, step + 1, 1)], axis=1)
                    # t1 = time.time() - tt
                else:
                    # tt = time.time()
                    astep = np.arange(1, step + 1, 1)
                    vstep = np.arange(0, step, 1)[:, None]
                    for r in range(sz, sz + middle, step):
                        mv[r:(r + step)] = x[(vstep + (r - sz)) + astep] @ fc1
                    # print(time.time() - tt)
                # no numpy broadcasting
                for r in range(middle, R, 1):
                    start = max(0, (sz - 1) - r)
                    end = sz + min(0, C - (r + 1))#min(sz, start + C)
                    xend = min(C, r + 1)
                    xstart = max(0, xend - (end - start))
                    mv[r] = np.dot(fc1[start:end], x[xstart:xend])
        return mv
    # matrix-matrix product
    def _matmat(x, c1: np.ndarray, r1: np.ndarray) -> np.ndarray:
        # number of rows and columns (shape of Toeplitz matrix)
        R, C = c1.shape[0], r1.shape[0]
        nzr = int(r1[0] != 0.0)
        nzr = np.count_nonzero(r1)
        if nzr > 0:
            # find the index 'sz' such that c1[i >= sz] = 0
            # all the elements with index greater or equal to 'sz' are zero
            if not K is None and K > 0:
                sz = K
            else:
                sz = 0
                for r in range(R):
                    nzr -= int(r1[r] != 0.0)
                    if nzr == 0:
                        sz = r + 1
                        break
            # print(r1[sz - 1], r1[sz], r1[sz + 1])
            if x.dtype == r1.dtype:
                vtype = r1.dtype
            else:
                if 'complex' in r1.dtype.str:
                    vtype = 'complex128'
                elif 'float' in r1.dtype.str:
                    vtype = 'float64'
                else:
                    vtype = r1.dtype
            mv = np.zeros((R, x.shape[0]), dtype=vtype)
            fr1 = r1[:sz]
            for r in range(min(R, C)):
                start = 0
                end = start + sz - min(0, (C - sz) - r)
                xstart = r
                xend = min(x.shape[0], xstart + end - start)
                mv[r, :] = fr1[start:end] @ x[xstart:xend, :]
        else:
            # find the index 'sz' such that c1[i >= sz] = 0
            # all the elements with index greater or equal to 'sz' are zero
            if not K is None and K > 0:
                sz = K
            else:
                nzc = np.count_nonzero(c1)
                sz = 0
                for r in range(R):
                    nzc -= int(c1[r] != 0.0)
                    if nzc == 0:
                        sz = r + 1
                        break
            # print(R, sz, c1[sz - 1], c1[sz], c1[sz + 1])
            if x.dtype == c1.dtype:
                vtype = c1.dtype
            else:
                if 'complex' in c1.dtype.str:
                    vtype = 'complex128'
                elif 'float' in c1.dtype.str:
                    vtype = 'float64'
                else:
                    vtype = c1.dtype
            mv = np.zeros((R, x.shape[0]), dtype=vtype)
            fc1 = np.flip(c1[:sz])
            # print(x.ndim, x.shape, x)
            for r in range(R):
                start = max(0, (sz - 1) - r)
                end = sz + min(0, C - (r + 1))
                xend = min(C, r + 1)
                xstart = max(0, xend - (end - start))
                mv[r, :] = fc1[start:end] @ x[xstart:xend, :]
        return mv
    return LazyLinearOp(
        (c1.shape[0], r1.shape[0]),
        matvec=lambda x: _matvec(x, c1, r1),
        rmatvec=lambda x: _matvec(x, r1, c1)# ,
        # matmat=lambda X: _matmat(X, c1, r1),
        # rmatmat=lambda X: _matmat(X, r1, c1)
    )

def convolve(in1, in2: np.ndarray, mode: str = 'full', method: str = 'lazy.scipy.signal.convolve'):
    """If shape of the signal has been passed return Lazy Linear Operator
    that corresponds to the convolution with the kernel.
    If signal has been passed return the convolution result.

    Args:
        kernel: np.ndarray
        kernel to use for the convolution, shape is (K, ) for 1D
        mode: str, optional
            'full' computes convolution (input + padding)
            'valid' computes 'full' mode and extract centered output that does not depend on the padding. 
            'same' computes 'full' mode and extract centered output that has the same shape that the input.
            'circ' computes circular convolution
        method: str, optional
             'auto' use lazy encapsulation of scipy.signal.convolve (optimization and benchmark in progress)
             'direct' direct computation using nested for loops (Numba implementation is work-in-progress)
             'lazy.scipy.signal.convolve' (default) to use lazy encapsulation of Scipy.signal convolve function
             'scipy.linalg.toeplitz' to use lazy encapsulation of Scipy implementation of Toeplitz matrix
             'pyfaust.toeplitz' to use pyfaust implementation of Toeplitz matrix
             'lazylinop.toeplitz_for_convolution' to use Toeplitz for convolution optimization
             'oa' to use lazylinop implementation of overlap-add method
             'scipy.linalg.circulant' use Scipy implementation of circulant matrix (works with mode='circ')
             'scipy.fft.fft' use Scipy implementation of FFT to compute circular convolution (works with mode='circ')
             'pyfaust.circ' use pyfaust implementation of circulant matrix (works with mode='circ')
             'pyfaust.dft' use pyfaust implementation of DFT (works with mode='circ')
        kwargs:
            shape (tuple) of the signal to convolve with kernel.
            input_array (np.ndarray) to convolve with kernel, shape is (S, ) or (S, T)

    Returns:
        LazyLinearOp or np.ndarray

    Raises:
        ValueError
        number of dimensions of the signal and/or the kernel is greater than one.
        ValueError
        mode is either 'full' (default), 'valid', 'same' or 'circ'
        ValueError
        shape or input_array are expected
        ValueError
        size of the kernel is greater than the size of signal.
        ValueError
        method is not in:
             'auto',
             'direct',
             'lazy.scipy.signal.convolve',
             'scipy.linalg.toeplitz',
             'pyfaust.toeplitz',
             'lazylinop.toeplitz_for_convolution',
             'oa',
             'scipy.linalg.circulant',
             'scipy.fft.fft',
             'pyfaust.circ',
             'pyfaust.dft'
        Exception
            in1 expects tuple or np.ndarray.
        ValueError
            method='scipy.linalg.circulant', 'pyfaust.circ', 'scipy.fft.fft' or 'pyfaust.dft' works only with mode='circ'.

    Examples:
        >>> #from lazylinop.wip.signal import convolve
        >>> import numpy as np
        >>> import scipy as sp
        >>> signal = np.random.rand(1024)
        >>> kernel = np.random.rand(32)
        >>> c1 = convolve(signal.shape, kernel, mode='same', method='lazylinop.toeplitz_for_convolution') @ signal
        >>> c2 = convolve(signal.shape, kernel, mode='same', method='pyfaust.toeplitz') @ signal
        >>> c3 = sp.signal.convolve(signal, kernel, mode='same', method='auto')
        >>> np.allclose(c1, c3)
        True
        >>> np.allclose(c2, c3)
        True
        >>> signal = np.random.rand(32768)
        >>> kernel = np.random.rand(48)
        >>> c1 = convolve(signal.shape, kernel, mode='circ', method='scipy.fft.fft') @ signal
        >>> c2 = convolve(signal.shape, kernel, mode='circ', method='pyfaust.dft') @ signal
        >>> c3 = convolve(signal, kernel, mode='same', method='scipy.fft.fft')
        >>> c4 = convolve(signal, kernel, mode='same', method='pyfaust.dft')
        >>> np.allclose(c1, c2)
        True
        >>> np.allclose(c1, c3)
        True
        >>> np.allclose(c1, c4)
        True
    """
    if not mode in ['full', 'valid', 'same', 'circ']:
        raise ValueError("mode is either 'full' (default), 'valid', 'same' or 'circ'.")

    methods = [
        'auto',
        'direct',
        'lazy.scipy.signal.convolve',
        'scipy.linalg.toeplitz',
        'pyfaust.toeplitz',
        'lazylinop.toeplitz_for_convolution',
        'oa',
        'scipy.linalg.circulant',
        'scipy.fft.fft',
        'pyfaust.circ',
        'pyfaust.dft'
    ]
    if not method in methods:
        raise ValueError("method is not in " + str(methods))

    if mode == 'circ' and (method != 'scipy.linalg.circulant' and method != 'pyfaust.circ' and method != 'scipy.fft.fft' and method != 'pyfaust.dft'):
        raise ValueError("mode 'circ' expects method to be 'scipy.linalg.circulant' or 'pyfaust.circ' or 'scipy.fft.fft' or 'pyfaust.dft'.")

    if mode != 'circ' and (method == 'scipy.linalg.circulant' or method == 'pyfaust.circ' or method == 'scipy.fft.fft' or method == 'pyfaust.dft'):
        raise ValueError("method='scipy.linalg.circulant', 'pyfaust.circ', 'scipy.fft.fft' or 'pyfaust.dft' works only with mode='circ'.")

    # check if signal has been passed to the function
    # check if shape of the signal has been passed to the function
    if type(in1) is tuple:
        return_lazylinop = True
        shape = in1
    elif type(in1) is np.ndarray:
        return_lazylinop = False
        shape = in1.shape
    else:
        raise Exception("in1 expects tuple or np.ndarray.")

    if shape[0] <= 0 or in2.ndim != 1:
        raise ValueError("number of dimensions of the signal and/or the kernel is not equal to 1.")

    K = in2.shape[0]
    S = shape[0]
    if K > S:
        raise ValueError("size of the kernel is greater than the size of the signal.")

    if mode == 'circ':
        compute = 'circ.' + method
    else:
        compute = method

    ckernel = True#bool('complex' in in2.dtype.str)

    # lazy linear operator
    # check which method is asked for
    if compute == 'direct':
        import numba
        from numba import prange
        @numba.jit(nopython=True)
        def _matvec(kernel, signal):
            K = kernel.shape[0]
            S = signal.shape[0]
            O = S + K - 1
            output = np.full(O, 0.0)
            # y[n] = sum(h[k] * s[n - k], k, 0, K - 1)
            if K > 1000:
                for i in prange(O):
                    for j in range(K):
                        output[i] += kernel[j] * (signal[i - j] if (i - j) >= 0 and (i - j) < S else 0.0)
            else:
                for i in range(O):
                    for j in range(K):
                        output[i] += kernel[j] * (signal[i - j] if (i - j) >= 0 and (i - j) < S else 0.0)
                # output[i] = np.dot(kernel[:min(K, i + 1)], signal[np.minimum(S - 1, np.subtract(i, np.arange(min(K, i + 1))))])
            return output
        @numba.jit(nopython=True)
        def _rmatvec(kernel, signal):
            K = kernel.shape[0]
            S = signal.shape[0]
            O = S + K - 1
            output = np.full(O, 0.0)
            # y[n] = sum(h[k] * s[k + n], k, 0, K - 1)
            if K > 1000:
                for i in prange(O):
                    for j in range(K):
                        output[i] += kernel[j] * (signal[j + i] if (j + i) < S else 0.0)
            else:
                for i in range(O):
                    for j in range(K):
                        output[i] += kernel[j] * (signal[j + i] if (j + i) < S else 0.0)
                # output[i] = np.dot(kernel[:min(K, i + 1)], signal[np.minimum(S - 1, np.add(i, np.arange(min(K, i + 1))))])
            return output
        LO = LazyLinearOp(
            (S + K - 1, S),
            matvec=lambda x: _matvec(in2, x),
            rmatvec=lambda x: _rmatvec(in2, x)
        )
    elif compute == 'lazy.scipy.signal.convolve' or method == 'auto':
        LO = LazyLinearOp(
            (S + K - 1, S),
            matvec=lambda x: sp.signal.convolve(x, in2, mode='full', method='auto'),
            rmatvec=lambda x: sp.signal.correlate(x, in2, mode='full', method='auto')
        )
    elif compute == 'scipy.linalg.toeplitz':
        LO = LazyLinearOp(
            (S + K - 1, S),
            matvec=lambda x: sp.linalg.toeplitz(np.pad(in2, (0, S - 1)), np.pad([in2[0]], (0, S - 1))) @ x,
            rmatvec=lambda x: sp.linalg.toeplitz(np.pad(in2, (0, S - 1)), np.pad([in2[0]], (0, S - 1))).T.conj() @ x
        )
    elif compute == 'pyfaust.toeplitz':
        from pyfaust import toeplitz
        LO = LazyLinearOp(
            (S + K - 1, S),
            matvec=lambda x: toeplitz(np.pad(in2, (0, S - 1)), np.pad([in2[0]], (0, S - 1)), diag_opt=False) @ x if ckernel or 'complex' in x.dtype.str else np.real(toeplitz(np.pad(in2, (0, S - 1)), np.pad([in2[0]], (0, S - 1)), diag_opt=False) @ x),
            rmatvec=lambda x: toeplitz(np.pad(in2, (0, S - 1)), np.pad([in2[0]], (0, S - 1)), diag_opt=False).T.conj() @ x if ckernel or 'complex' in x.dtype.str else np.real(toeplitz(np.pad(in2, (0, S - 1)), np.pad([in2[0]], (0, S - 1)), diag_opt=False).T.conj() @ x)
        )
    elif compute == 'lazylinop.toeplitz_for_convolution':
        LO = _ttoeplitz(np.pad(in2, (0, S - 1)), np.pad([in2[0]], (0, S - 1)), K)
    elif compute == 'oa':
        LO = _oaconvolve(in2, 'full', shape=shape)
    elif 'circ.' in compute:
        tmp_compute = compute.replace('circ.', '')
        LO = LazyLinearOp(
            (S, S),
            matvec=lambda x: _circconvolve(in2, tmp_compute, shape=shape) @ x if ckernel or 'complex' in x.dtype.str else np.real(_circconvolve(in2, tmp_compute, shape=shape) @ x),
            rmatvec=lambda x: _circconvolve(in2, tmp_compute, shape=shape).T.conj() @ x if ckernel or 'complex' in x.dtype.str else np.real(_circconvolve(in2, tmp_compute, shape=shape).T.conj() @ x)
        )
    else:
        pass

    # compute full mode and extract what we need
    dim = {}
    dim['full'] = S + K - 1
    dim['valid'] = S - K + 1
    dim['same'] = S
    dim['circ'] = S
    if mode == 'valid' or mode == 'same' or mode == 'circ':
        start = (S + K - 1) // 2 - dim[mode] // 2
        if return_lazylinop:
            return LO[start:(start + dim[mode]), :S]
        else:
            return LO[start:(start + dim[mode]), :S] @ in1
    else:
        if return_lazylinop:
            return LO
        else:
            return LO @ in1

def _circconvolve(kernel: np.ndarray, method: str = 'auto', **kwargs):
    """This function returns circular convolution.
    Length of the signal and length of the kernel must be the same.
    If shape of the signal has been passed return Lazy Linear Operator
    that corresponds to the convolution with the kernel.
    If signal has been passed return the convolution result.
    The function only considers the first dimension of both kernel and signal.

    Args:
        kernel: np.ndarray
        kernel to use for the convolution
        method: str, optional
            'auto' use lazy encapsulation of scipy.fft fft and ifft functions (optimization and benchmark in progress)
            'direct' direct computation using nested for loops (Numba implementation is work-in-progress)
            'scipy.linalg.circulant' use Scipy implementation of the circulant matrix
            'scipy.fft.fft' use Scipy implementation of the FFT
            'pyfaust.circ' use pyfaust implementation of circulant matrix
            'pyfaust.dft' use pyfaust implementation of DFT
        kwargs:
            shape (tuple) of the signal to convolve with kernel
            input_array (np.ndarray) to convolve with kernel, shape is (S, )

    Returns:
        LazyLinearOp or np.ndarray

    Raises:
        Exception
        kernel number of dimensions < 1.
        ValueError
        shape or input_array are expected.
        ValueError
        expect shape or input_array not both.
        ValueError
        method is not in ['auto', 'direct', 'scipy.linalg.circulant', 'scipy.fft.fft', 'pyfaust.circ', 'pyfaust.dft'].
        ValueError
        'scipy.fft.fft' and 'pyfaust.dft' methods expect the size of the signal to be a power of 2.
    """
    if not "shape" in kwargs.keys() and not "input_array" in kwargs.keys():
        raise ValueError("'shape' or 'input_array' are expected")
    if "shape" in kwargs.keys() and "input_array" in kwargs.keys():
        raise ValueError("expect 'shape' or 'input_array' not both")
    if not method in ['auto', 'direct', 'scipy.linalg.circulant', 'scipy.fft.fft', 'pyfaust.circ', 'pyfaust.dft']:
        raise ValueError("method is not in ['auto', 'direct', 'scipy.linalg.circulant', 'scipy.fft.fft', 'pyfaust.circ', 'pyfaust.dft']")

    # check if signal has been passed to the function
    # check if shape of the signal has been passed to the function
    return_lazylinop, B = True, 2
    for key, value in kwargs.items():
        if key == "shape":
            return_lazylinop = True
            shape = value
        elif key == "input_array":
            return_lazylinop = False
            shape = value.shape
        else:
            pass

    # keep only the first dimension of the kernel
    if kernel.ndim == 1:
        kernel1d = np.copy(kernel)
    elif kernel.ndim > 1:
        kernel1d = np.copy(kernel[:1])
    else:
        raise Exception("kernel number of dimensions < 1.")

    # size of the kernel
    K = kernel1d.size
    # size of the signal
    S = shape[0]
    # if K != S:
    #     raise ValueError("size of the kernel differs from the size of the signal.")
    if not _is_power_of_two(S) and (method == 'scipy.fft.fft' or method == 'pyfaust.dft'):
        raise ValueError("'scipy.fft.fft' and 'pyfaust.dft' methods expect the size of the signal to be a power of 2.")
    # size of the output
    O = S
    # pad the kernel
    if method == 'pyfaust.dft':
        P = O
        while not _is_power_of_two(P):
            P += 1
        pkernel = np.pad(kernel, (0, P - K), mode='constant', constant_values=0.0)
    else:
        pkernel = np.pad(kernel, (0, O - K), mode='constant', constant_values=0.0)

    if method == 'direct':
        import numba
        @numba.jit(nopython=True)
        def _matvec(kernel, signal):
            K = kernel.shape[0]
            S = signal.shape[0]
            O = S
            # seq = np.arange(K)
            output = np.full(O, 0.0)
            # y[n] = sum(h[k] * s[n - k mod N], k, 0, K - 1)
            for i in range(O):
                for j in range(K):
                    output[i] += kernel[j] * signal[np.mod(i - j, S)]
            # output = np.array([np.dot(kernel, signal[np.mod(np.subtract(i, seq), S)]) for i in range(O)])
            return output
        @numba.jit(nopython=True)
        def _rmatvec(kernel, signal):
            K = kernel.shape[0]
            S = signal.shape[0]
            O = S
            # seq = np.arange(K)
            output = np.full(O, 0.0)
            # y[n] = sum(h[k] * s[k + n mod N], k, 0, K - 1)
            for i in range(O):
                for j in range(K):
                    output[i] += kernel[j] * signal[np.mod(i + j, S)]
            # output = np.array([np.dot(kernel, signal[np.mod(np.add(seq, i), S)]) for i in range(O)])
            return output
        LO = LazyLinearOp(
            (O, S),
            matvec=lambda x: _matvec(kernel1d, x),
            rmatvec=lambda x: _rmatvec(kernel1d, x)
        )
    elif method == 'scipy.linalg.circulant':
        LO = LazyLinearOp(
            (O, S),
            matvec=lambda x: sp.linalg.circulant(np.pad(kernel, (0, O - K))) @ x,
            rmatvec=lambda x: sp.linalg.circulant(np.pad(kernel, (0, O - K))).T.conj() @ x
        )
    elif method == 'scipy.fft.fft' or method == 'auto':
        # Op @ signal
        # Op = FFT^-1 @ diag(FFT(kernel)) @ FFT
        # Op^H = FFT^H @ diag(FFT(kernel))^H @ (FFT^-1)^H
        # FFT^H equiv FFT^-1
        fft_kernel = sp.fft.fft(pkernel)
        ifft_kernel = sp.fft.ifft(pkernel)
        LO = LazyLinearOp(
            (O, S),
            matvec=lambda x: sp.fft.ifft(fft_kernel * sp.fft.fft(x)) if ckernel or 'complex' in x.dtype.str else np.real(sp.fft.ifft(fft_kernel * sp.fft.fft(x))),
            rmatvec=lambda x: sp.fft.ifft(ifft_kernel * sp.fft.fft(x)) if ckernel or 'complex' in x.dtype.str else np.real(sp.fft.ifft(ifft_kernel * sp.fft.fft(x)))
        )
    elif method == 'pyfaust.circ':
        from pyfaust import circ
        ckernel = True# 'complex' in pkernel.dtype.str
        LO = LazyLinearOp(
            (O, S),
            matvec=lambda x: circ(pkernel) @ x if ckernel or 'complex' in x.dtype.str else np.real(circ(pkernel) @ x),
            rmatvec=lambda x: circ(pkernel).T.conj() @ x if ckernel or 'complex' in x.dtype.str else np.real(circ(pkernel).T.conj() @ x),
        )
    elif method == 'pyfaust.dft':
        from pyfaust import dft
        norm = False
        fft_kernel = dft(P, normed=norm) @ np.multiply(1.0 / P, pkernel)
        ifft_kernel = dft(P, normed=norm).T.conj() @ np.multiply(1.0 / P, pkernel)
        ckernel = True# 'complex' in pkernel.dtype.str
        LO = LazyLinearOp(
            (P, S),
            matvec=lambda x: aslazylinearoperator(dft(P, normed=norm).T.conj()) @ diag(fft_kernel) @ aslazylinearoperator(dft(P, normed=norm)) @ eye(P, n=S, k=0) @ x if ckernel or 'complex' in x.dtype.str else np.real(aslazylinearoperator(dft(P, normed=norm).T.conj()) @ diag(fft_kernel) @ aslazylinearoperator(dft(P, normed=norm)) @ eye(P, n=S, k=0) @ x),
            rmatvec=lambda x: aslazylinearoperator(dft(P, normed=norm).T.conj()) @ diag(ifft_kernel) @ aslazylinearoperator(dft(P, normed=norm)) @ eye(P, n=S, k=0) @ x if ckernel or 'complex' in x.dtype.str else np.real(aslazylinearoperator(dft(P, normed=norm).T.conj()) @ diag(ifft_kernel) @ aslazylinearoperator(dft(P, normed=norm)) @ eye(P, n=S, k=0) @ x)
        )[:O, :]
    else:
        # TODO: auto
        pass

    # convolution
    if return_lazylinop:
        # return lazy linear operator
        # keep the middle of full mode (centered)
        start = O // 2 - S // 2
        return LO[start:(start + S), :]
    else:
        # return result of the convolution
        # keep the middle of full mode (centered)
        start = O // 2 - S // 2
        return (LO @ signal)[start:(start + S)]


def _oaconvolve(kernel: np.ndarray, mode: str = 'full', **kwargs):
    """This function implements overlap-add method for convolution.
    If shape of the signal has been passed return Lazy Linear Operator
    that corresponds to the convolution with the kernel.
    If signal has been passed return the convolution result.
    The function only considers the first dimension of both kernel and signal.

    Args:
        kernel: np.ndarray
        kernel to use for the convolution
        mode: str, optional
            'full' computes convolution (input + padding)
            'valid' computes 'full' mode and extract centered output that does not depend on the padding
            'same' computes 'full' mode and extract centered output that has the same shape that the input
            refer to Scipy documentation of scipy.signal.convolve function for more details
        kwargs:
            shape (tuple) of the signal to convolve with kernel
            input_array (np.ndarray) to convolve with kernel, shape is (S, )
            block_size (int) size of the block unit (a power of two)

    Returns:
        LazyLinearOp or np.ndarray

    Raises:
        Exception
        kernel number of dimensions < 1.
        ValueError
        mode is either 'full' (default), 'valid' or 'same'
        ValueError
        shape or input_array are expected
        ValueError
        expect shape or input_array not both.
        ValueError
        block_size argument expects a value that is a power of two.
        ValueError
        block_size must be greater than the kernel size.
        ValueError
        size of the kernel is greater than the size of the signal.
    """
    if not mode in ['full', 'valid', 'same']:
        raise ValueError("mode is either 'full' (default), 'valid' or 'same'")
    if not "shape" in kwargs.keys() and not "input_array" in kwargs.keys():
        raise ValueError("'shape' or 'input_array' are expected")
    if "shape" in kwargs.keys() and "input_array" in kwargs.keys():
        raise ValueError("expect 'shape' or 'input_array' not both.")

    # check if signal has been passed to the function
    # check if shape of the signal has been passed to the function
    return_lazylinop, B = True, 2
    for key, value in kwargs.items():
        if key == "shape":
            return_lazylinop = True
            shape = value
        elif key == "input_array":
            return_lazylinop = False
            shape = value.shape
        elif key == "block_size":
            B = value
            if B <= 0 or not _is_power_of_two(B):
                raise ValueError("block_size argument expects a value that is a power of two.")
        else:
            pass

    # keep only the first dimension of the kernel
    if kernel.ndim == 1:
        kernel1d = np.copy(kernel)
    elif kernel.ndim > 1:
        kernel1d = np.copy(kernel[:1])
    else:
        raise Exception("kernel number of dimensions < 1.")

    # size of the kernel
    K = kernel1d.size
    # size of the signal
    S = shape[0]
    if K > S:
        raise ValueError("size of the kernel is greater than the size of the signal.")
    # size of the output (full mode)
    O = S + K - 1

    # block size B, number of blocks X=S/B
    if not "block_size" in kwargs.keys():
        # no input for the block size: compute a value
        B = K
        while B < min(S, 2 * K) or not _is_power_of_two(B):
            B += 1
    else:
        if B < K:
            raise ValueError("block_size must be greater or equal to the kernel size.")
    # number of blocks
    R = S % B
    X = (S + R) // B

    # create linear operator LO that will be applied to all the blocks
    # LO = ifft(np.diag(fft(kernel)) @ fft(signal))
    # use Kronecker product between identity matrix and LO to apply to all the blocks
    # use pyfaust_multi_pad to pad each block
    # if the size of the signal is S the size of the result is 2*S
    if False:
        norm = False
        from pyfaust import dft
        fft_kernel = dft(2 * B, normed=norm) @ np.multiply(1.0 if norm else 1.0 / (2 * B), np.pad(kernel1d, ((0, 2 * B - K))))
        LO = overlap_add(B, 2 * X) @ kron(
            eye(X, n=X, k=0),
            aslazylinearoperator(dft(2 * B, normed=norm).T.conj()) @ diag(
                fft_kernel, k=0
            ) @ aslazylinearoperator(
                dft(2 * B, normed=norm)
            ) @ eye(2 * B, n=B, k=0),
            use_pylops=True
        )
    else:
        def lazy_fft(N: int):
            LLOp = LazyLinearOp(
                (N, N),
                matvec=lambda x: sp.fft.fft(x),
                rmatvec=lambda x: np.multiply(N, sp.fft.ifft(x))
            )
            return LLOp
        fft_kernel = np.multiply(1.0 / (2 * B), lazy_fft(2 * B) @ eye(2 * B, n=K, k=0) @ kernel1d)
        LO = overlap_add(B, 2 * X) @ kron(
            eye(X, n=X, k=0),
            lazy_fft(2 * B).H @ diag(fft_kernel, k=0) @ lazy_fft(2 * B),
            use_pylops=True
        ) @ multi_pad(B, X)

    is_complex = True#'complex' in kernel1d.dtype.str or (not return_lazylinop and 'complex' in signal.dtype.str)

    # convolution
    if return_lazylinop:
        # return lazy linear operator
        if mode == 'valid' or mode == 'same':
            if mode == 'valid':
                # compute full mode and extract what we need
                extract = S - K + 1
            else:
                # keep the middle of full mode (centered)
                extract = S
            start = O // 2 - extract // 2
            return LazyLinearOp(
                (extract, S),
                matvec=lambda x: LO[start:(start + extract), :] @ x if is_complex else np.real(LO[start:(start + extract), :] @ x),
                rmatvec=lambda x: LO[start:(start + extract), :].T.conj() @ x if is_complex else np.real(LO[start:(start + extract), :].T.conj() @ x)
            )
        else:
            # compute full mode
            return LazyLinearOp(
                (O, S),
                matvec=lambda x: LO[:O, :] @ x if is_complex else np.real(LO[:O, :] @ x),
                rmatvec=lambda x: LO[:O, :].T.conj() @ x if is_complex else np.real(LO[:O, :].T.conj() @ x)
            )
    else:
        # return result of the convolution
        psignal = np.pad(signal, ((0, R)))
        if mode == 'valid' or mode == 'same':
            if mode == 'valid':
                # compute full mode and extract what we need
                extract = S - K + 1
            else:
                # keep the middle of full mode (centered)
                extract = S
            start = O // 2 - extract // 2
            return (LO @ psignal)[start:(start + extract)] if is_complex else np.real((LO @ psignal)[start:(start + extract)])
        else:
            # compute full mode
            return (LO @ psignal)[:O] if is_complex else np.real((LO @ psignal)[:O])


def multi_pad(L: int, X: int, signal = None):
    """return a lazy linear operator or np.ndarray mp to pad each block of a signal.
    If you apply this operator to a vector of length L * X the output will have a length 2 * L * X.

    Args:
        L: int, block size
        X: int, number of blocks
        signal: np.ndarray, optional
        if signal is numpy array apply overlap-add linear operator (default is None).

    Returns:
        LazyLinearOp or np.ndarray

    Examples:
        >>> #from lazylinop.wip.signal import multi_pad
        >>> import numpy as np
        >>> signal = np.full(5, 1.0)
        >>> signal
        array([1., 1., 1., 1., 1.])
        >>> y = multi_pad(1, 5) @ signal
        >>> y
        array([1., 0., 1., 0., 1., 0., 1., 0., 1., 0.])
    """
    mp = np.zeros((2 * X, X))
    indices = np.arange(0, 2 * X, 2)
    mp[indices, np.floor_divide(indices, 2)] = 1
    if type(signal) is np.ndarray:
        return kron(mp, eye(L, n=L, k=0), use_pylops=True) @ signal
    else:
        return kron(mp, eye(L, n=L, k=0), use_pylops=True)


def overlap_add(L: int, X: int, signal = None):
    """return overlap-add linear operator or result of the overlap-add.
    If signal is a numpy array return the result of the matrix-vector product.
    The overlap-add linear operator adds block i > 0 (of size L) with
    block i + 1 (of size L). Of note, block i = 0 (of size L) does not change.

    Args:
        L: int
        block size
        X: int
        number of blocks
        signal: np.ndarray, optional
        if signal is numpy array apply overlap-add linear operator (default is None).

    Returns:
        LazyLinearOp or np.ndarray

    Raises:
        ValueError
        L is strictly positive.
        ValueError
        X is strictly positive.
        ValueError
        number of columns of the linear operator is not equal to the size of the signal.

    Examples:
        >>> #from lazylinop.wip.signal import overlap_add
        >>> import numpy as np
        >>> signal = np.full(16, 1.0)
        >>> oa1 = overlap_add(1, 16, None) @ signal
        >>> oa2 = overlap_add(1, 16, signal)
        >>> np.allclose(oa1, oa2)
        True
        >>> oa1
        array([1., 2., 2., 2., 2., 2., 2., 2., 1., 0., 0., 0., 0., 0., 0., 0.])
        >>> oa1 = overlap_add(2, 8, None) @ signal
        >>> oa2 = overlap_add(2, 8, signal)
        >>> np.allclose(oa1, oa2)
        True
        >>> oa1
        array([1., 1., 2., 2., 2., 2., 2., 2., 1., 1., 0., 0., 0., 0., 0., 0.])
    """
    if L <= 0:
        raise ValueError("L is strictly positive.")
    if X <= 0:
        raise ValueError("X is strictly positive.")
    if (X % 2) != 0:
        raise ValueError("number of blocks is not a multiple of 2.")
    if type(signal) is np.ndarray and (X * L) != signal.size:
        raise ValueError("L * X is not equal to the size of the signal.")
    def _matmat(x, L, X):
        rnz = X // 2 + 1
        if x.ndim == 1:
            x_is_1d = True
            y = np.reshape(x, newshape=(x.size, 1))
        else:
            x_is_1d = False
            y = np.copy(x)
        mv = np.full((X, y.shape[1]), 0.0, dtype=y.dtype)
        mv[0, :] = y[0, :]
        # for i in range(1, rnz - 1):
        #     mv[i, :] = y[2 * (i - 1) + 1, :] + y[2 * (i - 1) + 2, :]
        indices = np.arange(1, rnz - 1, 1)
        mv[indices, :] = y[2 * indices - 1, :] + y[2 * indices, :]
        mv[rnz - 1, :] = y[2 * ((rnz - 1) - 1) + 1, :]
        if x_is_1d:
            return mv.ravel()
        else:
            return mv
    if type(signal) is np.ndarray:
        rnz = X // 2 + 1
        oa = np.full((X, X), 0.0)
        oa[0, 0] = 1
        indices = np.arange(1, rnz - 1, 1)
        oa[indices, 2 * indices - 1] = 1
        oa[indices, 2 * indices] = 1
        oa[rnz - 1, 2 * ((rnz - 1) - 1) + 1] = 1
        return aslazylinearoperator(
            kron(
                oa,
                eye(L, n=L, k=0),
                use_pylops=True
            )
        ) @ signal
    else:
        return aslazylinearoperator(
            kron(
                LazyLinearOp(
                    (X, X),
                    matmat=lambda x: _matmat(x, L, X),
                    rmatmat=lambda x: _matmat(x, L, X).T.conj()
                ),
                eye(L, n=L, k=0),
                use_pylops=True
            )
        )

if __name__ == '__main__':
    import doctest
    doctest.testmod()
