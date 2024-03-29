# This code is part of Qiskit.
#
# (C) Copyright IBM 2020.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.
"""Tests .utils.get_truthtable_from_function function"""

import unittest

from qiskit.utils.optionals import HAS_TWEEDLEDUM
from test import QiskitTestCase  # pylint: disable=wrong-import-order

from .utils import get_truthtable_from_function
from . import examples


@unittest.skipUnless(HAS_TWEEDLEDUM, "Tweedledum is required for these tests.")
class TestGetTruthtableFromFunction(QiskitTestCase):
    """Tests .utils.get_truthtable_from_function function"""

    def test_grover_oracle(self):
        """Tests get_truthtable_from_function with examples.grover_oracle"""
        truth_table = get_truthtable_from_function(examples.grover_oracle)
        self.assertEqual(truth_table, "0000010000000000")
