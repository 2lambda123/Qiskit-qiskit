# This code is part of Qiskit.
#
# (C) Copyright IBM 2022.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

r"""

.. estimator-desc:

=====================
Overview of Estimator
=====================

Estimator class estimates expectation values of quantum circuits and observables.

An estimator is initialized with an empty parameter set. The estimator is used to
create a :class:`~qiskit.providers.JobV1`, via the
:meth:`qiskit.primitives.Estimator.run()` method. This method is called
with the following parameters

* quantum circuits (:math:`\psi_i(\theta)`): list of (parameterized) quantum circuits
  (a list of :class:`~qiskit.circuit.QuantumCircuit` objects).

* observables (:math:`H_j`): a list of :class:`~qiskit.quantum_info.SparsePauliOp`
  objects.

* parameter values (:math:`\theta_k`): list of sets of values
  to be bound to the parameters of the quantum circuits
  (list of list of float).

The method returns a :class:`~qiskit.providers.JobV1` object, calling
:meth:`qiskit.providers.JobV1.result()` yields the
a list of expectation values plus optional metadata like confidence intervals for
the estimation.

.. math::

    \langle\psi_i(\theta_k)|H_j|\psi_i(\theta_k)\rangle

Here is an example of how the estimator is used.

.. code-block:: python

    from qiskit.primitives import Estimator
    from qiskit.circuit.library import RealAmplitudes
    from qiskit.quantum_info import SparsePauliOp

    psi1 = RealAmplitudes(num_qubits=2, reps=2)
    psi2 = RealAmplitudes(num_qubits=2, reps=3)

    H1 = SparsePauliOp.from_list([("II", 1), ("IZ", 2), ("XI", 3)])
    H2 = SparsePauliOp.from_list([("IZ", 1)])
    H3 = SparsePauliOp.from_list([("ZI", 1), ("ZZ", 1)])

    theta1 = [0, 1, 1, 2, 3, 5]
    theta2 = [0, 1, 1, 2, 3, 5, 8, 13]
    theta3 = [1, 2, 3, 4, 5, 6]

    estimator = Estimator()

    # calculate [ <psi1(theta1)|H1|psi1(theta1)> ]
    job = estimator.run([psi1], [H1], [theta1])
    job_result = job.result() # It will block until the job finishes.
    print(f"The primitive-job finished with result {job_result}"))

    # calculate [ <psi1(theta1)|H1|psi1(theta1)>,
    #             <psi2(theta2)|H2|psi2(theta2)>,
    #             <psi1(theta3)|H3|psi1(theta3)> ]
    job2 = estimator.run([psi1, psi2, psi1], [H1, H2, H3], [theta1, theta2, theta3])
    job_result = job2.result()
    print(f"The primitive-job finished with result {job_result}")
"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Sequence
from copy import copy
from typing import Generic, TypeVar
import typing

from qiskit.circuit import QuantumCircuit
from qiskit.circuit.parametertable import ParameterView
from qiskit.providers import JobV1 as Job
from qiskit.quantum_info.operators import SparsePauliOp
from qiskit.quantum_info.operators.base_operator import BaseOperator
from qiskit.utils.deprecation import deprecate_func

from .base_primitive import BasePrimitive
from . import validation

if typing.TYPE_CHECKING:
    from qiskit.opflow import PauliSumOp

T = TypeVar("T", bound=Job)


class BaseEstimator(BasePrimitive, Generic[T]):
    """Estimator base class.

    Base class for Estimator that estimates expectation values of quantum circuits and observables.
    """

    __hash__ = None

    def __init__(
        self,
        *,
        options: dict | None = None,
    ):
        """
        Creating an instance of an Estimator, or using one in a ``with`` context opens a session that
        holds resources until the instance is ``close()`` ed or the context is exited.

        Args:
            options: Default options.
        """
        self._circuits = []
        self._observables = []
        self._parameters = []
        super().__init__(options)

    def run(
        self,
        circuits: Sequence[QuantumCircuit] | QuantumCircuit,
        observables: Sequence[BaseOperator | PauliSumOp | str] | BaseOperator | PauliSumOp | str,
        parameter_values: Sequence[Sequence[float]] | Sequence[float] | float | None = None,
        **run_options,
    ) -> T:
        """Run the job of the estimation of expectation value(s).

        ``circuits``, ``observables``, and ``parameter_values`` should have the same
        length. The i-th element of the result is the expectation of observable

        .. code-block:: python

            obs = observables[i]

        for the state prepared by

        .. code-block:: python

            circ = circuits[i]

        with bound parameters

        .. code-block:: python

            values = parameter_values[i].

        .. deprecated:: 0.46.0
           Implicit conversion from a ``PauliList`` to a ``SparsePauliOp`` with ``coeffs=1`` in
           the ``observables`` arguments is deprecated as of Qiskit 0.46 and will be removed
           in Qiskit 1.0. You should explicitly convert to a ``SparsePauli`` using
           ``SparsePauliOp(pauli_list)`` to avoid this warning.

        Args:
            circuits: one or more circuit objects.
            observables: one or more observable objects. Several formats are allowed;
                importantly, ``str`` should follow the string representation format for
                :class:`~qiskit.quantum_info.Pauli` objects.
            parameter_values: concrete parameters to be bound.
            run_options: runtime options used for circuit execution.

        Returns:
            The job object of EstimatorResult.

        Raises:
            TypeError: Invalid argument type given.
            ValueError: Invalid argument values given.
        """
        # Validation
        circuits, observables, parameter_values = validation._validate_estimator_args(
            circuits, observables, parameter_values
        )

        # Options
        run_opts = copy(self.options)
        run_opts.update_options(**run_options)

        return self._run(
            circuits,
            observables,
            parameter_values,
            **run_opts.__dict__,
        )

    @abstractmethod
    def _run(
        self,
        circuits: tuple[QuantumCircuit, ...],
        observables: tuple[SparsePauliOp, ...],
        parameter_values: tuple[tuple[float, ...], ...],
        **run_options,
    ) -> T:
        raise NotImplementedError("The subclass of BaseEstimator must implement `_run` method.")

    @staticmethod
    @deprecate_func(since="0.46.0")
    def _validate_observables(
        observables: Sequence[BaseOperator | PauliSumOp | str] | BaseOperator | PauliSumOp | str,
    ) -> tuple[SparsePauliOp, ...]:
        return validation._validate_observables(observables)

    @staticmethod
    @deprecate_func(since="0.46.0")
    def _cross_validate_circuits_observables(
        circuits: tuple[QuantumCircuit, ...], observables: tuple[BaseOperator | PauliSumOp, ...]
    ) -> None:
        return validation._cross_validate_circuits_observables(circuits, observables)

    @property
    def circuits(self) -> tuple[QuantumCircuit, ...]:
        """Quantum circuits that represents quantum states.

        Returns:
            The quantum circuits.
        """
        return tuple(self._circuits)

    @property
    def observables(self) -> tuple[SparsePauliOp, ...]:
        """Observables to be estimated.

        Returns:
            The observables.
        """
        return tuple(self._observables)

    @property
    def parameters(self) -> tuple[ParameterView, ...]:
        """Parameters of the quantum circuits.

        Returns:
            Parameters, where ``parameters[i][j]`` is the j-th parameter of the i-th circuit.
        """
        return tuple(self._parameters)
