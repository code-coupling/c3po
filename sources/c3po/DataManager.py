# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class :class:`.DataManager`. """
from __future__ import print_function, division


class DataManager(object):
    """ :class:`.DataManager` is a class interface (to be implemented) which standardizes methods to handle data outside of codes.

    They are mainly mathematical operators needed for some coupling algorithms.
    """

    def clone(self):
        """ Return a clone of ``self``.

        Returns
        -------
        DataManager
            A clone of ``self``. Data are copied.
        """
        raise NotImplementedError

    def cloneEmpty(self):
        """ Return a clone of ``self`` without copying the data.

        Returns
        -------
        DataManager
            An empty clone of ``self``.
        """
        raise NotImplementedError

    def copy(self, other):
        """ Copy data of ``other`` in ``self``.

        Parameters
        ----------
        other : DataManager
            A :class:`.DataManager` with the same list of data than ``self``.

        Raises
        ------
        Exception
            If ``self`` and ``other`` are not consistent.
        """
        raise NotImplementedError

    def normMax(self):
        """ Return the infinite norm.

        Returns
        -------
            The infinite norm of all data.
        """
        raise NotImplementedError

    def norm2(self):
        """ Return the norm 2.

        Returns
        -------
            ``sqrt(sum_i(val[i] * val[i]))`` where ``val[i]`` stands for each scalar and each component of stored data.
        """
        raise NotImplementedError

    def __add__(self, other):
        """ Return ``self + other``.

        Use ``"+"`` to call it. For example ``a = b + c``.

        Parameters
        ----------
        other : DataManager
            A :class:`.DataManager` with the same list of data then ``self``.

        Returns
        -------
        DataManager
            A new (consistent with self) :class:`.DataManager` where the data are added.

        Raises
        ------
        Exception
            If ``self`` and ``other`` are not consistent.
        """
        raise NotImplementedError

    def __iadd__(self, other):
        """ Add ``other`` in ``self`` (in place addition).

        Use ``"+="`` to call it. For example ``a += b``.

        Parameters
        ----------
        other : DataManager
            A :class:`.DataManager` with the same list of data then ``self``.

        Returns
        -------
        DataManager
            ``self``.

        Raises
        ------
        Exception
            If ``self`` and ``other`` are not consistent.
        """
        raise NotImplementedError

    def __sub__(self, other):
        """ Return ``self - other``.

        Use ``"-"`` to call it. For example ``a = b - c``.

        Parameters
        ----------
        other : DataManager
            A :class:`.DataManager` with the same list of data then ``self``.

        Returns
        -------
        DataManager
            A new (consistent with self) :class:`.DataManager` where the data are substracted.

        Raises
        ------
        Exception
            If ``self`` and ``other`` are not consistent.
        """
        raise NotImplementedError

    def __isub__(self, other):
        """ Substract ``other`` to ``self`` (in place subtraction).

        Use ``"-="`` to call it. For example ``a -= b``.

        Parameters
        ----------
        other : DataManager
            A :class:`.DataManager` with the same list of data then ``self``.

        Returns
        -------
        DataManager
            ``self``.

        Raises
        ------
        Exception
            If ``self`` and ``other`` are not consistent.
        """
        raise NotImplementedError

    def __mul__(self, scalar):
        """ Return ``scalar * self``.

        Use ``"*"`` to call it. For example ``a = b * c``. The scalar first.

        Parameters
        ----------
        scalar
            A scalar value.

        Returns
        -------
        DataManager
            A new (consistent with self) :class:`.DataManager` where the data are multiplied by ``scalar``.
        """
        raise NotImplementedError

    def __imul__(self, scalar):
        """ Multiply ``self`` by ``scalar`` (in place multiplication).

        Use ``"*="`` to call it. For example ``a *= b``.

        Parameters
        ----------
        scalar
            A scalar value.

        Returns
        -------
        DataManager
            ``self``.
        """
        raise NotImplementedError

    def imuladd(self, scalar, other):
        """ Add in ``self`` ``scalar * other`` (in place operation).

        In order to do so, ``other *= scalar`` and ``other *= 1./scalar`` are done.

        For example ``a.imuladd(b, c)``.

        Parameters
        ----------
        scalar
            A scalar value.
        other : DataManager
            A :class:`.DataManager` with the same list of data then ``self``.

        Returns
        -------
        DataManager
            ``self``.

        Raises
        ------
        Exception
            If ``self`` and ``other`` are not consistent.
        """
        raise NotImplementedError

    def dot(self, other):
        """ Return the scalar product of ``self`` with ``other``.

        Parameters
        ----------
        other : DataManager
            A :class:`.DataManager` with the same list of data then ``self``.

        Returns
        -------
            The scalar product of ``self`` with ``other``.

        Raises
        ------
        Exception
            If ``self`` and ``other`` are not consistent.
        """
        raise NotImplementedError
