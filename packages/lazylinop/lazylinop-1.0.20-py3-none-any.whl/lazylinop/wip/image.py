"""
Module for image processing related LazyLinearOps (work in progress).
"""
import numpy as np
import scipy as sp
from lazylinop import *
from lazylinop.wip.signal import convolve, decimate


_disable_numba = True

def _fconvolve2d(shape: tuple, in2: np.ndarray, backend: str = 'full_scipy'):
    """
    Constructs a lazy linear operator to convolve a kernel and an image of shape (X, Y).

    Args:
        shape: tuple
            the shape of the signal this operator will convolves.
        in2: np.ndarray
             the kernel to convolve.
        backend: str, optional
            'pyfaust' or 'scipy' to use lazylinop.fft2(backend='scipy') or 'full_scipy' to use scipy.signal.convolve2d.

    Returns:
        The LazyLinearOperator for the 2D convolution.

    Example:
        >>> import numpy as np
        >>> #from lazylinop.wip.signal import convolve2d
        >>> from scipy.signal import convolve2d as sconvolve2d
        >>> X =  np.random.rand(64, 64)
        >>> K = np.random.rand(4, 4)
        >>> C1 = convolve2d(X.shape, K, backend='scipy')
        >>> C2 = convolve2d(X.shape, K, backend='pyfaust')
        >>> C3 = convolve2d(X.shape, K, backend='full_scipy')
        >>> np.allclose((C1 @ X.ravel()).reshape(64, 64), sconvolve2d(X, K, 'same'))
        True
        >>> np.allclose((C2 @ X.ravel()).reshape(64, 64), sconvolve2d(X, K, 'same'))
        True
        >>> np.allclose((C3 @ X.ravel()).reshape(64, 64), sconvolve2d(X, K, 'same'))
        True

    """
    X, Y = shape[0], shape[1]
    K, L = in2.shape
    P, Q = X + K - 1, Y + L - 1

    if backend == 'full_scipy':
        from scipy.signal import convolve2d as sconvolve2d, correlate2d
        return LazyLinearOperator(
            shape=(P * Q, X * Y),
            matvec=lambda x: sconvolve2d(x.reshape(shape), in2, mode).ravel(),
            rmatvec=lambda x: correlate2d(x.reshape(shape), in2, mode).ravel()
        )
    else:
        if backend == 'pyfaust':
            from lazylinop.wip.signal import fft2
            F = fft2((P, Q), backend=backend, normed=True, diag_opt=True)
        elif backend == 'scipy':
            from lazylinop.wip.signal import fft2
            F = fft2((P, Q), backend=backend, norm='ortho')
        else:
            raise ValueError('Unknown backend')

        ckernel = 'complex' in in2.dtype.str

        # operator to pad the flattened image
        # scipy.signal.convolve2d adds 0 only on one side along both axis
        x1 = 0#(P - X) // 2
        x2 = P - X - x1
        y1 = 0#(Q - Y) // 2
        y2 = Q - Y - y1
        P1 = pad((X, Y), ((x1, x2), (y1, y2)))

        # operator to pad the flattened kernel
        # scipy.signal.convolve2d adds 0 only on one side along both axis
        x1 = 0#(P - K) // 2
        x2 = P - K - x1
        y1 = 0#(Q - L) // 2
        y2 = Q - L - y1
        P2 = pad((K, L), ((x1, x2), (y1, y2)))

        # Fin2 = np.multiply(1.0 / np.sqrt(P * Q), F @ P2 @ in2.flatten())
        Fin2 = np.multiply(np.sqrt(P * Q), F @ P2 @ in2.flatten())
        # Fin2 = F @ P2 @ in2.flatten()

        return LazyLinearOperator(
            shape = (P * Q, X * Y),
            matvec=lambda x: F.H @ (diag(Fin2, k=0) @ F) @ P1 @ x if ckernel else np.real(F.H @ (diag(Fin2, k=0) @ F) @ P1 @ x),
            # rmatvec=lambda x: (F.H @ (diag(Fin2, k=0) @ F) @ P1).H @ x if ckernel else np.real((F.H @ (diag(Fin2, k=0) @ F) @ P1).H @ x)
            rmatvec=lambda x: (P1.H @ (F.H @ diag(Fin2, k=0).H) @ F) @ x if ckernel else np.real((P1.H @ (F.H @ diag(Fin2, k=0).H) @ F) @ x)
        )


def _is_power_of_two(n: int) -> bool:
    """return True if integer 'n' is a power of two.

    Args:
        n: int

    Returns:
        bool
    """
    return ((n & (n - 1)) == 0) and n > 0


def bc(shape: tuple, n: int=1, boundary: str='periodic'):
    """Constructs a periodic or symmetric boundary condition lazy linear operator.
    It will be applied to a flattened image.
    It basically add image on bottom, left, top and right side.

    Args:
        shape: tuple
        shape of the image
        n: int, optional
        2 * n + 1 is the number of image along both axis.
        boundary: str, optional
        wrap/periodic (default) or symm/symmetric boundary condition

    Returns:
        LazyLinearOperator

    Raises:
        ValueError
            shape expects tuple (R, C).
        ValueError
            boundary excepts 'wrap', 'periodic', 'symm' or 'symmetric'.

    Examples:
    """
    if len(shape) != 2:
        raise ValueError("shape expects tuple (R, C).")

    # apply boundary condition and get X images
    X = 2 * n + 1

    if 'wrap' in boundary or boundary == 'periodic':
        # periodic boundary condition
        # work on rows and columns
        # use Kronecker product
        A1 = np.full((X, 1), 1.0)
        K1 = kron(A1, eye(shape[0], n=shape[0], k=0), use_pylops=True)
        A2 = np.full((1, X), 1.0)
        K2 = kron(A2, eye(shape[1], n=shape[1], k=0), use_pylops=True)
        # kron(K1, K2)^T = kron(K1^T, K2^T)
        # K1^T = kron(A1, E1)^T = kron(A1^T, E1^T)
        # K2^T = kron(A2, E2)^T = kron(A2^T, E2^T)
        return kron(K1, K2.T, use_pylops=True)
    elif 'symm' in boundary or boundary == 'symmetric':
        from lazylinop.wip.signal import flip
        # flip along rows and columns
        # use Kronecker product
        # rows
        A1 = np.full((X, 1), 1.0)
        K1 = kron(A1, eye(shape[0], n=shape[0], k=0), use_pylops=True)
        # flip one image every two images
        # do not flip image at the center
        for i in range(0, (X - 1) // 2, 2):
            K1 = flip(K1.shape, (n - 1 - i) * shape[0], (n - i) * shape[0]) @ K1
            K1 = flip(K1.shape, (n + 1 + i) * shape[0], (n + 2 + i) * shape[0]) @ K1
        # columns
        A2 = np.full((X, 1), 1.0)
        K2 = kron(A2, eye(shape[1], n=shape[1], k=0), use_pylops=True)
        # flip one image every two images
        # do not flip image at the center
        for i in range(0, (X - 1) // 2, 2):
            K2 = flip(K2.shape, (n - 1 - i) * shape[1], (n - i) * shape[1]) @ K2
            K2 = flip(K2.shape, (n + 1 + i) * shape[1], (n + 2 + i) * shape[1]) @ K2
            # K2 = flip(K2.shape, 0, None) @ K2
            # K2 = flip(K2.shape, 0, None) @ K2
        return kron(K1, K2, use_pylops=True)
    else:
        raise ValueError("boundary excepts either 'wrap', 'periodic', 'symm' or 'symmetric'.")


def dwt2d(shape: tuple, hfilter: np.ndarray, lfilter: np.ndarray, boundary: str = 'zero', level: int = None) -> list:
    """Constructs a multiple levels DWT lazy linear operator.

    Args:
        shape: tuple
        shape of the input array (X, Y)
        hfilter: np.ndarray
        quadratic mirror high-pass filter
        lfilter: np.ndarray
        quadratic mirror low-pass filter
        boundary: str, optional
        'zero', signal is padded with zeros (default)
        'periodic', image is treated as periodic image
        'symmetric', use mirroring to pad the signal
        see Pywavelets documentation for more details
        level: int, optional
        if level is None compute full decomposition (default)

    Returns:
        LazyLinearOperator

    Raises:
        Exception
            shape expects tuple.
        ValueError
            decomposition level must greater or equal to 1.
        ValueError
            decomposition level is greater than the maximum decomposition level.
        ValueError
            boundary is either 'zero', 'periodic' or 'symmetric'.

    References:
        See also `Pywavelets module <https://pywavelets.readthedocs.io/en/latest/ref/2d-dwt-and-idwt.html#ref-dwt2>`_
    """
    if not type(shape) is tuple:
        raise ValueError("shape expects tuple.")
    if not level is None and level < 1:
        raise ValueError("decomposition level must be greater or equal to 1.")
    
    # image has been flattened (with img.flatten(order='C'))
    # the result is vec = (row1, row2, ..., rowR) with size = X * Y
    # number of rows, columns
    X, Y = shape[0], shape[1]
    XY = X * Y
    # because of the decomposition the size
    # of the input has to be a power of 2
    # compute maximum decomposition level
    bufferX, bufferY = X, Y
    K = 0
    while (bufferX % 2) == 0 and (bufferY % 2) == 0:
        bufferX, bufferY = bufferX // 2, bufferY // 2
        K += 1
    if not level is None and level > K:
        raise ValueError("decomposition level is greater than the maximum decomposition level.")
    D = K if level < 1 else min(K, level)

    # boundary condition
    if boundary == 'zero':
        B = 1
        A = eye(XY, n=XY, k = 0)
    elif boundary == 'periodic':
        # add (B - 1) / 2 images on both sides
        B = 3
        A = bc((X, Y), n=(B - 1) // 2, boundary=boundary)
    elif boundary == 'symmetric':
        # add (B - 1) / 2 images on both sides
        B = 5
        A = bc((X, Y), n=(B - 1) // 2, boundary=boundary)
    else:
        raise ValueError("boundary is either 'zero', 'periodic' or 'symmetric'.")

    # loop over the decomposition level
    Xs, Ys = [B * X], [B * Y]
    for i in range(D):
        # low and high-pass filters + decimation
        # first work on the row ...
        # ... and then work on the column (use Kronecker product vec trick)
        GCx = convolve((Xs[i], ), lfilter, mode='same', method='lazy.scipy.signal.convolve')
        GCy = convolve((Ys[i], ), lfilter, mode='same', method='lazy.scipy.signal.convolve')
        HCx = convolve((Xs[i], ), hfilter, mode='same', method='lazy.scipy.signal.convolve')
        HCy = convolve((Ys[i], ), hfilter, mode='same', method='lazy.scipy.signal.convolve')
        Dx_Op = decimate(GCx.shape, 1, None, 2)
        Dy_Op = decimate(GCy.shape, 1, None, 2)
        # vertical stack
        GHx = vstack((Dx_Op @ GCx, Dx_Op @ HCx))
        GHy = vstack((Dy_Op @ GCy, Dy_Op @ HCy))
        # because we work on the rows and then on the columns we can write a Kronecker product that will be applied to the flatten image
        KGH = kron(GHx, GHy, use_pylops=True)
        # extract four sub-images
        # -------
        # |LL|HL|
        # -------
        # |LH|HH|
        # -------
        xy = (2 * Xs[i], 1)
        tmp_eye = eye(Ys[i] // 2, n=Ys[i] // 2, k=0)
        LL = kron(decimate(xy, 0, Xs[i], 2), tmp_eye, use_pylops=True)
        LH = kron(decimate(xy, 1, Xs[i], 2), tmp_eye, use_pylops=True)
        HL = kron(decimate(xy, Xs[i], 2 * Xs[i], 2), tmp_eye, use_pylops=True)
        HH = kron(decimate(xy, Xs[i] + 1, 2 * Xs[i], 2), tmp_eye, use_pylops=True)
        # vertical stack where LL is the first lazy linear operator
        # ----
        # |LL|
        # ----
        # |HL|
        # ----
        # |LH|
        # ----
        # |HH|
        # ----
        # V = eye(KGH.shape[0], n=KGH.shape[0], k=0)
        V = vstack((vstack((LL, HL)), vstack((LH, HH))))
        if i == 0:
            # first level of decomposition
            A = V @ KGH @ A
        else:
            # apply low and high-pass filters + decimation only to LL
            # because of lazy linear operator V, LL always comes first
            tmp_eye = eye(B ** 2 * XY - V.shape[0], n=(B ** 2 * XY - KGH.shape[1]), k=0)
            A = block_diag(*[V @ KGH, tmp_eye]) @ A
        Xs.append(Xs[i] // 2)
        Ys.append(Ys[i] // 2)
    return A


def dwt2d_coeffs(shape: tuple, in1: np.ndarray, boundary: str = 'zero', level: int = None) -> list:
    """Returns approximation, horizontal, vertical and details coefficients of 2d Discrete-Wavelet-Transform.

    Args:
        shape: tuple
        shape of the image (X, Y)
        in1: np.ndarray
        result of dwt2d @ image.flatten()
        boundary: str, optional
        'zero', signal is padded with zeros (default)
        'periodic', image is treated as periodic image
        'symmetric', use mirroring to pad the signal
        see Pywavelets documentation for more details
        level: int, optional
        if level is None compute full decomposition (default)

    Returns:
        [cAn, (cHn, cVn, cDn), ..., (cH1, cV1, cD1)]: list
        approximation, horizontal, vertical and detail coefficients, it follows Pywavelets format.

    Raises:
        Exception
            shape expects tuple (X, Y).
        Exception
            in1 expects np.ndarray.
        ValueError
            decomposition level must greater or equal to 1.
        ValueError
            decomposition level is greater than the maximum decomposition level.
        ValueError
            boundary is either 'zero', 'periodic' or 'symmetric'.

    References:
        See also `Pywavelets module <https://pywavelets.readthedocs.io/en/latest/ref/2d-dwt-and-idwt.html#ref-dwt2>`_
    """
    if not type(shape) is tuple:
        raise Exception("shape expects tuple (X, Y).")
    if not type(in1) is np.ndarray:
        raise Exception("in1 expects np.ndarray.")
    if not level is None and level < 1:
        raise ValueError("decomposition level must be greater or equal to 1.")

    # image has been flattened (with img.flatten(order='C'))
    # the result is vec = (row1, row2, ..., rowR) with size = X * Y
    # number of rows, columns
    X, Y = shape[0], shape[1]
    XY = X * Y
    # because of the decomposition the size
    # of the input has to be a power of 2
    # compute maximum decomposition level
    bufferX, bufferY = X, Y
    K = 0
    while (bufferX % 2) == 0 and (bufferY % 2) == 0:
        bufferX, bufferY = bufferX // 2, bufferY // 2
        K += 1
    if not level is None and level > K:
        raise ValueError("decomposition level is greater than the maximum decomposition level.")
    D = K if level is None else level

    # boundary condition
    if boundary == 'zero':
        B = 1
    elif boundary == 'periodic':
        B = 3
    elif boundary == 'symmetric':
        B = 5
    else:
        raise ValueError("boundary is either 'zero', 'periodic' or 'symmetric'.")

    # np.set_printoptions(edgeitems=10, linewidth=300)
    # print(in1.reshape(B * X, B * Y))
    for i in range(level, 0, -1):
        L = np.power(2, i)
        xx, yy = X // L, Y // L
        iLL = np.arange(yy)
        for j in range(xx - 1):
            iLL = np.append(iLL, np.arange((j + 1) * B * yy, (j + 1) * B * yy + yy))
        iHL = np.add(iLL, B ** 2 * xx * yy)
        iLH = np.add(iHL, B ** 2 * xx * yy)
        iHH = np.add(iLH, B ** 2 * xx * yy)
        if i == level:
            cAHVD = [in1[iLL].reshape(xx, yy)]
        cAHVD.append(
            (
                in1[iHL].reshape(xx, yy),
                in1[iLH].reshape(xx, yy),
                in1[iHH].reshape(xx, yy)
            )
        )
    return cAHVD


def convolve2d(in1, in2: np.ndarray, mode: str = 'full', boundary: str = 'fill', method: str = 'fft'):
    """Constructs a 2d convolution lazy linear operator.
    If shape of the image has been passed return Lazy Linear Operator.
    If image has been passed return the convolution result.
    Toeplitz based method use the fact that convolution of a kernel with an image
    can be written as a sum of Kronecker product between eye and Toeplitz matrices.

    Args:
        in1: tuple or np.ndarray,
             shape (tuple) of the signal to convolve with kernel.
             input_array (np.ndarray) to convolve with kernel, shape is (X, Y)
        in2: np.ndarray
            kernel to use for the convolution, shape is (K, L)
        mode: str, optional
            'full' computes convolution (input + padding)
            'valid' computes 'full' mode and extract centered output that does not depend on the padding. 
            'same' computes 'full' mode and extract centered output that has the same shape that the input.
            see also Scipy documentation of scipy.signal.convolve function for more details
        boundary: str, optional
            'fill' pads input array with zeros (default)
            'wrap' periodic boundary conditions
            'symm' symmetrical boundary conditions
            see also Scipy documentation of scipy.signal.convolve2d function
        method: str, optional
             'auto' use FFT method (benchmark and optimization work-in-progress)
             'scipy.linalg.toeplitz' to use lazy encapsulation of Scipy implementation of Toeplitz matrix
             'pyfaust.toeplitz' to use pyfaust implementation of Toeplitz matrix
             'lazylinop.toeplitz_for_convolution' to use Toeplitz for convolution optimization
             'fft' to use Fast-Fourier-Transform to compute convolution

    Returns:
        LazyLinearOperator or np.ndarray

    Raises:
        ValueError
        number of dimensions of the signal and/or the kernel is greater than one.
        ValueError
        mode is either 'full' (default), 'valid' or 'same'
        ValueError
        boundary is either 'fill' (default), 'wrap' or 'symm'
        ValueError
        size of the kernel is greater than the size of signal.
        ValueError
        method is not in:
             'auto',
             'scipy.linalg.toeplitz',
             'pyfaust.toeplitz',
             'lazylinop.toeplitz_for_convolution',
             'fft'
        Exception
            in1 expects tuple as (X, Y).
        Exception
            in1 expects array with shape (X, Y).
        ValueError
            negative dimension value is not allowed.

    Examples:
        >>> from lazylinop.wip.image import convolve2d
        >>> import scipy as sp
        >>> image = np.random.rand(6, 6)
        >>> kernel = np.random.rand(3, 3)
        >>> c1 = convolve2d(image, kernel, mode='same', boundary='fill', method='scipy.linalg.toeplitz')
        >>> c2 = convolve2d(image, kernel, mode='same', boundary='fill', method='pyfaust.toeplitz')
        >>> c3 = convolve2d(image.shape, kernel, mode='same', boundary='fill', method='lazylinop.toeplitz_for_convolution') @ image.flatten()
        >>> c4 = sp.signal.convolve2d(image, kernel, mode='same', boundary='fill')
        >>> np.allclose(c1, c2)
        True
        >>> np.allclose(c2, c3)
        True
        >>> np.allclose(c3, c4)
        True

    References:
        See also `scipy.signal.convolve2d <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.convolve2d.html>`_
    """
    if not mode in ['full', 'valid', 'same']:
        raise ValueError("mode is either 'full' (default), 'valid' or 'same'")
    if not boundary in ['fill', 'wrap', 'symm']:
        raise ValueError("boundary is either 'fill' (default), 'wrap' or 'symm'")
    if not method in ['auto', 'direct', 'scipy.linalg.toeplitz', 'pyfaust.toeplitz', 'lazylinop.toeplitz_for_convolution', 'fft']:
        raise ValueError("method is not in ['auto', 'direct', 'scipy.linalg.toeplitz', 'pyfaust.toeplitz', 'lazylinop.toeplitz_for_convolution', 'fft'].")

    # check if image has been passed to the function
    # check if shape of the image has been passed to the function
    return_lazylinop = type(in1) is tuple

    if type(in1) is tuple:
        return_laylinop = True
        if len(in1) != 2:
            raise Exception("in1 expects tuple (X, Y).")
        X, Y = in1[0], in1[1]
    else:
        return_lazylinop = False
        if len(in1.shape) != 2:
            raise Exception("in1 expects array with shape (X, Y).")
        X, Y = in1.shape

    if X <= 0 or Y <= 0:
        raise ValueError("zero or negative dimension is not allowed.")
    K, L = in2.shape
    if K > X or L > Y:
        raise ValueError("size of the kernel is greater than the size of the image.")
    if X <= 0 or Y <= 0 or K <= 0 or L <= 0:
        raise ValueError("negative dimension value is not allowed.")

    # boundary conditions
    if boundary == 'fill':
        B = 1
    else:
        B = 3

    # shape of the output image (full mode)
    # it takes into account the boundary conditions
    P, Q = B * X + K - 1, B * Y + L - 1

    if method == 'fft' or method == 'auto':
        LLOps = [_fconvolve2d(np.multiply(B, np.array(in1)), in2, backend='scipy')]
    else:
        # write 2d convolution as a sum of Kronecker products:
        # image * kernel = sum(kron(E_i, T_i), i, 1, M)
        # E_i is an eye matrix eye(P, n=X, k=-i).
        # T_i is a Toeplitz matrix build from the kernel.
        # first column is the i-th row of the kernel.
        # first row is 0
        LLOps = [None] * K
        for i in range(K):
            # does it need Toeplitz construction because it looks like an eye matrix ?
            if method == 'pyfaust.toeplitz':
                from pyfaust import toeplitz
                LLOps[i] = kron(eye(P, n=B * X, k=-i), toeplitz(np.pad(in2[i, :], (0, B * Y - 1)), np.pad([in2[i, 0]], (0, B * Y - 1)), diag_opt=True), use_pylops=True)
            elif method == 'lazylinop.toeplitz_for_convolution':
                from lazylinop.wip.signal import _ttoeplitz
                LLOps[i] = kron(eye(P, n=B * X, k=-i), _ttoeplitz(np.pad(in2[i, :], (0, B * Y - 1)), np.full(B * Y, 0.0), K), use_pylops=True)
            else:
                # default
                LLOps[i] = kron(eye(P, n=B * X, k=-i), sp.linalg.toeplitz(np.pad(in2[i, :], (0, B * Y - 1)), np.full(B * Y, 0.0)), use_pylops=True)

    # return lazy linear operator or the convolution result
    mt, af = False, False
    if return_lazylinop:
        if mode == 'valid' or mode == 'same':
            if mode == 'valid':
                # compute full mode and extract what we need
                # number of rows to extract is X - K + 1 (centered)
                # number of columns to extract is Y - L + 1 (centered)
                # if boundary conditions extract image from the center
                i1 = (P - (X - K + 1)) // 2
                s1 = i1 + X - K + 1
                i2 = (Q - (Y - L + 1)) // 2
                s2 = i2 + Y - L + 1
                indices = ((np.arange(P * Q).reshape(P, Q))[i1:s1, i2:s2]).ravel()
            else:
                # keep middle of the full mode
                # number of rows to extract is M (centered)
                # number of columns to extract is N (centered)
                # if boundary conditions extract image from the center
                i1 = (P - X) // 2
                s1 = i1 + X
                i2 = (Q - Y) // 2
                s2 = i2 + Y
                indices = ((np.arange(P * Q).reshape(P, Q))[i1:s1, i2:s2]).ravel()
            if B > 1:
                return (sum(*LLOps, mt=mt, af=af) @ bc((X, Y), n=1, boundary=boundary))[indices, :]
            else:
                return sum(*LLOps, mt=mt, af=af)[indices, :]
        else:
            # return full mode
            if B > 1:
                # if boundary conditions extract image from the center
                i1 = (P - (X + K - 1)) // 2
                s1 = i1 + X + K - 1
                i2 = (Q - (Y + L - 1)) // 2
                s2 = i2 + Y + L - 1
                indices = ((np.arange(P * Q).reshape(P, Q))[i1:s1, i2:s2]).ravel()
                return (sum(*LLOps, mt=mt, af=af) @ bc((X, Y), n=1, boundary=boundary))[indices, :]
            else:
                return sum(*LLOps, mt=mt, af=af)
    else:
        # return result of the 2D convolution
        if mode == 'valid' or mode == 'same':
            if mode == 'valid':
                # compute full mode result and extract what we need
                # number of rows to extract is X - K + 1
                # number of columns to extract is Y - K + 1
                i1 = (P - (X - K + 1)) // 2
                s1 = i1 + X - K + 1
                i2 = (Q - (Y - L + 1)) // 2
                s2 = i2 + Y - L + 1
            else:
                # keep middle of the full mode result
                # number of rows to extract is X
                # number of colums to extract is Y
                # centered
                i1 = (P - X) // 2
                s1 = i1 + X
                i2 = (Q - Y) // 2
                s2 = i2 + Y
            return ((sum(*LLOps) @ in1.flatten()).reshape(P, Q))[i1:s1, i2:s2]
        else:
            # compute full mode
            if B > 1:
                # if boundary conditions extract image from the center
                i1 = (P - (X + K - 1)) // 2
                s1 = i1 + X + K - 1
                i2 = (Q - (Y + L - 1)) // 2
                s2 = i2 + Y + L - 1
                return ((sum(*LLOps) @ in1.flatten()).reshape(P, Q))[i1:s1, i2:s2]
            else:
                return (sum(*LLOps) @ in1.flatten()).reshape(P, Q)


def pad(shape: tuple, pad_width: tuple):
    """Constructs a lazy linear operator Op for padding.
    Op is applied to a flattened image.
    The output of the padding of the image is given by Op @ image.flatten(order='C').
    The function uses Kronecker trick vec(M @ X @ N) = kron(M.T, N) @ vec(X).

    Args:
        shape: tuple
        shape of the image
        pad_width: tuple
        It can be (A, B):
        Add A zero columns and rows before and B zero columns and rows after.
        or ((A, B), (C, D)):
        Add A zero rows before and B zero rows after.
        Add C zero columns to the left and D zero columns to the right.

    Returns:
        LazyLinearOperator

    Raises:
        ValueError
            pad_width expects (A, B) or ((A, B), (C, D)).
        ValueError
            pad_width expects positive values.

    Examples:
        >>> from lazylinop.wip.image import pad
        >>> x = np.arange(1, 4 + 1, 1).reshape(2, 2)
        >>> x
        array([[1, 2],
               [3, 4]])
        >>> y = pad(x.shape, (1, 2)) @ x.flatten()
        >>> y.reshape(5, 5)
        array([[0., 0., 0., 0., 0.],
               [0., 1., 2., 0., 0.],
               [0., 3., 4., 0., 0.],
               [0., 0., 0., 0., 0.],
               [0., 0., 0., 0., 0.]])
        >>> x = np.arange(1, 6 + 1, 1).reshape(2, 3)
        >>> x
        array([[1, 2, 3],
               [4, 5, 6]])
        >>> y = pad(x.shape, ((2, 1), (2, 3))) @ x.flatten()
        >>> y.reshape(5, 8)
        array([[0., 0., 0., 0., 0., 0., 0., 0.],
               [0., 0., 0., 0., 0., 0., 0., 0.],
               [0., 0., 1., 2., 3., 0., 0., 0.],
               [0., 0., 4., 5., 6., 0., 0., 0.],
               [0., 0., 0., 0., 0., 0., 0., 0.]])

    References:
        See also `numpy.pad <https://numpy.org/doc/stable/reference/generated/numpy.pad.html>`_
    """
    W = len(pad_width)
    if W != 2:
        raise ValueError("pad_width expects (A, B) or ((A, B), (C, D)).")
    if type(pad_width[0]) is tuple:
        # pad_witdh is ((A, B), (C, D))
        for w in range(W):
            if pad_width[w][0] < 0 or pad_width[w][1] < 0:
                raise ValueError("pad_width expects positive values.")
            Ww = len(pad_width[w])
            if Ww != 2:
                raise ValueError("pad_width expects (A, B) or ((A, B), (C, D)).")
            if w == 0:
                M = eye(shape[0] + pad_width[w][0] + pad_width[w][1], n=shape[0], k=-pad_width[w][0])
            elif w == 1:
                # N = eye(shape[1], n=shape[1] + pad_width[w][0] + pad_width[w][1], k=pad_width[w][0])
                NT = eye(shape[1] + pad_width[w][0] + pad_width[w][1], n=shape[1], k=-pad_width[w][0])
        Op = kron(M, NT, use_pylops=True)
        return Op
    else:
        if pad_width[0] < 0 or pad_width[1] < 0:
            raise ValueError("pad_width expects positive values.")
        # pad_witdh is (A, B), pad each dimension
        M = eye(shape[0] + pad_width[0] + pad_width[1], n=shape[0], k=-pad_width[0])
        # N = eye(shape[1], n=shape[1] + pad_width[0] + pad_width[1], k=pad_width[0])
        NT = eye(shape[1] + pad_width[0] + pad_width[1], n=shape[1], k=-pad_width[0])
        Op = kron(M, NT, use_pylops=True)
        return Op

        
