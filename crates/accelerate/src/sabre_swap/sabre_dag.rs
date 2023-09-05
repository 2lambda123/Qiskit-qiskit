// This code is part of Qiskit.
//
// (C) Copyright IBM 2022
//
// This code is licensed under the Apache License, Version 2.0. You may
// obtain a copy of this license in the LICENSE.txt file in the root directory
// of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
//
// Any modifications or derivative works of this code must retain this
// copyright notice, and modified files need to carry a notice indicating
// that they have been altered from the originals.

use hashbrown::HashMap;
use hashbrown::HashSet;
use pyo3::exceptions::PyIndexError;
use pyo3::prelude::*;
use rustworkx_core::petgraph::prelude::*;

/// A DAG object used to represent the data interactions from a DAGCircuit
/// to run the the sabre algorithm. This is structurally identical to the input
/// DAGCircuit, but the contents of the node are a tuple of DAGCircuit node ids,
/// a list of qargs and a list of cargs
#[pyclass(module = "qiskit._accelerate.sabre_swap")]
#[derive(Clone, Debug)]
pub struct SabreDAG {
    pub num_qubits: usize,
    pub num_clbits: usize,
    pub dag: DiGraph<(usize, Vec<usize>), ()>,
    pub first_layer: Vec<NodeIndex>,
    pub nodes: Vec<(usize, Vec<usize>, HashSet<usize>)>,
    pub node_blocks: HashMap<usize, Vec<SabreDAG>>,
}

#[pymethods]
impl SabreDAG {
    #[new]
    #[pyo3(text_signature = "(num_qubits, num_clbits, nodes, node_blocks, /)")]
    pub fn new(
        num_qubits: usize,
        num_clbits: usize,
        nodes: Vec<(usize, Vec<usize>, HashSet<usize>)>,
        node_blocks: HashMap<usize, Vec<SabreDAG>>,
    ) -> PyResult<Self> {
        let mut qubit_pos: Vec<Option<NodeIndex>> = vec![None; num_qubits];
        let mut clbit_pos: Vec<Option<NodeIndex>> = vec![None; num_clbits];
        let mut dag: DiGraph<(usize, Vec<usize>), ()> =
            Graph::with_capacity(nodes.len(), 2 * nodes.len());
        let mut first_layer = Vec::<NodeIndex>::new();
        for node in &nodes {
            let qargs = &node.1;
            let cargs = &node.2;
            let gate_index = dag.add_node((node.0, qargs.clone()));
            let mut is_front = true;
            for x in qargs {
                let pos = qubit_pos.get_mut(*x).ok_or_else(|| {
                    PyIndexError::new_err(format!(
                        "qubit index {} is out of range for {} qubits",
                        *x, num_qubits
                    ))
                })?;
                if let Some(predecessor) = *pos {
                    is_front = false;
                    dag.add_edge(predecessor, gate_index, ());
                }
                *pos = Some(gate_index);
            }
            for x in cargs {
                let pos = clbit_pos.get_mut(*x).ok_or_else(|| {
                    PyIndexError::new_err(format!(
                        "clbit index {} is out of range for {} clbits",
                        *x, num_qubits
                    ))
                })?;
                if let Some(predecessor) = *pos {
                    is_front = false;
                    dag.add_edge(predecessor, gate_index, ());
                }
                *pos = Some(gate_index);
            }
            if is_front {
                first_layer.push(gate_index);
            }
        }
        Ok(SabreDAG {
            num_qubits,
            num_clbits,
            dag,
            first_layer,
            nodes,
            node_blocks,
        })
    }
}

#[cfg(test)]
mod test {
    use super::SabreDAG;
    use hashbrown::{HashMap, HashSet};

    #[test]
    fn no_panic_on_bad_qubits() {
        assert!(SabreDAG::new(2, 0, vec![(0, vec![0, 2], HashSet::new())], HashMap::new()).is_err())
    }

    #[test]
    fn no_panic_on_bad_clbits() {
        assert!(SabreDAG::new(2, 1, vec![(0, vec![0, 1], [0, 1].into())], HashMap::new()).is_err())
    }
}
