#!/usr/bin/env python3

import numpy as np

class CircularBufferIterator:
	def __init__(self, circularBuffer):
		assert(isinstance(circularBuffer, CircularBuffer))
		self._buffer = circularBuffer
		self._idx = 0

	def __next__(self):
		if self._idx < len(self._buffer):
			self._idx += 1
			return self._buffer[self._idx - 1]
		else:
			raise StopIteration


class CircularBuffer:
	def __init__(self, n):
		assert(n > 0)
		self._elements = [None] * n
		self._idx = 0
		self._numElements = 0
		self._shape = None

	def __getitem__(self, k):
		assert(k < min(self._numElements, len(self._elements)))
		assert(k >= -min(self._numElements, len(self._elements)))
		if k >= 0:
			return self._elements[(self._idx - len(self) + k) % len(self._elements)]
		else:
			return self._elements[(self._idx + k) % len(self._elements)]

	def __setitem__(self, k, val):
		assert(k < min(self._numElements, len(self._elements)))
		assert(k >= -min(self._numElements, len(self._elements)))
		assert(isinstance(val, np.ndarray))
		if k >= 0:
			self._elements[(self._idx - len(self) + k) % len(self._elements)] = val
		else:
			self._elements[(self._idx + k) % len(self._elements)]


	def add(self, value):
		assert(isinstance(value, np.ndarray))
		if self._shape is None:
			self._shape = value.shape
		else:
			assert(value.shape == self._shape)
		self._elements[self._idx] = value
		self._idx += 1
		self._idx %= len(self._elements)
		self._numElements += 1

	def __repr__(self):
		return '[' + ', '.join([repr(self._elements[idx]) for idx in list(range(self._idx, len(self._elements))) + list(range(0, self._idx))]) + ']'

	def __len__(self):
		return min(self._numElements, len(self._elements))

	def __iter__(self):
		return CircularBufferIterator(self)

	def max(self):
		maxVec = self._elements[0]
		for e in self._elements:
			if e is not None:
				maxVec = np.maximum(maxVec, e)
		return maxVec

	def median(self):
		return np.median(np.array(self._elements), axis=0)

	def to_array(self):
		newList = []
		for i in range(len(self)):
			newList.append(self[i])
		return np.block(newList)

	def sum(self):
		retval = np.zeros(self._shape)
		for vec in self:
			retval = retval + vec
		return retval
