# This code is part of Qiskit.
#
# (C) Copyright IBM 2020, 2023.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""EvolutionBase Class"""

from abc import ABC, abstractmethod

from qiskit.opflow.operator_base import OperatorBase
from qiskit.opflow.converters.converter_base import ConverterBase
from qiskit.utils.deprecation import deprecate_func


class EvolutionBase(ConverterBase, ABC):
    r"""
    Deprecated: A base for Evolution converters.
    Evolutions are converters which traverse an Operator tree, replacing any ``EvolvedOp`` `e`
    with a Schrodinger equation-style evolution ``CircuitOp`` equalling or approximating the
    matrix exponential of -i * the Operator contained inside (`e.primitive`). The Evolutions are
    essentially implementations of Hamiltonian Simulation algorithms, including various methods
    for Trotterization.

    """

    @deprecate_func(
        removal_timeline="in the Qiskit 1.0 release",
        since="0.24.0",
        package_name="qiskit-terra",
        additional_msg="For code migration guidelines, visit https://qisk.it/opflow_migration.",
    )
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def convert(self, operator: OperatorBase) -> OperatorBase:
        """Traverse the operator, replacing any ``EvolutionOps`` with their equivalent evolution
        ``CircuitOps``.

         Args:
             operator: The Operator to convert.

        Returns:
            The converted Operator, with ``EvolutionOps`` replaced by ``CircuitOps``.

        """
        raise NotImplementedError

    # TODO @abstractmethod
    # def error_bounds(self):
    #     """ error bounds """
    #     raise NotImplementedError
