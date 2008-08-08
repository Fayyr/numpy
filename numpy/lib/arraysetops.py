"""
Set operations for 1D numeric arrays based on sorting.

:Contains:
  ediff1d,
  unique1d,
  intersect1d,
  intersect1d_nu,
  setxor1d,
  setmember1d,
  union1d,
  setdiff1d

:Notes:

All functions work best with integer numerical arrays on input (e.g. indices).
For floating point arrays, innacurate results may appear due to usual round-off
and floating point comparison issues.

Except unique1d, union1d and intersect1d_nu, all functions expect inputs with
unique elements. Speed could be gained in some operations by an implementaion of
sort(), that can provide directly the permutation vectors, avoiding thus calls
to argsort().

Run _test_unique1d_speed() to compare performance of numpy.unique1d() and
numpy.unique() - it should be the same.

To do: Optionally return indices analogously to unique1d for all functions.

created:       01.11.2005
last revision: 07.01.2007

:Author: Robert Cimrman
"""
__all__ = ['ediff1d', 'unique1d', 'intersect1d', 'intersect1d_nu', 'setxor1d',
           'setmember1d', 'union1d', 'setdiff1d']

import time
import numpy as np

def ediff1d(ary, to_end=None, to_begin=None):
    """
    The differences between consecutive elements of an array.

    Parameters
    ----------
    ary : array
        This array will be flattened before the difference is taken.
    to_end : number, optional
        If provided, this number will be tacked onto the end of the returned
        differences.
    to_begin : number, optional
        If provided, this number will be taked onto the beginning of the
        returned differences.

    Returns
    -------
    ed : array
        The differences. Loosely, this will be (ary[1:] - ary[:-1]).

    """
    ary = np.asarray(ary).flat
    ed = ary[1:] - ary[:-1]
    arrays = [ed]
    if to_begin is not None:
        arrays.insert(0, to_begin)
    if to_end is not None:
        arrays.append(to_end)

    if len(arrays) != 1:
        # We'll save ourselves a copy of a potentially large array in the common
        # case where neither to_begin or to_end was given.
        ed = np.hstack(arrays)

    return ed

def unique1d(ar1, return_index=False):
    """
    Find the unique elements of an array.

    Parameters
    ----------
    ar1 : array-like
        This array will be flattened if it is not already 1-D.
    return_index : bool, optional
        If True, also return the indices against `ar1` that result in the
        unique array.

    Returns
    -------
    unique : ndarray
        The unique values.
    unique_indices : ndarray, optional
        The indices of the unique values. Only provided if `return_index` is
        True.

    See Also
    --------
      numpy.lib.arraysetops : Module with a number of other functions
                              for performing set operations on arrays.

    Examples
    --------
    >>> np.unique1d([1, 1, 2, 2, 3, 3])
    array([1, 2, 3])
    >>> a = np.array([[1, 1], [2, 3]])
    >>> np.unique1d(a)
    array([1, 2, 3])

    """
    ar = np.asarray(ar1).flatten()
    if ar.size == 0:
        if return_index: return np.empty(0, np.bool), ar
        else: return ar

    if return_index:
        perm = ar.argsort()
        aux = ar[perm]
        flag = np.concatenate( ([True], aux[1:] != aux[:-1]) )
        return perm[flag], aux[flag]

    else:
        ar.sort()
        flag = np.concatenate( ([True], ar[1:] != ar[:-1]) )
        return ar[flag]

def intersect1d(ar1, ar2):
    """
    Intersection returning repeated or unique elements common to both arrays.

    Parameters
    ----------
    ar1,ar2 : array_like
        Input arrays.

    Returns
    -------
    out : ndarray, shape(N,)
        Sorted 1D array of common elements with repeating elements.

    See Also
    --------
    intersect1d_nu : Returns only unique common elements.
    numpy.lib.arraysetops : Module with a number of other functions for
                            performing set operations on arrays.

    Examples
    --------
    >>> np.intersect1d([1,3,3],[3,1,1])
    array([1, 1, 3, 3])

    """
    aux = np.concatenate((ar1,ar2))
    aux.sort()
    return aux[aux[1:] == aux[:-1]]

def intersect1d_nu(ar1, ar2):
    """
    Intersection returning unique elements common to both arrays.

    Parameters
    ----------
    ar1,ar2 : array_like
        Input arrays.

    Returns
    -------
    out : ndarray, shape(N,)
        Sorted 1D array of common and unique elements.

    See Also
    --------
    intersect1d : Returns repeated or unique common elements.
    numpy.lib.arraysetops : Module with a number of other functions for
                            performing set operations on arrays.

    Examples
    --------
    >>> np.intersect1d_nu([1,3,3],[3,1,1])
    array([1, 3])

    """
    # Might be faster than unique1d( intersect1d( ar1, ar2 ) )?
    aux = np.concatenate((unique1d(ar1), unique1d(ar2)))
    aux.sort()
    return aux[aux[1:] == aux[:-1]]

def setxor1d(ar1, ar2):
    """
    Set exclusive-or of 1D arrays with unique elements.

    Use unique1d() to generate arrays with only unique elements to use as
    inputs to this function.

    Parameters
    ----------
    ar1 : array
        Input array.
    ar2 : array
        Input array.

    Returns
    -------
    xor : array
        The values that are only in one, but not both, of the input arrays.

    See Also
    --------
    numpy.lib.arraysetops : Module with a number of other functions for
                            performing set operations on arrays.

    """
    aux = np.concatenate((ar1, ar2))
    if aux.size == 0:
        return aux

    aux.sort()
#    flag = ediff1d( aux, to_end = 1, to_begin = 1 ) == 0
    flag = np.concatenate( ([True], aux[1:] != aux[:-1], [True] ) )
#    flag2 = ediff1d( flag ) == 0
    flag2 = flag[1:] == flag[:-1]
    return aux[flag2]

def setmember1d(ar1, ar2):
    """
    Return a boolean array set True where first element is in second array.

    Boolean array is the shape of `ar1` containing True where the elements
    of `ar1` are in `ar2` and False otherwise.

    Use unique1d() to generate arrays with only unique elements to use as
    inputs to this function.

    Parameters
    ----------
    ar1 : array
        Input array.
    ar2 : array
        Input array.

    Returns
    -------
    mask : bool-array
        The values ar1[mask] are in ar2.

    See Also
    --------
    numpy.lib.arraysetops : Module with a number of other functions for
                            performing set operations on arrays.

    """
    ar1 = np.asarray( ar1 )
    ar2 = np.asarray( ar2 )
    ar = np.concatenate( (ar1, ar2 ) )
    b1 = np.zeros( ar1.shape, dtype = np.int8 )
    b2 = np.ones( ar2.shape, dtype = np.int8 )
    tt = np.concatenate( (b1, b2) )

    # We need this to be a stable sort, so always use 'mergesort' here. The
    # values from the first array should always come before the values from the
    # second array.
    perm = ar.argsort(kind='mergesort')
    aux = ar[perm]
    aux2 = tt[perm]
#    flag = ediff1d( aux, 1 ) == 0
    flag = np.concatenate( (aux[1:] == aux[:-1], [False] ) )
    ii = np.where( flag * aux2 )[0]
    aux = perm[ii+1]
    perm[ii+1] = perm[ii]
    perm[ii] = aux

    indx = perm.argsort(kind='mergesort')[:len( ar1 )]

    return flag[indx]

def union1d(ar1, ar2):
    """
    Union of 1D arrays with unique elements.

    Use unique1d() to generate arrays with only unique elements to use as
    inputs to this function.

    Parameters
    ----------
    ar1 : array_like, shape(M,)
        Input array.
    ar2 : array_like, shape(N,)
        Input array.

    Returns
    -------
    union : array
        Unique union of input arrays.

    See also
    --------
    numpy.lib.arraysetops : Module with a number of other functions for
                            performing set operations on arrays.

    """
    return unique1d( np.concatenate( (ar1, ar2) ) )

def setdiff1d(ar1, ar2):
    """
    Set difference of 1D arrays with unique elements.

    Use unique1d() to generate arrays with only unique elements to use as
    inputs to this function.

    Parameters
    ----------
    ar1 : array
        Input array.
    ar2 : array
        Input comparison array.

    Returns
    -------
    difference : array
        The values in ar1 that are not in ar2.

    See Also
    --------
    numpy.lib.arraysetops : Module with a number of other functions for
                            performing set operations on arrays.

    """
    aux = setmember1d(ar1,ar2)
    if aux.size == 0:
        return aux
    else:
        return np.asarray(ar1)[aux == 0]
