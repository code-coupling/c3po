import math
from typing import Tuple

import c3po
from c3po.field.Field import Field


class DictContainer(Field):
    """! Field is a class interface (to be implemented) which standardizes the data exchanged by the exchangers.

    Before an operation with another field should be calling the function checkBeforeOperator before computing the operation.
    """
    def __init__(self, value: dict):
        self.value = value

    def clone(self):
        """! Return a clone of self.

        @return A clone of self. Data are copied.
        """
        return self * 1.

    def cloneEmpty(self):
        """! Return a clone of self without copying the data.

        @return An empty clone of self.
        """
        return DictContainer({})

    def copy(self, other):
        """! Copy data of other in self.

        @param other a LocalDataManager with the same list of data than self.

        @throw Exception if self and other are not consistent.
        """
        self.checkBeforeOperator(other)
        for key, value in other.value.items():
            self.value[key] = value

    def checkBeforeOperator(self, other: "DictContainer"):
        """! INTERNAL Make basic checks before the call of an operator: same data type, same lengths..."""
        assert set(self.value.keys()) == set(other.value.keys())

    def normMax(self):
        """! Return the infinite norm.

        @return The max of the absolute values of the scalars and of the infinite norms of the MED fields.
        """
        return max(self.value.values())

    def norm2(self):
        """! Return the norm 2.

        @return sqrt(sum_i(val[i] * val[i])) where val[i] stands for each scalar and each component of the MED fields.
        """
        return math.sqrt(sum([v**2 for v in self.value.values()]))

    def __add__(self, other: "DictContainer"):
        """! Return self + other.

        Use "+" to call it. For example a = b + c.

        @param other a DataManager with the same list of data then self.

        @return a new (consistent with self) DataManager where the data are added.

        @throw Exception if self and other are not consistent.
        """
        self.checkBeforeOperator(other)
        newContainer = DictContainer(self.value.copy())
        for key, value in other.value.items():
            newContainer.value[key] += value

        return newContainer

    def __iadd__(self, other: "DictContainer"):
        """! Add other in self (in place addition).

        Use "+=" to call it. For example a += b.

        @param other a DataManager with the same list of data then self.

        @return self.

        @throw Exception if self and other are not consistent.
        """
        self.checkBeforeOperator(other)
        for key, value in other.value.items():
            self.value[key] += value
        return self

    def __sub__(self, other: "DictContainer"):
        """! Return self - other.

        Use "-" to call it. For example a = b - c.

        @param other a DataManager with the same list of data then self.

        @return a new (consistent with self) DataManager where the data are substracted.

        @throw Exception if self and other are not consistent.
        """
        self.checkBeforeOperator(other)
        newContainer = DictContainer(self.value.copy())
        for key, value in other.value.items():
            newContainer.value[key] -= value

        return newContainer

    def __isub__(self, other: "DictContainer"):
        """! Substract other to self (in place subtraction).

        Use "-=" to call it. For example a -= b.

        @param other a DataManager with the same list of data then self.

        @return self.

        @throw Exception if self and other are not consistent.
        """
        self.checkBeforeOperator(other)
        for key, value in other.value.items():
            self.value[key] -= value
        return self

    def __mul__(self, scalar):
        """! Return scalar * self.

        Use "*" to call it. For example a = b * c. The scalar first.

        @param scalar a scalar value.

        @return a new (consistent with self) DataManager where the data are multiplied by scalar.
        """
        newContainer = DictContainer(self.value.copy())
        for key, value in self.value.items():
            newContainer.value[key] *= scalar

        return newContainer

    def __imul__(self, scalar):
        """! Multiply self by scalar (in place multiplication).

        Use "*=" to call it. For example a *= b.

        @param scalar a scalar value.

        @return self.
        """
        for key, value in self.value.items():
            self.value[key] *= scalar
        return self

    def __rmul__(self, scalar):
        """! Return self * scalar (reverse multiplication).

        Use "*" to call it. For example a = c * b.

        @param scalar a scalar value.

        @return a new (consistent with self) DataManager where the data are multiplied by scalar.
        """
        return self.__imul__(scalar)

    def imuladd(self, scalar, other: "DictContainer"):
        """! Add in self scalar * other (in place operation).

        In order to do so, other *= scalar and other *= 1./scalar are done.

        For example a.imuladd(b, c).

        @param scalar a scalar value.
        @param other a DataManager with the same list of data then self.

        @return self.

        @throw Exception if self and other are not consistent.
        """
        if scalar == 0:
            return self
        self.checkBeforeOperator(other)
        other *= scalar
        self += other
        other *= 1. / scalar
        return self

    def dot(self, other: "DictContainer"):
        """! Return the scalar product of self with other.

        @param other a DataManager with the same list of data then self.

        @return the scalar product of self with other.

        @throw Exception if self and other are not consistent.
        """
        self.checkBeforeOperator(other)
        return sum([
            e * f for e, f in zip(self.value.values(), other.value.values())
        ])


class ObjectDriver(c3po.PhysicsDriver):
    """Physics driver of a damped pendulum.
    """

    def __init__(self, init_dict: Field):
        super().__init__()

        # Parameters of the damped pendulum
        self.value: Field = init_dict * 1
        self.last_value: Field = init_dict * 1

    def initialize(self):
        pass

    def terminate(self):
        pass

    def presentTime(self) -> float:
        pass

    def computeTimeStep(self) -> Tuple[float, bool]:
        return (1., False)

    def initTimeStep(self, dt: float):
        pass

    def solveTimeStep(self) -> Tuple[bool, bool]:
        self.value = self.value * 0.25
        for key in self.value.value:
            self.value.value[key] += 1

        return True, False  # (succeed, converged)

    def abortTimeStep(self, ):
        """Reverts the current time step
        """
        self.value = self.last_value.clone()

    def validateTimeStep(self):
        pass

    def setInputObject(self, name: str, value: Field):
        """Setting the value from a Field as defined in the ShortcutToDict class

        Parameters
        ----------
        name : str
            value name
        value : Field
            value
        """
        self.value = value

    def getOutputObject(self, name: str) -> Field:
        """Returns a Field as defined in the ShortcutToDict class

        Parameters
        ----------
        name : str
            Value name

        Returns
        -------
        Field
            Value
        """
        return self.value
